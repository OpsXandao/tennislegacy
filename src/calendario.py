import random
from src.dados import (
    carregar_estado_torneio,
    carregar_temporada as carregar_temporada_dados,
    salvar_temporada as salvar_temporada_dados,
    obter_torneio_por_nome as obter_torneio_por_nome_dados,
    obter_torneios_da_semana as obter_torneios_da_semana_dados,
)
from src.jogador import normalizar_nome
from src.management import (
    processar_gastos_equipe,
    processar_expiracoes_contratos,
    processar_expiracoes_empresario,
    processar_despesas_operacionais,
    obter_profissional_da_equipe,
)
from src.dados import carregar_patrocinadores
from src.ranking import SistemaRanking
from src.calendario_participacao import (
    ajustar_prob_participacao_por_contexto,
    prob_participacao,
)
import logging

from src.constants.staff_constants import PROFISSIONAIS_DISPONIVEIS

logger = logging.getLogger(__name__)

from src.services.health_service import (
    normalizar_status_doenca,
    processar_recuperacao_semanal,
    tentar_doenca_semanal,
    FADIGA_RECUPERACAO_SEMANAL,
    ENERGIA_RECUPERACAO_SEMANAL_BASE,
    ENERGIA_RECUPERACAO_SEMANAL_POR_FISICO,
)
from src.services.communication_service import (
    gerar_convites_midia_email,
    gerar_propostas_carreira_email,
)
from src.services.sponsorship_service import processar_pagamentos_patrocinio

PATROCINADORES_DISPONIVEIS = carregar_patrocinadores()


def _chance_doenca(jogador, info_torneio=None):
    from src.services.health_service import chance_doenca

    return chance_doenca(jogador, info_torneio)


def _tentar_disparar_doenca(jogador, info_torneio=None):
    """Retorna (status_doenca, eventos: list[str])."""
    from src.services.health_service import (
        tentar_doenca_semanal,
        normalizar_status_doenca,
    )

    eventos = tentar_doenca_semanal(jogador, info_torneio)
    return normalizar_status_doenca(getattr(jogador, "status_doenca", {})), eventos


def _recuperar_energia_semana(jogador, eventos=None):
    from src.services.health_service import processar_recuperacao_semanal

    processar_recuperacao_semanal(jogador, eventos)


def _e_torneio_especial(tipo_torneio):
    return tipo_torneio in ("Davis Cup", "Billie Jean King Cup", "United Cup")


def _normalizar_superficie_torneio(quadra):
    if not quadra:
        return "dura"
    q = str(quadra).strip().lower()
    if "saibro" in q or "clay" in q or "terra" in q:
        return "saibro"
    if "grama" in q or "grass" in q:
        return "grama"
    return "dura"


def _superficie_preferida_jogador(jogador):
    attrs = jogador.get("atributos", {}) if isinstance(jogador, dict) else {}
    saque = attrs.get("saque", 50)
    voleio = attrs.get("voleio", 50)
    topspin = attrs.get("topspin", 50)
    if topspin > 70:
        return "saibro"
    if saque > 70 and voleio > 60:
        return "grama"
    return "dura"


def _torneio_prioridade(info_torneio):
    tipo = info_torneio.get("tipo", "")
    if tipo == "Grand Slam":
        return 0
    if tipo in {"ATP 1000", "WTA 1000"}:
        return 1
    if tipo in {"ATP 500", "WTA 500"}:
        return 2
    if tipo in {"ATP 250", "WTA 250"}:
        return 3
    if tipo == "Challenger 125":
        return 4
    if tipo in {"ITF 100", "ITF 25"}:
        return 5
    return 6


def _extrair_codigo_pais(valor):
    if not valor or not isinstance(valor, str):
        return ""
    if valor.startswith("[") and "]" in valor:
        fechamento = valor.find("]")
        return valor[1:fechamento].upper()
    return ""


def _prob_participacao(tipo, rank, is_home=False, superficie_match=False):
    return prob_participacao(
        tipo=tipo,
        rank=rank,
        is_home=is_home,
        superficie_match=superficie_match,
    )


def _coletar_participantes_estado(estado):
    nomes = set()
    if not estado:
        return nomes
    for jogador in estado.get("direct_entries", []):
        if isinstance(jogador, dict):
            nomes.add(normalizar_nome(jogador.get("nome", "")))
        else:
            nomes.add(normalizar_nome(str(jogador)))
    for confrontos in estado.get("rodadas", {}).values():
        for confronto in confrontos:
            if isinstance(confronto, dict):
                nome_a = confronto.get("jogador_a", {}).get("nome", "")
                nome_b = confronto.get("jogador_b", {}).get("nome", "")
            else:
                jogador_a, jogador_b = confronto
                nome_a = (
                    jogador_a.get("nome")
                    if isinstance(jogador_a, dict)
                    else str(jogador_a)
                )
                nome_b = (
                    jogador_b.get("nome")
                    if isinstance(jogador_b, dict)
                    else str(jogador_b)
                )
            nomes.add(normalizar_nome(nome_a))
            nomes.add(normalizar_nome(nome_b))
    return nomes


