from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from api.session import obter_sessao_ativa, Session, refresh_session
from src.services.sponsorship_service import (
    assinar_patrocinio,
    carregar_patrocinadores,
    listar_patrocinios_ativos,
    listar_patrocinios_disponiveis,
    migrar_patrocinios,
    resumir_contexto_patrocinio,
)
from src.constants.torneio_constants import RANKING_POSICAO_FALLBACK

router = APIRouter(prefix="/api/patrocinio", tags=["patrocinio"])
_PATROCINADORES = carregar_patrocinadores()


@router.get("/ativos")
def get_patrocinios_ativos(session: Session = Depends(obter_sessao_ativa)):
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessão não iniciada.")
    j = session.jogador
    rk = session.ranking_atp if j.genero == "masculino" else session.ranking_wta
    posicao = rk.obter_posicao(j.nome) if rk else None
    patrocinios_brutos = getattr(j, "patrocinios", [])
    if not isinstance(patrocinios_brutos, list):
        j.patrocinios = []
        patrocinios_brutos = []
    elif patrocinios_brutos and all(not isinstance(item, dict) for item in patrocinios_brutos):
        j.patrocinios = migrar_patrocinios(patrocinios_brutos)
    return {"patrocinios": listar_patrocinios_ativos(j, posicao, _PATROCINADORES)}


@router.get("/disponiveis")
def get_patrocinios_disponiveis(session: Session = Depends(obter_sessao_ativa)):
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessão não iniciada.")
    j = session.jogador
    rk = session.ranking_atp if j.genero == "masculino" else session.ranking_wta
    if rk is None:
        raise HTTPException(status_code=500, detail="Ranking não carregado")
    _pos = rk.obter_posicao(j.nome)
    posicao = _pos if (_pos is not None and _pos != 0) else RANKING_POSICAO_FALLBACK
    return {
        "contexto": resumir_contexto_patrocinio(j, posicao, _PATROCINADORES),
        "patrocinadores": listar_patrocinios_disponiveis(j, posicao, getattr(j, "seguidores", 0), _PATROCINADORES),
    }


class AssinarPatrocinioBody(BaseModel):
    patrocinio_id: str | None = None
    id: str | None = None


@router.post("/assinar")
def post_assinar_patrocinio(
    body: AssinarPatrocinioBody, session: Session = Depends(obter_sessao_ativa)
):
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessão não iniciada.")
    j = session.jogador
    rk = session.ranking_atp if j.genero == "masculino" else session.ranking_wta
    if rk is None:
        raise HTTPException(status_code=500, detail="Ranking não carregado")
    pat_id = body.patrocinio_id or body.id
    if not pat_id:
        raise HTTPException(status_code=422, detail="Patrocínio não informado.")
    _pos = rk.obter_posicao(j.nome)
    posicao = _pos if (_pos is not None and _pos != 0) else RANKING_POSICAO_FALLBACK
    resultado = assinar_patrocinio(session.nome_save_ativo, j, pat_id, posicao)
    if resultado.get("status") == 404:
        raise HTTPException(status_code=404, detail=resultado["mensagem"])
    refresh_session(session.nome_save_ativo)
    return resultado
