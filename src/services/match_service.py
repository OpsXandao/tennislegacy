from __future__ import annotations

import logging

from fastapi import HTTPException

from api.logging_utils import log_event, log_exception
from api.routes._match_runtime import criar_match_runtime, obter_match_runtime
from src.services.player_context_service import (
    carregar_torneio_api,
    encontrar_confronto_jogador,
)


def dupla_contem_jogador(dupla, nome_jogador: str) -> bool:
    from src.jogador import normalizar_nome

    alvo = normalizar_nome(nome_jogador)
    if isinstance(dupla, dict):
        jogadores = dupla.get("jogadores")
        if isinstance(jogadores, list):
            for item in jogadores:
                if isinstance(item, dict) and normalizar_nome(item.get("nome", "")) == alvo:
                    return True
        return normalizar_nome(dupla.get("nome", "")) == alvo
    return normalizar_nome(str(dupla)) == alvo


def _nome_item_resultado(item) -> str:
    if isinstance(item, dict):
        return str(item.get("nome", "")).strip()
    return str(item or "").strip()


def _historico_partidas_do_torneio_atual(instancia, nome_adversario: str) -> list[dict]:
    from src.jogador import normalizar_nome

    if not nome_adversario or not hasattr(instancia, "_carregar_estado"):
        return []

    try:
        estado = instancia._carregar_estado()
    except Exception:
        return []

    nome_norm = normalizar_nome(nome_adversario)
    resultados = estado.get("resultados", {}) or {}
    fases_ordem = []
    if hasattr(instancia, "_fases_ordem"):
        try:
            fases_ordem = list(instancia._fases_ordem())
        except Exception:
            fases_ordem = []

    fases = list(resultados.keys())
    if fases_ordem:
        fases.sort(key=lambda fase: fases_ordem.index(fase) if fase in fases_ordem else 999)

    historico = []
    for fase in fases:
        for resultado in resultados.get(fase, []) or []:
            jogador_a = resultado.get("jogador_a", resultado.get("jogador1"))
            jogador_b = resultado.get("jogador_b", resultado.get("jogador2"))
            nome_a = _nome_item_resultado(jogador_a)
            nome_b = _nome_item_resultado(jogador_b)
            envolvidos = {normalizar_nome(nome_a), normalizar_nome(nome_b)}
            if nome_norm not in envolvidos:
                continue

            vencedor = _nome_item_resultado(resultado.get("vencedor"))
            adversario = nome_b if normalizar_nome(nome_a) == nome_norm else nome_a
            historico.append(
                {
                    "torneio": instancia.tournament_data.get("nome", "Torneio"),
                    "fase": fase,
                    "adversario": adversario,
                    "placar": resultado.get("placar") or resultado.get("resultado") or "",
                    "resultado": (
                        "V" if normalizar_nome(vencedor) == nome_norm else "D"
                    ),
                }
            )

    return historico[-3:]


def _mesclar_historicos_recentes(historico_base: list[dict], historico_torneio: list[dict]) -> list[dict]:
    combinado = list(historico_base or [])
    chaves = {
        (
            str(item.get("torneio", "")),
            str(item.get("fase", "")),
            str(item.get("adversario", "")),
            str(item.get("placar", "")),
            str(item.get("resultado", "")),
        )
        for item in combinado
        if isinstance(item, dict)
    }
    for item in historico_torneio:
        chave = (
            str(item.get("torneio", "")),
            str(item.get("fase", "")),
            str(item.get("adversario", "")),
            str(item.get("placar", "")),
            str(item.get("resultado", "")),
        )
        if chave in chaves:
            continue
        combinado.append(item)
        chaves.add(chave)
    return combinado[-30:]


def resolver_adversario_partida(instancia, jogador) -> tuple[dict, str]:
    from src.davis_cup import DavisCup
    from src.jogador import normalizar_nome

    if isinstance(instancia, DavisCup):
        conf_davis = instancia.obter_confronto_jogador()
        if not conf_davis:
            raise HTTPException(
                status_code=409, detail="Não é a sua vez de jogar na Davis Cup."
            )
        if normalizar_nome(conf_davis["jogador1"]) == normalizar_nome(jogador.nome):
            adv_nome = conf_davis["jogador2"]
        else:
            adv_nome = conf_davis["jogador1"]
        return {"nome": adv_nome}, "simples"

    estado = instancia._carregar_estado()
    confronto = encontrar_confronto_jogador(estado, jogador.nome)
    adversario_data = None
    modalidade = "simples"

    if not confronto:
        fase_duplas = estado.get("fase_atual_duplas")
        if fase_duplas and fase_duplas != "finalizado":
            rodadas_duplas = estado.get("rodadas_duplas", {})
            for c in rodadas_duplas.get(fase_duplas, []):
                a_dupla = c[0]
                b_dupla = c[1]
                if dupla_contem_jogador(a_dupla, jogador.nome):
                    adversario_data = {
                        "nome": b_dupla["nome"] if isinstance(b_dupla, dict) else b_dupla
                    }
                    modalidade = "duplas"
                    break
                if dupla_contem_jogador(b_dupla, jogador.nome):
                    adversario_data = {
                        "nome": a_dupla["nome"] if isinstance(a_dupla, dict) else a_dupla
                    }
                    modalidade = "duplas"
                    break
        if not adversario_data:
            raise HTTPException(
                status_code=409,
                detail="Jogador nao possui confronto pendente nesta fase.",
            )
    else:
        adversario_data = confronto["adversario"]
        modalidade = "simples"
    return adversario_data, modalidade


