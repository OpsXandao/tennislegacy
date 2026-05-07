from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.session import Session, obter_sessao_ativa

router = APIRouter(prefix="/api/notificacoes", tags=["notificacoes"])


@router.get("")
def get_notificacoes(session: Session = Depends(obter_sessao_ativa)):
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessão não iniciada.")

    j = session.jogador
    # Emails não lidos
    emails_pendentes = [
        e
        for e in getattr(j, "caixa_email", [])
        if isinstance(e, dict) and e.get("status") == "pendente"
    ]

    # Propostas pendentes (são um tipo de email)
    propostas = [
        e
        for e in emails_pendentes
        if e.get("tipo") in {"patrocinio", "empresario"}
    ]

    # Eventos da semana (pode vir de algum log ou estado da temporada)
    # Por enquanto retornamos vazio ou algo genérico
    eventos = []

    return {
        "emails_nao_lidos": len(emails_pendentes),
        "eventos_semana": eventos,
        "propostas_pendentes": len(propostas),
    }


@router.post("/marcar-lidas")
def marcar_lidas(session: Session = Depends(obter_sessao_ativa)):
    # No sistema atual, as notificações (emails) são marcadas como lidas
    # individualmente quando aceitas/recusadas. 
    # Este endpoint pode ser usado para limpar badges visuais.
    return {"ok": True}
