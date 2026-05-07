from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.session import Session, obter_sessao_ativa
from src.davis_cup import DavisCup
from src.dados import carregar_estado_torneio, get_caminho_ranking_save
from src.ranking import SistemaRanking

router = APIRouter(prefix="/api/davis", tags=["davis"])


def _carregar_davis_ativo(session: Session) -> tuple[str, object, DavisCup, dict]:
    nome_save = session.nome_save_ativo
    jogador = session.jogador
    estado = carregar_estado_torneio(nome_save, genero=jogador.genero)
    tipos_validos = {"Davis Cup", "Billie Jean King Cup"}
    if not estado or estado.get("tipo") not in tipos_validos:
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
    return nome_save, jogador, instancia, instancia._carregar_estado()


@router.get("/estado")
def estado(session: Session = Depends(obter_sessao_ativa)) -> dict:
    _, _, instancia, _ = _carregar_davis_ativo(session)
    state = instancia.to_api_state()

    state["jogador_convocado"] = state["estado"].get("jogador_convocado", False)
    state["proximo"] = instancia.obter_proximo_confronto()

    conf = instancia.obter_confronto_jogador()
    state["partida_disponivel"] = conf is not None
    state["info_partida"] = conf

    return state


@router.get("/proximo")
def proximo(session: Session = Depends(obter_sessao_ativa)) -> dict | None:
    _, _, instancia, _ = _carregar_davis_ativo(session)
    return instancia.obter_proximo_confronto()


@router.post("/simular-atual")
def simular_atual(session: Session = Depends(obter_sessao_ativa)) -> dict:
    nome_save, _, instancia, estado_atual = _carregar_davis_ativo(session)

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
            return {
                "ok": True,
                "vencedor": venc,
                "placar": f"{confronto.get('placar_tie', [0,0])[0]}-{confronto.get('placar_tie', [0,0])[1]}",
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