def _marcar_historico_expirado(
    jogador, blocos_expirando, ano_novo=None, semana_nova=None
):
    """
    Marca entradas de historico_torneios como expiradas, priorizando identidade do torneio.
    """
    historico = (
        jogador.get("historico_torneios", [])
        if isinstance(jogador, dict)
        else getattr(jogador, "historico_torneios", [])
    )
    if not isinstance(historico, list) or not isinstance(blocos_expirando, list):
        return 0

    marcados = 0
    for bloco in blocos_expirando:
        if not isinstance(bloco, dict):
            continue

        nome_ref = normalizar_nome(bloco.get("torneio", ""))
        tipo_ref = str(bloco.get("tipo", "") or "")
        semana_ref = bloco.get("semana_origem")
        ano_ref = bloco.get("ano_origem")
        pontos_ref = bloco.get("pontos")

        alvo = None

        # 1) Prioriza identidade completa do torneio de origem.
        for item in historico:
            if not isinstance(item, dict) or item.get("expirado"):
                continue
            if (
                nome_ref
                and normalizar_nome(item.get("nome", "")) == nome_ref
                and (not tipo_ref or str(item.get("tipo", "")) == tipo_ref)
                and (semana_ref is None or item.get("semana") == semana_ref)
                and (ano_ref is None or item.get("ano") == ano_ref)
            ):
                alvo = item
                break

        # 2) Fallback por origem (tipo/semana/ano/pontos), quando nome não existir.
        if alvo is None:
            for item in historico:
                if not isinstance(item, dict) or item.get("expirado"):
                    continue
                if (
                    (not tipo_ref or str(item.get("tipo", "")) == tipo_ref)
                    and (semana_ref is None or item.get("semana") == semana_ref)
                    and (ano_ref is None or item.get("ano") == ano_ref)
                    and (pontos_ref is None or item.get("pontos") == pontos_ref)
                ):
                    alvo = item
                    break

        # 3) Último fallback por pontos (mantém compatibilidade de saves legados).
        if alvo is None and pontos_ref is not None:
            for item in historico:
                if not isinstance(item, dict) or item.get("expirado"):
                    continue
                if item.get("pontos") == pontos_ref:
                    alvo = item
                    break

        if alvo is not None:
            alvo["expirado"] = True
            if ano_novo is not None:
                alvo["ano_expiracao_processado"] = int(ano_novo)
            if semana_nova is not None:
                alvo["semana_expiracao_processado"] = int(semana_nova)
            marcados += 1

    return marcados


