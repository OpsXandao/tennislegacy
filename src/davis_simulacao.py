"""
Davis Cup / BJK Cup — Funções puras de simulação e utilidades.

Contém:
- Utilitários puros: ties_por_seeding, vitorias_para_vencer_tie,
  criar_agenda_tie, forca_simples, forca_duplas.
- Simulação NPC: simular_confronto_npc, simular_restante_fase,
  avancar_fase.

Todas as funções recebem os dados necessários por parâmetro (sem estado
global nem acesso a self) para facilitar testes unitários.
"""

import random

from src.davis_selecao import SelecaoNacional

# ---------------------------------------------------------------------------
# Utilitários puros
# ---------------------------------------------------------------------------


def ties_por_seeding(equipes_ordenadas):
    """Gera os confrontos pelo critério de seeding (1 vs último, 2 vs penúltimo…)."""
    result = []
    i = 0
    j = len(equipes_ordenadas) - 1
    while i < j:
        result.append((equipes_ordenadas[i], equipes_ordenadas[j]))
        i += 1
        j -= 1
    return result


def vitorias_para_vencer_tie(estado):
    """Retorna quantas vitórias são necessárias para vencer o tie naquela fase.

    Desde 2019 o formato unificado é melhor-de-3 (alvo = 2 vitórias) em todas
    as fases, incluindo qualifiers.  Final 8 também usa alvo 2.
    """
    return 2


def criar_agenda_tie(total, s1_j, s2_j, s1_a, s2_a):
    """
    Retorna a lista de partidas do tie.

    Formato: [(tipo, jogador_equipe_casa, jogador_equipe_visitante), …]
    tipo ∈ {"simples", "duplas"}
    """
    if total == 3:
        return [
            ("simples", s2_j, s2_a),
            ("simples", s1_j, s1_a),
            ("duplas", None, None),
        ]
    return [
        ("simples", s2_j, s2_a),
        ("simples", s1_j, s1_a),
        ("duplas", None, None),
        ("simples", s1_j, s2_a),
        ("simples", s2_j, s1_a),
    ]


def forca_simples(atleta):
    """Score para escalar simples (ranking atual + overall)."""
    if not isinstance(atleta, dict):
        return 0
    pontos = int(atleta.get("pontos_ranking", atleta.get("pontos", 0)) or 0)
    overall = int(atleta.get("overall", 50) or 50)
    return pontos * 2 + overall * 25


def forca_duplas(atleta):
    """Score para escalar duplas (ranking de duplas + voleio + atributo duplas)."""
    if not isinstance(atleta, dict):
        return 0
    pontos_duplas = int(
        atleta.get("pontos_ranking_duplas", atleta.get("pontos_duplas", 0)) or 0
    )
    atributos = (
        atleta.get("atributos", {}) if isinstance(atleta.get("atributos"), dict) else {}
    )
    voleio = int(atributos.get("voleio", 50) or 50)
    saque = int(atributos.get("vel_saque", 50) or 50)
    duplas_attr = int(atributos.get("duplas", 60) or 60)
    return pontos_duplas * 3 + voleio * 20 + saque * 12 + duplas_attr * 15


# ---------------------------------------------------------------------------
# Simulação NPC
# ---------------------------------------------------------------------------


def simular_confronto_npc(
    equipe_a,
    equipe_b,
    alvo_vitorias,
    estado,
    ranking,
    genero,
    paises_iguais_fn,
    info_local_fn,
):
    """
    Simula um confronto NPC baseado no overall das equipes e vantagem de casa.

    Parâmetros:
        equipe_a, equipe_b  — identificadores de país.
        alvo_vitorias       — vitórias necessárias para vencer o tie.
        estado              — dicionário de estado carregado.
        ranking             — instância de SistemaRanking.
        genero              — "masculino" ou "feminino".
        paises_iguais_fn    — callable(pais1, pais2) → bool.
        info_local_fn       — callable(modo_competicao, ea, eb) → dict|None.

    Retorna dicionário com equipe_a/b, vencedor, placar, partidas, cidade,
    pais_sede, superficie.
    """
    total_partidas = 5 if alvo_vitorias == 3 else 3
    v_a = 0
    v_b = 0

    local_info = info_local_fn(estado.get("modo_competicao"), equipe_a, equipe_b) or {}

    ovr_a = 65
    ovr_b = 65
    sel_a = None
    sel_b = None

    try:
        sel_a = SelecaoNacional(equipe_a, ranking, genero=genero)
        sel_a.completar_convocacao(2)
        ovr_a = sum(j.get("overall", 65) for j in sel_a.convocados[:2]) / 2

        sel_b = SelecaoNacional(equipe_b, ranking, genero=genero)
        sel_b.completar_convocacao(2)
        ovr_b = sum(j.get("overall", 65) for j in sel_b.convocados[:2]) / 2
    except Exception:
        pass

    # Bônus de especialidade de superfície.
    sup_raw = local_info.get("superficie", "hard").lower()
    if "saibro" in sup_raw:
        sup_key = "saibro"
    elif "grama" in sup_raw:
        sup_key = "grama"
    else:
        sup_key = "hard"

    def _bonus_sup(convocados, key):
        vals = [
            (c.get("especialidade_superficie") or {}).get(key, 70)
            for c in convocados[:2]
        ]
        return sum(v - 70 for v in vals) * 0.12 if vals else 0

    if sel_a is not None:
        ovr_a += _bonus_sup(sel_a.convocados, sup_key)
    if sel_b is not None:
        ovr_b += _bonus_sup(sel_b.convocados, sup_key)

    # Bônus de casa apenas nos qualifiers (equipe_a é mandante no tie oficial).
    if estado.get("fase_atual") == "qualifiers":
        ovr_a += 3

    prob_a = 0.5 + (ovr_a - ovr_b) * 0.04
    prob_a = max(0.1, min(0.9, prob_a))

    for _ in range(total_partidas):
        if v_a >= alvo_vitorias or v_b >= alvo_vitorias:
            break
        if random.random() < prob_a:
            v_a += 1
        else:
            v_b += 1

    vencedor = equipe_a if v_a >= alvo_vitorias else equipe_b
    return {
        "equipe_a": equipe_a,
        "equipe_b": equipe_b,
        "vencedor": vencedor,
        "placar": f"{v_a}-{v_b}",
        # Campos explícitos para deixar claro que o placar representa partidas
        # do tie (ex.: 2-1), não sets de uma única partida.
        "placar_tie": f"{v_a}-{v_b}",
        "placar_tipo": "partidas",
        "partidas": [],
        "cidade": local_info.get("cidade"),
        "pais_sede": local_info.get("pais"),
        "superficie": local_info.get("superficie"),
    }


