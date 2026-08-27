import random
from src.torneio_npc import simular_partida_npc_basica


def _nome(entidade):
    if isinstance(entidade, dict):
        return entidade.get("nome", "")
    return str(entidade or "")


def _risco_retirada_pre_jogo(entidade: dict) -> float:
    status_lesao = entidade.get("status_lesao", {}) if isinstance(entidade, dict) else {}
    status_doenca = entidade.get("status_doenca", {}) if isinstance(entidade, dict) else {}
    if isinstance(status_lesao, dict) and status_lesao.get("lesionado"):
        return 1.0
    if isinstance(status_doenca, dict) and status_doenca.get("doente"):
        return 0.28
    energia = int(entidade.get("energia", 100) or 100)
    fadiga = int(entidade.get("fadiga", 0) or 0)
    risco = 0.0
    if energia <= 18:
        risco += 0.32
    elif energia <= 32:
        risco += 0.15
    if fadiga >= 92:
        risco += 0.28
    elif fadiga >= 82:
        risco += 0.14
    nivel = status_lesao.get("nivel") if isinstance(status_lesao, dict) else None
    if nivel == "limitado":
        risco += 0.18
    elif nivel == "desconforto":
        risco += 0.06
    return min(0.72, risco)


def _resultado_walkover(ent_a: dict, ent_b: dict, retirado: dict, vencedor: dict) -> dict:
    retirado_nome = _nome(retirado)
    vencedor_nome = _nome(vencedor)
    return {
        "jogador_a": ent_a,
        "jogador_b": ent_b,
        "vencedor": vencedor,
        "resultado": "W.O.",
        "placar": "W.O.",
        "walkover": True,
        "retirado": retirado_nome,
        "motivo": "retirada_pre_jogo_fisica",
        "resumo": f"{vencedor_nome} avançou por W.O. após retirada de {retirado_nome}.",
        "pontos_disputados": 0,
        "games_total": 0,
    }


def simular_partida_npc(torneio_inst, a, b, modalidade="simples"):
    """Simula uma partida entre dois NPCs usando o motor de simulação básica."""
    # Garante dados físicos vindos do ranking ou estado
    nome_a = a.get("nome") if isinstance(a, dict) else a
    nome_b = b.get("nome") if isinstance(b, dict) else b

    # Busca dados completos se necessário
    ent_a = torneio_inst.garantir_dados_completos(a)
    ent_b = torneio_inst.garantir_dados_completos(b)

    risco_a = _risco_retirada_pre_jogo(ent_a)
    risco_b = _risco_retirada_pre_jogo(ent_b)
    if risco_a >= 1.0 or (risco_a > 0 and random.random() < risco_a):
        return _resultado_walkover(ent_a, ent_b, ent_a, ent_b)
    if risco_b >= 1.0 or (risco_b > 0 and random.random() < risco_b):
        return _resultado_walkover(ent_a, ent_b, ent_b, ent_a)

    venc, perd, placar, pts, games = simular_partida_npc_basica(
        ent_a,
        ent_b,
        torneio_inst.best_of_sets,
        superficie=getattr(torneio_inst, "tournament_data", {}).get("quadra"),
    )

    # Aplica consequências físicas e morais (delegando de volta pro Torneio por enquanto para manter compatibilidade)
    # TODO: Mover logica de fadiga NPC para ca tambem
    torneio_inst._aplicar_fadiga_npc_por_nome(nome_a, pts)
    torneio_inst._aplicar_fadiga_npc_por_nome(nome_b, pts)
    torneio_inst._aplicar_moral_npc_partida(venc["nome"], perd["nome"])

    return {
        "jogador_a": ent_a,
        "jogador_b": ent_b,
        "vencedor": venc,
        "resultado": placar,
        "pontos_disputados": pts,
        "games_total": games,
    }


def processar_simulacao_rodada(torneio_inst, confrontos, modalidade="simples"):
    """Simula uma lista de confrontos NPC."""
    resultados = []
    for a, b in confrontos:
        res = simular_partida_npc(torneio_inst, a, b, modalidade)
        resultados.append(res)
    return resultados
