from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from api.session import obter_sessao_ativa, Session
from src.save import salvar_jogo

router = APIRouter(prefix="/api/progressao", tags=["progressao"])


class AlocarRequest(BaseModel):
    tipo: str  # "tecnico" ou "psicologico"
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
    j = session.jogador

    pontos = getattr(j, "pontos_de_skill", 0)
    if pontos <= 0:
        raise HTTPException(status_code=400, detail="Sem pontos de skill disponíveis.")

    if req.tipo == "tecnico":
        if req.atributo not in j.atributos:
            raise HTTPException(
                status_code=404, detail=f"Atributo '{req.atributo}' nao encontrado."
            )
        if j.atributos[req.atributo] >= 100:
            raise HTTPException(status_code=400, detail="Atributo já no máximo.")
        j.atributos[req.atributo] = min(100, j.atributos[req.atributo] + 1)
    elif req.tipo == "psicologico":
        psico = getattr(j, "atributos_psicologicos", {})
        if req.atributo not in psico:
            raise HTTPException(
                status_code=404, detail=f"Atributo '{req.atributo}' nao encontrado."
            )
        if psico[req.atributo] >= 100:
            raise HTTPException(status_code=400, detail="Atributo já no máximo.")
        psico[req.atributo] = min(100, psico[req.atributo] + 1)
    else:
        raise HTTPException(
            status_code=422, detail="Tipo deve ser 'tecnico' ou 'psicologico'."
        )

    j.pontos_de_skill = pontos - 1

    if hasattr(j, "_sanitizar_atributos"):
        j._sanitizar_atributos()
    if hasattr(j, "calcular_overall"):
        j.calcular_overall()

    salvar_jogo(session.nome_save_ativo, j)

    return {
        "ok": True,
        "pontos_de_skill": j.pontos_de_skill,
        "atributos": j.atributos,
        "atributos_psicologicos": getattr(j, "atributos_psicologicos", {}),
    }
