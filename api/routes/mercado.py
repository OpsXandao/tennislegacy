from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.session import Session, obter_sessao_ativa
from src.management import (
    obter_max_equipe,
    obter_profissional_da_equipe,
)
from src.save import salvar_jogo
from src.staff_constants import EMPRESARIOS_DISPONIVEIS, PROFISSIONAIS_DISPONIVEIS

router = APIRouter(prefix="/api/mercado", tags=["mercado"])


class HireRequest(BaseModel):
    prof_id: str


class FireRequest(BaseModel):
    prof_id: str


@router.get("/profissionais")
def listar_profissionais():
    categorias = {
        "treinador": [],
        "fisioterapeuta": [],
        "psicologo": [],
        "marketing": [],
        "empresario": [],
    }

    for pid, info in PROFISSIONAIS_DISPONIVEIS.items():
        cat = info.get("categoria")
        if cat in categorias:
            categorias[cat].append({"id": pid, **info})

    for eid, info in EMPRESARIOS_DISPONIVEIS.items():
        categorias["empresario"].append({"id": eid, **info})

    return categorias


@router.post("/contratar")
def contratar_profissional(
    req: HireRequest, session: Session = Depends(obter_sessao_ativa)
):
    j = session.jogador
    pid = req.prof_id

    if pid in EMPRESARIOS_DISPONIVEIS:
        info = EMPRESARIOS_DISPONIVEIS[pid]
        j.empresario = {
            "id": pid,
            "semanas_restantes": 26,
            "salario": info["salario_semanal"],
        }
        salvar_jogo(session.nome_save_ativo, j)
        return {
            "ok": True,
            "mensagem": f"{info['nome']} contratado como seu novo empresário!",
        }

    if pid in PROFISSIONAIS_DISPONIVEIS:
        info = PROFISSIONAIS_DISPONIVEIS[pid]
        cat = info["categoria"]

        existente = obter_profissional_da_equipe(j.equipe, cat)
        if existente:
            raise HTTPException(
                status_code=400,
                detail=f"Você já possui um {cat} na equipe. Demita-o primeiro.",
            )

        max_equipe = obter_max_equipe(j)
        if len(j.equipe) >= max_equipe:
            raise HTTPException(
                status_code=400,
                detail=f"Sua equipe está cheia (máximo {max_equipe} profissionais). Melhore seu empresário para aumentar o limite.",
            )

        j.equipe.append(
            {"id": pid, "semanas_restantes": 26, "salario": info["salario_semanal"]}
        )

        salvar_jogo(session.nome_save_ativo, j)
        return {"ok": True, "mensagem": f"{info['nome']} contratado com sucesso!"}

    raise HTTPException(status_code=404, detail="Profissional não encontrado.")


@router.post("/demitir")
def demitir_profissional(
    req: FireRequest, session: Session = Depends(obter_sessao_ativa)
):
    j = session.jogador
    pid = req.prof_id

    if j.empresario and j.empresario.get("id") == pid:
        j.empresario = None
        salvar_jogo(session.nome_save_ativo, j)
        return {"ok": True, "mensagem": "Empresário demitido."}

    nova_equipe = [c for c in j.equipe if c.get("id") != pid]
    if len(nova_equipe) < len(j.equipe):
        j.equipe = nova_equipe
        salvar_jogo(session.nome_save_ativo, j)
        return {"ok": True, "mensagem": "Profissional demitido."}

    raise HTTPException(
        status_code=404, detail="Profissional não encontrado na sua equipe."
    )
