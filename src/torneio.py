"""
Compat layer para manter API pública do módulo de torneio.

Implementação principal em `src.torneio_core`.
"""

from __future__ import annotations

from src.dados import (
    carregar_estado_torneio,
    get_caminho_ranking_save,
    get_caminho_torneio_save,
)
from src.json_utils import salvar_json_seguro
from src.ranking import SistemaRanking
from src.repositories.tournament_repository import load_regular_tournament
from src.torneio_core import Torneio


def extrair_nome_puro(resultado) -> str:
    if isinstance(resultado, dict):
        vencedor = resultado.get("vencedor", {})
        if isinstance(vencedor, dict):
            return str(vencedor.get("nome", "Desconhecido")).strip()
        if vencedor:
            return str(vencedor).strip()
        nome = resultado.get("nome")
        if nome:
            return str(nome).strip()
        return "Desconhecido"
    if isinstance(resultado, str):
        partes = resultado.split(" x ")
        if len(partes) > 1:
            nome = " x ".join(partes[:-1]).strip()
            nome = nome.rstrip("0123456789").strip()
            return nome or resultado.strip()
        return resultado.strip()
    return str(resultado).strip() if resultado is not None else "Desconhecido"


def salvar_torneio(torneio: Torneio) -> None:
    caminho = get_caminho_torneio_save(torneio.nome_save, genero=torneio.genero)
    salvar_json_seguro(caminho, torneio._carregar_estado())


def carregar_torneio(nome_save: str, genero: str | None = None) -> Torneio | None:
    return load_regular_tournament(nome_save, genero=genero)


def criar_torneio(torneio_data, jogador, nome_save, semana):
    genero = getattr(jogador, "genero", "masculino")
    tournament_data = dict(torneio_data or {})
    tournament_data.setdefault("semana", semana)
    ranking = SistemaRanking(
        get_caminho_ranking_save(nome_save, genero=genero),
        modalidade="simples",
    )
    instancia = Torneio(
        tournament_data,
        jogador.nome,
        jogador.nacionalidade,
        ranking,
        nome_save=nome_save,
        genero=genero,
    )
    instancia.iniciar_torneio(tournament_data.get("nome", "Torneio"), ranking.ranking)
    return instancia


def simular_partidas_npc(torneio: Torneio, nome_jogador=None) -> None:
    if nome_jogador is None:
        nome_jogador = torneio.jogador_nome
    torneio.simular_npcs_na_fase_atual(nome_jogador)


def avancar_fase(torneio: Torneio) -> None:
    estado = torneio._carregar_estado()
    torneio._atualizar_fase_se_necessario(estado)
    torneio._salvar_estado(estado)

__all__ = [
    "Torneio",
    "criar_torneio",
    "salvar_torneio",
    "carregar_torneio",
    "simular_partidas_npc",
    "avancar_fase",
    "extrair_nome_puro",
    "carregar_estado_torneio",
    "get_caminho_torneio_save",
    "salvar_json_seguro",
]
