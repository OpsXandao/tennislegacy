from __future__ import annotations

from src.dados import carregar_jogador
from src.save import salvar_jogo


def load_player(nome_save: str):
    return carregar_jogador(nome_save)


def save_player(nome_save: str, jogador) -> None:
    salvar_jogo(nome_save, jogador)
