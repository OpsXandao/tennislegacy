from __future__ import annotations
from typing import Any, List, Dict, Optional
from src.dados import get_caminho_ranking_save, get_caminho_ranking_duplas
from src.ranking import SistemaRanking

def processar_expiracao_ranking(nome_save: str, semana_atual: int, ano_atual: int):
    """Remove pontos que expiraram nesta semana (há 52 semanas) em todos os rankings."""
    for genero in ["masculino", "feminino"]:
        # 1. Ranking de Simples
        path_s = get_caminho_ranking_save(nome_save, genero=genero)
        rk_s = SistemaRanking(path_s, modalidade="simples")
        _limpar_ranking_obj(rk_s, semana_atual, ano_atual)

        # 2. Ranking de Duplas
        path_d = get_caminho_ranking_duplas(nome_save, genero=genero)
        rk_d = SistemaRanking(path_d, modalidade="duplas")
        _limpar_ranking_obj(rk_d, semana_atual, ano_atual)

def _limpar_ranking_obj(ranking_obj: SistemaRanking, semana_atual: int, ano_atual: int):
    """Lógica interna de limpeza de pontos expirados para um objeto SistemaRanking."""
    mudou_global = False
    is_duplas = ranking_obj.modalidade == "duplas"
    c_pts = "pontos_detalhados" if not is_duplas else "pontos_detalhados_duplas"

    for j in ranking_obj.ranking:
        # Se for um shard lean, precisamos carregar para limpar os pontos detalhados
        if j.get("is_lean"):
            ranking_obj.buscar_jogador_por_nome(j["nome"])

        detalhes = j.get(c_pts, [])
        if not detalhes:
            continue

        novos_detalhes = []
        mudou_jogador = False
        for p in detalhes:
            sem_exp = p.get("semana_expiracao")
            ano_exp = p.get("ano_expiracao")

            expirou = False
            if ano_exp is not None and sem_exp is not None:
                if ano_atual > ano_exp:
                    expirou = True
                elif ano_atual == ano_exp and semana_atual >= sem_exp:
                    expirou = True
            elif sem_exp is not None:
                if semana_atual >= sem_exp:
                    expirou = True

            if expirou:
                mudou_jogador = True
            else:
                novos_detalhes.append(p)

        if mudou_jogador:
            j[c_pts] = novos_detalhes
            mudou_global = True

    if mudou_global:
        ranking_obj.ordenar(recalculate=True)
        ranking_obj.salvar_ranking()
