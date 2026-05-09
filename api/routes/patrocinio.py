from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from api.session import obter_sessao_ativa, Session
from src.dados import carregar_patrocinadores
from src.services.sponsorship_service import (
    listar_patrocinios_ativos,
    listar_patrocinios_disponiveis,
    migrar_patrocinios,
    pode_assinar_patrocinio,
    resumir_contexto_patrocinio,
)
from src.constants.torneio_constants import RANKING_POSICAO_FALLBACK
from src.save import salvar_jogo

router = APIRouter(prefix="/api/patrocinio", tags=["patrocinio"])
PATROCINADORES_DISPONIVEIS = carregar_patrocinadores()


@router.get("/ativos")
def get_patrocinios_ativos(session: Session = Depends(obter_sessao_ativa)):
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessão não iniciada.")

    patrocinios_brutos = getattr(session.jogador, "patrocinios", [])
    if all(not isinstance(item, dict) for item in patrocinios_brutos):
        session.jogador.patrocinios = migrar_patrocinios(patrocinios_brutos)

    return {
        "patrocinios": listar_patrocinios_ativos(
            session.jogador, PATROCINADORES_DISPONIVEIS
        )
    }


@router.get("/disponiveis")
def get_patrocinios_disponiveis(session: Session = Depends(obter_sessao_ativa)):
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessão não iniciada.")

    j = session.jogador
    rk = session.ranking_atp if j.genero == "masculino" else session.ranking_wta
    if rk is None:
        raise HTTPException(status_code=500, detail="Ranking não carregado")

    posicao = rk.obter_posicao(j.nome) or RANKING_POSICAO_FALLBACK
    seguidores = getattr(j, "seguidores", 0)

    return {
        "contexto": resumir_contexto_patrocinio(
            j, posicao, PATROCINADORES_DISPONIVEIS
        ),
        "patrocinadores": listar_patrocinios_disponiveis(
            j, posicao, seguidores, PATROCINADORES_DISPONIVEIS
        ),
    }


class AssinarPatrocinioBody(BaseModel):
    patrocinio_id: str | None = None
    id: str | None = None


@router.post("/assinar")
def assinar_patrocinio(
    body: AssinarPatrocinioBody, session: Session = Depends(obter_sessao_ativa)
):
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessão não iniciada.")

    j = session.jogador
    rk = session.ranking_atp if j.genero == "masculino" else session.ranking_wta
    if rk is None:
        raise HTTPException(status_code=500, detail="Ranking não carregado")

    posicao = rk.obter_posicao(j.nome) or RANKING_POSICAO_FALLBACK
    patrocinio_id = body.patrocinio_id or body.id
    if not patrocinio_id:
        raise HTTPException(status_code=422, detail="Patrocínio não informado.")

    pode, motivo = pode_assinar_patrocinio(j, patrocinio_id, posicao, j.seguidores)
    if not pode:
        return {"ok": False, "mensagem": motivo}

    pat = PATROCINADORES_DISPONIVEIS.get(patrocinio_id)
    if not pat:
        raise HTTPException(status_code=404, detail="Patrocinador não encontrado")

    j.patrocinios.append(patrocinio_id)

    # Bônus de assinatura
    bonus = int(pat.get("bonus_assinatura", 0) or 0)
    if bonus > 0:
        j.registrar_transacao(
            bonus,
            f"Bônus Assinatura: {pat.get('nome', patrocinio_id)}",
            categoria="patrocinio",
        )

    salvar_jogo(session.nome_save_ativo, j)
    return {"ok": True, "mensagem": f"Contrato assinado com {pat.get('nome')}!"}
