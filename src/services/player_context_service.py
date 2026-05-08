from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import HTTPException

from api.logging_utils import log_event
from api.session import Session
from src.constants.torneio_constants import START_YEAR
from src.calendario import carregar_temporada
from src.dados import carregar_estado_torneio
from src.jogador import carregar_jogador, normalizar_nome
from src.repositories.tournament_repository import load_regular_tournament

if TYPE_CHECKING:
    from src.jogador import Jogador


def resolver_save_ativo(session: Session) -> str:
    nome_save = getattr(session, "nome_save_ativo", None)
    if nome_save:
        return nome_save
    log_event(
        logging.WARNING,
        "sessao_nao_iniciada",
        motivo="Nenhum save ativo na sessao.",
    )
    raise HTTPException(status_code=400, detail="Sessao nao iniciada.")


def carregar_contexto_jogador(session: Session) -> tuple[str, Jogador]:
    nome_save = resolver_save_ativo(session)
    jogador = session.jogador
    if jogador is None:
        log_event(
            logging.WARNING,
            "contexto_jogador_indisponivel",
            nome_save=nome_save,
            jogador_carregado=False,
            motivo="jogador=None com save ativo.",
        )
        raise HTTPException(status_code=400, detail="Sessao nao iniciada.")
    return nome_save, jogador


def tour_para_genero(tour: str | None, genero_padrao: str) -> str:
    if tour is None:
        return genero_padrao
    tour_n = str(tour).strip().lower()
    if tour_n == "wta":
        return "feminino"
    return "masculino"


def genero_para_tour(genero: str) -> str:
    return "wta" if genero == "feminino" else "atp"


def _genero_oposto(genero: str) -> str:
    return "feminino" if genero == "masculino" else "masculino"


def _carregar_davis_do_jogador(nome_save: str, jogador):
    from src.davis_cup import carregar_davis_cup

    return carregar_davis_cup(nome_save, jogador)


def _criar_jogador_genero_alternativo(jogador, nome_save: str):
    from src.jogador import Jogador

    return Jogador(
        jogador.nome,
        jogador.idade,
        jogador.nacionalidade,
        nome_save,
        genero=_genero_oposto(jogador.genero),
    )


def _carregar_davis_genero_alternativo(nome_save: str, jogador):
    try:
        jogador_outro = _criar_jogador_genero_alternativo(jogador, nome_save)
        return _carregar_davis_do_jogador(nome_save, jogador_outro)
    except Exception as exc:
        log_event(
            logging.WARNING,
            "davis_cross_gender_load_failed",
            save_ativo=nome_save,
            genero_tentado=_genero_oposto(jogador.genero),
            reason=str(exc),
            error_type=type(exc).__name__,
        )
        return None


def carregar_torneio_api(nome_save: str):
    instancia = load_regular_tournament(nome_save)
    if instancia:
        return instancia

    jogador = carregar_jogador(nome_save)
    if not jogador:
        return None

    davis = _carregar_davis_do_jogador(nome_save, jogador)
    if davis:
        return davis

    return _carregar_davis_genero_alternativo(nome_save, jogador)


def obter_estado_torneio(nome_save: str, genero: str | None = None) -> dict | None:
    if genero:
        return carregar_estado_torneio(nome_save, genero=genero)

    for genero_tentativa in ("masculino", "feminino"):
        estado = carregar_estado_torneio(nome_save, genero=genero_tentativa)
        if estado:
            return estado
    return None


def encontrar_confronto_jogador(estado: dict, nome_jogador: str) -> dict | None:
    fase = estado.get("fase_atual")
    if not fase:
        return None

    for indice, confronto in enumerate(
        estado.get("rodadas", {}).get(fase, []), start=1
    ):
        if not isinstance(confronto, (list, tuple)) or len(confronto) != 2:
            continue
        a, b = confronto
        nome_a = a.get("nome", str(a)) if isinstance(a, dict) else str(a)
        nome_b = b.get("nome", str(b)) if isinstance(b, dict) else str(b)
        if normalizar_nome(nome_a) == normalizar_nome(nome_jogador):
            return {
                "indice": indice,
                "fase": fase,
                "jogador": a,
                "adversario": b,
            }
        if normalizar_nome(nome_b) == normalizar_nome(nome_jogador):
            return {
                "indice": indice,
                "fase": fase,
                "jogador": b,
                "adversario": a,
            }
    return None


def resumir_proxima_partida(instancia, nome_jogador: str) -> dict | None:
    estado = instancia._carregar_estado()
    confronto = encontrar_confronto_jogador(estado, nome_jogador)
    if not confronto:
        return None

    adversario = confronto["adversario"]
    adversario_nome = (
        adversario.get("nome", "Adversario")
        if isinstance(adversario, dict)
        else str(adversario)
    )
    return {
        "fase": confronto["fase"],
        "indice": confronto["indice"],
        "adversario": adversario_nome,
        "torneio": estado.get("torneio"),
    }


def carregar_temporada_atual(nome_save: str) -> dict[str, int]:
    temporada = carregar_temporada(nome_save)
    return {
        "semana": int(temporada.get("semana", 1)),
        "ano": int(temporada.get("ano", START_YEAR)),
    }
