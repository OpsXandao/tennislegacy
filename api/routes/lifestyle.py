from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import json
import os
from api.session import Session, obter_sessao_ativa
from src.save import salvar_jogo

router = APIRouter(prefix="/api/lifestyle", tags=["lifestyle"])

DB_PATH = "db/lifestyle_items.json"


def carregar_itens_lifestyle():
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/itens")
def get_lifestyle_itens(session: Session = Depends(obter_sessao_ativa)):
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessão não iniciada.")

    itens = carregar_itens_lifestyle()
    possuidos = getattr(session.jogador, "lifestyle", [])

    # Adiciona flag 'comprado'
    res = {}
    for cat, lista in itens.items():
        res[cat] = []
        for item in lista:
            item_copy = item.copy()
            item_copy["comprado"] = item["id"] in possuidos
            item_copy["pode_comprar"] = (
                session.jogador.dinheiro >= item["preco"] and not item_copy["comprado"]
            )
            res[cat].append(item_copy)

    return res


class BuyItemRequest(BaseModel):
    item_id: str


@router.post("/comprar")
def comprar_item(req: BuyItemRequest, session: Session = Depends(obter_sessao_ativa)):
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessão não iniciada.")

    itens_all = carregar_itens_lifestyle()
    item_alvo = None
    for cat in itens_all.values():
        for item in cat:
            if item["id"] == req.item_id:
                item_alvo = item
                break
        if item_alvo:
            break

    if not item_alvo:
        raise HTTPException(status_code=404, detail="Item não encontrado.")

    if item_alvo["id"] in session.jogador.lifestyle:
        raise HTTPException(status_code=400, detail="Você já possui este item.")

    if session.jogador.dinheiro < item_alvo["preco"]:
        raise HTTPException(status_code=400, detail="Saldo insuficiente.")

    session.jogador.dinheiro -= item_alvo["preco"]
    session.jogador.lifestyle.append(item_alvo["id"])

    session.jogador.registrar_transacao(
        -item_alvo["preco"], f"Compra: {item_alvo['nome']}", categoria="lifestyle"
    )

    salvar_jogo(session.nome_save_ativo, session.jogador)
    return {"ok": True, "mensagem": f"Você adquiriu {item_alvo['nome']}!"}
