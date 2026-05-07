from __future__ import annotations

from src.domain_types import TournamentState
from src.dados import (
    carregar_estado_torneio,
    get_caminho_ranking_save,
    get_caminho_torneio_save,
)
from src.jogador import carregar_jogador
from src.ranking import SistemaRanking
from src.torneio_core import Torneio


def load_tournament_state(nome_save: str, genero: str) -> TournamentState | None:
    return carregar_estado_torneio(nome_save, genero=genero)


def load_regular_tournament(
    nome_save: str, genero: str | None = None
) -> Torneio | None:
    generos = [genero] if genero else ["masculino", "feminino"]
    for genero_alvo in generos:
        estado = load_tournament_state(nome_save, genero=genero_alvo)
        if not estado:
            continue

        jogador = carregar_jogador(nome_save)
        jogador_nome = jogador.nome if jogador else estado.get("jogador", "Jogador")
        jogador_nacionalidade = (
            jogador.nacionalidade
            if jogador
            else estado.get("jogador_nacionalidade", "??")
        )
        tournament_data = estado.get("tournament_data") or {
            "nome": estado.get("torneio", "Torneio"),
            "tipo": estado.get("tipo", "ATP 250"),
            "semana": estado.get("semana", 1),
        }
        ranking = SistemaRanking(
            get_caminho_ranking_save(nome_save, genero=genero_alvo),
            modalidade="simples",
        )
        instancia = Torneio(
            tournament_data,
            jogador_nome,
            jogador_nacionalidade,
            ranking,
            nome_save=nome_save,
            genero=genero_alvo,
        )
        instancia.caminho_json = get_caminho_torneio_save(
            nome_save, genero=genero_alvo
        )
        return instancia
    return None