def _selecionar_participantes_para_torneio(
    info_torneio, ranking_ordenado, disponiveis_set, max_jogadores=None
):
    """
    Seleciona jogadores do ranking para um torneio.

    max_jogadores: quando fornecido, limita quantos são selecionados E removidos do
    pool. Usado por tournament_manager/world_tour_sync onde não há qualifying NPC —
    evita esgotar o pool desnecessariamente.
    """
    tipo = info_torneio.get("tipo", "")
    torneio_pais = _extrair_codigo_pais(info_torneio.get("pais_sede", ""))
    superficie_torneio = _normalizar_superficie_torneio(
        info_torneio.get("quadra", "dura")
    )

    # Cálculo dinâmico do total necessário (Main Draw + Qualy)
    if max_jogadores is not None:
        # Chamador sabe exatamente quantos precisa (ex: draw_size sem qualifying NPC)
        total_necessario = max_jogadores
    elif tipo == "Grand Slam":
        total_necessario = 128 + 128  # 256
    elif "1000" in tipo:
        total_necessario = 96 + 64  # 160
    elif tipo == "ATP Finals" or tipo == "WTA Finals":
        total_necessario = 8
    elif _e_torneio_especial(tipo):
        total_necessario = 64  # Valor base para simulação rápida
    else:
        # 250 e 500 (draw 32 + 16 qualy)
        total_necessario = 32 + 16  # 48

    def _eh_jogador_real(j):
        # "Bot Externo" / "Bot Leo Williams" → falso. "Botic van de Zandschulp" → real.
        return not bool(j.get("is_bot")) and not str(j.get("nome", "")).startswith(
            "Bot "
        )

    # Ranking base: prioriza jogadores reais para evitar placeholders em ATP/WTA.
    ranking_base = ranking_ordenado
    posicao_ranking = {
        normalizar_nome(j.get("nome", "")): idx
        for idx, j in enumerate(ranking_base, 1)
        if j.get("nome")
    }
    ranking_reais = [j for j in ranking_base if _eh_jogador_real(j)]
    ranking_bots = [j for j in ranking_base if not _eh_jogador_real(j)]

    selecionados = []
    # Primeira passada: seleciona jogadores reais por probabilidade de participação.
    for jogador in ranking_reais:
        nome_norm = normalizar_nome(jogador.get("nome", ""))
        if nome_norm not in disponiveis_set:
            continue

        # Pula jogadores lesionados
        status_lesao = jogador.get("status_lesao", {})
        if isinstance(status_lesao, dict) and status_lesao.get("lesionado"):
            continue

        jogador_pais = _extrair_codigo_pais(jogador.get("nacionalidade", ""))
        is_home = torneio_pais and jogador_pais == torneio_pais
        superficie_pref = _superficie_preferida_jogador(jogador)
        jogador["superficie_preferida"] = jogador.get(
            "superficie_preferida", superficie_pref
        )
        superficie_match = jogador.get("superficie_preferida") == superficie_torneio

        # Probabilidade base de participação
        idx = posicao_ranking.get(nome_norm, len(ranking_base))
        prob = _prob_participacao(
            tipo, idx, is_home=is_home, superficie_match=superficie_match
        )
        prob = ajustar_prob_participacao_por_contexto(
            prob,
            jogador,
            tipo=tipo,
            rank=idx,
            nome_torneio=info_torneio.get("nome", ""),
            semana_atual=info_torneio.get("semana"),
            ano_atual=info_torneio.get("ano"),
        )
        prob = min(0.99, prob * 1.2)  # viés pró-jogador real

        if random.random() < prob:
            selecionados.append(jogador)
            if len(selecionados) >= total_necessario:
                break

    # Segunda passada: completa com jogadores reais restantes, sem sorteio.
    if len(selecionados) < total_necessario:
        for jogador in ranking_reais:
            nome_norm = normalizar_nome(jogador.get("nome", ""))
            if nome_norm not in disponiveis_set or jogador in selecionados:
                continue
            selecionados.append(jogador)
            if len(selecionados) >= total_necessario:
                break

    # Terceira passada: só usa bots se realmente não houver reais suficientes.
    if len(selecionados) < total_necessario:
        for jogador in ranking_bots:
            nome_norm = normalizar_nome(jogador.get("nome", ""))
            if nome_norm not in disponiveis_set or jogador in selecionados:
                continue
            selecionados.append(jogador)
            if len(selecionados) >= total_necessario:
                break

    for jogador in selecionados:
        disponiveis_set.discard(normalizar_nome(jogador.get("nome", "")))
    return selecionados


def obter_torneios_da_semana(semana, genero="masculino"):
    return obter_torneios_da_semana_dados(semana, genero=genero)


def obter_torneio_por_nome(semana, nome_torneio, genero="masculino"):
    return obter_torneio_por_nome_dados(semana, nome_torneio, genero=genero)


def obter_info_torneio_e_fase(nome_save, genero="masculino"):
    estado = carregar_estado_torneio(nome_save, genero=genero)
    if not estado:
        return "Nenhum torneio em andamento", "sem_torneio"

    nome_torneio = estado.get("torneio", "Torneio Desconhecido")
    fase = estado.get("fase_atual", "fase_desconhecida")
    semana = estado.get("semana", 0)

    info = obter_torneio_por_nome(semana, nome_torneio, genero=genero)
    if info:
        pais = info.get("pais_sede", "??")
        tipo = info.get("tipo", "??")
        estrelas = "⭐" * info.get("popularidade", 0)
        premio = info.get("premiacao", 0)
        return (
            f"{nome_torneio} ({pais}) - {tipo} | Popularidade: {estrelas} | 💰 Premiação: ${premio}",
            fase,
        )

    return nome_torneio, fase


def carregar_temporada(nome_save):
    """Carrega o estado da temporada (ano e semana) do save."""
    return carregar_temporada_dados(nome_save)


def salvar_temporada(nome_save, data):
    """Salva o estado da temporada (ano e semana) no save."""
    salvar_temporada_dados(nome_save, data)


def _calcular_expiracao_pontos(semana_atual, ano_atual):
    semana_expiracao = ((semana_atual - 1) % 52) + 1
    return semana_expiracao, int(ano_atual) + 1


def _migrar_pontuacao(ranking_obj, semana_atual, ano_atual):
    """Migra a estrutura de pontos antiga para a nova (pontos_detalhados)."""
    logger.info("migrando_estrutura_pontuacao_ranking_continuo")
    semana_expiracao, ano_expiracao = _calcular_expiracao_pontos(
        semana_atual, ano_atual
    )
    for jogador in ranking_obj.ranking:
        pontos_antigos = jogador.get("pontos", 0)
        pontos_detalhados = jogador.get("pontos_detalhados")
        if pontos_antigos > 0 and (
            pontos_detalhados is None or pontos_detalhados == []
        ):
            jogador["pontos_detalhados"] = [
                {
                    "pontos": pontos_antigos,
                    "semana_expiracao": semana_expiracao,
                    "ano_expiracao": ano_expiracao,
                }
            ]
            jogador["pontos"] = pontos_antigos  # Mantém o campo total
    ranking_obj.salvar_ranking()
    logger.info("migracao_pontuacao_concluida")
    return True


