from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.logging_utils import log_exception
from api.routes._match_runtime import obter_match_runtime
from api.session import Session, obter_sessao_ativa
from src.services.match_service import (
    completar_adversario,
    dupla_contem_jogador,
    get_active_match,
    preview_match,
    resolver_adversario_partida,
    start_match,
)

router = APIRouter(prefix="/api/partida", tags=["partida"])

_dupla_contem_jogador = dupla_contem_jogador
_resolver_adversario_partida = resolver_adversario_partida
_completar_adversario = completar_adversario


class IniciarPartidaBody(BaseModel):
    modo: str


class PontoBody(BaseModel):
    partida_id: str


class EstrategiaBody(BaseModel):
    partida_id: str
    estrategia: str


class SimulacaoBody(BaseModel):
    partida_id: str


class AjusteTaticoBody(BaseModel):
    partida_id: str
    estrategia: str
    set_numero: int = 0


class ScoutH2H(BaseModel):
    vitorias_jogador: int
    vitorias_adversario: int


class ScoutResponse(BaseModel):
    nome: str
    ranking: int
    overall: int
    atributos: dict[str, int]
    atributos_psicologicos: dict[str, int]
    superficie_favorita: str
    forma_recente: list[str]
    h2h: ScoutH2H
    nacionalidade: str


@router.get("/ativa")
def obter_ativa(session: Session = Depends(obter_sessao_ativa)) -> dict | None:
    return get_active_match(session.nome_save_ativo)


@router.get("/preview")
def preview(session: Session = Depends(obter_sessao_ativa)) -> dict:
    return preview_match(session.nome_save_ativo, session.jogador)


@router.get("/scout/{nome_adversario}", response_model=ScoutResponse)
def scout(
    nome_adversario: str, session: Session = Depends(obter_sessao_ativa)
) -> ScoutResponse:
    """Retorna dados de scouting do adversário: atributos, H2H, forma recente."""
    from src.match_history import MatchHistoryManager
    from src.nome_utils import normalizar_nome
    from src.services.player_context_service import carregar_torneio_api

    nome_save = session.nome_save_ativo
    jogador = session.jogador

    # Dados do adversário via estado do torneio ativo
    adversario: dict = {}
    instancia = carregar_torneio_api(nome_save)
    if instancia:
        try:
            state = instancia.to_api_state()
            info = state.get("info_partida") or {}
            adv_raw = info.get("adversario") or {}
            nome_norm = normalizar_nome(adv_raw.get("nome", nome_adversario))
            if normalizar_nome(adv_raw.get("nome", "")) == nome_norm:
                adversario = adv_raw
        except Exception:
            pass

    # Fallback: buscar no ranking
    if not adversario:
        ranking = (
            session.ranking_atp
            if jogador.genero == "masculino"
            else session.ranking_wta
        )
        if ranking:
            nome_norm = normalizar_nome(nome_adversario)
            for entrada in ranking.ranking[:500]:
                if normalizar_nome(entrada.get("nome", "")) == nome_norm:
                    adversario = entrada
                    break

    # H2H via match history
    h2h = {"vitorias_jogador": 0, "vitorias_adversario": 0}
    forma_recente: list[str] = []
    try:
        mhm = MatchHistoryManager(nome_save)
        nome_jog_norm = normalizar_nome(jogador.nome)
        nome_adv_norm = normalizar_nome(nome_adversario)
        historico_adv = mhm.buscar_por_jogador(nome_adversario)
        # Forma recente do adversário (últimas 5 partidas)
        for partida in sorted(
            historico_adv, key=lambda p: p.get("semana", 0), reverse=True
        )[:5]:
            jogadores = [normalizar_nome(j) for j in partida.get("jogadores", [])]
            vencedor = normalizar_nome(partida.get("vencedor", ""))
            forma_recente.append("V" if vencedor == nome_adv_norm else "D")
        # H2H com jogador humano
        for partida in historico_adv:
            jogadores = [normalizar_nome(j) for j in partida.get("jogadores", [])]
            if nome_jog_norm not in jogadores:
                continue
            vencedor = normalizar_nome(partida.get("vencedor", ""))
            if vencedor == nome_jog_norm:
                h2h["vitorias_jogador"] += 1
            elif vencedor == nome_adv_norm:
                h2h["vitorias_adversario"] += 1
    except Exception:
        pass

    # Superfície favorita a partir dos atributos
    atributos = adversario.get("atributos") or {}
    superficie_favorita = "Hard"
    if atributos:
        clay_score = atributos.get("topspin", 0) + atributos.get("slice", 0)
        grass_score = atributos.get("saque", 0) + atributos.get("voleio", 0)
        hard_score = atributos.get("forehand", 0) + atributos.get("backhand", 0)
        melhor = max(clay_score, grass_score, hard_score)
        if melhor == clay_score:
            superficie_favorita = "Clay"
        elif melhor == grass_score:
            superficie_favorita = "Grass"

    return ScoutResponse(
        nome=adversario.get("nome", nome_adversario),
        ranking=adversario.get("ranking_pos") or adversario.get("ranking", 0),
        overall=adversario.get("overall", 0),
        atributos=atributos,
        atributos_psicologicos=adversario.get("atributos_psicologicos") or {},
        superficie_favorita=superficie_favorita,
        forma_recente=forma_recente,
        h2h=ScoutH2H(**h2h),
        nacionalidade=adversario.get("nacionalidade", ""),
    )


