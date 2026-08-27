import base64
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.session import Session, obter_sessao_ativa
from src.imprensa import obter_pergunta_contextual, processar_resposta_imprensa
from src.save import salvar_jogo

router = APIRouter(prefix="/api/imprensa", tags=["imprensa"])


def _calcular_hash_pergunta(texto: str) -> str:
    return base64.b64encode(texto[:50].encode("utf-8")).decode("ascii")


@router.get("/pergunta")
def get_pergunta(contexto: str = "geral", session: Session = Depends(obter_sessao_ativa)):
    pergunta = obter_pergunta_contextual(contexto)
    if not pergunta:
        return {"pergunta": None}
    p = dict(pergunta)
    p["etiquetas"] = list(p.get("etiquetas", set()))
    p["pergunta_hash"] = _calcular_hash_pergunta(p.get("texto", ""))
    return {"pergunta": p}


class ResponderBody(BaseModel):
    opcao_idx: int
    contexto: str = "geral"
    pergunta_hash: Optional[str] = None


@router.post("/responder")
def responder(body: ResponderBody, session: Session = Depends(obter_sessao_ativa)):
    pergunta = obter_pergunta_contextual(body.contexto)
    if not pergunta:
        return {"ok": False, "mensagem": "Nenhuma pergunta disponível"}

    if body.pergunta_hash is not None:
        hash_atual = _calcular_hash_pergunta(pergunta.get("texto", ""))
        if hash_atual != body.pergunta_hash:
            return {"ok": False, "mensagem": "Pergunta desatualizada, recarregue."}

    opcoes = pergunta.get("opcoes", [])
    if body.opcao_idx < 0 or body.opcao_idx >= len(opcoes):
        return {"ok": False, "mensagem": "Índice de opção inválido"}

    opcao = opcoes[body.opcao_idx]
    moral_delta, rep_delta = processar_resposta_imprensa(session.jogador, pergunta, opcao)
    salvar_jogo(session.nome_save_ativo, session.jogador)

    return {
        "ok": True,
        "texto_opcao": opcao.get("texto"),
        "moral_delta": moral_delta,
        "rep_delta": rep_delta,
        "moral": getattr(session.jogador, "moral", 70),
        "reputacao": getattr(session.jogador, "reputacao", 50),
    }