def _simular_torneios_semanais_npc(
    nome_save, semana_atual, ranking_principal, jogador, player_active_tournament_state
):
    """Encapsula a simulação de torneios onde o jogador não participa, em ambos os tours."""
    from src.tournament_manager import WeekTournamentManager

    # Gerenciadores para ambos os tours
    manager_atp = WeekTournamentManager(nome_save, semana_atual, genero="masculino")
    manager_wta = WeekTournamentManager(nome_save, semana_atual, genero="feminino")

    jogador_em_torneio_ativo = _estado_torneio_ativo(
        player_active_tournament_state, semana_referencia=semana_atual
    )

    # 1. Inicializa os torneios se ainda não foram (cria as chaves)
    for gen, manager in [("masculino", manager_atp), ("feminino", manager_wta)]:
        torneios_info = obter_torneios_da_semana(semana_atual, genero=gen)
        # Marca qual torneio o jogador está participando
        for info in torneios_info:
            if jogador_em_torneio_ativo and gen == jogador.genero:
                if info["nome"] == player_active_tournament_state.get("torneio"):
                    info["participando"] = True

        manager.inicializar_torneios(torneios_info, jogador_nome=jogador.nome)

    # 2. Simula todos os torneios até o fim (pois estamos avançando a semana)
    # O manager irá simular rodada por rodada
    for manager in [manager_atp, manager_wta]:
        # Simula até 7 rodadas (máximo de um Grand Slam)
        for _ in range(7):
            manager.simular_rodada_para_todos(
                fase_alvo="finalizado", jogador_nome=jogador.nome
            )

    # 3. Coleta e exibe os campeões
    def _campeao_exibivel(nome_campeao):
        nome = str(nome_campeao or "").strip()
        if not nome:
            return False
        nome_norm = normalizar_nome(nome)
        return not (
            nome_norm.startswith("bot externo")
            or nome_norm.startswith("bot ")
            or nome_norm in {"---", "tbd", "none", "null", "na", "n/a", "cancelado"}
            or nome_norm.startswith("n/a ")
            or nome_norm.startswith("cancelado")
        )

    campeoes_da_semana = []
    oficiais_semana = {}
    for gen, label in [("masculino", "ATP"), ("feminino", "WTA")]:
        oficiais_semana[label] = {}
        for info in obter_torneios_da_semana(semana_atual, genero=gen):
            if not isinstance(info, dict):
                continue
            oficiais_semana[label][info.get("nome")] = {
                "simples": info.get("ultimo_campeao"),
                "duplas": info.get("ultimo_campeao_duplas"),
            }

    for manager in [manager_atp, manager_wta]:
        resumos = manager.obter_resumo_semanal()
        t_label = "ATP" if manager.genero == "masculino" else "WTA"
        for r in resumos:
            nome_torneio = r.get("nome")
            oficial = oficiais_semana.get(t_label, {}).get(nome_torneio, {})
            campeao_simples = r.get("campeao")
            campeao_duplas = r.get("campeao_duplas")
            if not _campeao_exibivel(campeao_simples):
                campeao_simples = oficial.get("simples")
            if not _campeao_exibivel(campeao_duplas):
                campeao_duplas = oficial.get("duplas")

            if _campeao_exibivel(campeao_simples):
                campeoes_da_semana.append(
                    {
                        "tour": t_label,
                        "torneio": nome_torneio,
                        "simples": campeao_simples,
                        "duplas": (
                            campeao_duplas
                            if _campeao_exibivel(campeao_duplas)
                            else None
                        ),
                    }
                )

    if campeoes_da_semana:
        logger.info("campeoes_da_semana", extra={"total": len(campeoes_da_semana)})

    return campeoes_da_semana


