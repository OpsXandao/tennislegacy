import random
from src.jogador import normalizar_nome
from src.constants.torneio_constants import RANKING_POSICAO_FALLBACK, SEEDS_ATP_1000


def numero_seeds_main_draw(draw_size: int) -> int:
    if draw_size >= 128:
        return 32
    if draw_size >= 64:
        return 16
    if draw_size >= 32:
        return 8
    if draw_size >= 16:
        return 4
    return 2


def seed_positions(draw_size: int, num_seeds: int) -> list[int]:
    from src.torneio_draw import seed_positions as core_seed_positions

    return core_seed_positions(draw_size, num_seeds)


def montar_chave_principal(jogadores, draw_size, ranking, garantir_dados_fn):
    from src.torneio_draw import montar_chave_principal as core_montar_chave

    return core_montar_chave(jogadores, draw_size, ranking, garantir_dados_fn)


def main_draw_tem_vagas_invalidas(confrontos) -> bool:
    for confronto in confrontos:
        if not isinstance(confronto, (list, tuple)) or len(confronto) != 2:
            return True
        if confronto[0] is None or confronto[1] is None:
            return True
    return False


def montar_rodada_r96(
    main_draw_players,
    ranking,
    jogador_nome,
    jogador_nacionalidade,
    garantir_dados_fn,
    incluir_jogador_principal=False,
):
    """Lógica especializada para ATP 1000 com Bye pros Seeds (R96)."""
    jogadores_ordenados = sorted(
        main_draw_players,
        key=lambda j: ranking.obter_posicao(j.get("nome", ""))
        or RANKING_POSICAO_FALLBACK,
    )
    seeds = jogadores_ordenados[:SEEDS_ATP_1000]
    nao_seeds = jogadores_ordenados[SEEDS_ATP_1000:]

    if incluir_jogador_principal and normalizar_nome(jogador_nome) not in [
        normalizar_nome(p["nome"]) for p in jogadores_ordenados
    ]:
        jogador_humano_dict = {
            "nome": jogador_nome,
            "nacionalidade": jogador_nacionalidade,
        }
        if nao_seeds:
            nao_seeds[-1] = jogador_humano_dict
        else:
            nao_seeds.append(jogador_humano_dict)

    random.shuffle(nao_seeds)
    confrontos_r96 = []
    for i in range(0, len(nao_seeds), 2):
        if i + 1 < len(nao_seeds):
            confrontos_r96.append(
                (garantir_dados_fn(nao_seeds[i]), garantir_dados_fn(nao_seeds[i + 1]))
            )
    return seeds, confrontos_r96


def jogador_em_seed_entries(seeds, nome_jogador: str) -> bool:
    nome_norm = normalizar_nome(nome_jogador)
    for s in seeds:
        if normalizar_nome(s.get("nome", "")) == nome_norm:
            return True
    return False