def completar_adversario(instancia, adversario_data: dict) -> dict:
    adversario_completo = (
        instancia.garantir_dados_completos(adversario_data)
        if hasattr(instancia, "garantir_dados_completos")
        else {"nome": adversario_data.get("nome", "BOT")}
    )
    if isinstance(adversario_completo, dict):
        nome_adversario = str(adversario_completo.get("nome", "")).strip()
        if (
            nome_adversario
            and not adversario_completo.get("ranking")
            and not adversario_completo.get("ranking_pos")
        ):
            ranking_instancia = getattr(instancia, "ranking", None)
            if ranking_instancia and hasattr(ranking_instancia, "obter_posicao"):
                adversario_completo["ranking_pos"] = (
                    ranking_instancia.obter_posicao(nome_adversario) or 0
                )
        historico_torneio = _historico_partidas_do_torneio_atual(
            instancia, nome_adversario
        )
        if historico_torneio:
            historico_existente = list(
                adversario_completo.get("historico_partidas", []) or []
            )
            adversario_completo["historico_partidas"] = _mesclar_historicos_recentes(
                historico_existente, historico_torneio
            )
        if "overall" not in adversario_completo and isinstance(
            adversario_completo.get("atributos"), dict
        ):
            atributos = adversario_completo.get("atributos", {}) or {}
            psico = adversario_completo.get("atributos_psicologicos", {}) or {}
            tec = list(atributos.values())
            psi = list(psico.values())
            avg_tec = sum(tec) / len(tec) if tec else 50
            avg_psi = sum(psi) / len(psi) if psi else 50
            adversario_completo["overall"] = round((avg_tec * 0.8) + (avg_psi * 0.2))
    return adversario_completo


def get_active_match(nome_save: str) -> dict | None:
    from api.routes._match_store import load_snapshot, snapshot_path

    matches_dir = snapshot_path(nome_save, "__probe__").parent
    if not matches_dir.exists():
        return None

    for snap in matches_dir.glob("*.json"):
        try:
            data = load_snapshot(nome_save, snap.stem)
            if data and not data.get("encerrado"):
                runtime = obter_match_runtime(snap.stem)
                if runtime:
                    config = runtime.config
                    return {
                        "partida_id": runtime.partida_id,
                        "config": {
                            "modo": runtime.modo,
                            "superficie": config.superficie,
                            "melhor_de": config.melhor_de,
                            "nome_torneio": config.nome_torneio,
                            "tipo_torneio": config.tipo_torneio,
                        },
                        "adversario": runtime.adversario,
                        "placar": runtime.serializar(),
                    }
        except Exception:
            continue

    return None


def preview_match(nome_save: str, jogador) -> dict:
    instancia = carregar_torneio_api(nome_save)
    if not instancia:
        raise HTTPException(
            status_code=404,
            detail="Nao existe torneio ativo para preparar partida.",
        )
    adversario_data, _modalidade = resolver_adversario_partida(instancia, jogador)
    return {"adversario": completar_adversario(instancia, adversario_data)}


def start_match(modo: str, nome_save: str, jogador) -> dict:
    instancia = carregar_torneio_api(nome_save)
    if not instancia:
        log_event(
            logging.WARNING,
            "partida_sem_torneio_ativo",
            save=nome_save,
            jogador=jogador.nome,
            causa_provavel="Nenhum torneio ativo encontrado.",
        )
        raise HTTPException(
            status_code=404, detail="Nao existe torneio ativo para iniciar partida."
        )

    ativa = get_active_match(nome_save)
    if ativa:
        return ativa

    adversario_data, modalidade = resolver_adversario_partida(instancia, jogador)
    try:
        adversario_completo = completar_adversario(instancia, adversario_data)
        runtime = criar_match_runtime(
            save_name=nome_save,
            jogador=jogador,
            adversario=adversario_completo,
            torneio_info=instancia.tournament_data,
            modo=modo,
            modalidade=modalidade,
        )
    except Exception as exc:
        log_exception(
            "erro_ao_criar_runtime_partida",
            exc,
            save=nome_save,
            jogador=jogador.nome,
            adversario=(
                adversario_data.get("nome")
                if isinstance(adversario_data, dict)
                else str(adversario_data)
            ),
            modo=modo,
            causa_provavel="Falha ao instanciar o motor de partida.",
        )
        raise HTTPException(status_code=500, detail="Erro ao iniciar partida.") from exc

    log_event(
        logging.INFO,
        "partida_iniciada",
        save=nome_save,
        jogador=jogador.nome,
        adversario=(
            adversario_data.get("nome")
            if isinstance(adversario_data, dict)
            else str(adversario_data)
        ),
        modo=modo,
        partida_id=runtime.partida_id,
    )
    config = runtime.config
    return {
        "partida_id": runtime.partida_id,
        "config": {
            "modo": modo,
            "superficie": config.superficie,
            "melhor_de": config.melhor_de,
            "tiebreak_decisivo_pontos": config.tiebreak_decisivo_pontos,
            "nome_torneio": config.nome_torneio,
            "tipo_torneio": config.tipo_torneio,
        },
        "adversario": getattr(runtime, "adversario", adversario_completo),
        "placar": runtime.serializar(event_type="setup", descricao=""),
    }