def _atualizar_recuperacao_jogador(jogador, info_torneio=None) -> list:
    """
    Processa a recuperação física e médica do jogador ao avançar a semana.
    Retorna lista de strings com mensagens para o chamador exibir (API ou CLI).
    """
    eventos: list = []

    status = jogador.status_lesao if isinstance(jogador.status_lesao, dict) else {}
    status.setdefault("lesionado", False)
    status.setdefault("semanas_restantes", 0)
    status.setdefault("nivel", "limitado" if status.get("lesionado") else "saudavel")
    status.setdefault("penalidade_atributos", 0.18 if status.get("lesionado") else 0.0)
    if not status.get("lesionado") and status.get("nivel") == "lesionado":
        status["nivel"] = "limitado"
        status["penalidade_atributos"] = 0.12
        status["semanas_restantes"] = max(
            1, int(status.get("semanas_restantes", 0) or 0)
        )

    jogador.fadiga = max(
        0, int(getattr(jogador, "fadiga", 0) or 0) - FADIGA_RECUPERACAO_SEMANAL
    )
    _recuperar_energia_semana(jogador, eventos)

    fisio_fadiga = obter_profissional_da_equipe(
        getattr(jogador, "equipe", []), "fisioterapeuta"
    )
    if fisio_fadiga:
        bonus = fisio_fadiga.get("bonus_fadiga", 0)
        if bonus > 0:
            jogador.fadiga = max(0, jogador.fadiga - bonus)
            eventos.append(f"🩺 {fisio_fadiga['nome']}: -{bonus} fadiga extra.")

    eventos.append(f"😌 Sua fadiga atual: {jogador.fadiga}%.")

    if status["lesionado"]:
        status["semanas_restantes"] -= 1
        fisio = obter_profissional_da_equipe(
            getattr(jogador, "equipe", []), "fisioterapeuta"
        )
        if fisio:
            bonus_rec = fisio.get("bonus_recuperacao_lesao", 0)
            if bonus_rec > 0:
                status["semanas_restantes"] = max(
                    0, status["semanas_restantes"] - bonus_rec
                )
                eventos.append(
                    f"🩺 {fisio['nome']}: recuperação acelerada em {bonus_rec} semana(s)!"
                )
        eventos.append(
            f"❤️  Você está se recuperando da lesão. Semanas restantes: {status['semanas_restantes']}"
        )
        if status["semanas_restantes"] <= 0:
            status["lesionado"] = False
            status["nivel"] = "desconforto"
            status["semanas_restantes"] = 0
            status["penalidade_atributos"] = 0.06
            eventos.append(
                "🟠 Lesão fechada! Você ainda sente algum desconforto físico."
            )
    else:
        nivel = status.get("nivel", "saudavel")
        if nivel == "limitado":
            status["nivel"] = "desconforto"
            status["penalidade_atributos"] = 0.06
            eventos.append("🟠 Sua condição melhorou: de limitado para desconforto.")
        elif nivel == "desconforto":
            status["nivel"] = "saudavel"
            status["penalidade_atributos"] = 0.0
            eventos.append("✅ Você se recuperou totalmente!")

    jogador.status_lesao = status

    status_doenca = _normalizar_status_doenca(getattr(jogador, "status_doenca", {}))
    if status_doenca.get("doente"):
        status_doenca["semanas_restantes"] -= 1
        if status_doenca["semanas_restantes"] <= 0:
            status_doenca = _normalizar_status_doenca({"doente": False})
    else:
        status_doenca, ev_doenca = _tentar_disparar_doenca(
            jogador, info_torneio=info_torneio
        )
        eventos.extend(ev_doenca)

    jogador.status_doenca = _normalizar_status_doenca(status_doenca)
    return eventos


def _estado_torneio_ativo(estado_torneio, semana_referencia=None):
    if not isinstance(estado_torneio, dict):
        return False
    if not estado_torneio.get("torneio"):
        return False
    if str(estado_torneio.get("fase_atual", "")).lower() == "finalizado":
        return False
    if semana_referencia is not None:
        try:
            if int(estado_torneio.get("semana", semana_referencia)) != int(
                semana_referencia
            ):
                return False
        except (TypeError, ValueError):
            return False
    return True


def _semana_estado_torneio(estado_torneio):
    if not isinstance(estado_torneio, dict):
        return None
    try:
        return int(estado_torneio.get("semana"))
    except (TypeError, ValueError):
        return None


def _carregar_rankings_temporada(nome_save):
    from src.dados import get_caminho_ranking_duplas, get_caminho_ranking_save

    return {
        "simples_atp": SistemaRanking(
            get_caminho_ranking_save(nome_save, genero="masculino"),
            modalidade="simples",
        ),
        "duplas_atp": SistemaRanking(
            get_caminho_ranking_duplas(nome_save, genero="masculino"),
            modalidade="duplas",
        ),
        "simples_wta": SistemaRanking(
            get_caminho_ranking_save(nome_save, genero="feminino"),
            modalidade="simples",
        ),
        "duplas_wta": SistemaRanking(
            get_caminho_ranking_duplas(nome_save, genero="feminino"),
            modalidade="duplas",
        ),
    }


def _migrar_rankings_semana_se_preciso(rankings, semana_atual, ano_atual):
    for chave in ("simples_atp", "simples_wta"):
        rk = rankings[chave]
        if rk.ranking and "pontos_detalhados" not in rk.ranking[0]:
            _migrar_pontuacao(rk, semana_atual, ano_atual)


def _recuperar_npcs_semana(rankings):
    grupos = (
        [rankings["simples_atp"], rankings["duplas_atp"]],
        [rankings["simples_wta"], rankings["duplas_wta"]],
    )
    for lista_rk in grupos:
        jogadores_vistos = {}
        for rk in lista_rk:
            for j in rk.ranking:
                nome = j.get("nome")
                if nome not in jogadores_vistos:
                    processar_recuperacao_semanal(j)
                    jogadores_vistos[nome] = j
                    continue
                j_fonte = jogadores_vistos[nome]
                for campo in (
                    "fadiga",
                    "energia",
                    "moral",
                    "status_lesao",
                    "status_doenca",
                    "protected_ranking_semanas",
                ):
                    if campo in j_fonte:
                        j[campo] = j_fonte[campo]
        for rk in lista_rk:
            rk.salvar_ranking()


