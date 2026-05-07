from __future__ import annotations

from src.domain_types import SeasonState
from src.dados import carregar_temporada, salvar_temporada


def load_season(nome_save: str) -> SeasonState:
    return carregar_temporada(nome_save)


def save_season(nome_save: str, temporada: SeasonState) -> None:
    salvar_temporada(nome_save, temporada)
