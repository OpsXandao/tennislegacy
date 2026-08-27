"""
Pipeline de avanço semanal da temporada.

Cada etapa recebe um `SemanaContext` e o mutaciona.  O estado compartilhado
é explícito — sem variáveis locais espalhadas em uma função monolítica.

Ordem do pipeline:
  1. recuperar_npcs          — recuperação física de todos os NPCs
  2. simular_torneios        — torneios NPC da semana atual
  3. avancar_calendario      — incrementa semana/ano
  4. expirar_pontos          — point-decay do novo período
  5. processar_jogador       — recuperação, lesão, fadiga do jogador humano
  6. processar_financas      — gestão de carreira, emails, patrocínios
  7. inicializar_nova_semana — snapshot, reset de modalidade, salva, init torneios
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Any

from src.constants.torneio_constants import START_YEAR
from src.domain_types import SeasonState, RankingsByTour, TournamentState
from src.utils.log_jogo import log_erro

if TYPE_CHECKING:
    from src.jogador import Jogador
    from src.ranking import SistemaRanking


@dataclass
class SemanaContext:
    nome_save: str
    temporada: SeasonState
    jogador: "Jogador"
    rankings: RankingsByTour
    ranking: "SistemaRanking"  # principal do gênero do jogador
    semana_atual: int
    ano_atual: int
    player_active_tournament_state: Optional[TournamentState]
    jogador_em_torneio_ativo: bool
    jogador_participou: bool
    # Preenchidos pelas etapas
    semana_nova: int = 0
    ano_novo: int = 0
    torneio_info_semana: Optional[dict] = None
    resumo_campeoes: list = field(default_factory=list)
    torneios_semana_atual: list = field(default_factory=list)
    eventos_api: list = field(default_factory=list)
    recuperacao: dict = field(default_factory=dict)
    torneios_disponiveis: list = field(default_factory=list)
    pontos_expirados: int = 0
    nova_posicao_ranking: int | None = None
    rival_info: dict | None = None
    processamento_etapas: list[dict] = field(default_factory=list)


STAGE_META = {
    "_recuperar_npcs": {
        "id": "recover_npcs",
        "titulo": "Recuperação global",
        "resumo": "Recuperando energia e disponibilidade física do circuito.",
        "tom": "info",
    },
    "_simular_torneios": {
        "id": "simulate_tournaments",
        "titulo": "Resultados do circuito",
        "resumo": "Consolidando torneios da semana e definindo campeões.",
        "tom": "neutral",
    },
    "_avancar_calendario": {
        "id": "advance_calendar",
        "titulo": "Calendário",
        "resumo": "Virando a semana oficial da temporada.",
        "tom": "info",
    },
    "_expirar_pontos": {
        "id": "expire_points",
        "titulo": "Ranking",
        "resumo": "Aplicando expiração e recomposição dos pontos.",
        "tom": "warning",
    },
    "_processar_jogador": {
        "id": "process_player",
        "titulo": "Seu jogador",
        "resumo": "Atualizando recuperação, fadiga e status físico.",
        "tom": "positive",
    },
    "_processar_eventos_narrativos": {
        "id": "narrative_events",
        "titulo": "Vida de Atleta",
        "resumo": "Acontecimentos e bastidores da sua rotina.",
        "tom": "info",
    },
    "_processar_logistica": {
        "id": "process_logistics",
        "titulo": "Logística e Viagens",
        "resumo": "Organizando deslocamentos entre torneios e continentes.",
        "tom": "neutral",
    },
    "_processar_financas": {
        "id": "process_finances",
        "titulo": "Carreira",
        "resumo": "Processando finanças, equipe, mídia e bastidores.",
        "tom": "neutral",
    },
    "_processar_convites_duplas": {
        "id": "doubles_invites",
        "titulo": "Convites de Duplas",
        "resumo": "Jogadores do tour interessados em formar parceria.",
        "tom": "positive",
    },
    "_processar_dinamica_staff": {
        "id": "staff_dynamics",
        "titulo": "Equipe e Bastidores",
        "resumo": "Processando clima interno e conselhos da sua equipe tecnica.",
        "tom": "info",
    },
    "_inicializar_nova_semana": {
        "id": "init_next_week",
        "titulo": "Nova semana",
        "resumo": "Preparando agenda, ranking e torneios disponíveis.",
        "tom": "positive",
    },
}


def _resumir_eventos_etapa(eventos: list[str], categoria: str = "info") -> list[dict]:
    detalhes: list[dict] = []
    for evento in eventos:
        texto = str(evento or "").strip()
        if not texto:
            continue
        detalhes.append({"texto": texto, "categoria": categoria})
        if len(detalhes) >= 4:
            break
    return detalhes


def _registrar_etapa(
    ctx: SemanaContext, nome_etapa: str, eventos_etapa: list[str]
) -> None:
    meta = STAGE_META.get(nome_etapa)
    if not meta:
        return

    # Mapeamento de categoria padrão por etapa
    cat_padrao = "info"
    if nome_etapa == "_simular_torneios":
        cat_padrao = "success"
    if nome_etapa == "_expirar_pontos":
        cat_padrao = "warning"
    if nome_etapa == "_processar_financas":
        cat_padrao = "finance"
    if nome_etapa == "_processar_eventos_narrativos":
        cat_padrao = "narrative"

    detalhes = _resumir_eventos_etapa(eventos_etapa, categoria=cat_padrao)

    if nome_etapa == "_simular_torneios" and ctx.resumo_campeoes:
        for item in ctx.resumo_campeoes[:3]:
            detalhes.append(
                {
                    "texto": f"{item.get('tour', 'TOUR')}: {item.get('torneio', 'Torneio')} — {item.get('simples', 'Campeão')}",
                    "categoria": "success",
                }
            )
    elif nome_etapa == "_expirar_pontos" and ctx.pontos_expirados > 0:
        detalhes.insert(
            0,
            {
                "texto": f"{ctx.pontos_expirados} pontos saíram da conta semanal.",
                "categoria": "warning",
            },
        )
    elif nome_etapa == "_processar_jogador":
        fadiga_antes = int(round(ctx.recuperacao.get("fadiga_antes", 0)))
        fadiga_depois = int(round(ctx.recuperacao.get("fadiga_depois", 0)))
        status_fis = ctx.recuperacao.get("lesao_status", "saudavel")
        detalhes.insert(
            0,
            {
                "texto": f"Fadiga: {fadiga_antes}% → {fadiga_depois}%",
                "categoria": "info",
            },
        )
        detalhes.insert(
            1,
            {
                "texto": f"Status físico: {status_fis}",
                "categoria": "warning" if status_fis != "saudavel" else "success",
            },
        )
    elif nome_etapa == "_inicializar_nova_semana":
        detalhes.insert(
            0,
            {
                "texto": f"Semana {ctx.semana_nova}/{ctx.ano_novo} pronta.",
                "categoria": "success",
            },
        )
        detalhes.insert(
            1,
            {
                "texto": f"Torneios disponíveis: {len(ctx.torneios_disponiveis)}",
                "categoria": "info",
            },
        )

    ctx.processamento_etapas.append(
        {
            "id": meta["id"],
            "titulo": meta["titulo"],
            "resumo": meta["resumo"],
            "tom": meta["tom"],
            "detalhes": detalhes[:6],
        }
    )


def _somar_pontos_detalhados(
    jogador_ranking: object, modalidade: str = "simples"
) -> int:
    if not isinstance(jogador_ranking, dict):
        return 0

    chave = (
        "pontos_detalhados_duplas" if modalidade == "duplas" else "pontos_detalhados"
    )
    detalhes = jogador_ranking.get(chave, [])
    if isinstance(detalhes, list) and detalhes:
        return sum(
            int(item.get("pontos", 0) or 0)
            for item in detalhes
            if isinstance(item, dict)
        )
    return int(jogador_ranking.get("pontos", 0) or 0)


def _buscar_registro_jogador_ranking(ctx: SemanaContext) -> dict | None:
    buscar = getattr(ctx.ranking, "buscar_jogador_por_nome", None)
    if not callable(buscar):
        return None
    registro = buscar(getattr(ctx.jogador, "nome", ""))
    return registro if isinstance(registro, dict) else None


def _recarregar_ranking_principal(ctx: SemanaContext) -> None:
    from src.repositories.ranking_repository import load_singles_ranking

    genero = getattr(ctx.jogador, "genero", "masculino")
    chave = "simples_atp" if genero == "masculino" else "simples_wta"
    ranking_atualizado = load_singles_ranking(ctx.nome_save, genero)
    ctx.rankings[chave] = ranking_atualizado
    ctx.ranking = ranking_atualizado


def _resetar_estado_semanal_jogador(ctx: SemanaContext) -> None:
    ctx.jogador.modalidade_atual = "simples"
    ctx.jogador.parceiro_duplas = None


def _registrar_historico_ranking(ctx: SemanaContext, pontos: int) -> None:
    if not hasattr(ctx.jogador, "historico_ranking"):
        ctx.jogador.historico_ranking = []

    ctx.jogador.historico_ranking.append(
        {
            "semana": ctx.semana_nova,
            "ano": ctx.ano_novo,
            "posicao": ctx.nova_posicao_ranking or 0,
            "pontos": int(pontos),
        }
    )


def _atualizar_contexto_ranking_pos_semana(ctx: SemanaContext) -> None:
    from src.jogador import obter_rival_info

    _recarregar_ranking_principal(ctx)
    ordenar = getattr(ctx.ranking, "ordenar", None)
    if callable(ordenar):
        try:
            ordenar(modalidade="simples", recalculate=False)
        except TypeError:
            ordenar()

    obter_posicao = getattr(ctx.ranking, "obter_posicao", None)
    if callable(obter_posicao):
        ctx.nova_posicao_ranking = obter_posicao(ctx.jogador.nome, modalidade="simples")

    ctx.rival_info = obter_rival_info(ctx.jogador, ranking=ctx.ranking)
    jogador_ranking = ctx.ranking.buscar_jogador_por_nome(ctx.jogador.nome)
    pontos = jogador_ranking.get("pontos_ranking", 0) if jogador_ranking else 0
    _registrar_historico_ranking(ctx, pontos)


# ---------------------------------------------------------------------------
# Etapas do pipeline
# ---------------------------------------------------------------------------


def _recuperar_npcs(ctx: SemanaContext) -> None:
    from src.services.health_service import recuperar_npcs_semana

    recuperar_npcs_semana(ctx.rankings)


def _simular_torneios(ctx: SemanaContext) -> None:
    from src import calendario as cal
    from src.dados import obter_torneios_da_semana
    from src.pontuacao import aplicar_penalidade_ausencia

    ctx.resumo_campeoes = cal._simular_torneios_semanais_npc(
        ctx.nome_save,
        ctx.semana_atual,
        ctx.ranking,
        ctx.jogador,
        ctx.player_active_tournament_state,
    )

    genero = getattr(ctx.jogador, "genero", "masculino")
    ctx.torneios_semana_atual = obter_torneios_da_semana(
        ctx.semana_atual, genero=genero
    )

    if not ctx.jogador_em_torneio_ativo:
        for t in ctx.torneios_semana_atual:
            tipo = t.get("tipo", "")
            nome = t.get("nome", "")
            if nome and tipo:
                aplicar_penalidade_ausencia(
                    ctx.nome_save,
                    nome,
                    tipo,
                    ctx.semana_atual,
                    ctx.ano_atual,
                    genero,
                )


def _processar_virada_ano(
    temporada: dict, jogador: Any, rankings: dict, eventos_api: list
):
    if temporada["semana"] <= 52:
        return

    from src.progressao import processar_envelhecimento_anual
    from src.jogador import normalizar_nome

    temporada["semana"] = 1
    temporada["ano"] += 1
    eventos_api.append(f"Feliz Ano Novo! Bem-vindo a {temporada['ano']}!")

    processar_envelhecimento_anual(jogador)
    jogador.pontos_ytd = 0

    nome_humano_norm = normalizar_nome(jogador.nome)
    for rk_obj in (rankings.get("simples_atp"), rankings.get("simples_wta")):
        if not rk_obj:
            continue
        for j in getattr(rk_obj, "ranking", []) or []:
            if normalizar_nome(j.get("nome", "")) == nome_humano_norm:
                j["pontos_ytd"] = 0
                continue
            processar_envelhecimento_anual(j)
            j["pontos_ytd"] = 0
        rk_obj.salvar_ranking()


def _avancar_calendario(ctx: SemanaContext) -> None:
    ctx.temporada["semana"] += 1
    _processar_virada_ano(ctx.temporada, ctx.jogador, ctx.rankings, ctx.eventos_api)
    ctx.semana_nova = ctx.temporada["semana"]
    ctx.ano_novo = ctx.temporada["ano"]
    ctx.eventos_api.append(
        f"Semana avancada para {ctx.semana_nova}/{ctx.temporada['ano']}."
    )


def _expirar_pontos(ctx: SemanaContext) -> None:
    from src.services.ranking_service import processar_expiracao_ranking

    pontos_antes = _somar_pontos_detalhados(_buscar_registro_jogador_ranking(ctx))
    processar_expiracao_ranking(ctx.nome_save, ctx.semana_nova, ctx.ano_novo)
    _recarregar_ranking_principal(ctx)
    pontos_depois = _somar_pontos_detalhados(_buscar_registro_jogador_ranking(ctx))
    ctx.pontos_expirados = max(0, pontos_antes - pontos_depois)
    ctx.jogador.semana = ctx.semana_nova


def _processar_jogador(ctx: SemanaContext) -> None:
    from src import calendario as cal
    from src.fadiga import (
        aplicar_fadiga_extra_energia_final,
        calcular_condicao_pre_partida,
    )

    if ctx.jogador_em_torneio_ativo:
        sem_ref = ctx.player_active_tournament_state.get("semana", ctx.semana_atual)
        ctx.torneio_info_semana = cal.obter_torneio_por_nome(
            sem_ref,
            ctx.player_active_tournament_state.get("torneio"),
            genero=ctx.jogador.genero,
        )

    fadiga_antes = float(getattr(ctx.jogador, "fadiga", 0) or 0)

    # Ajuste de fadiga pós-partida pelo nível de energia final
    if ctx.jogador_participou:
        energia_final = int(getattr(ctx.jogador, "energia", 100) or 100)
        aplicar_fadiga_extra_energia_final(ctx.jogador, energia_final)

    eventos = cal._atualizar_recuperacao_jogador(
        ctx.jogador, info_torneio=ctx.torneio_info_semana
    )
    ctx.eventos_api.extend(eventos)

    if not ctx.jogador_participou:
        ctx.jogador.fadiga = max(0, ctx.jogador.fadiga - 20)
        if ctx.jogador.energia < 95:
            ctx.jogador.energia = min(100, ctx.jogador.energia + 15)
        ctx.eventos_api.append("Semana de descanso com bonus de recuperacao fisica.")

    # Calcula condição pré-partida para a próxima semana
    dias_descanso = 2  # default seguro (jogador sem torneio imediato)
    if ctx.jogador_participou and ctx.semana_nova:
        dias_descanso = 1  # jogou esta semana, menos descanso
    ctx.jogador.condicao = calcular_condicao_pre_partida(
        getattr(ctx.jogador, "fadiga", 0), dias_descanso
    )

    # Processamento de Ritmo de Jogo
    processar_ritmo = getattr(ctx.jogador, "processar_ritmo_semanal", None)
    if callable(processar_ritmo):
        processar_ritmo(participou=ctx.jogador_participou)
    if not ctx.jogador_participou:
        ctx.eventos_api.append(
            "Sua inatividade esta deixando seu ritmo de jogo 'enferrujado'."
        )
    else:
        try:
            ritmo_jogo = int(getattr(ctx.jogador, "ritmo_jogo", 0) or 0)
        except (TypeError, ValueError):
            ritmo_jogo = 0
        if ritmo_jogo >= 85:
            ctx.eventos_api.append(
                "Voce esta com o ritmo de jogo em dia. Suas pancadas estao saindo com precisao."
            )

    # Erosão de Atributos (Realismo de Manutenção)
    from src.progressao import processar_erosao_semanal

    erosaos = processar_erosao_semanal(ctx.jogador, participou=ctx.jogador_participou)
    ctx.eventos_api.extend(erosaos)

    status_lesao = (
        getattr(ctx.jogador, "status_lesao", {})
        if isinstance(getattr(ctx.jogador, "status_lesao", {}), dict)
        else {}
    )
    ctx.recuperacao = {
        "fadiga_antes": fadiga_antes,
        "fadiga_depois": float(getattr(ctx.jogador, "fadiga", 0) or 0),
        "lesao_status": str(status_lesao.get("nivel", "saudavel") or "saudavel"),
    }


def _processar_eventos_narrativos(ctx: SemanaContext) -> None:
    """Dispara eventos narrativos aleatórios semanais carregados do JSON."""
    try:
        from pathlib import Path
        import json

        caminho = Path(__file__).parent.parent.parent / "db" / "narrativa_eventos.json"
        with open(caminho, "r", encoding="utf-8") as f:
            pool = json.load(f).get("semanais", [])
    except Exception:
        pool = []

    if not pool or random.random() > 0.18:
        return

    evento = random.choice(pool)
    ev_texto = evento.get("texto", "Algo aconteceu nos bastidores.")
    efeitos = evento.get("efeitos", {})

    # Aplica efeitos
    for key, val in efeitos.items():
        if key == "seguidores":
            ctx.jogador.seguidores = max(0, ctx.jogador.seguidores + val)
        elif key == "energia":
            if hasattr(ctx.jogador, "ajustar_energia"):
                ctx.jogador.ajustar_energia(val)
            else:
                ctx.jogador.energia = max(
                    0, min(100, (ctx.jogador.energia or 100) + val)
                )
        elif key == "moral":
            ctx.jogador.moral = max(
                0, min(100, (getattr(ctx.jogador, "moral", 70) or 70) + val)
            )

    ctx.eventos_api.append(ev_texto)


def _processar_dinamica_staff(ctx: SemanaContext) -> None:
    """Processa satisfacao da equipe e gera emails de conselhos (FM-style)."""
    from src.services.staff_advice_service import (
        processar_satisfacao_staff,
        StaffAdviceService,
    )

    # 1. Atualiza satisfação e processa pedidos de demissão
    eventos_clima = processar_satisfacao_staff(ctx.jogador)
    ctx.eventos_api.extend(eventos_clima)

    # 2. Gera e-mails de conselhos técnicos/físicos/mkt
    conselhos = StaffAdviceService.generate_weekly_advice(ctx.jogador)
    if conselhos:
        if not hasattr(ctx.jogador, "caixa_email"):
            ctx.jogador.caixa_email = []
        ctx.jogador.caixa_email.extend(conselhos)
        ctx.eventos_api.append(
            f"SUGESTÃO: Voce recebeu {len(conselhos)} novo(s) conselho(s) da sua equipe no e-mail."
        )


def _processar_convites_duplas(ctx: SemanaContext) -> None:
    """Gera convites de duplas vindo de NPCs para a caixa de entrada do jogador."""
    from src.services.communication_service import gerar_convite_duplas_inbound

    # Chama a lógica de geração de convites
    gerar_convite_duplas_inbound(ctx.jogador, ctx.ranking)


def _processar_rotinas_semanais_jogador(
    jogador: Any,
    temporada: dict,
    ranking: Any,
    torneio_info_semana: Optional[dict],
    jogador_participou: bool,
    eventos_api: list,
):
    from src.management import (
        processar_despesas_operacionais,
        processar_expiracoes_empresario,
        processar_gastos_equipe,
        processar_expiracoes_contratos,
    )
    from src.services.sponsorship_service import processar_pagamentos_patrocinio
    from src.services.communication_service import (
        gerar_propostas_carreira_email,
        gerar_convites_midia_email,
    )
    from src import calendario as cal

    processar_despesas_operacionais(
        jogador, temporada=temporada, info_torneio=torneio_info_semana
    )
    processar_expiracoes_empresario(jogador)
    processar_gastos_equipe(jogador)
    processar_expiracoes_contratos(jogador)
    processar_pagamentos_patrocinio(jogador)
    eventos_api.extend(cal.processar_progressao_semanal(jogador))
    cal.processar_seguidores(jogador, ranking, participou=jogador_participou)
    cal.processar_avisos_patrocinio(jogador, ranking)

    caixa_antes = len(getattr(jogador, "caixa_email", []) or [])
    gerar_propostas_carreira_email(jogador, ranking)
    gerar_convites_midia_email(jogador, ranking)
    caixa_depois = len(getattr(jogador, "caixa_email", []) or [])
    novos_emails = max(0, caixa_depois - caixa_antes)
    if novos_emails > 0:
        eventos_api.append(f"{novos_emails} novo(s) email(s) de carreira recebido(s).")


def _processar_logistica(ctx: SemanaContext) -> None:
    """Calcula custos de viagem e impacto de jet lag se o jogador mudar de continente."""
    from src.utils.geo_utils import (
        obter_continente,
        calcular_custo_viagem,
        calcular_fadiga_viagem,
    )

    if not ctx.jogador_em_torneio_ativo or not ctx.torneio_info_semana:
        return

    pais_torneio = ctx.torneio_info_semana.get("pais_sede", "Internacional")
    continente_torneio = obter_continente(pais_torneio)

    if continente_torneio != ctx.jogador.continente_atual:
        custo = calcular_custo_viagem(ctx.jogador.continente_atual, continente_torneio)
        fadiga_extra = calcular_fadiga_viagem(
            ctx.jogador.continente_atual, continente_torneio
        )

        ctx.jogador.registrar_transacao(
            -custo, f"Viagem para {continente_torneio}", categoria="logistica"
        )
        ctx.jogador.ajustar_energia(-fadiga_extra)

        ctx.eventos_api.append(
            f"LOGÍSTICA: Viagem transcontinental para a {continente_torneio}. Custo: ${custo}. Jet lag: -{fadiga_extra}% energia."
        )
        ctx.jogador.continente_atual = continente_torneio
    else:
        ctx.jogador.registrar_transacao(
            -200, "Deslocamento local", categoria="logistica"
        )


def _processar_financas(ctx: SemanaContext) -> None:
    _processar_rotinas_semanais_jogador(
        ctx.jogador,
        ctx.temporada,
        ctx.ranking,
        ctx.torneio_info_semana,
        ctx.jogador_participou,
        ctx.eventos_api,
    )


from src.services.milestone_service import MilestoneService

...


def _inicializar_nova_semana(ctx: SemanaContext) -> None:
    from src import calendario as cal
    from src.repositories.player_repository import save_player
    from src.repositories.season_repository import save_season
    from src.save import tirar_snapshot_carreira

    if ctx.jogador.semana in [1, 26]:
        tirar_snapshot_carreira(ctx.jogador, ano=ctx.ano_novo)

    # Detecção de Ranking Milestones
    rk_milestones = MilestoneService.detect_ranking_milestones(
        ctx.jogador, ctx.nova_posicao_ranking or 9999
    )
    if rk_milestones:
        ctx.eventos_api.extend(rk_milestones)

    _resetar_estado_semanal_jogador(ctx)

    # Limpa marcos da semana após processar
    if hasattr(ctx.jogador, "milestones_semana"):
        ctx.eventos_api.extend(ctx.jogador.milestones_semana)
        delattr(ctx.jogador, "milestones_semana")

    save_player(ctx.nome_save, ctx.jogador)

    cal._inicializar_torneios_nova_semana(
        ctx.nome_save, ctx.semana_nova, ctx.jogador.nome
    )
    save_season(ctx.nome_save, ctx.temporada)
    ctx.eventos_api.append("Ranking semanal atualizado.")
    ctx.torneios_disponiveis = cal.obter_torneios_da_semana(
        ctx.semana_nova, genero=ctx.jogador.genero
    )
    _atualizar_contexto_ranking_pos_semana(ctx)
    save_player(ctx.nome_save, ctx.jogador)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

PIPELINE = [
    _recuperar_npcs,
    _simular_torneios,
    _avancar_calendario,
    _expirar_pontos,
    _processar_jogador,
    _processar_logistica,
    _processar_eventos_narrativos,
    _processar_financas,
    _processar_dinamica_staff,
    _processar_convites_duplas,
    _inicializar_nova_semana,
]


def _build_context(nome_save: str) -> SemanaContext:
    from src import calendario as cal
    from src.repositories.player_repository import load_player
    from src.repositories.ranking_repository import load_all_rankings
    from src.repositories.season_repository import load_season
    from src.repositories.tournament_repository import load_tournament_state
    from src.services.ranking_service import migrar_rankings_semana_se_preciso

    temporada = load_season(nome_save)
    jogador = load_player(nome_save)
    semana_atual = temporada["semana"]
    ano_atual = temporada.get("ano", START_YEAR)

    rankings = load_all_rankings(nome_save)
    migrar_rankings_semana_se_preciso(rankings, semana_atual, ano_atual)

    ranking = (
        rankings["simples_atp"]
        if jogador.genero == "masculino"
        else rankings["simples_wta"]
    )

    state = load_tournament_state(nome_save, genero=jogador.genero)
    em_torneio = cal._estado_torneio_ativo(state, semana_referencia=semana_atual)
    participou = cal._semana_estado_torneio(state) == semana_atual

    return SemanaContext(
        nome_save=nome_save,
        temporada=temporada,
        jogador=jogador,
        rankings=rankings,
        ranking=ranking,
        semana_atual=semana_atual,
        ano_atual=ano_atual,
        player_active_tournament_state=state,
        jogador_em_torneio_ativo=em_torneio,
        jogador_participou=participou,
    )


def advance_week(nome_save: str, expected_week: Optional[int] = None) -> dict:
    """
    Executa o pipeline de avanço semanal e retorna o novo estado da semana.
    """
    ctx = _build_context(nome_save)

    if expected_week is not None and ctx.semana_atual != expected_week:
        return {
            "ok": False,
            "motivo": "semana_ja_avancada",
            "semana": ctx.semana_atual,
            "ano": ctx.ano_atual,
        }

    for etapa in PIPELINE:
        eventos_antes = len(ctx.eventos_api)
        try:
            etapa(ctx)
        except Exception as exc:
            log_erro(ctx.nome_save, etapa.__name__, exc)
            ctx.eventos_api.append(f"[aviso] etapa {etapa.__name__} falhou: {exc}")
        _registrar_etapa(ctx, etapa.__name__, ctx.eventos_api[eventos_antes:])

    return {
        "semana": ctx.temporada["semana"],
        "ano": ctx.temporada["ano"],
        "recuperacao": ctx.recuperacao,
        "torneios_disponiveis": ctx.torneios_disponiveis,
        "eventos": ctx.eventos_api,
        "pontos_expirados": ctx.pontos_expirados,
        "nova_posicao_ranking": ctx.nova_posicao_ranking,
        "rival_info": ctx.rival_info,
        "processamento": ctx.processamento_etapas,
        "resumo_mundial": {
            "campeoes": ctx.resumo_campeoes or [],
        },
    }
