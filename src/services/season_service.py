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

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from src.constants.torneio_constants import START_YEAR

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
    "_processar_financas": {
        "id": "process_finances",
        "titulo": "Carreira",
        "resumo": "Processando finanças, equipe, mídia e bastidores.",
        "tom": "neutral",
    },
    "_inicializar_nova_semana": {
        "id": "init_next_week",
        "titulo": "Nova semana",
        "resumo": "Preparando agenda, ranking e torneios disponíveis.",
        "tom": "positive",
    },
}


def _resumir_eventos_etapa(eventos: list[str]) -> list[str]:
    detalhes: list[str] = []
    for evento in eventos:
        texto = str(evento or "").strip()
        if not texto:
            continue
        detalhes.append(texto)
        if len(detalhes) >= 4:
            break
    return detalhes


def _registrar_etapa(
    ctx: SemanaContext, nome_etapa: str, eventos_etapa: list[str]
) -> None:
    meta = STAGE_META.get(nome_etapa)
    if not meta:
        return

    detalhes = _resumir_eventos_etapa(eventos_etapa)
    if nome_etapa == "_simular_torneios" and ctx.resumo_campeoes:
        detalhes = detalhes + [
            f"{item.get('tour', 'TOUR')}: {item.get('torneio', 'Torneio')} — {item.get('simples', 'Campeão')}"
            for item in ctx.resumo_campeoes[:3]
        ]
    elif nome_etapa == "_expirar_pontos" and ctx.pontos_expirados > 0:
        detalhes = [f"{ctx.pontos_expirados} pontos saíram da conta semanal."] + detalhes
    elif nome_etapa == "_processar_jogador":
        fadiga_antes = int(round(ctx.recuperacao.get("fadiga_antes", 0)))
        fadiga_depois = int(round(ctx.recuperacao.get("fadiga_depois", 0)))
        detalhes = [
            f"Fadiga: {fadiga_antes}% → {fadiga_depois}%",
            f"Status físico: {ctx.recuperacao.get('lesao_status', 'saudavel')}",
        ] + detalhes
    elif nome_etapa == "_inicializar_nova_semana":
        detalhes = [
            f"Semana {ctx.semana_nova}/{ctx.ano_novo} pronta.",
            f"Torneios disponíveis: {len(ctx.torneios_disponiveis)}",
        ] + detalhes

    ctx.processamento_etapas.append(
        {
            "id": meta["id"],
            "titulo": meta["titulo"],
            "resumo": meta["resumo"],
            "tom": meta["tom"],
            "detalhes": detalhes[:5],
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
    from src import calendario as cal

    cal._recuperar_npcs_semana(ctx.rankings)


def _simular_torneios(ctx: SemanaContext) -> None:
    from src import calendario as cal

    ctx.resumo_campeoes = cal._simular_torneios_semanais_npc(
        ctx.nome_save,
        ctx.semana_atual,
        ctx.ranking,
        ctx.jogador,
        ctx.player_active_tournament_state,
    )


def _avancar_calendario(ctx: SemanaContext) -> None:
    from src import calendario as cal

    ctx.temporada["semana"] += 1
    cal._processar_virada_ano(ctx.temporada, ctx.jogador, ctx.rankings, ctx.eventos_api)
    ctx.semana_nova = ctx.temporada["semana"]
    ctx.ano_novo = ctx.temporada["ano"]
    ctx.eventos_api.append(
        f"Semana avancada para {ctx.semana_nova}/{ctx.temporada['ano']}."
    )


def _expirar_pontos(ctx: SemanaContext) -> None:
    from src import calendario as cal

    pontos_antes = _somar_pontos_detalhados(_buscar_registro_jogador_ranking(ctx))
    cal._processar_expiracao_ranking(ctx.nome_save, ctx.semana_nova, ctx.ano_novo)
    _recarregar_ranking_principal(ctx)
    pontos_depois = _somar_pontos_detalhados(_buscar_registro_jogador_ranking(ctx))
    ctx.pontos_expirados = max(0, pontos_antes - pontos_depois)
    ctx.jogador.semana = ctx.semana_nova


def _processar_jogador(ctx: SemanaContext) -> None:
    from src import calendario as cal

    if ctx.jogador_em_torneio_ativo:
        sem_ref = ctx.player_active_tournament_state.get("semana", ctx.semana_atual)
        ctx.torneio_info_semana = cal.obter_torneio_por_nome(
            sem_ref,
            ctx.player_active_tournament_state.get("torneio"),
            genero=ctx.jogador.genero,
        )

    fadiga_antes = float(getattr(ctx.jogador, "fadiga", 0) or 0)
    eventos = cal._atualizar_recuperacao_jogador(
        ctx.jogador, info_torneio=ctx.torneio_info_semana
    )
    ctx.eventos_api.extend(eventos)

    if not ctx.jogador_participou:
        ctx.jogador.fadiga = max(0, ctx.jogador.fadiga - 20)
        if ctx.jogador.energia < 95:
            ctx.jogador.energia = min(100, ctx.jogador.energia + 15)
        ctx.eventos_api.append("Semana de descanso com bonus de recuperacao fisica.")

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


def _processar_financas(ctx: SemanaContext) -> None:
    from src import calendario as cal

    cal._processar_rotinas_semanais_jogador(
        ctx.jogador,
        ctx.temporada,
        ctx.ranking,
        ctx.torneio_info_semana,
        ctx.jogador_participou,
        ctx.eventos_api,
    )


def _inicializar_nova_semana(ctx: SemanaContext) -> None:
    from src import calendario as cal
    from src.repositories.player_repository import save_player
    from src.repositories.season_repository import save_season
    from src.save import tirar_snapshot_carreira

    if ctx.jogador.semana in [1, 26]:
        tirar_snapshot_carreira(ctx.jogador, ano=ctx.ano_novo)

    _resetar_estado_semanal_jogador(ctx)
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
    _processar_financas,
    _inicializar_nova_semana,
]


def _build_context(nome_save: str) -> SemanaContext:
    from src import calendario as cal
    from src.repositories.player_repository import load_player
    from src.repositories.ranking_repository import load_all_rankings
    from src.repositories.season_repository import load_season
    from src.repositories.tournament_repository import load_tournament_state

    temporada = load_season(nome_save)
    jogador = load_player(nome_save)
    semana_atual = temporada["semana"]
    ano_atual = temporada.get("ano", START_YEAR)

    rankings = load_all_rankings(nome_save)
    cal._migrar_rankings_semana_se_preciso(rankings, semana_atual, ano_atual)

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
        etapa(ctx)
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
