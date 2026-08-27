from __future__ import annotations

from typing import Any

from src.constants.torneio_constants import START_YEAR
from src.jogador import atualizar_rivalidade
from src.utils.match_runtime_utils import (
    atualizar_historico_torneios,
    fase_alcancada_apos_partida,
)


def registrar_historicos(runtime: Any, instancia: Any) -> None:
    from src.dados import carregar_temporada
    from src.match_history import MatchHistoryManager

    temporada = carregar_temporada(runtime.save_name)
    fase = str(
        runtime.torneio_info.get("fase_atual") or runtime.torneio_info.get("fase") or ""
    )
    if not fase:
        try:
            fase = str(instancia._carregar_estado().get("fase_atual") or "")
        except Exception:
            pass

    adversario_nome = runtime.adversario.get("nome", "Adversario")
    placar_final = runtime._placar_final_texto()
    jogador_venceu = runtime.vencedor == "jogador"
    fase_alcancada = fase_alcancada_apos_partida(instancia, fase, jogador_venceu)

    partida_jogador = {
        "ano": temporada.get("ano"),
        "semana": temporada.get("semana"),
        "torneio": runtime.torneio_info.get("nome", "Torneio"),
        "fase": fase,
        "adversario": adversario_nome,
        "placar": placar_final,
        "resultado": "V" if jogador_venceu else "D",
    }
    historico_partidas = list(getattr(runtime.jogador, "historico_partidas", []) or [])
    historico_partidas.append(partida_jogador)
    runtime.jogador.historico_partidas = historico_partidas[-30:]

    atualizar_rivalidade(
        runtime.jogador, adversario_nome, jogador_venceu, semana=temporada.get("semana")
    )
    fase_final = fase_alcancada or fase
    atualizar_historico_torneios(
        runtime.jogador,
        {
            "nome": runtime.torneio_info.get("nome"),
            "torneio": runtime.torneio_info.get("nome"),
            "tipo": runtime.torneio_info.get("tipo", ""),
            "semana": temporada.get("semana"),
            "ano": temporada.get("ano"),
            "fase": fase_final,
            "fase_alcancada": fase_final,
            "pontos": 0,
            "premio": 0,
            "modalidade": runtime.modalidade,
            "expirado": False,
        },
    )

    # Registrar troféu ao vencer o torneio
    if jogador_venceu and fase_final == "campeao":
        tipo_torneio = runtime.torneio_info.get("tipo", "")
        categoria = (
            "Grand Slam"
            if tipo_torneio == "Grand Slam"
            else (
                "Masters 1000"
                if "1000" in tipo_torneio
                else (
                    "ATP Finals"
                    if "Finals" in tipo_torneio
                    else "ATP 500" if "500" in tipo_torneio else "ATP 250"
                )
            )
        )
        trofeu = {
            "torneio": runtime.torneio_info.get("nome"),
            "tipo": tipo_torneio,
            "categoria": categoria,
            "semana": temporada.get("semana"),
            "ano": temporada.get("ano"),
            "modalidade": runtime.modalidade,
        }
        if not isinstance(getattr(runtime.jogador, "trofeus", None), list):
            runtime.jogador.trofeus = []
        runtime.jogador.trofeus.append(trofeu)

    ranking = getattr(instancia, "ranking", None)
    if ranking and adversario_nome:
        adversario_ranking = ranking.buscar_jogador_por_nome(adversario_nome)
        if isinstance(adversario_ranking, dict):
            _registrar_historico_adversario(
                runtime,
                ranking,
                adversario_ranking,
                temporada,
                fase,
                placar_final,
                jogador_venceu,
            )

    try:
        MatchHistoryManager(runtime.save_name).adicionar_partida(
            torneio=runtime.torneio_info.get("nome"),
            semana=temporada.get("semana", 1),
            ano=temporada.get("ano", START_YEAR),
            modalidade=runtime.modalidade,
            jogadores=[getattr(runtime.jogador, "nome", "Jogador"), adversario_nome],
            resultado=placar_final,
            vencedor=(
                getattr(runtime.jogador, "nome", "Jogador")
                if jogador_venceu
                else adversario_nome
            ),
            fase=fase,
        )
    except Exception as exc:
        from src.utils.log_jogo import log_erro

        log_erro(runtime.save_name, "MatchHistoryManager", exc)


