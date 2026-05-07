from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.logging_utils import log_event
from api.routes._shared import carregar_temporada_atual
from api.session import Session, obter_sessao_ativa
from src.calendario import obter_torneios_da_semana
from src.ranking import SistemaRanking
from src.dados import get_caminho_ranking_save
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
    nome_save = session.nome_save_ativo
    jogador = session.jogador
    temporada = carregar_temporada_atual(nome_save)
    torneios = obter_torneios_da_semana(temporada["semana"], genero=jogador.genero)

    davis_data = next(
        (t for t in torneios if t.get("tipo") in {"Davis Cup", "Billie Jean King Cup"}),
        None,
    )
    if not davis_data:
        return {"convocado": False, "mensagem": "Não há Copa Davis esta semana."}

    ranking_path = get_caminho_ranking_save(nome_save, genero=jogador.genero)
    ranking = SistemaRanking(ranking_path)

    from src.davis_cup import DavisCup

    davis = DavisCup(davis_data, jogador, ranking, nome_save)
    convocado, posicao, msg = davis.verificar_convocacao()

    return {
        "convocado": convocado,
        "posicao": posicao,
        "mensagem": msg,
        "torneio": davis_data,
    }


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
    jogador = session.jogador
    historico = getattr(jogador, "historico_torneios", [])
    entradas = [h for h in historico if h.get("nome") == nome]
    if not entradas:
        return {"pontos_a_defender": 0, "ultima_colocacao": None}
    entradas.sort(key=lambda h: (h.get("ano", 0), h.get("semana", 0)), reverse=True)
    ultima = entradas[0]
    return {
        "pontos_a_defender": ultima.get("pontos", 0),
        "ultima_colocacao": ultima.get("fase"),
    }


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
    tour = "atp" if jogador.genero == "masculino" else "wta"

    from src.services.tournament_service import withdraw_from_tournament, simulate_tournament_remainder
    withdraw_from_tournament(nome_save)
    simulate_tournament_remainder(nome_save)

    from src.pontuacao import distribuir_pontos_torneio
    distribuir_pontos_torneio(nome_save, genero=jogador.genero)

    from src.calendario import avancar_semana
    resultado = avancar_semana(nome_save, expected_week=session.semana_atual)

    from api.session import refresh_session
    refresh_session(nome_save)

    # G-2: Limpeza de torneio_atp.json após finalizar
    import os
    import json
    from src.dados import get_caminho_torneio_save
    caminho_torneio = get_caminho_torneio_save(nome_save, genero=jogador.genero)
    if os.path.exists(caminho_torneio):
        with open(caminho_torneio) as f:
            estado = json.load(f)
        if estado.get("fase_atual") == "finalizado":
            os.remove(caminho_torneio)

    return {"ok": True, **resultado}
