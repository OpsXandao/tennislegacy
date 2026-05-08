from __future__ import annotations

from fastapi import HTTPException
from api.session import Session
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


def _serializar_parceiro(p: dict, com_vinculo: bool = False) -> dict:
    result = {
        "nome": p.get("nome"),
        "nacionalidade": p.get("nacionalidade"),
        "overall": p.get("overall", 50),
        "duplas": p.get("atributos", {}).get("duplas", 0),
        "posicao": p.get("posicao"),
    }
    if com_vinculo:
        result["vinculo"] = p.get("_vinculo")
    return result


def buscar_sugestoes(session: Session) -> list:
    nome_save = session.nome_save_ativo
    jogador = session.jogador
    rk = _carregar_ranking_duplas_ou_simples(nome_save, jogador.genero)
    vinculos = getattr(jogador, "vinculos_dupla", {})
    parceiros = buscar_parceiros_disponiveis(jogador, rk.ranking, n=10, vinculos=vinculos)
    return [_serializar_parceiro(p, com_vinculo=True) for p in parceiros]


def buscar(session: Session, nome: str | None, nacionalidade: str | None) -> list:
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

    return [_serializar_parceiro(p) for p in parceiros[:50]]


def convidar(session: Session, npc_nome: str, torneio_tipo: str) -> dict:
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

    npc = _buscar_npc_no_ranking(rk_duplas, npc_nome) or _buscar_npc_no_ranking(
        rk_simples, npc_nome
    )
    if not npc:
        raise HTTPException(status_code=404, detail="Jogador não encontrado no ranking.")

    vinculos = getattr(jogador, "vinculos_dupla", {})
    vinculo = _obter_vinculo(vinculos, npc["nome"])
    pos = rk_simples.obter_posicao(npc["nome"], modalidade="simples") or 999

    aceitou, msg = tentar_convidar_parceiro(
        jogador, npc, ranking_pos=pos, torneio_tipo=torneio_tipo, vinculo=vinculo
    )

    if aceitou:
        parceiro = {"nome": npc["nome"], "nacionalidade": npc.get("nacionalidade", "??")}
        setattr(jogador, "parceiro_duplas", parceiro)
        salvar_jogo(nome_save, jogador)
        return {"ok": True, "mensagem": msg, "parceiro": parceiro}

    return {"ok": False, "mensagem": msg}
