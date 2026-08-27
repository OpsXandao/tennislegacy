import random
from src.jogador import normalizar_nome
from src.constants.torneio_constants import (
    RANKING_LIMITE_ENTRADA_DIRETA,
    RANKING_LIMITE_CHALLENGER,
    RANKING_LIMITE_ITF,
)

def promover_protected_ranking(qualy_players: list[dict], limit: int = RANKING_LIMITE_ENTRADA_DIRETA) -> tuple[list[dict], list[dict]]:
    """Move jogadores com PR de volta para a chave principal se necessário."""
    promovidos = []
    restantes = list(qualy_players)
    for j in qualy_players:
        if int(j.get("protected_ranking_semanas", 0) or 0) > 0:
            pr = int(j.get("protected_ranking", 9999))
            if pr <= limit:
                promovidos.append(j)
                if j in restantes: restantes.remove(j)
    return promovidos, restantes

def eh_elegivel_por_ranking_torneio(ranking_pos: int, tipo_torneio: str) -> bool:
    tipo = str(tipo_torneio).lower()
    if "grand slam" in tipo or "1000" in tipo or "500" in tipo or "250" in tipo: return True
    if "challenger" in tipo: return ranking_pos >= 50
    if "itf" in tipo: return ranking_pos >= 150
    return True

def ranking_limite_torneio(tipo_torneio: str) -> int:
    tipo = str(tipo_torneio).lower()
    if "grand slam" in tipo: return 120
    if "1000" in tipo: return 100
    if "500" in tipo: return 150
    if "250" in tipo: return 250
    if "challenger" in tipo: return RANKING_LIMITE_CHALLENGER
    if "itf" in tipo: return RANKING_LIMITE_ITF
    return 9999

def _extrair_codigo_pais(valor):
    from src.torneio_utils import extrair_codigo_pais
    return extrair_codigo_pais(valor)

def _normalizar_superficie_torneio(quadra):
    v = str(quadra or "").lower()
    if "saibro" in v or "clay" in v: return "clay"
    if "grama" in v or "grass" in v: return "grass"
    return "hard"

def _superficie_preferida_jogador(jogador):
    return jogador.get("superficie_preferida", "hard")

def _prob_participacao(tipo, rank, is_home=False, superficie_match=False):
    from src.calendario_participacao import prob_participacao
    return prob_participacao(tipo, rank, is_home=is_home, superficie_match=superficie_match)

def selecionar_participantes(
    info_torneio, ranking_ordenado, disponiveis_set, max_jogadores=None
):
    """
    Seleciona jogadores do ranking para um torneio.
    """
    from src.calendario_participacao import ajustar_prob_participacao_por_contexto
    
    tipo = info_torneio.get("tipo", "")
    torneio_pais = _extrair_codigo_pais(info_torneio.get("pais_sede", ""))
    superficie_torneio = _normalizar_superficie_torneio(info_torneio.get("quadra", "dura"))

    if max_jogadores is not None:
        total_necessario = max_jogadores
    elif tipo == "Grand Slam":
        total_necessario = 256
    elif "1000" in tipo:
        total_necessario = 160
    elif tipo in {"ATP Finals", "WTA Finals", "Next Gen ATP Finals"}:
        total_necessario = 8
    else:
        total_necessario = 48

    def _eh_jogador_real(j):
        return not bool(j.get("is_bot")) and not str(j.get("nome", "")).startswith("Bot ")

    ranking_base = ranking_ordenado
    posicao_ranking = {
        normalizar_nome(j.get("nome", "")): idx
        for idx, j in enumerate(ranking_base, 1)
        if j.get("nome")
    }
    ranking_reais = [j for j in ranking_base if _eh_jogador_real(j)]
    ranking_bots = [j for j in ranking_base if not _eh_jogador_real(j)]

    selecionados = []
    for jogador in ranking_reais:
        nome_norm = normalizar_nome(jogador.get("nome", ""))
        if nome_norm not in disponiveis_set: continue
        status_lesao = jogador.get("status_lesao", {})
        if isinstance(status_lesao, dict) and status_lesao.get("lesionado"): continue

        jogador_pais = _extrair_codigo_pais(jogador.get("nacionalidade", ""))
        is_home = torneio_pais and jogador_pais == torneio_pais
        superficie_pref = _superficie_preferida_jogador(jogador)
        jogador["superficie_preferida"] = jogador.get("superficie_preferida", superficie_pref)
        superficie_match = jogador.get("superficie_preferida") == superficie_torneio

        idx = posicao_ranking.get(nome_norm, len(ranking_base))
        prob = _prob_participacao(tipo, idx, is_home=is_home, superficie_match=superficie_match)
        prob = ajustar_prob_participacao_por_contexto(
            prob, jogador, tipo=tipo, rank=idx, nome_torneio=info_torneio.get("nome", ""),
            semana_atual=info_torneio.get("semana"), ano_atual=info_torneio.get("ano"),
        )
        prob = min(0.99, prob * 1.2)
        if random.random() < prob:
            selecionados.append(jogador)
            if len(selecionados) >= total_necessario: break

    if len(selecionados) < total_necessario:
        for jogador in ranking_reais:
            nome_norm = normalizar_nome(jogador.get("nome", ""))
            if nome_norm not in disponiveis_set or jogador in selecionados: continue
            selecionados.append(jogador)
            if len(selecionados) >= total_necessario: break

    if len(selecionados) < total_necessario:
        for jogador in ranking_bots:
            nome_norm = normalizar_nome(jogador.get("nome", ""))
            if nome_norm not in disponiveis_set or jogador in selecionados: continue
            selecionados.append(jogador)
            if len(selecionados) >= total_necessario: break

    for jogador in selecionados:
        disponiveis_set.discard(normalizar_nome(jogador.get("nome", "")))
    return selecionados
