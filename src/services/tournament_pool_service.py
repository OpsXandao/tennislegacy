"""
Lógica de seleção de pool de participantes do torneio.

Responsável por determinar quais jogadores entram na chave principal,
no qualifying e na lista de alternates, incluindo pontuação de
probabilidade de participação e seleção de wildcards.
"""

import random

from src.calendario_participacao import (
    ajustar_prob_participacao_por_contexto,
    prob_participacao,
)
from src.jogador import normalizar_nome
from src.torneio_utils import extrair_codigo_pais


def parametros_participacao(tipo_torneio: str) -> dict:
    """Retorna os tamanhos de draw main, qualy e vagas_qualy por tipo de torneio."""
    if tipo_torneio == "Grand Slam":
        return {"draw_main": 104, "draw_qualy": 128, "vagas_qualy": 16}
    if "1000" in tipo_torneio:
        draw_main = 78 if "96" in tipo_torneio else 44
        return {"draw_main": draw_main, "draw_qualy": 48, "vagas_qualy": 12}
    if "500" in tipo_torneio:
        return {"draw_main": 25, "draw_qualy": 16, "vagas_qualy": 4}
    return {"draw_main": 24, "draw_qualy": 16, "vagas_qualy": 4}


def score_pool_torneio(
    jogador: dict,
    tipo_torneio: str,
    tournament_data: dict,
    obter_rank_entrada,
    semana: int = 1,
) -> float:
    """
    Calcula a pontuação de probabilidade de participação de um jogador
    no torneio, combinando prob base, bônus de casa, superfície e ruído.
    """
    rank = obter_rank_entrada(jogador)
    torneio_pais = extrair_codigo_pais(tournament_data.get("pais_sede", ""))
    jogador_pais = extrair_codigo_pais(jogador.get("nacionalidade", ""))
    is_home = bool(torneio_pais and torneio_pais == jogador_pais)
    superficie_torneio = str(tournament_data.get("quadra", "dura") or "dura").lower()
    superficie_pref = str(jogador.get("superficie_preferida", "") or "").lower()
    superficie_match = bool(superficie_pref and superficie_pref in superficie_torneio)

    prob = prob_participacao(
        tipo_torneio,
        rank,
        is_home=is_home,
        superficie_match=superficie_match,
    )
    prob = ajustar_prob_participacao_por_contexto(
        prob,
        jogador,
        tipo=tipo_torneio,
        rank=rank,
        nome_torneio=tournament_data.get("nome", ""),
        semana_atual=tournament_data.get("semana", semana),
        ano_atual=tournament_data.get("ano"),
    )
    bonus_home = 0.18 if is_home else 0.0
    bonus_surface = 0.08 if superficie_match else 0.0
    bonus_pr = (
        0.12 if int(jogador.get("protected_ranking_semanas", 0) or 0) > 0 else 0.0
    )
    noise = random.uniform(0.0, 0.08)
    score = prob + bonus_home + bonus_surface + bonus_pr + noise
    return min(1.0, score)


def selecionar_pool_torneio_realista(
    jogadores_aptos: list,
    total_necessario: int,
    tipo_torneio: str,
    tournament_data: dict,
    jogador_nome: str,
    jogador_nacionalidade: str,
    obter_rank_entrada,
    deduplicar_jogadores,
    semana: int = 1,
    priorizar_jogador: bool = True,
) -> list:
    """
    Seleciona até *total_necessario* jogadores do pool apto, ordenados por score
    de participação. O jogador humano é sempre incluído se *priorizar_jogador*.
    """
    jogadores_reais = [j for j in jogadores_aptos if not j.get("is_bot")]
    ordenados = sorted(jogadores_reais, key=obter_rank_entrada)
    candidatos = [
        (
            score_pool_torneio(
                jogador, tipo_torneio, tournament_data, obter_rank_entrada, semana
            ),
            jogador,
        )
        for jogador in ordenados
    ]
    candidatos.sort(key=lambda item: (-item[0], obter_rank_entrada(item[1])))

    pool = [jogador for _score, jogador in candidatos[:total_necessario]]
    nomes_pool = {normalizar_nome(j.get("nome", "")) for j in pool}

    if priorizar_jogador and normalizar_nome(jogador_nome) not in nomes_pool:
        jogador_humano = next(
            (
                j
                for j in jogadores_aptos
                if normalizar_nome(j.get("nome", "")) == normalizar_nome(jogador_nome)
            ),
            {
                "nome": jogador_nome,
                "nacionalidade": jogador_nacionalidade,
                "is_bot": False,
            },
        )
        if len(pool) >= total_necessario and pool:
            pool.pop()
        pool.append(jogador_humano)

    return sorted(deduplicar_jogadores(pool), key=obter_rank_entrada)


def selecionar_wildcards_realistas(
    remaining_pool: list,
    nome_jogador_lower: str,
    num_wildcards: int,
    pais_sede: str,
    obter_rank_entrada,
) -> tuple:
    """
    Seleciona *num_wildcards* jogadores para wildcard.
    Prioriza jogadores do mesmo país da sede, depois o jogador humano.
    Retorna (wildcards, restantes).
    """
    if num_wildcards <= 0:
        return [], list(remaining_pool)

    pais_sede_code = extrair_codigo_pais(pais_sede)
    elegiveis = list(remaining_pool)

    def wildcard_score(jogador):
        rank = obter_rank_entrada(jogador)
        jogador_pais = extrair_codigo_pais(jogador.get("nacionalidade", ""))
        same_country = pais_sede_code and jogador_pais == pais_sede_code
        local_bonus = 1000 if same_country else 0
        humana_bonus = (
            500 if normalizar_nome(jogador.get("nome", "")) == nome_jogador_lower else 0
        )
        proximity_bonus = max(0, 200 - min(rank, 200))
        anti_star_penalty = -400 if rank <= 20 else (-180 if rank <= 50 else 0)
        return local_bonus + humana_bonus + proximity_bonus + anti_star_penalty

    elegiveis.sort(
        key=lambda jogador: (
            -wildcard_score(jogador),
            obter_rank_entrada(jogador),
        )
    )
    wildcards = elegiveis[:num_wildcards]
    nomes_wc = {normalizar_nome(j.get("nome", "")) for j in wildcards}
    restantes = [
        j for j in remaining_pool if normalizar_nome(j.get("nome", "")) not in nomes_wc
    ]
    return wildcards, restantes
