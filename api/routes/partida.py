from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.logging_utils import log_exception
from api.routes._match_runtime import obter_match_runtime
from api.routes._match_store import delete_snapshot
from api.session import Session, obter_sessao_ativa, refresh_session
from src.services.match_service import (
    get_active_match,
    preview_match,
    start_match,
)
from src.services.scouting_service import montar_relatorio_scouting

router = APIRouter(prefix="/api/partida", tags=["partida"])


def _aplicar_fm_tactics(
    runtime, texto: str, extra_fields: dict | None = None
) -> dict | None:
    """Parseia táticas FM-style (pipe-delimited) e aplica ao runtime. Retorna None se não reconhecido."""
    if "|" not in texto:
        return None
    partes = texto.split("|")
    if texto.startswith("fm|") and len(partes) >= 5:
        _, mentalidade, abordagem, instrucao, segundo_saque = partes[:5]
    elif len(partes) == 3:
        mentalidade, abordagem, instrucao = partes
        segundo_saque = None
    else:
        return None
    runtime.contexto_partida.mentalidade = mentalidade
    runtime.contexto_partida.abordagem = abordagem
    runtime.contexto_partida.instrucao_especifica = instrucao
    if segundo_saque is not None:
        runtime.contexto_partida.segundo_saque = segundo_saque
    runtime.aplicar_estrategia(texto)
    runtime._persistir()
    return {"ok": True, "tipo": "fm_tactics", **(extra_fields or {})}


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
    metricas: dict[str, int]
    texto: str
    dicas: list[str]
    pontos_fortes: list[str]
    fraquezas: list[str]
    is_rival: bool = False


class PartidaConfigResponse(BaseModel):
    modo: str
    superficie: str
    melhor_de: int
    nome_torneio: str | None = None
    tipo_torneio: str | None = None
    tiebreak_decisivo_pontos: int | None = None


class AdversarioPayload(BaseModel):
    nome: str
    nacionalidade: str | None = None
    idade: int | None = None
    altura: int | None = None
    peso: int | None = None
    mao_dominante: str | None = None
    reves: str | None = None
    estilo_jogo: str | None = None
    overall: int | None = None
    ranking: int | None = None
    ranking_pos: int | None = None
    energia: int | None = None
    fadiga: int | None = None
    pontos: int | None = None
    pontos_ytd: int | None = None
    pico_carreira: int | None = None
    atributos: dict[str, int] | None = None
    atributos_psicologicos: dict[str, int] | None = None
    trofeus: list[dict] | None = None
    historico_torneios: list[dict] | None = None
    historico_partidas: list[dict] | None = None
    resumo_fifa: dict[str, int] | None = None


class PartidaPreviewResponse(BaseModel):
    adversario: AdversarioPayload


class PartidaAtivaResponse(BaseModel):
    partida_id: str
    config: PartidaConfigResponse
    adversario: AdversarioPayload
    placar: dict


class PartidaIniciarResponse(BaseModel):
    partida_id: str
    config: PartidaConfigResponse
    adversario: AdversarioPayload | None = None
    placar: dict | None = None


class MatchStatsResponse(BaseModel):
    aces: int
    duplas_faltas: int
    primeiro_saque_pct: str
    winners: int
    erros_nao_forcados: int
    pontos_saque_pct: str
    pontos_devolucao_pct: str
    break_points: str
    rallies_curtos: int
    rallies_medios: int
    rallies_longos: int


class MatchStrategyResponse(BaseModel):
    estilo: str | None = None
    saque: str | None = None
    saque_tipo: str | None = None
    intencao: str | None = None
    mentalidade: str | None = None
    abordagem: str | None = None
    instrucao: str | None = None


class MatchRuntimeResponse(BaseModel):
    tipo: str
    descricao: str
    descricao_json: dict
    sets: list[int]
    games: list[int]
    pontos: list[str]
    servindo: str
    log: list[str]
    encerrado: bool
    vencedor: str | None = None
    placar_final: str | None = None
    stats_j: MatchStatsResponse
    stats_a: MatchStatsResponse
    last_point_stats: dict
    energia_j: int
    energia_a: int
    fadiga_j: int
    fadiga_a: int
    estrategia_j: MatchStrategyResponse
    estrategia_a: MatchStrategyResponse
    ajuste_tatico_j: str
    ajuste_tatico_a: str
    quimica_j: dict | None = None
    quimica_a: dict | None = None
    comentario_parceiro: str | None = None


@router.get("/ativa")
def obter_ativa(
    session: Session = Depends(obter_sessao_ativa),
) -> PartidaAtivaResponse | None:
    return get_active_match(session.nome_save_ativo)


@router.get("/preview")
def preview(session: Session = Depends(obter_sessao_ativa)) -> PartidaPreviewResponse:
    return preview_match(session.nome_save_ativo, session.jogador)


