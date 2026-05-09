from fastapi import APIRouter, Depends

from api.session import Session, obter_sessao_ativa
from api.services.mundo_service import obter_campeoes, obter_goat

router = APIRouter(prefix="/api/historico", tags=["historico"])


@router.get("/goat")
def get_goat(session: Session = Depends(obter_sessao_ativa)):
    trofeus = getattr(session.jogador, "trofeus", [])
    return obter_goat(session.nome_save_ativo, trofeus)


@router.get("/campeoes")
def get_campeoes(session: Session = Depends(obter_sessao_ativa)):
    return obter_campeoes(session.nome_save_ativo)
