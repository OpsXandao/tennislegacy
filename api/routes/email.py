from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.session import Session, obter_sessao_ativa
from src.patrocinios import processar_acao_email_carreira
from src.save import salvar_jogo

router = APIRouter(prefix="/api/email", tags=["email"])


class EmailActionRequest(BaseModel):
    email_id: str
    acao: str  # "aceitar", "recusar", "deletar"


@router.get("/inbox")
def listar_emails(session: Session = Depends(obter_sessao_ativa)):
    caixa = getattr(session.jogador, "caixa_email", [])
    nao_lidos = sum(1 for e in caixa if not e.get("lido"))
    return {"emails": caixa, "unread_count": nao_lidos}


@router.get("/unread-count")
def obter_contagem_nao_lidos(session: Session = Depends(obter_sessao_ativa)):
    caixa = getattr(session.jogador, "caixa_email", [])
    nao_lidos = sum(1 for e in caixa if not e.get("lido"))
    return {"unread_count": nao_lidos}


@router.post("/marcar-lidos")
def marcar_emails_como_lidos(session: Session = Depends(obter_sessao_ativa)):
    j = session.jogador
    caixa = getattr(j, "caixa_email", [])
    houve_mudanca = False
    for email in caixa:
        if not email.get("lido"):
            email["lido"] = True
            houve_mudanca = True

    if houve_mudanca:
        salvar_jogo(session.nome_save_ativo, j)

    return {"ok": True}


@router.post("/acao")
def processar_email(
    req: EmailActionRequest, session: Session = Depends(obter_sessao_ativa)
):
    j = session.jogador
    caixa = getattr(j, "caixa_email", [])

    proposta = next((p for p in caixa if p.get("id") == req.email_id), None)
    if not proposta:
        raise HTTPException(status_code=404, detail="E-mail não encontrado.")

    if req.acao in ["recusar", "deletar"]:
        j.caixa_email = [p for p in caixa if p.get("id") != req.email_id]
        salvar_jogo(session.nome_save_ativo, j)
        return {"ok": True, "mensagem": "E-mail removido."}

    if req.acao == "aceitar":
        rk = session.ranking_atp if j.genero == "masculino" else session.ranking_wta
        sucesso, msg = processar_acao_email_carreira(j, proposta, "aceitar", rk)
        if sucesso:
            j.caixa_email = [p for p in caixa if p.get("id") != req.email_id]
            salvar_jogo(session.nome_save_ativo, j)
            return {"ok": True, "mensagem": msg}
        else:
            raise HTTPException(status_code=400, detail=msg)

    raise HTTPException(status_code=400, detail="Ação inválida.")
