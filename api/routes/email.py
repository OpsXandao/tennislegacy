from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.session import Session, obter_sessao_ativa
from src.services.communication_service import (
    aceitar_email,
    marcar_emails_lidos,
    remover_email,
)

router = APIRouter(prefix="/api/email", tags=["email"])


class EmailActionRequest(BaseModel):
    email_id: str
    acao: str


@router.get("/inbox")
def listar_emails(session: Session = Depends(obter_sessao_ativa)):
    caixa = getattr(session.jogador, "caixa_email", [])
    nao_lidos = sum(1 for e in caixa if not e.get("lido"))
    return {"emails": caixa, "unread_count": nao_lidos}


@router.get("/unread-count")
def obter_contagem_nao_lidos(session: Session = Depends(obter_sessao_ativa)):
    caixa = getattr(session.jogador, "caixa_email", [])
    return {"unread_count": sum(1 for e in caixa if not e.get("lido"))}


@router.post("/marcar-lidos")
def marcar_lidos(session: Session = Depends(obter_sessao_ativa)):
    marcar_emails_lidos(session.nome_save_ativo, session.jogador)
    return {"ok": True}


@router.post("/acao")
def processar_email(
    req: EmailActionRequest, session: Session = Depends(obter_sessao_ativa)
):
    nome_save = session.nome_save_ativo
    j = session.jogador
    rk = session.ranking_atp if j.genero == "masculino" else session.ranking_wta

    if req.acao in ("recusar", "deletar"):
        resultado = remover_email(nome_save, j, req.email_id)
    elif req.acao == "aceitar":
        resultado = aceitar_email(nome_save, j, req.email_id, rk)
    else:
        raise HTTPException(status_code=400, detail="Ação inválida.")

    if not resultado.get("ok"):
        raise HTTPException(
            status_code=resultado.get("status", 400), detail=resultado["mensagem"]
        )
    return resultado