def _processar_virada_ano(temporada, jogador, rankings, eventos_api):
    if temporada["semana"] <= 52:
        return

    from src.progressao import processar_envelhecimento_anual

    temporada["semana"] = 1
    temporada["ano"] += 1
    eventos_api.append(f"Feliz Ano Novo! Bem-vindo a {temporada['ano']}!")

    processar_envelhecimento_anual(jogador)
    jogador.pontos_ytd = 0

    nome_humano_norm = normalizar_nome(jogador.nome)
    for rk_obj in (rankings["simples_atp"], rankings["simples_wta"]):
        for j in rk_obj.ranking:
            if normalizar_nome(j.get("nome", "")) == nome_humano_norm:
                j["pontos_ytd"] = 0
                continue
            processar_envelhecimento_anual(j)
            j["pontos_ytd"] = 0
        rk_obj.salvar_ranking()


def _processar_rotinas_semanais_jogador(
    jogador, temporada, ranking, torneio_info_semana, jogador_participou, eventos_api
):
    processar_despesas_operacionais(
        jogador, temporada=temporada, info_torneio=torneio_info_semana
    )
    processar_expiracoes_empresario(jogador)
    processar_gastos_equipe(jogador)
    processar_expiracoes_contratos(jogador)
    processar_pagamentos_patrocinio(jogador)
    eventos_api.extend(processar_progressao_semanal(jogador))
    processar_seguidores(jogador, ranking, participou=jogador_participou)
    processar_avisos_patrocinio(jogador, ranking)

    caixa_antes = len(getattr(jogador, "caixa_email", []) or [])
    gerar_propostas_carreira_email(jogador, ranking)
    gerar_convites_midia_email(jogador, ranking)
    caixa_depois = len(getattr(jogador, "caixa_email", []) or [])
    novos_emails = max(0, caixa_depois - caixa_antes)
    if novos_emails > 0:
        eventos_api.append(f"{novos_emails} novo(s) email(s) de carreira recebido(s).")


def _inicializar_torneios_nova_semana(nome_save, semana_nova, jogador_nome):
    from src.tournament_manager import WeekTournamentManager

    for gen in ["masculino", "feminino"]:
        manager = WeekTournamentManager(nome_save, semana_nova, genero=gen)
        torneios_info = obter_torneios_da_semana(semana_nova, genero=gen)
        manager.inicializar_torneios(torneios_info, jogador_nome=jogador_nome)


def processar_progressao_semanal(jogador) -> list:
    """
    Aplica ganhos semanais de atributos mentais via psicólogo da equipe.
    Retorna lista de eventos para o chamador exibir.
    """
    eventos: list = []
    equipe = getattr(jogador, "equipe", [])
    for contrato in equipe:
        prof_id = contrato.get("id") if isinstance(contrato, dict) else contrato
        prof = PROFISSIONAIS_DISPONIVEIS.get(prof_id)
        if not prof or prof.get("categoria") != "psicologo":
            continue
        chance = float(prof.get("chance_mental", 0) or 0)
        if random.random() < chance:
            attrs_mentais = list(getattr(jogador, "atributos_psicologicos", {}).keys())
            if not attrs_mentais:
                continue
            attr = random.choice(attrs_mentais)
            bonus_max = int(prof.get("bonus_mental", 1) or 1)
            bonus = random.randint(1, bonus_max) if bonus_max > 1 else 1
            jogador.atributos_psicologicos[attr] = min(
                100, int(jogador.atributos_psicologicos.get(attr, 0)) + bonus
            )

            ganho_moral = int(prof.get("estrelas", 2)) * 1.5
            jogador.moral = min(100, jogador.moral + int(ganho_moral))

            nome_attr = attr.replace("_", " ").title()
            eventos.append(
                f"🧠 Sessão com {prof['nome']}: +{bonus} em {nome_attr} e moral subiu para {jogador.moral}!"
            )
    return eventos


