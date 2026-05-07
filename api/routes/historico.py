from fastapi import APIRouter, Depends

from api.session import Session, obter_sessao_ativa
from src.dados import carregar_historico

router = APIRouter(prefix="/api/historico", tags=["historico"])


@router.get("/goat")
def obter_goat_list(session: Session = Depends(obter_sessao_ativa)):
    hist = carregar_historico(session.nome_save_ativo)
    recordes = hist.get("recordes", {})
    meus_titulos = getattr(session.jogador, "trofeus", [])
    return {
        "recordes": recordes,
        "meus_titulos": meus_titulos,
        "goat_points": 0,
        "GoatPoints": 0,
    }


@router.get("/campeoes")
def listar_campeoes_por_ano(session: Session = Depends(obter_sessao_ativa)):
    hist = carregar_historico(session.nome_save_ativo)
    return {"campeoes": hist.get("campeoes", {})}
