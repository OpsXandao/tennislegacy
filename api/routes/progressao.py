from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from api.session import obter_sessao_ativa, Session
from api.services.training_service import alocar_skill

router = APIRouter(prefix="/api/progressao", tags=["progressao"])


class AlocarRequest(BaseModel):
    tipo: str
    atributo: str


@router.get("/status")
def status(session: Session = Depends(obter_sessao_ativa)):
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessao nao iniciada.")
    j = session.jogador
    return {
        "nivel": j.nivel,
        "xp": j.xp,
        "xp_para_proximo_nivel": getattr(j, "xp_para_proximo_nivel", 100),
        "pontos_de_skill": getattr(j, "pontos_de_skill", 0),
        "atributos": j.atributos,
        "atributos_psicologicos": getattr(j, "atributos_psicologicos", {}),
    }


@router.post("/alocar")
def alocar(req: AlocarRequest, session: Session = Depends(obter_sessao_ativa)):
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessao nao iniciada.")
    resultado = alocar_skill(session, req.tipo, req.atributo)
    if not resultado.get("ok"):
        raise HTTPException(status_code=resultado.get("status", 400), detail=resultado["erro"])
    return resultado
