"""
Lógica de desistência e walkover em torneios.

Responsável por marcar eliminações no estado do torneio quando
o jogador humano se retira (walkover) ou desiste voluntariamente.
"""

from src.jogador import normalizar_nome


def marcar_eliminacao_em_item(item, nome_jogador: str, fase_saida: str) -> None:
    """
    Percorre recursivamente *item* (dict, list ou tuple) e marca
    como eliminado qualquer nó cujo "nome" corresponda a *nome_jogador*.
    Mutação in-place.
    """
    if isinstance(item, dict) and "nome" in item:
        if normalizar_nome(item.get("nome", "")) == normalizar_nome(nome_jogador):
            item["vivo"] = False
            item["fase_saida"] = fase_saida
        for valor in item.values():
            marcar_eliminacao_em_item(valor, nome_jogador, fase_saida)
        return
    if isinstance(item, list):
        for valor in item:
            marcar_eliminacao_em_item(valor, nome_jogador, fase_saida)
    elif isinstance(item, tuple):
        for valor in item:
            marcar_eliminacao_em_item(valor, nome_jogador, fase_saida)


def resolver_walkovers_pendentes(
    estado: dict,
    nome_jogador: str,
    garantir_dados_completos,
    nomes_da_entidade,
) -> dict:
    """
    Para cada confronto da fase atual que envolva *nome_jogador*, registra
    walkover em favor do adversário, marca o jogador como eliminado e remove
    o confronto da rodada.

    Parâmetros:
        estado                  — estado mutável do torneio
        nome_jogador            — nome do jogador que desistiu
        garantir_dados_completos — callable(jogador) → dict com campos completos
        nomes_da_entidade        — callable(entidade) → list[str] com nomes
    """
    fase_atual = estado.get("fase_atual")
    if not fase_atual or fase_atual == "finalizado":
        return estado

    nome_norm = normalizar_nome(nome_jogador)
    confrontos = list(estado.get("rodadas", {}).get(fase_atual, []) or [])
    confrontos_restantes = []
    houve_walkover = False

    for confronto in confrontos:
        if not isinstance(confronto, (list, tuple)) or len(confronto) != 2:
            confrontos_restantes.append(confronto)
            continue

        jogador_a, jogador_b = confronto
        nomes_a = [normalizar_nome(n) for n in nomes_da_entidade(jogador_a)]
        nomes_b = [normalizar_nome(n) for n in nomes_da_entidade(jogador_b)]
        jogador_no_lado_a = nome_norm in nomes_a
        jogador_no_lado_b = nome_norm in nomes_b

        if not jogador_no_lado_a and not jogador_no_lado_b:
            confrontos_restantes.append(confronto)
            continue

        adversario = jogador_b if jogador_no_lado_a else jogador_a
        estado.setdefault("resultados", {}).setdefault(fase_atual, []).append(
            {
                "jogador_a": garantir_dados_completos(jogador_a),
                "jogador_b": garantir_dados_completos(jogador_b),
                "vencedor": garantir_dados_completos(adversario),
                "resultado": "W.O.",
                "walkover": True,
                "desistencia_jogador": True,
                "fase_saida": fase_atual,
            }
        )
        houve_walkover = True

    if houve_walkover:
        estado.setdefault("rodadas", {})[fase_atual] = confrontos_restantes
        estado["jogador_vivo"] = False
        estado["desistencia_jogador"] = True
        estado["jogador_fase_saida"] = fase_atual
        marcar_eliminacao_em_item(estado, nome_jogador, fase_atual)
    return estado