@router.post("/iniciar")
def iniciar(
    body: IniciarPartidaBody, session: Session = Depends(obter_sessao_ativa)
) -> dict:
    return start_match(body.modo, session.nome_save_ativo, session.jogador)


@router.post("/desistir")
def desistir_partida(
    body: PontoBody, session: Session = Depends(obter_sessao_ativa)
) -> dict:
    runtime = obter_match_runtime(body.partida_id, session.nome_save_ativo)
    if runtime.encerrado:
        return {"ok": True}

    runtime.encerrado = True
    runtime.vencedor = "adversario"
    runtime.log.append("Jogador desistiu da partida (W.O.).")
    runtime._finalizar_torneio()
    return {"ok": True}


@router.post("/ponto")
def ponto(body: PontoBody, session: Session = Depends(obter_sessao_ativa)) -> dict:
    try:
        runtime = obter_match_runtime(body.partida_id, session.nome_save_ativo)
        return runtime.jogar_ponto()
    except HTTPException:
        raise
    except Exception as exc:
        log_exception(
            "erro_ao_jogar_ponto",
            exc,
            partida_id=body.partida_id,
            causa_provavel="Runtime de partida pode ter sido perdido após restart do servidor.",
        )
        raise HTTPException(status_code=500, detail="Erro ao processar ponto.") from exc


@router.post("/estrategia")
def estrategia(
    body: EstrategiaBody, session: Session = Depends(obter_sessao_ativa)
) -> dict:
    runtime = obter_match_runtime(body.partida_id, session.nome_save_ativo)

    texto = str(body.estrategia or "")
    if "|" in texto:
        partes = texto.split("|")
        if texto.startswith("fm|") and len(partes) >= 5:
            _, mentalidade, abordagem, instrucao, _segundo_saque = partes[:5]
            runtime.contexto_partida.mentalidade = mentalidade
            runtime.contexto_partida.abordagem = abordagem
            runtime.contexto_partida.instrucao_especifica = instrucao
            runtime.aplicar_estrategia(texto)
            runtime._persistir()
            return {"ok": True, "tipo": "fm_tactics"}
        if len(partes) == 3:
            mentalidade, abordagem, instrucao = partes
            runtime.contexto_partida.mentalidade = mentalidade
            runtime.contexto_partida.abordagem = abordagem
            runtime.contexto_partida.instrucao_especifica = instrucao
            runtime.aplicar_estrategia(texto)
            runtime._persistir()
            return {"ok": True, "tipo": "fm_tactics"}

    runtime.aplicar_estrategia(body.estrategia)
    runtime._persistir()
    return {"ok": True}