def simular_restante_fase(estado, fase, simular_fn):
    """
    Simula todos os confrontos não disputados de uma fase.

    Parâmetros:
        estado      — dicionário de estado (modificado in-place).
        fase        — nome da fase ("quartas", "semifinal", "final", …).
        simular_fn  — callable(equipe_a, equipe_b, alvo_vitorias) → resultado.
    """
    chave = estado.get("eliminatorias", {}).get(fase, [])
    # Desde 2019 todas as fases usam melhor-de-3 (alvo = 2 vitórias).
    alvo_vitorias = 2
    for confronto in chave:
        if confronto.get("vencedor"):
            continue
        resultado = simular_fn(
            confronto["equipe_a"],
            confronto["equipe_b"],
            alvo_vitorias=alvo_vitorias,
        )
        confronto["vencedor"] = resultado["vencedor"]
        estado.setdefault("resultados_confrontos", []).append(resultado)


def avancar_fase(estado, fase, pais_jogador, paises_iguais_fn):
    """
    Avança o estado do torneio para a próxima fase após completar a atual.

    Modifica ``estado`` in-place.

    Parâmetros:
        estado            — dicionário de estado.
        fase              — fase que acabou de ser disputada.
        pais_jogador      — país do jogador humano.
        paises_iguais_fn  — callable(pais1, pais2) → bool.
    """
    chave_atual = estado.get("eliminatorias", {}).get(fase, [])
    vencedores = [c.get("vencedor") for c in chave_atual if c.get("vencedor")]

    if fase == "quartas":
        if len(vencedores) < 4:
            return
        estado["eliminatorias"]["semifinal"] = [
            {
                "equipe_a": vencedores[0],
                "equipe_b": vencedores[1],
                "vencedor": None,
            },
            {
                "equipe_a": vencedores[2],
                "equipe_b": vencedores[3],
                "vencedor": None,
            },
        ]
        estado["fase_atual"] = "semifinal"
        estado["confronto_atual"] = next(
            (
                c
                for c in estado["eliminatorias"]["semifinal"]
                if paises_iguais_fn(pais_jogador, c["equipe_a"])
                or paises_iguais_fn(pais_jogador, c["equipe_b"])
            ),
            None,
        )
        return

    if fase == "semifinal":
        if len(vencedores) < 2:
            return
        estado["eliminatorias"]["final"] = [
            {"equipe_a": vencedores[0], "equipe_b": vencedores[1], "vencedor": None}
        ]
        estado["fase_atual"] = "final"
        confronto_final = estado["eliminatorias"]["final"][0]
        if paises_iguais_fn(
            pais_jogador, confronto_final["equipe_a"]
        ) or paises_iguais_fn(pais_jogador, confronto_final["equipe_b"]):
            estado["confronto_atual"] = confronto_final
        else:
            estado["confronto_atual"] = None
        return

    if fase == "final":
        if not vencedores:
            return
        estado["fase_atual"] = "finalizado"
        estado["campeao"] = vencedores[0]
        # Campos usados por distribuir_pontos_davis para bônus de campeão/finalista.
        estado["vencedor_torneio"] = vencedores[0]
        chave_final = estado.get("eliminatorias", {}).get("final", [])
        if chave_final:
            confronto_final = chave_final[0]
            finalista = (
                confronto_final["equipe_b"]
                if paises_iguais_fn(vencedores[0], confronto_final["equipe_a"])
                else confronto_final["equipe_a"]
            )
            estado["finalista_torneio"] = finalista
        estado["confronto_atual"] = None
        estado["jogador_vivo"] = paises_iguais_fn(vencedores[0], pais_jogador)
