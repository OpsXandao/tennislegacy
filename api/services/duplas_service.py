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
from src.services.doubles_realism_service import (
    availability_status,
    combined_rank,
    doubles_match_format,
    partnership_profile,
)


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


def _ranking_pos_por_lista(ranking: SistemaRanking, nome: str) -> int | None:
    obter = getattr(ranking, "obter_posicao", None)
    if callable(obter):
        try:
            pos = obter(nome, modalidade=getattr(ranking, "modalidade", None))
        except TypeError:
            pos = obter(nome)
        if pos:
            return int(pos)
    nome_norm = normalizar_nome(nome)
    for idx, entrada in enumerate(getattr(ranking, "ranking", []) or [], 1):
        if normalizar_nome(entrada.get("nome", "")) == nome_norm:
            return idx
    return None


def _serializar_parceiro(
    p: dict,
    jogador,
    rk_duplas: SistemaRanking,
    rk_simples: SistemaRanking | None = None,
    com_vinculo: bool = False,
    torneio_tipo: str = "ATP 250",
) -> dict:
    vinculo = p.get("_vinculo")
    rank_duplas_jogador = _ranking_pos_por_lista(rk_duplas, jogador.nome)
    rank_duplas_parceiro = _ranking_pos_por_lista(rk_duplas, p.get("nome", ""))
    rank_simples_parceiro = (
        _ranking_pos_por_lista(rk_simples, p.get("nome", "")) if rk_simples else None
    )
    perfil = partnership_profile(jogador, p, vinculo=vinculo)
    disponibilidade = availability_status(
        jogador,
        p,
        torneio_tipo=torneio_tipo,
        parceiro_rank_simples=rank_simples_parceiro,
        vinculo=vinculo,
    )
    result = {
        "nome": p.get("nome"),
        "nacionalidade": p.get("nacionalidade"),
        "overall": p.get("overall", 50),
        "duplas": p.get("atributos", {}).get("duplas", p.get("duplas", 0)),
        "estilo_jogo": p.get("estilo_jogo", "All-court"),
        "posicao": rank_duplas_parceiro or p.get("posicao"),
        "ranking_duplas": rank_duplas_parceiro,
        "ranking_simples": rank_simples_parceiro,
        "ranking_combinado": combined_rank(rank_duplas_jogador, rank_duplas_parceiro),
        "perfil_parceria": perfil,
        "disponibilidade": disponibilidade,
        "formato_duplas": doubles_match_format(torneio_tipo),
    }
    if com_vinculo:
        result["vinculo"] = vinculo
    return result


def buscar_sugestoes(session: Session) -> list:
    nome_save = session.nome_save_ativo
    jogador = session.jogador
    rk = _carregar_ranking_duplas_ou_simples(nome_save, jogador.genero)
    rk_simples = SistemaRanking(
        get_caminho_ranking_save(nome_save, genero=jogador.genero), modalidade="simples"
    )
    vinculos = getattr(jogador, "vinculos_dupla", {})
    parceiros = buscar_parceiros_disponiveis(jogador, rk.ranking, n=10, vinculos=vinculos)
    return [
        _serializar_parceiro(p, jogador, rk, rk_simples, com_vinculo=True)
        for p in parceiros
    ]


def buscar(session: Session, nome: str | None, nacionalidade: str | None) -> list:
    nome_save = session.nome_save_ativo
    jogador = session.jogador
    rk = _carregar_ranking_duplas_ou_simples(nome_save, jogador.genero)
    rk_simples = SistemaRanking(
        get_caminho_ranking_save(nome_save, genero=jogador.genero), modalidade="simples"
    )

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

    return [_serializar_parceiro(p, jogador, rk, rk_simples) for p in parceiros[:50]]


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
    disponibilidade = availability_status(
        jogador, npc, torneio_tipo=torneio_tipo, parceiro_rank_simples=pos, vinculo=vinculo
    )
    if disponibilidade["status"] == "indisponivel":
        return {
            "ok": False,
            "mensagem": f"{npc['nome']} nao esta disponivel para duplas nesta semana.",
            "disponibilidade": disponibilidade,
        }

    aceitou, msg = tentar_convidar_parceiro(
        jogador, npc, ranking_pos=pos, torneio_tipo=torneio_tipo, vinculo=vinculo
    )

    if aceitou:
        if npc.get("is_lean"):
            return {"ok": False, "mensagem": msg}
        parceiro = {"nome": npc["nome"], "nacionalidade": npc.get("nacionalidade", "??")}
        setattr(jogador, "parceiro_duplas", parceiro)
        salvar_jogo(nome_save, jogador)
        return {"ok": True, "mensagem": msg, "parceiro": parceiro, "disponibilidade": disponibilidade}

    return {"ok": False, "mensagem": msg, "disponibilidade": disponibilidade}
