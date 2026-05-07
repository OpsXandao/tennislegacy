from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from api.logging_utils import log_event, log_exception
from api.session import Session, obter_sessao_ativa, refresh_session
from src.presenters.tournament_presenter import formatar_torneio_resumido
from src.services.player_context_service import carregar_temporada_atual, tour_para_genero
from src.calendario import avancar_semana, obter_torneios_da_semana
from src.pontuacao import distribuir_pontos_torneio

router = APIRouter(prefix="/api/calendario", tags=["calendario"])

@router.get("/semana/{numero}")
def obter_semana(
    numero: int,
    tour: str | None = Query(default=None),
    session: Session = Depends(obter_sessao_ativa),
) -> dict:
    jogador = session.jogador
    genero = tour_para_genero(tour, jogador.genero)
    torneios = obter_torneios_da_semana(numero, genero=genero)
    return {
        "semana": numero,
        "tour": "atp" if genero == "masculino" else "wta",
        "torneios": [formatar_torneio_resumido(t) for t in torneios],
    }


@router.get("/atual")
def obter_atual(
    tour: str | None = Query(default=None),
    session: Session = Depends(obter_sessao_ativa),
) -> dict:
    nome_save = session.nome_save_ativo
    jogador = session.jogador
    temporada = carregar_temporada_atual(nome_save)
    genero = tour_para_genero(tour, jogador.genero)
    torneios = obter_torneios_da_semana(temporada["semana"], genero=genero)
    return {
        "semana": temporada["semana"],
        "ano": temporada["ano"],
        "tour": "atp" if genero == "masculino" else "wta",
        "torneios": [formatar_torneio_resumido(t) for t in torneios],
    }


@router.post("/avancar")
def avancar(session: Session = Depends(obter_sessao_ativa)) -> dict:
    nome_save = session.nome_save_ativo
    jogador = session.jogador
    try:
        try:
            distribuir_pontos_torneio(nome_save, genero=jogador.genero)
        except Exception:
            pass
        resultado = avancar_semana(nome_save, expected_week=session.semana_atual)
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
