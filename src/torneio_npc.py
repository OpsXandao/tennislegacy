import random


def limpar_nome_resultado(nome: str) -> str:
    if not isinstance(nome, str):
        return str(nome)
    return nome.strip().rstrip("0123456789").strip()


def estimar_pontos_partida(best_of_sets: int, sets_d: int, rng=None) -> int:
    rng = rng or random
    if best_of_sets == 5:
        if sets_d == 0:
            base = 120
        elif sets_d == 1:
            base = 150
        else:
            base = 190
        return rng.randint(base - 10, base + 10)

    if sets_d == 0:
        base = 70
    else:
        base = 110
    return rng.randint(base - 8, base + 8)


def estimar_games_partida(best_of_sets: int, sets_d: int, rng=None) -> int:
    rng = rng or random
    if best_of_sets == 5:
        if sets_d == 0:
            return rng.randint(18, 27)
        if sets_d == 1:
            return rng.randint(25, 35)
        return rng.randint(30, 42)

    if sets_d == 0:
        return rng.randint(12, 20)
    return rng.randint(18, 30)


def simular_partida_npc_basica(
    a: dict, b: dict, best_of_sets: int, superficie: str = None, rng=None
):
    rng = rng or random

    def _esta_apto(j):
        if not isinstance(j, dict):
            return True
        # Verifica lesão
        status_lesao = j.get("status_lesao", {})
        if isinstance(status_lesao, dict) and status_lesao.get("lesionado"):
            return False
        # Verifica exaustão extrema (energia < 5)
        if int(j.get("energia", 100) or 100) < 5:
            return False
        return True

    apto_a = _esta_apto(a)
    apto_b = _esta_apto(b)

    # Lógica de Walkover (W/O)
    if not apto_a or not apto_b:
        if not apto_a and not apto_b:
            # Ambos inaptos (raro), o melhor ranqueado avança por WO
            vencedor = a if a.get("overall", 50) >= b.get("overall", 50) else b
        elif not apto_a:
            vencedor = b
        else:
            vencedor = a

        perdedor = b if vencedor is a else a
        nome_v = limpar_nome_resultado(vencedor.get("nome", "??"))
        nome_p = limpar_nome_resultado(perdedor.get("nome", "??"))

        return vencedor, perdedor, f"{nome_v} def. {nome_p} (W/O)", 0, 0

    # PEGAR OVERALL (com fallback para 50)
    ov_a = a.get("overall", 50) if isinstance(a, dict) else getattr(a, "overall", 50)
    ov_b = b.get("overall", 50) if isinstance(b, dict) else getattr(b, "overall", 50)

    # Pegar moral (fallback 70)
    moral_a = a.get("moral", 70) if isinstance(a, dict) else getattr(a, "moral", 70)
    moral_b = b.get("moral", 70) if isinstance(b, dict) else getattr(b, "moral", 70)

    # Cálculo de probabilidade baseada na diferença de overall
    prob_a = 0.5 + (ov_a - ov_b) * 0.04

    # Impacto da moral
    impacto_moral = (moral_a - moral_b) * 0.002
    prob_a += impacto_moral

    # Impacto da Superfície (Especialistas)
    if superficie:

        def _get_pref(j):
            return (
                j.get("superficie_preferida")
                if isinstance(j, dict)
                else getattr(j, "superficie_preferida", None)
            )

        pref_a = _get_pref(a)
        pref_b = _get_pref(b)

        if pref_a == superficie:
            prob_a += 0.05  # +5% de chance de vitória
        if pref_b == superficie:
            prob_a -= 0.05  # -5% de chance de vitória

    prob_a = max(0.05, min(0.95, prob_a))

    vencedor = a if rng.random() < prob_a else b
    perdedor = b if vencedor is a else a

    if best_of_sets == 5:
        sets_v = 3
        sets_d = rng.choice([0, 1, 2])
    else:
        sets_v = 2
        sets_d = rng.choice([0, 1])

    nome_vencedor = limpar_nome_resultado(vencedor.get("nome", ""))
    nome_perdedor = limpar_nome_resultado(perdedor.get("nome", ""))
    placar = f"{nome_vencedor} {sets_v} x {sets_d} {nome_perdedor}"
    pontos_disputados = estimar_pontos_partida(best_of_sets, sets_d, rng=rng)
    games_total = estimar_games_partida(best_of_sets, sets_d, rng=rng)

    return vencedor, perdedor, placar, pontos_disputados, games_total
