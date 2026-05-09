from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.session import Session, obter_sessao_ativa
from src.imprensa import obter_pergunta_contextual, processar_resposta_imprensa
from src.save import salvar_jogo

router = APIRouter(prefix="/api/imprensa", tags=["imprensa"])


@router.get("/pergunta")
def get_pergunta(contexto: str = "geral", session: Session = Depends(obter_sessao_ativa)):
    pergunta = obter_pergunta_contextual(contexto)
    if not pergunta:
        return {"pergunta": None}
    p = dict(pergunta)
    p["etiquetas"] = list(p.get("etiquetas", set()))
    return {"pergunta": p}


class ResponderBody(BaseModel):
    opcao_idx: int
    contexto: str = "geral"


@router.post("/responder")
def responder(body: ResponderBody, session: Session = Depends(obter_sessao_ativa)):
    pergunta = obter_pergunta_contextual(body.contexto)
    if not pergunta:
        return {"ok": False, "mensagem": "Nenhuma pergunta disponível"}

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
