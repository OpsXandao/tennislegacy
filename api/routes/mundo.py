from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from api.session import Session, obter_sessao_ativa
from api.services import mundo_service
from src.services.player_context_service import carregar_temporada_atual

router = APIRouter(prefix="/api/mundo", tags=["mundo"])


@router.get("/proximos")
def obter_proximos(session: Session = Depends(obter_sessao_ativa)):
    return mundo_service.obter_proximos(session)


@router.get("/noticias")
def _estruturar_noticia(texto: str, idx: int, semana: int) -> dict:
    titulo = texto.split(":", 1)[0] if ":" in texto else texto.split("!", 1)[0]
    tipo = "mundo"
    upper = texto.upper()
    if "CAMPE" in upper or "TÍTULO" in upper or "TITULO" in upper:
        tipo = "titulo"
    elif "SURPRESA" in upper:
        tipo = "zebra"
    elif "RANKING" in upper or "TOP" in upper or "MELHORES" in upper:
        tipo = "ranking"
    elif "MERCADO" in upper or "INVESTIDORES" in upper:
        tipo = "mercado"
    return {
        "id": f"news-{semana}-{idx}",
        "tipo": tipo,
        "titulo": titulo.strip().upper()[:80],
        "subtitulo": texto,
        "impacto": "alto" if tipo in {"titulo", "zebra"} else "medio",
        "semana": semana,
        "prioridade": idx,
        "texto": texto,
    }


@router.get("/noticias")
def obter_noticias(session: Session = Depends(obter_sessao_ativa)):
    temporada = carregar_temporada_atual(session.nome_save_ativo)
    noticias = mundo_service.obter_noticias(session)
    return {
        "noticias": noticias,
        "feed": [_estruturar_noticia(texto, idx, temporada["semana"]) for idx, texto in enumerate(noticias)],
    }


@router.get("/torneio/{nome}")
def obter_detalhes_torneio(
    nome: str,
    tour: str | None = None,
    session: Session = Depends(obter_sessao_ativa),
):
    nome_save = session.nome_save_ativo
    jogador = session.jogador
    temporada = carregar_temporada_atual(nome_save)

    genero = jogador.genero
    if tour == "atp":
        genero = "masculino"
    elif tour == "wta":
        genero = "feminino"

    return mundo_service.obter_torneio(nome_save, temporada["semana"], nome, genero)


@router.get("/ao-vivo")
def ao_vivo(session: Session = Depends(obter_sessao_ativa)):
    nome_save = session.nome_save_ativo
    temporada = carregar_temporada_atual(nome_save)
    return {"semana": temporada["semana"], "torneios": mundo_service.obter_ao_vivo(nome_save, temporada["semana"])}


@router.get("/race-to-finals")
def race_to_finals(session: Session = Depends(obter_sessao_ativa)):
    return mundo_service.obter_race_to_finals(session)


@router.get("/bracket")
def bracket_torneio_externo(
    torneio: str = Query(...),
    tour: str = Query(default="atp"),
    session: Session = Depends(obter_sessao_ativa),
):
    nome_save = session.nome_save_ativo
    temporada = carregar_temporada_atual(nome_save)
    return mundo_service.obter_bracket(nome_save, temporada["semana"], torneio, tour)


@router.get("/ranking-nacoes")
def get_ranking_nacoes():
    return {"nacoes": mundo_service.obter_ranking_nacoes()}