def processar_seguidores(jogador, ranking, participou=True):
    """Aplica ganhos/perdas de seguidores na virada da semana."""
    posicao = ranking.obter_posicao(jogador.nome) or 9999

    # Ganho base por ranking (ex: Top 100 ganha mais que Top 1000)
    # 10000 / pos -> #1 ganha 10000, #100 ganha 100, #1000 ganha 10
    ganho_base = int(10000 / max(1, posicao))

    # Se não jogou torneio, o ganho de base (orgânico) é 90% menor
    if not participou:
        ganho_base = int(ganho_base * 0.1)
    else:
        # Bônus por título ou boa campanha (se ele jogou)
        from src.dados import carregar_estado_torneio

        estado_t = carregar_estado_torneio(jogador.save_name, genero=jogador.genero)
        if estado_t:
            # Campeão ganha bônus de 5x no ganho base da semana
            if str(estado_t.get("fase_atual", "")).lower() == "finalizado":
                # Verificamos se ele foi campeão (jogador_vivo continua True no fim se vencer)
                if estado_t.get("jogador_vivo"):
                    ganho_base *= 5
                    logger.debug("🏆 Bônus de popularidade por título!")
            elif (
                estado_t.get("jogador_vivo_duplas")
                and str(estado_t.get("fase_atual_duplas")).lower() == "finalizado"
            ):
                # Campeão de duplas ganha 3x
                ganho_base *= 3
                logger.debug("🏆 Bônus de popularidade por título de duplas!")

    equipe = getattr(jogador, "equipe", [])
    ganho_marketing = 0
    for contrato in equipe:
        prof_id = contrato.get("id") if isinstance(contrato, dict) else contrato
        prof = PROFISSIONAIS_DISPONIVEIS.get(prof_id)
        if prof and prof.get("categoria") == "marketing":
            ganho_marketing += random.randint(
                prof.get("seguidores_min", 0), prof.get("seguidores_max", 0)
            )

    total_ganho = ganho_base + ganho_marketing
    total = getattr(jogador, "seguidores", 0) + total_ganho

    # Penalidades por moral/psicológico baixos
    if getattr(jogador, "moral", 70) < 30:
        total = int(total * 0.90)
    psico = getattr(jogador, "atributos_psicologicos", {})
    if psico and sum(psico.values()) / len(psico) < 35:
        total = int(total * 0.95)

    jogador.seguidores = max(0, total)
    if total_ganho > 0:
        logger.debug(
            "seguidores_ganhos",
            extra={
                "ganho": total_ganho,
                "base": ganho_base,
                "marketing": ganho_marketing,
            },
        )


def processar_avisos_patrocinio(jogador, ranking):
    """Verifica requisitos dos patrocinadores e emite avisos ou cancela contratos."""
    posicao = ranking.obter_posicao(jogador.nome) or 9999
    seguidores = getattr(jogador, "seguidores", 0)
    avisos = getattr(
        jogador, "avisos_patrocinio", {}
    )  # Agora mapeia pat_id -> semanas_insatisfeito (int)
    patrocinios = list(getattr(jogador, "patrocinios", []))

    for pat_id in patrocinios:
        pat = PATROCINADORES_DISPONIVEIS.get(pat_id)
        if not pat:
            continue
        req_ranking = pat.get("requisito_ranking", 9999)
        req_seg = pat.get("req_seguidores", 0)

        # Regra mais suave: Tolera até 50% de desvio no ranking e 30% nos seguidores antes de reclamar
        insatisfeito = posicao > req_ranking * 1.5 or (
            req_seg > 0 and seguidores < req_seg * 0.7
        )

        if insatisfeito:
            semanas = avisos.get(pat_id, 0) + 1
            avisos[pat_id] = semanas

            if semanas >= 3:
                # Cancelar contrato após 3 semanas de insatisfação
                if pat_id in jogador.patrocinios:
                    jogador.patrocinios.remove(pat_id)
                avisos.pop(pat_id, None)
                logger.info("patrocinio_cancelado", extra={"nome": pat["nome"]})
            else:
                prazo = 3 - semanas
                msg = "ranking" if posicao > req_ranking * 1.5 else "seguidores"
                logger.debug(
                    "patrocinador_insatisfeito",
                    extra={"nome": pat["nome"], "motivo": msg, "prazo": prazo},
                )
        else:
            if pat_id in avisos:
                avisos.pop(pat_id)
                logger.debug(
                    "patrocinador_satisfeito_novamente", extra={"nome": pat["nome"]}
                )

    jogador.avisos_patrocinio = avisos


def _simular_torneios_semanais_npc(
    nome_save, semana_atual, ranking_principal, jogador, player_active_tournament_state
):
    """Encapsula a simulação de torneios onde o jogador não participa, em ambos os tours."""
    from src.services.tournament_npc_service import simular_torneios_semanais_npc

    return simular_torneios_semanais_npc(
        nome_save, semana_atual, jogador, player_active_tournament_state
    )


def _processar_recuperacao_ranking(ranking):
    """Atualiza fadiga, lesão e energia de todos os NPCs no ranking."""
    from src.services.health_service import processar_recuperacao_semanal

    for j in ranking.ranking:
        if isinstance(j, dict):
            processar_recuperacao_semanal(j)
    ranking.salvar_ranking()


def _processar_expiracao_ranking(nome_save, semana_atual, ano_atual):
    """Remove pontos que expiraram nesta semana (há 52 semanas) em todos os rankings."""
    from src.services.ranking_service import processar_expiracao_ranking

    processar_expiracao_ranking(nome_save, semana_atual, ano_atual)


def avancar_semana(nome_save, expected_week=None):
    from src.services.season_service import advance_week

    return advance_week(nome_save, expected_week=expected_week)


