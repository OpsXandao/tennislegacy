from __future__ import annotations

import logging
from typing import Any

from fastapi import HTTPException

from api.logging_utils import extract_exception_details, log_event
from src.services.player_context_service import (
    carregar_torneio_api,
    carregar_temporada_atual,
    resumir_proxima_partida,
)
from src.calendario import avancar_semana, obter_torneios_da_semana
from src.jogador import normalizar_nome
from src.pontuacao import distribuir_pontos_torneio
from src.repositories.player_repository import save_player
from src.repositories.ranking_repository import load_singles_ranking
from src.repositories.tournament_repository import load_tournament_state
from src.davis_cup import criar_torneio_davis
from src.torneio_constants import RANKING_LIMITE_CHALLENGER, RANKING_LIMITE_ITF
from src.torneio import avancar_fase, criar_torneio


def _torneio_disponivel_por_ranking(
    torneio: dict[str, Any], ranking_pos: int | None
) -> bool:
    if ranking_pos is None:
        return True

    tipo = str(torneio.get("tipo", "") or "")
    if tipo == "Challenger 125":
        return ranking_pos > RANKING_LIMITE_CHALLENGER
    if tipo in {"ITF 100", "ITF 25"}:
        return ranking_pos > RANKING_LIMITE_ITF
    return True


def _filtrar_torneios_elegiveis(
    torneios: list[dict[str, Any]], ranking_pos: int | None
) -> list[dict[str, Any]]:
    return [
        torneio
        for torneio in torneios
        if _torneio_disponivel_por_ranking(torneio, ranking_pos)
    ]


def _escolher_torneio(
    torneios: list[dict[str, Any]], nome: str | None
) -> dict[str, Any]:
    if nome:
        for torneio in torneios:
            if torneio.get("nome") == nome:
                return torneio
        raise HTTPException(
            status_code=404, detail="Torneio solicitado nao encontrado."
        )

    if len(torneios) == 1:
        return torneios[0]

    def prioridade(item: dict[str, Any]) -> tuple[int, int]:
        tipo = str(item.get("tipo", ""))
        if tipo == "Grand Slam":
            peso = 0
        elif "1000" in tipo:
            peso = 1
        elif "500" in tipo:
            peso = 2
        elif "250" in tipo:
            peso = 3
        elif "Challenger" in tipo:
            peso = 4
        elif "ITF" in tipo:
            peso = 5
        else:
            peso = 6
        return (peso, -int(item.get("popularidade", 0) or 0))

    torneios_validos = [
        torneio
        for torneio in torneios
        if torneio.get("tipo")
        not in {"Davis Cup", "Billie Jean King Cup", "United Cup"}
    ]
    if not torneios_validos:
        davis = [
            t
            for t in torneios
            if t.get("tipo") in {"Davis Cup", "Billie Jean King Cup"}
        ]
        if davis:
            return davis[0]
        raise HTTPException(
            status_code=409,
            detail="Nao ha torneio individual disponivel para inscricao.",
        )
    return sorted(torneios_validos, key=prioridade)[0]


def _resolver_parceiro(
    nome_save: str, jogador: Any, parceiro: str | None, tipo_duplas: str
) -> dict[str, Any] | None:
    if not parceiro:
        return None

    genero_parceiro = jogador.genero
    if tipo_duplas == "mista":
        genero_parceiro = "feminino" if jogador.genero == "masculino" else "masculino"

    ranking = load_singles_ranking(nome_save, genero=genero_parceiro)
    parceiro_norm = normalizar_nome(parceiro)
    for entrada in ranking.ranking:
        if normalizar_nome(entrada.get("nome", "")) == parceiro_norm:
            return entrada

    return {"nome": parceiro, "nacionalidade": "??"}


