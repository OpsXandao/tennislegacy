import random
from src.torneio_npc import simular_partida_npc_basica


def simular_partida_npc(torneio_inst, a, b, modalidade="simples"):
    """Simula uma partida entre dois NPCs usando o motor de simulação básica."""
    # Garante dados físicos vindos do ranking ou estado
    nome_a = a.get("nome") if isinstance(a, dict) else a
    nome_b = b.get("nome") if isinstance(b, dict) else b

    # Busca dados completos se necessário
    ent_a = torneio_inst.garantir_dados_completos(a)
    ent_b = torneio_inst.garantir_dados_completos(b)

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
