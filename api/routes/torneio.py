from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.logging_utils import log_event
from api.routes._shared import carregar_temporada_atual
from api.session import Session, obter_sessao_ativa, refresh_session
from src.services.davis_service import (
    checar_convocacao_na_semana,
    recusar_convocacao_na_semana,
)
from src.services.tournament_service import (
    advance_tournament_phase,
    create_tournament,
    get_tournament_state,
    withdraw_from_tournament,
)

router = APIRouter(prefix="/api/torneio", tags=["torneio"])


class CriarTorneioBody(BaseModel):
    modalidade: str
    parceiro: str | None = None
    torneio_nome: str | None = None


@router.get("/checar-convocacao")
def checar_convocacao(session: Session = Depends(obter_sessao_ativa)):
    temporada = carregar_temporada_atual(session.nome_save_ativo)
    return checar_convocacao_na_semana(
        session.nome_save_ativo, session.jogador, temporada["semana"]
    )


@router.post("/recusar-convocacao")
def recusar_convocacao(session: Session = Depends(obter_sessao_ativa)) -> dict:
    temporada = carregar_temporada_atual(session.nome_save_ativo)
    recusar_convocacao_na_semana(
        session.nome_save_ativo, session.jogador, temporada["semana"]
    )
    return {"ok": True, "mensagem": "Convocação recusada. Moral afetada."}


@router.post("/criar")
def criar(
    body: CriarTorneioBody, session: Session = Depends(obter_sessao_ativa)
) -> dict:
    return create_tournament(
        nome_save=session.nome_save_ativo,
        jogador=session.jogador,
        modalidade=body.modalidade,
        parceiro=body.parceiro,
        torneio_nome=body.torneio_nome,
    )


@router.get("/historico")
def historico_torneio(
    nome: str, session: Session = Depends(obter_sessao_ativa)
) -> dict:
    historico = getattr(session.jogador, "historico_torneios", [])
    entradas = [h for h in historico if h.get("nome") == nome]
    if not entradas:
        return {"pontos_a_defender": 0, "ultima_colocacao": None}
    entradas.sort(key=lambda h: (h.get("ano", 0), h.get("semana", 0)), reverse=True)
    ultima = entradas[0]
    return {"pontos_a_defender": ultima.get("pontos", 0), "ultima_colocacao": ultima.get("fase")}


@router.get("/estado")
def get_estado(session: Session = Depends(obter_sessao_ativa)):
    return get_tournament_state(session.nome_save_ativo)


@router.post("/avancar-fase")
def avancar(session: Session = Depends(obter_sessao_ativa)) -> dict:
    return advance_tournament_phase(session.nome_save_ativo)


@router.post("/desistir")
def desistir(session: Session = Depends(obter_sessao_ativa)) -> dict:
    nome_save = session.nome_save_ativo
    jogador = session.jogador
    resultado = withdraw_from_tournament(
        nome_save,
        genero=jogador.genero,
        expected_week=session.semana_atual,
    )
    refresh_session(nome_save)
    return {"ok": True, **resultado}
