from __future__ import annotations

from typing import NotRequired, TypedDict

from src.ranking import SistemaRanking


class EmailMessage(TypedDict, total=False):
    id: str
    assunto: str
    corpo: str
    tipo: str
    lido: bool


class SeasonState(TypedDict):
    ano: int
    semana: int


class RankingEntry(TypedDict, total=False):
    nome: str
    nacionalidade: str
    pontos: int
    pontos_duplas: int
    pontos_ranking: int
    pontos_ranking_duplas: int
    pontos_ytd: int
    overall: int
    energia: int
    fadiga: int
    moral: int
    is_lean: bool
    is_bot: bool
    e_ficticio: bool
    atributos: dict[str, int]
    atributos_psicologicos: dict[str, int]
    historico_torneios: list[dict]
    historico_partidas: list[dict]
    pontos_detalhados: list[dict]
    pontos_detalhados_duplas: list[dict]
    status_lesao: dict
    status_doenca: dict
    protected_ranking: int | None
    protected_ranking_semanas: int


class TournamentState(TypedDict, total=False):
    torneio: str
    semana: int
    fase_atual: str
    fase_atual_duplas: str
    jogador: str
    jogador_vivo: bool
    jogador_vivo_duplas: bool
    tournament_data: dict
    genero: str
    tipo: str
    rodadas: dict[str, list]
    resultados: dict[str, list]
    rodadas_duplas: dict[str, list]
    resultados_duplas: dict[str, list]
    agenda_dia: dict
    entry_status: dict
    campeao_simples: NotRequired[str | None]
    campeao_duplas: NotRequired[str | None]
    lucky_losers: NotRequired[list[RankingEntry]]


class RankingsByTour(TypedDict):
    simples_atp: SistemaRanking
    duplas_atp: SistemaRanking
    simples_wta: SistemaRanking
    duplas_wta: SistemaRanking
