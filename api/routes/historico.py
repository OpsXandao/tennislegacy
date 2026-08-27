from fastapi import APIRouter, Depends

from api.session import Session, obter_sessao_ativa
from api.services.mundo_service import obter_campeoes, obter_goat

router = APIRouter(prefix="/api/historico", tags=["historico"])


@router.get("/goat")
def get_goat(session: Session = Depends(obter_sessao_ativa)):
    trofeus = getattr(session.jogador, "trofeus", [])
    historico_torneios = getattr(session.jogador, "historico_torneios", [])
    return obter_goat(session.nome_save_ativo, trofeus, historico_torneios)


@router.get("/campeoes")
def get_campeoes(session: Session = Depends(obter_sessao_ativa)):
    return obter_campeoes(session.nome_save_ativo)


@router.get("/campeoes-temporada")
def get_campeoes_temporada(session: Session = Depends(obter_sessao_ativa)):
    """Campeões de torneios disputados na temporada atual (ano corrente do save)."""
    from src.dados import carregar_temporada, carregar_historico

    temporada = carregar_temporada(session.nome_save_ativo)
    ano_atual = temporada.get("ano") if temporada else None
    hist = carregar_historico(session.nome_save_ativo)
    campeoes_raw = hist.get("campeoes", {})

    # Títulos do jogador na temporada
    trofeus_jogador = [
        t
        for t in (getattr(session.jogador, "trofeus", []) or [])
        if not ano_atual or t.get("ano") == ano_atual
    ]

    # Campeões NPC da temporada (do histórico de resultados)
    campeoes_temporada = []
    if isinstance(campeoes_raw, dict):
        for torneio_nome, historico_lista in campeoes_raw.items():
            if not isinstance(historico_lista, list):
                continue
            for entrada in historico_lista:
                if not isinstance(entrada, dict):
                    continue
                if ano_atual and entrada.get("ano") != ano_atual:
                    continue
                campeoes_temporada.append(
                    {
                        "torneio": torneio_nome,
                        "campeao": entrada.get("campeao") or entrada.get("vencedor"),
                        "ano": entrada.get("ano"),
                        "semana": entrada.get("semana"),
                        "tipo": entrada.get("tipo", ""),
                    }
                )

    return {
        "ano": ano_atual,
        "titulos_jogador": trofeus_jogador,
        "campeoes_npc": sorted(campeoes_temporada, key=lambda x: x.get("semana", 0)),
    }
