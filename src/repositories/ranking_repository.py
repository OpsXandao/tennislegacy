from __future__ import annotations

from src.domain_types import RankingsByTour
from src.dados import get_caminho_ranking_duplas, get_caminho_ranking_save
from src.ranking import SistemaRanking


def load_all_rankings(nome_save: str) -> RankingsByTour:
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


def load_singles_ranking(nome_save: str, genero: str) -> SistemaRanking:
    return SistemaRanking(
        get_caminho_ranking_save(nome_save, genero=genero), modalidade="simples"
    )
