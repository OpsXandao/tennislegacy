from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.session import Session, obter_sessao_ativa
from api.services import staff_service

router = APIRouter(prefix="/api/staff", tags=["staff"])


class HireRequest(BaseModel):
    prof_id: str


class FireRequest(BaseModel):
    prof_id: str


@router.get("/equipe")
def get_equipe(session: Session = Depends(obter_sessao_ativa)):
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessão não iniciada.")
    return staff_service.get_equipe_dict(session.jogador)


@router.get("/profissionais")
def listar_profissionais():
    return staff_service.listar_todos()


@router.post("/contratar")
def contratar_profissional(req: HireRequest, session: Session = Depends(obter_sessao_ativa)):
    return staff_service.contratar(session, req.prof_id)


@router.post("/demitir")
def demitir_profissional(req: FireRequest, session: Session = Depends(obter_sessao_ativa)):
    return staff_service.demitir(session, req.prof_id)
