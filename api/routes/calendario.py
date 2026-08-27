from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from api.logging_utils import log_event, log_exception
from api.session import Session, obter_sessao_ativa, refresh_session
from api.services import calendario_service

router = APIRouter(prefix="/api/calendario", tags=["calendario"])


@router.get("/semana/{numero}")
def obter_semana(
    numero: int,
    tour: str | None = Query(default=None),
    session: Session = Depends(obter_sessao_ativa),
) -> dict:
    return calendario_service.obter_semana_por_numero(numero, tour, session.jogador)


@router.get("/atual")
def obter_atual(
    tour: str | None = Query(default=None),
    session: Session = Depends(obter_sessao_ativa),
) -> dict:
    return calendario_service.obter_semana_atual(session.nome_save_ativo, tour, session.jogador)


@router.post("/avancar")
def avancar(session: Session = Depends(obter_sessao_ativa)) -> dict:
    nome_save = session.nome_save_ativo
    jogador = session.jogador
    try:
        resultado = calendario_service.avancar(session)
        refresh_session(nome_save)
        log_event(
            logging.INFO,
            "semana_avancada",
            save=nome_save,
            jogador=jogador.nome,
            semana_nova=resultado.get("semana"),
            num_eventos=len(resultado.get("eventos", [])),
        )
        return resultado
    except Exception as exc:
        log_exception(
            "erro_ao_avancar_semana",
            exc,
            save=nome_save,
            jogador=jogador.nome,
            causa_provavel="Falha em avancar_semana() — pode ser torneio NPC com estado corrompido "
            "ou erro na expiração de pontos do ranking.",
        )
        raise HTTPException(status_code=500, detail="Erro ao avançar semana.") from exc
