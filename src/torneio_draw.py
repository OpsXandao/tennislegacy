import random
from src.jogador import normalizar_nome


def shuffle_with_rng(lista, rng=None):
    if rng:
        rng.shuffle(lista)
    else:
        random.shuffle(lista)


def organizar_confrontos(jogadores, rng=None):
    """Divide a lista de jogadores em pares para a rodada."""
    shuffle_with_rng(jogadores, rng)
    return [jogadores[i : i + 2] for i in range(0, len(jogadores), 2)]


def gerar_chave_simples(
    jogadores,
    fases_ordem,
    fase_inicial,
    num_rounds,
    jogador_nome,
    ranking,
    seeds_count=0,
    rng=None,
):
    """Gera a estrutura inicial de chaves para o torneio de simples."""
    estado = {
        "jogador": jogador_nome,
        "fase_atual": fase_inicial,
        "rodadas": {},
        "resultados": {},
    }

    # Identifica seeds se necessário
    if seeds_count > 0:
        jogadores_reais = [j for j in jogadores if not j.get("is_bot")]

        def get_pos(j):
            return ranking.obter_posicao(j.get("nome", "")) or 9999

        jogadores_reais.sort(key=get_pos)
        seeds = jogadores_reais[:seeds_count]
        outros = [j for j in jogadores if j not in seeds]
        shuffle_with_rng(seeds, rng)
        shuffle_with_rng(outros, rng)

        # Distribuição simplificada de seeds (poderia ser mais complexa como chaves reais)
        campo_final = []
        for i in range(len(jogadores) // 2):
            if i < len(seeds):
                campo_final.append(seeds[i])
                if outros:
                    campo_final.append(outros.pop(0))
            else:
                if len(outros) >= 2:
                    campo_final.extend([outros.pop(0), outros.pop(0)])
                elif outros:
                    campo_final.append(outros.pop(0))
        jogadores = campo_final

    confrontos = organizar_confrontos(jogadores, rng)
    estado["rodadas"][fase_inicial] = confrontos
    return estado


def seed_positions(draw_size, num_seeds):
    """Retorna as posições fixas das cabeças de chave baseadas no tamanho da chave (ATP/WTA Standard)."""
    if draw_size == 128:
        # Posições para 32 seeds em draw de 128
        return [0, 127, 63, 64, 31, 96, 32, 95, 15, 112, 47, 80, 16, 111, 48, 79, 7, 120, 55, 72, 24, 103, 39, 88, 8, 119, 56, 71, 23, 104, 40, 87]
    elif draw_size == 64:
        # Posições para 16 seeds em draw de 64
        return [0, 63, 31, 32, 15, 48, 16, 47, 7, 56, 24, 39, 8, 55, 23, 40]
    elif draw_size == 32:
        # Posições para 8 seeds em draw de 32
        return [0, 31, 15, 16, 7, 24, 8, 23]
    elif draw_size == 16:
        # Posições para 4 seeds em draw de 16
        return [0, 15, 7, 8]
    return []


def montar_chave_principal(jogadores, draw_size, ranking, garantir_dados_fn):
    """Monta a chave principal distribuindo sementes e sorteando restantes."""
    from src.constants.torneio_constants import DRAW_SIZE_GRAND_SLAM, DRAW_SIZE_ATP_1000

    num_seeds = (
        32
        if draw_size == DRAW_SIZE_GRAND_SLAM
        else 16 if draw_size == DRAW_SIZE_ATP_1000 else 8
    )

    def get_pos(j):
        return ranking.obter_posicao(j.get("nome", "")) or 9999

    jogadores_ordenados = sorted(jogadores, key=get_pos)

    seeds = jogadores_ordenados[:num_seeds]
    restantes = jogadores_ordenados[num_seeds:]
    posicoes = seed_positions(draw_size, num_seeds)

    slots = [None] * draw_size
    for jogador_seed, pos in zip(seeds, posicoes):
        if pos < draw_size:
            slots[pos] = jogador_seed

    random.shuffle(restantes)
    idx_restantes = 0
    for i in range(draw_size):
        if slots[i] is None and idx_restantes < len(restantes):
            slots[i] = restantes[idx_restantes]
            idx_restantes += 1

    return [
        (garantir_dados_fn(a), garantir_dados_fn(b))
        for a, b in zip(slots[::2], slots[1::2])
    ]
