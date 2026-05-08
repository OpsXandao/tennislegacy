from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from api.session import Session, obter_sessao_ativa
from api.services import duplas_service

router = APIRouter(prefix="/api/duplas", tags=["duplas"])


class InviteRequest(BaseModel):
    npc_nome: str
    torneio_tipo: str = "ATP 250"


@router.get("/sugestoes")
def sugerir_parceiros(session: Session = Depends(obter_sessao_ativa)):
    return {"parceiros": duplas_service.buscar_sugestoes(session)}


@router.get("/buscar")
def buscar_parceiros(
    nome: Optional[str] = None,
    nacionalidade: Optional[str] = None,
    session: Session = Depends(obter_sessao_ativa),
):
    return {"parceiros": duplas_service.buscar(session, nome, nacionalidade)}


@router.post("/convidar")
def convidar(req: InviteRequest, session: Session = Depends(obter_sessao_ativa)):
    return duplas_service.convidar(session, req.npc_nome, req.torneio_tipo)