def _registrar_historico_adversario(
    runtime: Any,
    ranking: Any,
    adversario_ranking: dict,
    temporada: dict,
    fase: str,
    placar_final: str,
    jogador_venceu: bool,
) -> None:
    historico = list(adversario_ranking.get("historico_partidas", []) or [])
    historico.append(
        {
            "ano": temporada.get("ano"),
            "semana": temporada.get("semana"),
            "torneio": runtime.torneio_info.get("nome"),
            "fase": fase,
            "adversario": getattr(runtime.jogador, "nome", "Jogador"),
            "placar": placar_final,
            "resultado": "D" if jogador_venceu else "V",
        }
    )
    adversario_ranking["historico_partidas"] = historico[-30:]
    adversario_ranking["energia"] = int(round(runtime.contexto_partida.stamina_a))
    adversario_ranking["fadiga"] = runtime._fadiga_ao_vivo("a")
    if not adversario_ranking.get("overall"):
        from api.routes.ranking import _calcular_overall

        adversario_ranking["overall"] = _calcular_overall(adversario_ranking)
    adversario_ranking["ranking_pos"] = ranking.obter_posicao(
        runtime.adversario.get("nome", "")
    ) or adversario_ranking.get("ranking_pos", 0)
    runtime.adversario.update(
        {
            "historico_partidas": adversario_ranking["historico_partidas"],
            "overall": adversario_ranking.get("overall"),
            "ranking_pos": adversario_ranking.get("ranking_pos"),
            "nacionalidade": adversario_ranking.get("nacionalidade"),
        }
    )
    ranking.salvar_ranking()


def finalizar_torneio(runtime: Any) -> None:
    if runtime.finalizado_torneio:
        return

    import random

    from api.routes._shared import carregar_torneio_api
    from src.save import salvar_jogo
    from src.services.milestone_service import MilestoneService
    from src.torneio import avancar_fase

    instancia = carregar_torneio_api(runtime.save_name)
    if not instancia:
        runtime.finalizado_torneio = True
        return

    jogador_venceu = runtime.vencedor == "jogador"
    adversario_nome = runtime.adversario.get("nome", "Adversario")
    vencedor_nome = (
        getattr(runtime.jogador, "nome", "Jogador")
        if jogador_venceu
        else adversario_nome
    )
    instancia.processar_resultado_partida(
        runtime.jogador,
        runtime.adversario,
        {"nome": vencedor_nome},
        runtime._placar_final_texto(),
    )
    try:
        instancia.simular_npcs_na_fase_atual(instancia.jogador_nome)
        avancar_fase(instancia)
    except Exception as exc:
        from src.utils.log_jogo import log_erro

        log_erro(runtime.save_name, "finalizar_torneio:avancar", exc)

    runtime._registrar_historicos(instancia)
    _aplicar_consequencias_pos_partida(runtime, instancia, jogador_venceu)

    try:
        adv_ranking_pos = int(runtime.adversario.get("ranking_pos", 999) or 999)
    except (TypeError, ValueError):
        adv_ranking_pos = 999
    milestones = MilestoneService.detect_match_milestones(
        runtime.jogador,
        adversario_nome,
        adv_ranking_pos,
        jogador_venceu,
    )
    if milestones:
        if not hasattr(runtime, "log") or not isinstance(runtime.log, list):
            runtime.log = []
        runtime.log.extend(milestones)
        if not hasattr(runtime.jogador, "milestones_semana"):
            runtime.jogador.milestones_semana = []
        runtime.jogador.milestones_semana.extend(milestones)

    ajustar_ritmo = getattr(runtime.jogador, "ajustar_ritmo", None)
    if callable(ajustar_ritmo):
        ajustar_ritmo(random.randint(5, 8))
        if not hasattr(runtime, "log") or not isinstance(runtime.log, list):
            runtime.log = []
        runtime.log.append("Ritmo de jogo aumentando apos partida intensa.")

    salvar_jogo(runtime.save_name, runtime.jogador)

    estado = instancia._carregar_estado()
    if estado.get("fase_atual") == "finalizado" or not estado.get("jogador_vivo", True):
        from src.pontuacao import distribuir_pontos_torneio

        distribuir_pontos_torneio(
            runtime.save_name,
            genero=getattr(runtime.jogador, "genero", "masculino"),
        )
    runtime.finalizado_torneio = True
    runtime._persistir()


