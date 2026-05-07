from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from api.session import Session, obter_sessao_ativa
from src.duplas import (
    buscar_parceiros_disponiveis,
    tentar_convidar_parceiro,
    buscar_parceiro_por_ranking,
    buscar_parceiro_por_nacionalidade,
)
from src.ranking import SistemaRanking
from src.dados import get_caminho_ranking_save, get_caminho_ranking_duplas
from src.jogador import normalizar_nome
from src.save import salvar_jogo

router = APIRouter(prefix="/api/duplas", tags=["duplas"])


def _carregar_ranking_duplas_ou_simples(nome_save: str, genero: str) -> SistemaRanking:
    path_duplas = get_caminho_ranking_duplas(nome_save, genero=genero)
    ranking_duplas = SistemaRanking(path_duplas, modalidade="duplas")
    if ranking_duplas.ranking:
        return ranking_duplas

    path_simples = get_caminho_ranking_save(nome_save, genero=genero)
    return SistemaRanking(path_simples, modalidade="simples")


def _buscar_npc_no_ranking(ranking: SistemaRanking, nome_npc: str):
    nome_norm = normalizar_nome(nome_npc)
    for entrada in ranking.ranking:
        if normalizar_nome(entrada.get("nome", "")) != nome_norm:
            continue
        if entrada.get("is_lean"):
            return ranking.buscar_jogador_por_nome(entrada["nome"]) or entrada
        return entrada
    return None


def _obter_vinculo(vinculos: dict, nome_npc: str):
    if nome_npc in vinculos:
        return vinculos[nome_npc]
    nome_norm = normalizar_nome(nome_npc)
    for nome_salvo, vinculo in vinculos.items():
        if normalizar_nome(nome_salvo) == nome_norm:
            return vinculo
    return None


class InviteRequest(BaseModel):
    npc_nome: str
    torneio_tipo: str = "ATP 250"


@router.get("/sugestoes")
def sugerir_parceiros(session: Session = Depends(obter_sessao_ativa)):
    nome_save = session.nome_save_ativo
    jogador = session.jogador
    rk = _carregar_ranking_duplas_ou_simples(nome_save, jogador.genero)

    vinculos = getattr(jogador, "vinculos_dupla", {})
    parceiros = buscar_parceiros_disponiveis(
        jogador, rk.ranking, n=10, vinculos=vinculos
    )

    return {
        "parceiros": [
            {
                "nome": p.get("nome"),
                "nacionalidade": p.get("nacionalidade"),
                "overall": p.get("overall", 50),
                "duplas": p.get("atributos", {}).get("duplas", 0),
                "posicao": p.get("posicao"),
                "vinculo": p.get("_vinculo"),
            }
            for p in parceiros
        ]
    }


@router.get("/buscar")
def buscar_parceiros(
    nome: Optional[str] = None,
    nacionalidade: Optional[str] = None,
    session: Session = Depends(obter_sessao_ativa),
):
    nome_save = session.nome_save_ativo
    jogador = session.jogador
    rk = _carregar_ranking_duplas_ou_simples(nome_save, jogador.genero)

    if nacionalidade:
        parceiros = buscar_parceiro_por_nacionalidade(
            rk.ranking, nacionalidade, nome_jogador_excluir=jogador.nome
        )
    elif nome:
        nome_norm = normalizar_nome(nome)
        parceiros = [
            p
            for p in rk.ranking
            if nome_norm in normalizar_nome(p.get("nome", ""))
            and normalizar_nome(p.get("nome", "")) != normalizar_nome(jogador.nome)
        ]
    else:
        parceiros = buscar_parceiro_por_ranking(
            rk.ranking, n=50, nome_jogador_excluir=jogador.nome
        )

    return {
        "parceiros": [
            {
                "nome": p.get("nome"),
                "nacionalidade": p.get("nacionalidade"),
                "overall": p.get("overall", 50),
                "duplas": p.get("atributos", {}).get("duplas", 0),
                "posicao": p.get("posicao"),
            }
            for p in parceiros[:50]
        ]
    }


@router.post("/convidar")
def convidar(req: InviteRequest, session: Session = Depends(obter_sessao_ativa)):
    nome_save = session.nome_save_ativo
    jogador = session.jogador

    rk_duplas = SistemaRanking(
        get_caminho_ranking_duplas(nome_save, genero=jogador.genero),
        modalidade="duplas",
    )
    rk_simples = SistemaRanking(
        get_caminho_ranking_save(nome_save, genero=jogador.genero),
        modalidade="simples",
    )

    npc = _buscar_npc_no_ranking(rk_duplas, req.npc_nome) or _buscar_npc_no_ranking(
        rk_simples, req.npc_nome
    )

    if not npc:
        raise HTTPException(
            status_code=404, detail="Jogador não encontrado no ranking."
        )

    vinculos = getattr(jogador, "vinculos_dupla", {})
    vinculo = _obter_vinculo(vinculos, npc["nome"])

    pos = rk_simples.obter_posicao(npc["nome"], modalidade="simples") or 999

    aceitou, msg = tentar_convidar_parceiro(
        jogador, npc, ranking_pos=pos, torneio_tipo=req.torneio_tipo, vinculo=vinculo
    )

    if aceitou:
        parceiro = {
            "nome": npc["nome"],
            "nacionalidade": npc.get("nacionalidade", "??"),
        }
        setattr(jogador, "parceiro_duplas", parceiro)
        salvar_jogo(nome_save, jogador)
        return {
            "ok": True,
            "mensagem": msg,
            "parceiro": parceiro,
        }
    else:
        return {"ok": False, "mensagem": msg}
