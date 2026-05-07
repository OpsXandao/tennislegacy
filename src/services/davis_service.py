from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from src.davis_cup import DavisCup
from src.dados import carregar_estado_torneio, get_caminho_ranking_save
from src.ranking import SistemaRanking

_TIPOS_DAVIS_VALIDOS = {"Davis Cup", "Billie Jean King Cup"}


def carregar_davis_ativo(
    nome_save: str,
    jogador: Any,
) -> tuple[DavisCup, dict[str, Any]]:
    estado = carregar_estado_torneio(nome_save, genero=jogador.genero)
    if not estado or estado.get("tipo") not in _TIPOS_DAVIS_VALIDOS:
        raise HTTPException(
            status_code=404, detail="Nenhuma competicao Davis/BJK ativa."
        )

    ranking = SistemaRanking(get_caminho_ranking_save(nome_save, genero=jogador.genero))
    instancia = DavisCup(
        tournament_data=estado.get("tournament_data", {}),
        jogador=jogador,
        ranking=ranking,
        nome_save=nome_save,
    )
    return instancia, instancia._carregar_estado()


def obter_estado_davis(nome_save: str, jogador: Any) -> dict[str, Any]:
    instancia, _ = carregar_davis_ativo(nome_save, jogador)
    state = instancia.to_api_state()

    state["jogador_convocado"] = state["estado"].get("jogador_convocado", False)
    state["proximo"] = instancia.obter_proximo_confronto()

    conf = instancia.obter_confronto_jogador()
    state["partida_disponivel"] = conf is not None
    state["info_partida"] = conf
    return state


def obter_proximo_davis(nome_save: str, jogador: Any) -> dict[str, Any] | None:
    instancia, _ = carregar_davis_ativo(nome_save, jogador)
    return instancia.obter_proximo_confronto()


def simular_davis_atual(nome_save: str, jogador: Any) -> dict[str, Any]:
    instancia, estado_atual = carregar_davis_ativo(nome_save, jogador)

    if estado_atual.get("jogador_convocado") and estado_atual.get("jogador_vivo"):
        conf_humano = instancia.obter_confronto_jogador()
        if conf_humano:
            raise HTTPException(
                status_code=409,
                detail="É a sua vez de jogar! Vá para a quadra.",
            )

        instancia.simular_npcs_na_fase_atual(instancia.jogador.nome)

        estado_novo = instancia._carregar_estado()
        confronto = estado_novo.get("confronto_atual") or {}
        venc = confronto.get("vencedor")
        if venc:
            placar_tie = confronto.get("placar_tie", [0, 0])
            return {
                "ok": True,
                "vencedor": venc,
                "placar": f"{placar_tie[0]}-{placar_tie[1]}",
            }
        return {"ok": True, "vencedor": None, "placar": ""}

    confronto = estado_atual.get("confronto_atual") or {}
    resultado = instancia._simular_confronto_npc(
        confronto.get("equipe_a"),
        confronto.get("equipe_b"),
        alvo_vitorias=instancia._vitorias_para_vencer_tie(estado_atual),
    )
    instancia._atualizar_estado_apos_confronto(resultado)
    estado_novo = instancia._carregar_estado()
    if estado_novo.get("fase_atual") == "finalizado":
        try:
            from src.pontuacao import distribuir_pontos_davis

            distribuir_pontos_davis(nome_save)
        except Exception:
            pass
    return resultado