@router.get("/scout/{nome_adversario}", response_model=ScoutResponse)
def scout(
    nome_adversario: str, session: Session = Depends(obter_sessao_ativa)
) -> ScoutResponse:
    """Retorna dados de scouting do adversário: atributos, H2H, forma recente."""
    from src.match_history import MatchHistoryManager
    from src.utils.nome_utils import normalizar_nome
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

    atributos = adversario.get("atributos") or {}
    superficie = getattr(instancia, "superficie", "") if instancia else ""
    if not superficie and instancia:
        tournament_data = getattr(instancia, "tournament_data", {}) or {}
        if isinstance(tournament_data, dict):
            superficie = tournament_data.get("superficie") or tournament_data.get(
                "quadra", ""
            )
    relatorio = montar_relatorio_scouting(adversario, superficie)

    from src.jogador import rival_ativo as _rival_ativo

    return ScoutResponse(
        nome=adversario.get("nome", nome_adversario),
        ranking=adversario.get("ranking_pos") or adversario.get("ranking", 0),
        overall=adversario.get("overall", 0),
        atributos=atributos,
        atributos_psicologicos=adversario.get("atributos_psicologicos") or {},
        superficie_favorita=relatorio["superficie_favorita"],
        forma_recente=forma_recente,
        h2h=ScoutH2H(**h2h),
        nacionalidade=adversario.get("nacionalidade", ""),
        metricas=relatorio["metricas"],
        texto=relatorio["texto"],
        dicas=relatorio["dicas"],
        pontos_fortes=relatorio["pontos_fortes"],
        fraquezas=relatorio["fraquezas"],
        is_rival=_rival_ativo(jogador, nome_adversario),
    )


@router.post("/iniciar", response_model=PartidaIniciarResponse)
def iniciar(
    body: IniciarPartidaBody, session: Session = Depends(obter_sessao_ativa)
) -> PartidaIniciarResponse:
    return start_match(body.modo, session.nome_save_ativo, session.jogador)


@router.post("/desistir")
def desistir_partida(
    body: PontoBody, session: Session = Depends(obter_sessao_ativa)
) -> dict:
    runtime = obter_match_runtime(body.partida_id, session.nome_save_ativo)
    if getattr(runtime, "encerrado", False):
        delete_snapshot(session.nome_save_ativo, body.partida_id)
        return {"ok": True}

    runtime.encerrado = True
    runtime.vencedor = "adversario"
    runtime.log.append("Jogador desistiu da partida (W.O.).")
    runtime._finalizar_torneio()
    refresh_session(session.nome_save_ativo)
    delete_snapshot(session.nome_save_ativo, body.partida_id)
    return {"ok": True}


@router.post("/ponto", response_model=MatchRuntimeResponse)
def ponto(
    body: PontoBody, session: Session = Depends(obter_sessao_ativa)
) -> MatchRuntimeResponse:
    try:
        runtime = obter_match_runtime(body.partida_id, session.nome_save_ativo)
        res = runtime.jogar_ponto()
        if getattr(runtime, "encerrado", False):
            refresh_session(session.nome_save_ativo)
            delete_snapshot(session.nome_save_ativo, body.partida_id)
        return res
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
    fm = _aplicar_fm_tactics(runtime, texto)
    if fm is not None:
        return fm

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
    extra = {"set_ajustado": body.set_numero}

    if texto in {"agressivo", "seguro", "manter"}:
        runtime.aplicar_ajuste_tatico(texto)
        return {"ok": True, "ajuste": texto, **extra}

    fm = _aplicar_fm_tactics(runtime, texto, extra_fields=extra)
    if fm is not None:
        return fm

    runtime.aplicar_estrategia(body.estrategia)
    runtime._persistir()
    return {"ok": True, **extra}


@router.post("/simular-set", response_model=MatchRuntimeResponse)
def simular_set(
    body: SimulacaoBody, session: Session = Depends(obter_sessao_ativa)
) -> MatchRuntimeResponse:
    try:
        runtime = obter_match_runtime(body.partida_id, session.nome_save_ativo)
        res = runtime.simular_set()
        if getattr(runtime, "encerrado", False):
            refresh_session(session.nome_save_ativo)
            delete_snapshot(session.nome_save_ativo, body.partida_id)
        return res
    except HTTPException:
        raise
    except Exception as exc:
        log_exception("erro_simular_set", exc, partida_id=body.partida_id)
        raise HTTPException(status_code=500, detail="Erro ao simular set.") from exc


@router.post("/simular-partida", response_model=MatchRuntimeResponse)
def simular_partida(
    body: SimulacaoBody, session: Session = Depends(obter_sessao_ativa)
) -> MatchRuntimeResponse:
    try:
        runtime = obter_match_runtime(body.partida_id, session.nome_save_ativo)
        res = runtime.simular_partida()
        refresh_session(session.nome_save_ativo)
        delete_snapshot(session.nome_save_ativo, body.partida_id)
        return res
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
            "set_scores": runtime.set_scores,
        },
        "stats_jogador": runtime._serializar_stats_lado(runtime.stats_j),
        "stats_adversario": runtime._serializar_stats_lado(runtime.stats_a),
        "total_pontos": runtime.total_pontos,
    }


@router.get("/{partida_id}/log")
def get_partida_log(
    partida_id: str, session: Session = Depends(obter_sessao_ativa)
) -> dict:
    """Retorna o log completo da partida."""
    runtime = obter_match_runtime(partida_id, session.nome_save_ativo)
    return {"log": runtime.log}
