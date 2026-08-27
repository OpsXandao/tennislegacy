from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.session import Session, obter_sessao_ativa, refresh_session
from src.save import salvar_jogo
from src.services.communication_service import (
    aceitar_email,
    marcar_email_especifico_lido,
    marcar_emails_lidos,
    remover_email,
)

router = APIRouter(prefix="/api/email", tags=["email"])


class EmailActionRequest(BaseModel):
    email_id: str
    acao: str


def _normalizar_email_payload(email: dict) -> dict:
    payload = dict(email)
    tipo = payload.get("tipo")
    if tipo == "patrocinio":
        payload.setdefault("tipo_original", tipo)
        payload["tipo"] = "proposta_patrocinio"
        payload.setdefault("acao", "contrato")
    elif tipo == "empresario":
        payload.setdefault("tipo_original", tipo)
        payload["tipo"] = "proposta_empresario"
        payload.setdefault("acao", "contrato")
    payload.setdefault("assunto", payload.get("titulo") or "PROPOSTA DE CARREIRA")
    payload.setdefault("corpo", payload.get("mensagem") or payload.get("texto") or "")
    payload.setdefault("remetente", payload.get("from") or "Tennis Legacy")
    payload.setdefault("id", payload.get("ref_id", ""))
    payload.setdefault("lido", False)
    return payload


@router.get("/inbox")
def listar_emails(session: Session = Depends(obter_sessao_ativa)):
    caixa = getattr(session.jogador, "caixa_email", [])
    emails = [_normalizar_email_payload(e) for e in caixa if isinstance(e, dict)]
    nao_lidos = sum(1 for e in emails if not e.get("lido"))
    return {"emails": emails, "unread_count": nao_lidos}


@router.get("/unread-count")
def obter_contagem_nao_lidos(session: Session = Depends(obter_sessao_ativa)):
    caixa = getattr(session.jogador, "caixa_email", [])
    return {"unread_count": sum(1 for e in caixa if not e.get("lido"))}


@router.post("/marcar-lidos")
def marcar_lidos(session: Session = Depends(obter_sessao_ativa)):
    marcar_emails_lidos(session.nome_save_ativo, session.jogador)
    return {"ok": True}


@router.post("/{email_id}/lido")
def marcar_lido_especifico(email_id: str, session: Session = Depends(obter_sessao_ativa)):
    marcar_email_especifico_lido(session.nome_save_ativo, session.jogador, email_id)
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
    refresh_session(nome_save)
    return resultado
