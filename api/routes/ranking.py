from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from api.routes._carta import carta_jogador
from api.session import Session, obter_sessao_ativa
from src.dados import carregar_ranking_nacoes_davis
from src.player_identity import derive_player_identity
from src.player_ratings import ajustar_atributo_duplas, calcular_overall_contextual
from src.ranking import SistemaRanking

router = APIRouter(prefix="/api/ranking")


FASE_LABEL = {
    "campeao": "CAMPEÃO",
    "final": "FINAL",
    "semifinal": "SEMIFINAL",
    "quartas": "QUARTAS",
    "oitavas": "OITAVAS",
    "r16": "R16",
    "r32": "R32",
    "r64": "R64",
    "r128": "R128",
}


def _resumo_fifa(j: dict) -> dict:
    atributos = j.get("atributos", {}) or {}
    return {
        "MOV": int(atributos.get("movimento", 60) or 60),
        "SAQ": int(atributos.get("saque", 60) or 60),
        "FOR": int(atributos.get("forehand", 60) or 60),
        "BAC": int(atributos.get("backhand", 60) or 60),
        "FIS": int(atributos.get("fisico", 60) or 60),
        "TEC": int(
            (
                int(atributos.get("voleio", 60) or 60)
                + int(atributos.get("topspin", 60) or 60)
                + int(atributos.get("slice", 60) or 60)
                + int(atributos.get("lob", 60) or 60)
                + int(atributos.get("winner", 60) or 60)
            )
            / 5
        ),
    }


def _calcular_overall(j: dict) -> int:
    if not j.get("atributos"):
        return int(j.get("overall", 0) or 0)
    ajustar_atributo_duplas(j)
    return calcular_overall_contextual(j)


def _overall_com_bonus(j: dict, bonus: dict) -> int:
    """OVR com bônus da carta aplicado (cap 99 por atributo)."""
    atributos_boosted = dict(j.get("atributos", {}) or {})
    psi_boosted = dict(j.get("atributos_psicologicos", {}) or {})
    for k, v in bonus.items():
        if k in atributos_boosted:
            atributos_boosted[k] = min(99, atributos_boosted[k] + v)
        elif k in psi_boosted:
            psi_boosted[k] = min(99, psi_boosted[k] + v)
    fake_j = dict(j)
    fake_j["atributos"] = atributos_boosted
    fake_j["atributos_psicologicos"] = psi_boosted
    return _calcular_overall(fake_j)


def _resolver_ranking(
    session: Session, tour: str, modalidade: str = "simples"
) -> SistemaRanking | None:
    if modalidade == "duplas":
        return (
            session.ranking_duplas_wta if tour == "wta" else session.ranking_duplas_atp
        )
    return session.ranking_wta if tour == "wta" else session.ranking_atp


def _serializar_perfil_jogador(
    j: dict, ranking: SistemaRanking | None, tour: str, modalidade: str = "simples"
) -> dict:
    nome = j.get("nome") or "Desconhecido"
    ajustar_atributo_duplas(j)
    if modalidade == "duplas":
        pontos = int(j.get("pontos_ranking_duplas", j.get("pontos_duplas", 0)) or 0)
    else:
        pontos = int(j.get("pontos_ranking", j.get("pontos", 0)) or 0)
    ranking_pos = (
        ranking.obter_posicao(nome, modalidade=modalidade) if ranking else 9999
    )
    carta = carta_jogador(j, ranking_pos if isinstance(ranking_pos, int) else 9999)
    overall = calcular_overall_contextual(j, ranking_pos=ranking_pos)
    overall_boosted = (
        _overall_com_bonus(j, carta.get("bonus", {})) if carta.get("bonus") else overall
    )
    identity = derive_player_identity(
        j,
        ranking_pos=ranking_pos if isinstance(ranking_pos, int) else None,
        modalidade=modalidade,
    )
    return {
        "nome": nome,
        "tour": tour,
        "modalidade": modalidade,
        "nacionalidade": j.get("nacionalidade") or "??",
        "idade": int(j.get("idade", 0) or 0),
        "altura": int(j.get("altura", 0) or 0),
        "peso": int(j.get("peso", 0) or 0),
        "mao_dominante": j.get("mao_dominante"),
        "reves": j.get("reves"),
        "estilo_jogo": j.get("estilo_jogo"),
        "ranking": ranking_pos if isinstance(ranking_pos, int) else None,
        "pontos": pontos,
        "pontos_ytd": int(j.get("pontos_ytd", 0) or 0),
        "overall": overall,
        "overall_boosted": overall_boosted,
        "energia": int(j.get("energia", 100) or 100),
        "fadiga": int(j.get("fadiga", 0) or 0),
        "pico_carreira": int(j.get("pico_carreira", 0) or 0),
        "atributos": j.get("atributos", {}) or {},
        "atributos_psicologicos": j.get("atributos_psicologicos", {}) or {},
        "resumo_fifa": _resumo_fifa(j),
        "trofeus": list(j.get("trofeus", []) or []),
        "historico_torneios": list(j.get("historico_torneios", []) or []),
        "historico_partidas": list(j.get("historico_partidas", []) or []),
        "carta": carta,
        "identity": identity,
    }