def create_tournament(
    nome_save: str,
    jogador: Any,
    modalidade: str,
    parceiro: str | None = None,
    torneio_nome: str | None = None,
) -> dict:
    temporada = carregar_temporada_atual(nome_save)
    semana_atual = temporada["semana"]

    instancia_ativa = carregar_torneio_api(nome_save)
    if instancia_ativa and hasattr(instancia_ativa, "_carregar_estado"):
        estado_ativo = instancia_ativa._carregar_estado()
        semana_estado = estado_ativo.get("semana", 0) if estado_ativo else 0
        try:
            semana_estado = int(semana_estado)
        except (TypeError, ValueError):
            semana_estado = 0

        if (
            estado_ativo
            and semana_estado == semana_atual
            and estado_ativo.get("fase_atual") != "finalizado"
        ):
            state = instancia_ativa.to_api_state()
            tipo = str(state.get("tipo", "") or "")
            state["destino_click_hub"] = (
                "/davis"
                if tipo in {"Davis Cup", "Billie Jean King Cup"} or state.get("davis")
                else "/tournament"
            )
            return {"ok": True, "torneio": state}

    estado_atual = load_tournament_state(nome_save, genero=jogador.genero)
    semana_estado = estado_atual.get("semana", 0) if estado_atual else 0
    try:
        semana_estado = int(semana_estado)
    except (TypeError, ValueError):
        semana_estado = 0
    if (
        estado_atual
        and semana_estado == semana_atual
        and estado_atual.get("fase_atual") != "finalizado"
    ):
        tipo = estado_atual.get("tipo", "")
        estado_atual["destino_click_hub"] = (
            "/davis" if tipo in {"Davis Cup", "Billie Jean King Cup"} else "/tournament"
        )
        return {"ok": True, "torneio": estado_atual}

    torneios = obter_torneios_da_semana(semana_atual, genero=jogador.genero)
    ranking = load_singles_ranking(nome_save, genero=jogador.genero)
    ranking_pos = (
        ranking.obter_posicao(jogador.nome)
        if ranking and hasattr(ranking, "obter_posicao")
        else None
    )
    torneios = _filtrar_torneios_elegiveis(torneios, ranking_pos)
    if not torneios:
        raise HTTPException(
            status_code=409,
            detail="Nao ha torneio elegivel disponivel para o ranking atual.",
        )
    torneio_escolhido = _escolher_torneio(torneios, torneio_nome)

    if torneio_escolhido.get("tipo") in {"Davis Cup", "Billie Jean King Cup"}:
        from src.davis_cup import DavisCup

        davis = DavisCup(torneio_escolhido, jogador, ranking, nome_save)
        convocado, _pos, _ = davis.verificar_convocacao()
        if not convocado:
            raise HTTPException(
                status_code=403, detail="Você não foi convocado para a Copa Davis."
            )

        criar_torneio_davis(torneio_escolhido, jogador, nome_save, semana_atual)
        return {
            "ok": True,
            "torneio": {
                "nome": torneio_escolhido["nome"],
                "tipo": torneio_escolhido["tipo"],
                "davis": True,
                "destino_click_hub": "/davis",
                "fase_atual": "qualifiers",
            },
        }

    modalidade_normalizada = modalidade.strip().lower()
    tipo_duplas = "mesmo_genero"
    if modalidade_normalizada == "mistas":
        jogador.modalidade_atual = "duplas"
        tipo_duplas = "mista"
    elif modalidade_normalizada in {"simples", "duplas", "ambos"}:
        jogador.modalidade_atual = modalidade_normalizada
    else:
        raise HTTPException(status_code=422, detail="Modalidade invalida.")

    jogador.tipo_duplas_atual = tipo_duplas
    jogador.parceiro_duplas = _resolver_parceiro(
        nome_save, jogador, parceiro, tipo_duplas
    )
    save_player(nome_save, jogador)

    try:
        instancia = criar_torneio(
            torneio_escolhido, jogador, nome_save, temporada["semana"]
        )
        state = instancia.to_api_state()
    except Exception as exc:
        from api.logging_utils import log_exception as _log_exc

        _log_exc(
            "erro_ao_criar_torneio",
            exc,
            save=nome_save,
            jogador=jogador.nome,
            torneio=torneio_escolhido.get("nome"),
            modalidade=modalidade_normalizada,
            causa_provavel="Falha em criar_torneio() ou to_api_state() — pode ser ranking corrompido ou torneio sem jogadores suficientes.",
        )
        raise HTTPException(status_code=500, detail="Erro ao criar torneio.") from exc

    log_event(
        logging.INFO,
        "torneio_criado",
        save=nome_save,
        jogador=jogador.nome,
        torneio=torneio_escolhido.get("nome"),
        modalidade=modalidade_normalizada,
    )
    state["destino_click_hub"] = "/tournament"
    return {"ok": True, "torneio": state}


