from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.session import Session, obter_sessao_ativa
from src.services.davis_service import (
    obter_estado_davis,
    obter_proximo_davis,
    simular_davis_atual,
)

router = APIRouter(prefix="/api/davis", tags=["davis"])

class DavisPartidaHistoricoResponse(BaseModel):
    jogador_a: str
    jogador_b: str
    placar: str
    vencedor: str


class DavisConfrontoResponse(BaseModel):
    equipe_a: str
    equipe_b: str
    placar_tie: list[int]
    partidas: list[DavisPartidaHistoricoResponse]
    vencedor: str | None = None


class DavisInfoPartidaResponse(BaseModel):
    jogador1: str
    jogador2: str
    partida_idx: int | None = None
    tipo: str | None = None


class DavisEstadoResponse(BaseModel):
    nome: str
    tipo: str
    fase_atual: str
    jogador_ativo: bool
    jogador_convocado: bool
    partida_disponivel: bool
    info_partida: DavisInfoPartidaResponse | None = None
    confronto_atual: DavisConfrontoResponse | None = None
    proximo: dict | None = None
    estado: dict


class DavisSimulacaoResponse(BaseModel):
    ok: bool
    placar: str
    vencedor: str | None = None


@router.get("/estado")
def estado(session: Session = Depends(obter_sessao_ativa)) -> DavisEstadoResponse:
    return obter_estado_davis(session.nome_save_ativo, session.jogador)


@router.get("/proximo")
def proximo(session: Session = Depends(obter_sessao_ativa)) -> dict | None:
    return obter_proximo_davis(session.nome_save_ativo, session.jogador)


@router.post("/simular-atual")
def simular_atual(
    session: Session = Depends(obter_sessao_ativa),
) -> DavisSimulacaoResponse:
    return simular_davis_atual(session.nome_save_ativo, session.jogador)
