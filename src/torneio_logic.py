import random
from src.jogador import normalizar_nome
from src.torneio_utils import weighted_sample_sem_reposicao, deduplicar_jogadores
from src.torneio_constants import (
    RANKING_POSICAO_FALLBACK,
    RANKING_LIMITE_ENTRADA_DIRETA,
    RANKING_TOP_POOL,
    RANKING_TOP_20,
    RANKING_TOP_50,
)

def obter_rank_entrada(jogador, ranking):
    """Calcula o rank de entrada, considerando Ranking Protegido e lesões."""
    nome = jogador.get("nome", "") if isinstance(jogador, dict) else ""
    rank_atual = ranking.obter_posicao(nome) or RANKING_POSICAO_FALLBACK
    if not isinstance(jogador, dict):
        return rank_atual

    status_lesao = jogador.get("status_lesao", {})
    lesionado = isinstance(status_lesao, dict) and status_lesao.get("lesionado", False)

    if lesionado:
        return 99999

    if int(jogador.get("protected_ranking_semanas", 0) or 0) > 0:
        pr = int(jogador.get("protected_ranking", rank_atual))
        return min(rank_atual, pr)

    return rank_atual

def _get_weight_from_ranges(pos, ranges):
    for r in ranges:
        if pos <= r["max_pos"]:
            return r["weight"]
    return 1.0

def selecionar_entrada_direta(
    ranking,
    jogadores_ranking_ordenado,
    num_top_diretos,
    nome_jogador,
    nacionalidade_jogador,
    priorizar_jogador,
    cfg,
):
    """Lógica centralizada para seleção de entrada direta (Direct Entry) em chaves."""
    jogadores_reais = [j for j in jogadores_ranking_ordenado if not j.get("is_bot")]

    def get_pos(j):
        return ranking.obter_posicao(j.get("nome", "")) or RANKING_POSICAO_FALLBACK

    top100 = [j for j in jogadores_reais if get_pos(j) <= RANKING_TOP_POOL]
    if not top100:
        top100 = list(jogadores_reais)

    top20 = [j for j in top100 if get_pos(j) <= RANKING_TOP_20]
    top50 = [
        j for j in top100 if (RANKING_TOP_20 + 1) <= get_pos(j) <= RANKING_TOP_50
    ]
    mid = [
        j for j in top100 if (RANKING_TOP_50 + 1) <= get_pos(j) <= RANKING_TOP_POOL
    ]

    num_top20 = min(len(top20), random.randint(cfg["min_top20"], cfg["max_top20"]))
    pesos_top20 = cfg["pesos_top20"](top20)
    selecionados_top20 = weighted_sample_sem_reposicao(top20, pesos_top20, num_top20)

    restantes = num_top_diretos - len(selecionados_top20)
    if restantes < 0:
        chave_principal = selecionados_top20[:num_top_diretos]
    else:
        if cfg["usa_top50"]:
            alvo_top50 = max(0, min(len(top50), int(restantes * cfg["fracao_top50"])))
            pesos_top50 = cfg["pesos_top50"](top50)
            selecionados_top50 = weighted_sample_sem_reposicao(
                top50, pesos_top50, alvo_top50
            )
            restantes -= len(selecionados_top50)
            pesos_mid = cfg["pesos_mid"](mid)
            selecionados_mid = weighted_sample_sem_reposicao(
                mid, pesos_mid, restantes
            )
            chave_principal = selecionados_top20 + selecionados_top50 + selecionados_mid
        else:
            pool_mid = top50 + mid
            # Usa peso_mid_por_posicao lambda
            pesos_mid = [cfg["peso_mid_por_posicao"](get_pos(j)) for j in pool_mid]
            selecionados_mid = weighted_sample_sem_reposicao(
                pool_mid,
                pesos_mid,
                restantes,
            )
            chave_principal = selecionados_top20 + selecionados_mid

    # Corte e completude (Pool 80)
    chave_principal = [
        j for j in chave_principal if get_pos(j) <= RANKING_LIMITE_ENTRADA_DIRETA
    ]
    if len(chave_principal) < num_top_diretos:
        pool80 = [
            j
            for j in jogadores_reais
            if get_pos(j) <= RANKING_LIMITE_ENTRADA_DIRETA and j not in chave_principal
        ]
        # Usa peso_pool80_por_posicao lambda
        pesos_pool80 = [cfg["peso_pool80_por_posicao"](get_pos(j)) for j in pool80]
        faltam = num_top_diretos - len(chave_principal)
        chave_principal.extend(
            weighted_sample_sem_reposicao(pool80, pesos_pool80, faltam)
        )

    # Garante Jogador Principal
    if (
        priorizar_jogador
        and get_pos({"nome": nome_jogador}) <= RANKING_LIMITE_ENTRADA_DIRETA
    ):
        nomes_norm = {normalizar_nome(j.get("nome", "")) for j in chave_principal}
        if normalizar_nome(nome_jogador) not in nomes_norm:
            jogador_principal_obj = {
                "nome": nome_jogador,
                "nacionalidade": nacionalidade_jogador,
            }
            if len(chave_principal) < num_top_diretos:
                chave_principal.append(jogador_principal_obj)
            else:
                ordenado_pior = sorted(
                    [
                        j
                        for j in chave_principal
                        if normalizar_nome(j.get("nome", ""))
                        != normalizar_nome(nome_jogador)
                    ],
                    key=get_pos,
                    reverse=True,
                )
                if ordenado_pior:
                    removido = ordenado_pior[0]
                    chave_principal.remove(removido)
                    chave_principal.append(jogador_principal_obj)

    return chave_principal

def selecionar_campo_finals(jogadores_ranking_ordenado, num_top_diretos):
    """Seleciona o campo do ATP/WTA Finals por pontos YTD."""
    por_ytd = sorted(
        jogadores_ranking_ordenado,
        key=lambda j: int(j.get("pontos_ytd", 0) or 0),
        reverse=True,
    )
    return deduplicar_jogadores(por_ytd[:num_top_diretos])