def get_tournament_state(nome_save: str) -> dict | None:
    instancia = carregar_torneio_api(nome_save)
    if not instancia:
        return None

    try:
        state = instancia.to_api_state()
    except Exception as exc:
        error_info = extract_exception_details(exc)
        tournament_data = getattr(instancia, "tournament_data", {})
        log_event(
            logging.ERROR,
            "torneio_state_serialization_failed",
            save_ativo=nome_save,
            torneio=(
                tournament_data.get("nome")
                if isinstance(tournament_data, dict)
                else None
            ),
            reason=error_info["root_cause"],
            **error_info,
        )
        raise HTTPException(
            status_code=500,
            detail="Falha ao converter o estado do torneio para resposta da API.",
        ) from exc

    is_davis = state.get("davis", False)
    state["destino_click_hub"] = "/davis" if is_davis else "/tournament"

    if is_davis:
        from src.davis_cup import DavisCup

        if isinstance(instancia, DavisCup):
            conf = instancia.obter_confronto_jogador()
            state["partida_disponivel"] = conf is not None
            state["info_partida"] = conf
        return state

    jogador_nome = state.get("estado", {}).get("jogador")
    fase = state.get("fase_atual")
    rodadas = state.get("estado", {}).get("rodadas", {})
    confrontos_fase = rodadas.get(fase, [])

    partida_pendente = None
    norm_j = normalizar_nome(jogador_nome)
    for c in confrontos_fase:
        n1 = normalizar_nome(c[0]["nome"] if isinstance(c[0], dict) else c[0])
        n2 = normalizar_nome(c[1]["nome"] if isinstance(c[1], dict) else c[1])
        if norm_j not in (n1, n2):
            continue
        adversario_raw = c[1] if norm_j == n1 else c[0]
        adversario_info = (
            instancia.garantir_dados_completos(adversario_raw)
            if hasattr(instancia, "garantir_dados_completos")
            else adversario_raw
        )
        if isinstance(adversario_info, dict):
            nome_adv = str(adversario_info.get("nome", "")).strip()
            ranking_instancia = getattr(instancia, "ranking", None)
            if (
                nome_adv
                and ranking_instancia
                and hasattr(ranking_instancia, "obter_posicao")
            ):
                if not adversario_info.get("ranking_pos"):
                    adversario_info["ranking_pos"] = (
                        ranking_instancia.obter_posicao(nome_adv) or 0
                    )
            if "overall" not in adversario_info and isinstance(
                adversario_info.get("atributos"), dict
            ):
                atributos = adversario_info.get("atributos", {}) or {}
                psico = adversario_info.get("atributos_psicologicos", {}) or {}
                tec = list(atributos.values())
                psi = list(psico.values())
                avg_tec = sum(tec) / len(tec) if tec else 50
                avg_psi = sum(psi) / len(psi) if psi else 50
                adversario_info["overall"] = round((avg_tec * 0.8) + (avg_psi * 0.2))
        partida_pendente = {
            "jogador1": c[0]["nome"] if isinstance(c[0], dict) else c[0],
            "jogador2": c[1]["nome"] if isinstance(c[1], dict) else c[1],
            "fase": fase,
            "adversario": adversario_info,
        }
        break

    state["partida_disponivel"] = partida_pendente is not None
    state["info_partida"] = partida_pendente
    return state


def advance_tournament_phase(nome_save: str) -> dict:
    instancia = carregar_torneio_api(nome_save)
    if not instancia:
        log_event(
            logging.WARNING,
            "avancar_fase_sem_torneio",
            save=nome_save,
            causa_provavel="Nenhum torneio_atp.json/wta.json no save ativo.",
        )
        raise HTTPException(status_code=404, detail="Nenhum torneio ativo encontrado.")

    try:
        fase_anterior = instancia._carregar_estado().get("fase_atual")
        instancia.simular_npcs_na_fase_atual(instancia.jogador_nome)
        avancar_fase(instancia)
        estado_atual = instancia._carregar_estado()
        resultados = estado_atual.get("resultados", {}).get(fase_anterior, [])
        log_event(
            logging.INFO,
            "fase_avancada",
            save=nome_save,
            fase_anterior=fase_anterior,
            fase_atual=estado_atual.get("fase_atual"),
            num_resultados=len(resultados),
        )
        return {
            "fase": estado_atual.get("fase_atual"),
            "resultados": resultados,
            "proximo": resumir_proxima_partida(instancia, instancia.jogador_nome),
        }
    except HTTPException:
        raise
    except Exception as exc:
        from api.logging_utils import log_exception as _log_exc

        _log_exc(
            "erro_ao_avancar_fase",
            exc,
            save=nome_save,
            causa_provavel="Falha em simular_npcs_na_fase_atual() ou avancar_fase().",
        )
        raise HTTPException(status_code=500, detail="Erro ao avançar fase.") from exc


def withdraw_from_tournament(nome_save: str) -> dict:
    instancia = carregar_torneio_api(nome_save)
    if not instancia:
        raise HTTPException(status_code=404, detail="Nenhum torneio ativo encontrado.")
    instancia.desistir_do_torneio()
    try:
        instancia.simular_torneio_restante()
    except Exception:
        pass
    try:
        distribuir_pontos_torneio(nome_save)
    except Exception:
        pass
    resultado = avancar_semana(nome_save)
    return {"ok": True, **resultado}