@router.get("/atp")
def get_ranking_atp(
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(obter_sessao_ativa),
):
    if not session.ranking_atp:
        raise HTTPException(status_code=503, detail="Ranking ATP não disponível.")

    if session._cache_ranking_atp is None:
        session.ranking_atp.ordenar()
        ranking = session.ranking_atp.ranking
        total = len(ranking)
        session._cache_ranking_atp = {
            "ranking": [
                {
                    "nome": j.get("nome") or "Desconhecido",
                    "nacionalidade": j.get("nacionalidade") or "??",
                    "idade": int(j.get("idade", 0) or 0),
                    "pontos": j.get("pontos_ranking") or j.get("pontos", 0),
                    "overall": calcular_overall_contextual(j, ranking_pos=i + 1),
                    "carta_tipo": carta_jogador(j, i + 1).get("tipo", "bronze"),
                    "carta_raridade": carta_jogador(j, i + 1).get(
                        "raridade", "bronze"
                    ),
                }
                for i, j in enumerate(ranking[:1000]) # Cache apenas os top 1000
            ],
            "total": total,
        }

    cached = session._cache_ranking_atp
    sliced = cached["ranking"][offset : offset + limit]
    
    # Adiciona a posição correta (offset+1) baseada no fatiamento
    for i, item in enumerate(sliced):
        item["posicao"] = offset + i + 1

    return {
        "ranking": sliced,
        "total": cached["total"],
    }