@router.post("/ajuste-tatico")
def ajuste_tatico(
    body: AjusteTaticoBody, session: Session = Depends(obter_sessao_ativa)
) -> dict:
    """Aplica ajuste tático entre sets. Aceita estilos como 'agressivo', 'seguro' ou 'manter'
    que fornecem bônus temporários em atributos psicológicos."""
    runtime = obter_match_runtime(body.partida_id, session.nome_save_ativo)

    texto = str(body.estrategia or "").lower()
    
    # Suporte a ajustes simples (X-5)
    if texto in {"agressivo", "seguro", "manter"}:
        runtime.aplicar_ajuste_tatico(texto)
        return {"ok": True, "set_ajustado": body.set_numero, "ajuste": texto}

    # Fallback para pacotes complexos (FM-style)
    if "|" in texto:
        partes = texto.split("|")
        if texto.startswith("fm|") and len(partes) >= 5:
            _, mentalidade, abordagem, instrucao, _segundo_saque = partes[:5]
            runtime.contexto_partida.mentalidade = mentalidade
            runtime.contexto_partida.abordagem = abordagem
            runtime.contexto_partida.instrucao_especifica = instrucao
            runtime.aplicar_estrategia(texto)
            runtime._persistir()
            return {"ok": True, "set_ajustado": body.set_numero, "tipo": "fm_tactics"}
        if len(partes) == 3:
            mentalidade, abordagem, instrucao = partes
            runtime.contexto_partida.mentalidade = mentalidade
            runtime.contexto_partida.abordagem = abordagem
            runtime.contexto_partida.instrucao_especifica = instrucao
            runtime.aplicar_estrategia(texto)
            runtime._persistir()
            return {"ok": True, "set_ajustado": body.set_numero, "tipo": "fm_tactics"}

    runtime.aplicar_estrategia(body.estrategia)
    runtime._persistir()
    return {"ok": True, "set_ajustado": body.set_numero}


@router.post("/simular-set")
def simular_set(
    body: SimulacaoBody, session: Session = Depends(obter_sessao_ativa)
) -> dict:
    try:
        runtime = obter_match_runtime(body.partida_id, session.nome_save_ativo)
        return runtime.simular_set()
    except HTTPException:
        raise
    except Exception as exc:
        log_exception("erro_simular_set", exc, partida_id=body.partida_id)
        raise HTTPException(status_code=500, detail="Erro ao simular set.") from exc


@router.post("/simular-partida")
def simular_partida(
    body: SimulacaoBody, session: Session = Depends(obter_sessao_ativa)
) -> dict:
    try:
        runtime = obter_match_runtime(body.partida_id, session.nome_save_ativo)
        return runtime.simular_partida()
    except HTTPException:
        raise
    except Exception as exc:
        log_exception("erro_simular_partida", exc, partida_id=body.partida_id)
        raise HTTPException(status_code=500, detail="Erro ao simular partida.") from exc


@router.get("/{partida_id}/stats")
def get_partida_stats(
    partida_id: str, session: Session = Depends(obter_sessao_ativa)
) -> dict:
    """Retorna estatísticas detalhadas da partida."""
    runtime = obter_match_runtime(partida_id, session.nome_save_ativo)
    return {
        "encerrado": runtime.encerrado,
        "vencedor": runtime.vencedor,
        "placar": {
            "sets": runtime.sets,
            "games": runtime.games,
            "set_scores": runtime.set_scores
        },
        "stats_jogador": runtime._serializar_stats_lado(runtime.stats_j),
        "stats_adversario": runtime._serializar_stats_lado(runtime.stats_a),
        "total_pontos": runtime.total_pontos
    }


@router.get("/{partida_id}/log")
def get_partida_log(
    partida_id: str, session: Session = Depends(obter_sessao_ativa)
) -> dict:
    """Retorna o log completo da partida."""
    runtime = obter_match_runtime(partida_id, session.nome_save_ativo)
    return {"log": runtime.log}