# ---------------------------------------------------------------------------
# Helpers de calendário/entry reutilizáveis pelos menus
# ---------------------------------------------------------------------------

_PESOS_FASE = {
    "qualy_1": 0,
    "qualy_2": 1,
    "qualy_r1": 0,
    "qualy_r2": 1,
    "qualy_r3": 2,
    "r128": 3,
    "r96": 3,
    "r64": 4,
    "r32": 5,
    "r16": 6,
    "oitavas": 6,
    "quartas": 7,
    "semifinal": 8,
    "final": 9,
    "campeao": 10,
}


def calcular_melhor_resultado_por_torneio(historico_torneios: list) -> dict:
    """
    Recebe uma lista de entradas de histórico de torneios do jogador e retorna
    um dict {nome_torneio: fase_melhor_resultado}.
    """
    melhor: dict = {}
    for h in historico_torneios:
        t_nome = h.get("torneio")
        fase = h.get("fase_alcancada", "r128")
        if t_nome not in melhor or _PESOS_FASE.get(fase, 0) > _PESOS_FASE.get(
            melhor[t_nome], 0
        ):
            melhor[t_nome] = fase
    return melhor


def badge_entry_status(ranking_pos, torneio: dict) -> str:
    """
    Retorna uma badge de status de inscrição para o torneio.
    Usa status_entry do torneio se disponível; caso contrário estima pelo ranking.
    """
    from src.constants.torneio_constants import (
        NUM_TOP_DIRETOS_GRAND_SLAM,
        NUM_TOP_DIRETOS_ATP_1000,
        NUM_TOP_DIRETOS_PADRAO,
        DRAW_SIZE_GRAND_SLAM,
        DRAW_SIZE_ATP_1000,
        DRAW_SIZE_PADRAO,
        RANKING_LIMITE_CHALLENGER,
        RANKING_LIMITE_ITF,
    )

    def _limite_categoria(tipo_torneio: str):
        if tipo_torneio == "Challenger 125":
            return RANKING_LIMITE_CHALLENGER
        if tipo_torneio in {"ITF 100", "ITF 25"}:
            return RANKING_LIMITE_ITF
        return None

    status_real = torneio.get("status_entry")
    if status_real:
        badges = {
            "direct": "[Main Draw]",
            "wildcard": "[Wildcard ★]",
            "qualifier": "[Qualifying]",
            "lucky_loser": "[Lucky Loser]",
            "alternate": "[Alternate]",
        }
        return badges.get(status_real, "")

    if ranking_pos is None:
        return ""

    tipo = torneio.get("tipo", "")
    limite_categoria = _limite_categoria(tipo)
    if limite_categoria is not None and ranking_pos <= limite_categoria:
        return "[Ineligible]"

    cortes = {
        "Grand Slam": (NUM_TOP_DIRETOS_GRAND_SLAM, DRAW_SIZE_GRAND_SLAM),
        "ATP 1000": (NUM_TOP_DIRETOS_ATP_1000, DRAW_SIZE_ATP_1000),
        "WTA 1000": (NUM_TOP_DIRETOS_ATP_1000, DRAW_SIZE_ATP_1000),
        "ATP 500": (NUM_TOP_DIRETOS_PADRAO, DRAW_SIZE_PADRAO + 16),
        "WTA 500": (NUM_TOP_DIRETOS_PADRAO, DRAW_SIZE_PADRAO + 16),
        "ATP 250": (NUM_TOP_DIRETOS_PADRAO, DRAW_SIZE_PADRAO + 16),
        "WTA 250": (NUM_TOP_DIRETOS_PADRAO, DRAW_SIZE_PADRAO + 16),
        "Challenger 125": (
            RANKING_LIMITE_CHALLENGER + DRAW_SIZE_PADRAO,
            RANKING_LIMITE_CHALLENGER + DRAW_SIZE_PADRAO + 16,
        ),
        "ITF 100": (
            RANKING_LIMITE_ITF + DRAW_SIZE_PADRAO,
            RANKING_LIMITE_ITF + DRAW_SIZE_PADRAO + 16,
        ),
        "ITF 25": (
            RANKING_LIMITE_ITF + DRAW_SIZE_PADRAO,
            RANKING_LIMITE_ITF + DRAW_SIZE_PADRAO + 16,
        ),
        "ATP Finals": (None, None),
        "WTA Finals": (None, None),
        "Next Gen ATP Finals": (None, None),
        "United Cup": (None, None),
        "Davis Cup": (None, None),
        "Billie Jean King Cup": (None, None),
    }
    corte_md, corte_q = cortes.get(tipo, (NUM_TOP_DIRETOS_PADRAO, 64))
    if corte_md is None:
        return ""
    if ranking_pos <= corte_md:
        return "[Main Draw]"
    elif ranking_pos <= corte_q:
        return "[Qualifying]"
    else:
        return "[Alternates]"