def _aplicar_consequencias_pos_partida(
    runtime: Any, instancia: Any, jogador_venceu: bool
) -> None:
    from src.fadiga import handle_fadiga_e_lesao, handle_fadiga_e_lesao_npc
    from src.match_dynamics import (
        calcular_impacto_moral_ranking,
        calcular_impacto_moral_sets,
        normalizar_energia_pos_partida,
    )
    from src.progressao import handle_progressao_natural, handle_xp_e_level_up

    runtime.jogador.energia = normalizar_energia_pos_partida(
        runtime.contexto_partida.stamina_j,
        getattr(runtime.jogador, "atributos", {}).get("fisico", 50),
        runtime.total_pontos,
        superficie=getattr(runtime.config, "superficie", "dura"),
        energia_inicial=runtime.energia_inicial,
    )
    delta_moral = calcular_impacto_moral_sets(
        runtime.jogador, runtime.set_scores, jogador_venceu
    )
    delta_moral += calcular_impacto_moral_ranking(
        runtime.jogador, runtime.adversario, jogador_venceu
    )
    if delta_moral != 0:
        runtime.jogador.moral = max(
            0, min(100, int(getattr(runtime.jogador, "moral", 70) + delta_moral))
        )

    runtime.jogador = handle_xp_e_level_up(runtime.jogador, jogador_venceu)
    handle_progressao_natural(
        runtime.jogador,
        runtime.stats_j,
        runtime.estrategia_j,
        runtime.total_pontos,
        modalidade=runtime.modalidade,
    )
    fatores_fadiga = instancia._montar_fatores_fadiga(
        runtime.config, runtime.adversario
    )
    runtime.jogador = handle_fadiga_e_lesao(
        runtime.jogador,
        pontos_disputados=runtime.total_pontos,
        fatores_partida=fatores_fadiga,
        energia_perdida=max(
            0, runtime.energia_inicial - int(round(runtime.contexto_partida.stamina_j))
        ),
        ranking=instancia.ranking,
    )
    runtime.adversario = (
        handle_fadiga_e_lesao_npc(
            runtime.adversario,
            pontos_disputados=runtime.total_pontos,
            fatores_partida=fatores_fadiga,
            energia_perdida=max(
                0,
                runtime.energia_inicial_a
                - int(round(runtime.contexto_partida.stamina_a)),
            ),
            rank_atual=runtime.adversario.get("ranking_pos"),
        )
        or runtime.adversario
    )
    _recuperar_jogador_entre_rodadas(runtime, instancia, jogador_venceu)


def _recuperar_jogador_entre_rodadas(
    runtime: Any, instancia: Any, jogador_venceu: bool
) -> None:
    if not jogador_venceu:
        return

    try:
        estado = instancia._carregar_estado()
    except Exception:
        return

    if estado.get("fase_atual") == "finalizado":
        return
    if not estado.get("jogador_vivo", True):
        return

    from src.fadiga import recuperar_energia_entre_rodadas

    multiplicador = 1.0
    agenda = estado.get("agenda_dia", {})
    jogos_no_dia = (
        agenda.get("jogos_realizados", []) if isinstance(agenda, dict) else []
    )
    if jogos_no_dia:
        try:
            multiplicador = float(instancia._multiplicador_recuperacao_mesmo_dia())
        except Exception:
            pass

    jogador_recuperado, eventos = recuperar_energia_entre_rodadas(
        runtime.jogador,
        multiplicador=multiplicador,
        return_eventos=True,
    )
    runtime.jogador = jogador_recuperado
    if not hasattr(runtime, "log") or not isinstance(runtime.log, list):
        runtime.log = []
    runtime.log.extend(evento.mensagem for evento in eventos)