@router.get("/wta")
def get_ranking_wta(
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(obter_sessao_ativa),
):
    if not session.ranking_wta:
        raise HTTPException(status_code=503, detail="Ranking WTA não disponível.")

    if session._cache_ranking_wta is None:
        session.ranking_wta.ordenar()
        ranking = session.ranking_wta.ranking
        total = len(ranking)
        session._cache_ranking_wta = {
            "ranking": [
                {
                    "nome": j.get("nome") or "Desconhecida",
                    "nacionalidade": j.get("nacionalidade") or "??",
                    "idade": int(j.get("idade", 0) or 0),
                    "pontos": j.get("pontos_ranking") or j.get("pontos", 0),
                    "overall": calcular_overall_contextual(j, ranking_pos=i + 1),
                    "carta_tipo": carta_jogador(j, i + 1).get("tipo", "bronze"),
                    "carta_raridade": carta_jogador(j, i + 1).get(
                        "raridade", "bronze"
                    ),
                }
                for i, j in enumerate(ranking[:1000])
            ],
            "total": total,
        }

    cached = session._cache_ranking_wta
    sliced = cached["ranking"][offset : offset + limit]
    
    for i, item in enumerate(sliced):
        item["posicao"] = offset + i + 1

    return {
        "ranking": sliced,
        "total": cached["total"],
    }


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
        ranking = _resolver_ranking(session, tour_atual, modalidade_norm)
        if not ranking:
            continue
        jogador = ranking.buscar_jogador_por_nome(nome)
        if jogador:
            return _serializar_perfil_jogador(
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
    rk = (
        session.ranking_duplas_atp
        if tour.lower() == "atp"
        else session.ranking_duplas_wta
    )

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
    dados = carregar_ranking_nacoes_davis()
    nacoes = dados.get("nations", [])
    nacoes_ordenadas = sorted(
        nacoes,
        key=lambda x: (x.get("points", 0), x.get("ties_played", 0), x.get("name", "")),
        reverse=True,
    )

    sliced = nacoes_ordenadas[offset : offset + limit]
    formatted = []
    for i, n in enumerate(sliced, offset + 1):
        codigo = str(n.get("id", "") or n.get("code", "") or "").upper()
        nome = str(n.get("name", codigo or "Nação"))
        formatted.append(
            {
                "posicao": i,
                "nome": nome,
                "codigo": codigo,
                "pontos": int(n.get("points", 0) or 0),
            }
        )

    return {"ranking": formatted, "total": len(nacoes_ordenadas)}


@router.get("/superficie/{superficie}")
def get_ranking_superficie(
    superficie: str,
    tour: str = Query(default="atp"),
    limit: int = 50,
    session: Session = Depends(obter_sessao_ativa),
):
    from src.superficie_utils import normalizar_superficie

    sup_norm = normalizar_superficie(superficie)
    cache_key = f"{sup_norm}_{tour.lower()}"
    
    if cache_key not in session._cache_ranking_superficies:
        rk_obj = session.ranking_wta if tour.lower() == "wta" else session.ranking_atp

        if not rk_obj:
            raise HTTPException(
                status_code=503, detail=f"Ranking {tour.upper()} não disponível."
            )

        def _calcular_overall_superficie(j: dict, sup: str) -> int:
            attrs = j.get("atributos", {}) or {}

            def _a(k, p=60):
                return int(attrs.get(k, p) or p)

            if sup == "saibro":
                # Pesos Saibro: Topspin, Fundo, Movimento, Físico
                ovr = (
                    _a("topspin") * 0.30
                    + _a("forehand") * 0.20
                    + _a("backhand") * 0.20
                    + _a("movimento") * 0.15
                    + _a("fisico") * 0.15
                )
            elif sup == "grama":
                # Pesos Grama: Saque, Voleio, Slice, Forehand
                ovr = (
                    _a("saque") * 0.30
                    + _a("voleio") * 0.25
                    + _a("slice") * 0.15
                    + _a("forehand") * 0.20
                    + _a("movimento") * 0.10
                )
            else:  # Dura / Geral
                ovr = (
                    _a("saque") * 0.20
                    + _a("forehand") * 0.25
                    + _a("backhand") * 0.20
                    + _a("movimento") * 0.20
                    + _a("fisico") * 0.15
                )
            return round(ovr)

        ranking_data = []
        for idx, j in enumerate(rk_obj.ranking):
            # Para evitar lentidão, calculamos apenas para os top 300
            if idx > 300:
                break

            ovr_sup = _calcular_overall_superficie(j, sup_norm)
            ranking_data.append(
                {
                    "nome": j.get("nome", "Desconhecido"),
                    "nacionalidade": j.get("nacionalidade", "??"),
                    "pontos_superficie": ovr_sup,  # Usamos o overall como "pontos" para ordenar
                    "overall": calcular_overall_contextual(j, ranking_pos=idx + 1),
                }
            )

        # Ordena pelo "overall de superfície"
        ranking_data.sort(key=lambda x: x["pontos_superficie"], reverse=True)
        session._cache_ranking_superficies[cache_key] = ranking_data

    full_ranking = session._cache_ranking_superficies[cache_key]
    sliced = full_ranking[:limit]
    
    # Faz uma cópia para não poluir o cache com posições mutáveis
    final_data = []
    for i, item in enumerate(sliced, 1):
        final_data.append({**item, "posicao": i})

    return {"superficie": sup_norm, "jogadores": final_data}
