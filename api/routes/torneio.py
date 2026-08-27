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
from src.services.world_clock_service import avancar_ate_proximo_momento, obter_agenda_torneio

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


@router.post("/inscrever")
def inscrever(semana: int, nome: str, session: Session = Depends(obter_sessao_ativa)):
    if semana <= session.semana_atual + 2:
        raise HTTPException(status_code=400, detail="Inscrições fecham com 3 semanas de antecedência.")
    session.jogador.inscrever_torneio(semana, nome)
    from src.save import salvar_jogo
    salvar_jogo(session.nome_save_ativo, session.jogador)
    return {"ok": True, "mensagem": f"Inscrição confirmada para {nome} na semana {semana}."}


@router.post("/criar")
def criar(
    body: CriarTorneioBody, session: Session = Depends(obter_sessao_ativa)
) -> dict:
    jogador = session.jogador
    # Validação de Entry List (Realismo de Calendário)
    inscrito = jogador.obter_inscricao_semana(session.semana_atual)
    custo_wc = 0
    
    if inscrito != body.torneio_nome:
        # Taxa de wildcard escalonada por tier do torneio
        _WC_TAXA = {
            "ITF 25": 300,
            "ITF 100": 500,
            "Challenger 125": 500,
            "ATP 250": 800,
            "WTA 250": 800,
            "ATP 500": 1500,
            "WTA 500": 1500,
            "ATP 1000": 2500,
            "WTA 1000": 2500,
            "Grand Slam": 4000,
        }
        # Busca o tipo do torneio no calendário pelo nome
        tipo_torneio = ""
        try:
            from src.dados import carregar_calendario
            genero = "masculino" if jogador.genero == "masculino" else "feminino"
            cal = carregar_calendario(genero)
            nome_alvo = (body.torneio_nome or "").lower()
            for semana_info in (cal if isinstance(cal, list) else cal.values()):
                torneios = semana_info if isinstance(semana_info, list) else [semana_info]
                for t in torneios:
                    if isinstance(t, dict) and t.get("nome", "").lower() == nome_alvo:
                        tipo_torneio = t.get("tipo", "")
                        break
                if tipo_torneio:
                    break
        except Exception:
            pass

        custo_wc = _WC_TAXA.get(tipo_torneio, 1000)
        if jogador.dinheiro < custo_wc:
            raise HTTPException(
                status_code=400,
                detail=f"Você não se inscreveu. Wildcard: ${custo_wc:,} ({tipo_torneio or 'torneio'}). Saldo insuficiente.",
            )
        jogador.registrar_transacao(
            -custo_wc, f"Wildcard: {body.torneio_nome}", categoria="torneio"
        )

    jogador.desinscrever_torneio(session.semana_atual)

    res = create_tournament(
        nome_save=session.nome_save_ativo,
        jogador=session.jogador,
        modalidade=body.modalidade,
        parceiro=body.parceiro,
        torneio_nome=body.torneio_nome,
    )
    return {**res, "wc_pago": custo_wc > 0}


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


@router.get("/agenda")
def get_agenda(session: Session = Depends(obter_sessao_ativa)) -> dict:
    return obter_agenda_torneio(session.nome_save_ativo, genero=session.jogador.genero)


@router.post("/avancar-proximo-momento")
def avancar_proximo_momento(session: Session = Depends(obter_sessao_ativa)) -> dict:
    return avancar_ate_proximo_momento(session.nome_save_ativo)


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
