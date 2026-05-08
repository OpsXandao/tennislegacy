from fastapi import HTTPException
from typing import Optional, List, Dict, Any
from api.session import Session
from src.player_ratings import calcular_overall_contextual, ajustar_atributo_duplas
from src.player_identity import derive_player_identity
from api.routes._carta import carta_jogador
from src.ranking import SistemaRanking
from src.constants.torneio_constants import RANKING_POSICAO_FALLBACK

RANKING_CACHE_LIMIT = 2000
RANKING_SURFACE_LIMIT = 500

def get_resumo_fifa(j: dict) -> dict:
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

def overall_com_bonus(j: dict, bonus: dict) -> int:
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
    ajustar_atributo_duplas(fake_j)
    return calcular_overall_contextual(fake_j)

def serializar_perfil_jogador(
    j: dict, ranking: SistemaRanking | None, tour: str, modalidade: str = "simples"
) -> dict:
    nome = j.get("nome") or "Desconhecido"
    ajustar_atributo_duplas(j)
    if modalidade == "duplas":
        pontos = int(j.get("pontos_ranking_duplas", j.get("pontos_duplas", 0)) or 0)
    else:
        pontos = int(j.get("pontos_ranking", j.get("pontos", 0)) or 0)
    
    ranking_pos = (
        ranking.obter_posicao(nome, modalidade=modalidade) if ranking else RANKING_POSICAO_FALLBACK
    )
    
    carta = carta_jogador(j, ranking_pos if isinstance(ranking_pos, int) else RANKING_POSICAO_FALLBACK)
    overall = calcular_overall_contextual(j, ranking_pos=ranking_pos)
    overall_boosted = (
        overall_com_bonus(j, carta.get("bonus", {})) if carta.get("bonus") else overall
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
        "resumo_fifa": get_resumo_fifa(j),
        "trofeus": list(j.get("trofeus", []) or []),
        "historico_torneios": list(j.get("historico_torneios", []) or []),
        "historico_partidas": list(j.get("historico_partidas", []) or []),
        "carta": carta,
        "identity": identity,
    }

def resolver_ranking(
    session: Session, tour: str, modalidade: str = "simples"
) -> SistemaRanking | None:
    if modalidade == "duplas":
        return (
            session.ranking_duplas_wta if tour == "wta" else session.ranking_duplas_atp
        )
    return session.ranking_wta if tour == "wta" else session.ranking_atp

def get_ranking_superficie(
    session: Session, superficie: str, tour: str, limit: int
):
    from src.utils.superficie_utils import normalizar_superficie as normalizar_surface
    
    sup_norm = normalizar_surface(superficie)
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
            if idx > RANKING_SURFACE_LIMIT:
                break

            ovr_sup = _calcular_overall_superficie(j, sup_norm)
            ranking_data.append(
                {
                    "nome": j.get("nome", "Desconhecido"),
                    "nacionalidade": j.get("nacionalidade", "??"),
                    "pontos_superficie": ovr_sup,
                    "overall": calcular_overall_contextual(j, ranking_pos=idx + 1),
                }
            )

        ranking_data.sort(key=lambda x: x["pontos_superficie"], reverse=True)
        session._cache_ranking_superficies[cache_key] = ranking_data

    full_ranking = session._cache_ranking_superficies[cache_key]
    sliced = full_ranking[:limit]
    
    final_data = []
    for i, item in enumerate(sliced, 1):
        final_data.append({**item, "posicao": i})

    return {"superficie": sup_norm, "jogadores": final_data}

def get_cached_ranking(session: Session, tour: str, limit: int, offset: int):
    is_wta = tour.lower() == "wta"
    rk_obj = session.ranking_wta if is_wta else session.ranking_atp
    cache_attr = "_cache_ranking_wta" if is_wta else "_cache_ranking_atp"
    
    if not rk_obj:
        raise HTTPException(status_code=503, detail=f"Ranking {tour.upper()} não disponível.")

    if getattr(session, cache_attr) is None:
        rk_obj.ordenar()
        ranking = rk_obj.ranking
        total = len(ranking)
        
        cached_data = {
            "ranking": [
                {
                    "nome": j.get("nome") or ("Desconhecida" if is_wta else "Desconhecido"),
                    "nacionalidade": j.get("nacionalidade") or "??",
                    "idade": int(j.get("idade", 0) or 0),
                    "pontos": j.get("pontos_ranking") or j.get("pontos", 0),
                    "overall": calcular_overall_contextual(j, ranking_pos=i + 1),
                    "carta_tipo": carta_jogador(j, i + 1).get("tipo", "bronze"),
                    "carta_raridade": carta_jogador(j, i + 1).get("raridade", "bronze"),
                }
                for i, j in enumerate(ranking[:RANKING_CACHE_LIMIT])
            ],
            "total": total,
        }
        setattr(session, cache_attr, cached_data)

    cached = getattr(session, cache_attr)
    sliced = cached["ranking"][offset : offset + limit]
    
    for i, item in enumerate(sliced):
        item["posicao"] = offset + i + 1

    return {
        "ranking": sliced,
        "total": cached["total"],
    }


def get_nacoes_davis(limit: int, offset: int) -> dict:
    from src.dados import carregar_ranking_nacoes_davis

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
