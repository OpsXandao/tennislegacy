from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from api.session import Session, obter_sessao_ativa
from api.services import ranking_service

router = APIRouter(prefix="/api/ranking")

@router.get("/atp")
def get_ranking_atp(
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(obter_sessao_ativa),
):
    return ranking_service.get_cached_ranking(session, "atp", limit, offset)

@router.get("/wta")
def get_ranking_wta(
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(obter_sessao_ativa),
):
    return ranking_service.get_cached_ranking(session, "wta", limit, offset)

@router.get("/jogador")
def get_perfil_jogador(
    nome: str = Query(..., min_length=1),
    tour: Optional[str] = Query(default=None),
    modalidade: str = Query(default="simples"),
    session: Session = Depends(obter_sessao_ativa),
):
    modalidade_norm = "duplas" if modalidade.lower() == "duplas" else "simples"
    tours = (
        [tour.lower()] if tour and tour.lower() in {"atp", "wta"} else ["atp", "wta"]
    )

    for tour_atual in tours:
        ranking = ranking_service.resolver_ranking(session, tour_atual, modalidade_norm)
        if not ranking:
            continue
        jogador = ranking.buscar_jogador_por_nome(nome)
        if jogador:
            return ranking_service.serializar_perfil_jogador(
                jogador, ranking, tour_atual, modalidade_norm
            )

    raise HTTPException(status_code=404, detail="Jogador não encontrado.")

@router.get("/duplas/{tour}")
def get_ranking_duplas(
    tour: str,
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(obter_sessao_ativa),
):
    rk = ranking_service.resolver_ranking(session, tour, "duplas")

    if not rk:
        raise HTTPException(status_code=503, detail="Ranking de duplas não disponível.")

    rk.ordenar()
    ranking = rk.ranking
    total = len(ranking)
    sliced = ranking[offset : offset + limit]

    return {
        "ranking": [
            {
                "posicao": offset + i + 1,
                "nome": j.get("nome") or "Desconhecido",
                "nacionalidade": j.get("nacionalidade") or "??",
                "idade": int(j.get("idade", 0) or 0),
                "pontos": j.get("pontos_duplas", j.get("pontos", 0)),
            }
            for i, j in enumerate(sliced)
        ],
        "total": total,
    }

@router.get("/nacoes/davis")
def get_ranking_nacoes_davis(limit: int = 20, offset: int = 0):
    return ranking_service.get_nacoes_davis(limit, offset)

@router.get("/superficie/{superficie}")
def get_ranking_superficie(
    superficie: str,
    tour: str = Query(default="atp"),
    limit: int = 50,
    session: Session = Depends(obter_sessao_ativa),
):
    return ranking_service.get_ranking_superficie(session, superficie, tour, limit)
