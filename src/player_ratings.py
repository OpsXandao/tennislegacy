from __future__ import annotations

import math
from typing import Any


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, low: int, high: int) -> int:
    return max(low, min(high, round(value)))


def calcular_overall_base(atributos: dict | None) -> int:
    atributos = atributos or {}

    def _a(chave: str, padrao: int = 60) -> int:
        return _int(atributos.get(chave), padrao)

    tec_avg = (
        _a("voleio") + _a("topspin") + _a("slice") + _a("lob") + _a("winner")
    ) / 5

    ovr = (
        _a("forehand") * 0.25
        + _a("backhand") * 0.25
        + _a("movimento") * 0.20
        + _a("fisico") * 0.15
        + _a("saque") * 0.10
        + tec_avg * 0.05
    )
    return round(ovr)


def overall_por_posicao(posicao: int | None) -> int | None:
    if not posicao or posicao <= 0:
        return None

    anchors = [
        (1, 98),
        (2, 97),
        (5, 95),
        (10, 93),
        (20, 91),
        (50, 89),
        (100, 87),
        (250, 82),
        (500, 78),
        (1000, 73),
        (2000, 68),
    ]

    if posicao <= anchors[0][0]:
        return anchors[0][1]

    for idx in range(1, len(anchors)):
        rank_a, overall_a = anchors[idx - 1]
        rank_b, overall_b = anchors[idx]
        if posicao <= rank_b:
            log_a = math.log10(rank_a)
            log_b = math.log10(rank_b)
            log_p = math.log10(posicao)
            fator = 0.0 if log_b == log_a else (log_p - log_a) / (log_b - log_a)
            return _clamp(overall_a + (overall_b - overall_a) * fator, 58, 98)

    ultimo_rank, ultimo_ovr = anchors[-1]
    excedente = max(0.0, math.log10(posicao) - math.log10(ultimo_rank))
    return _clamp(ultimo_ovr - excedente * 8, 55, 98)


def overall_por_pontos(pontos: int | None) -> int | None:
    pontos = _int(pontos, 0)
    if pontos <= 0:
        return None
    # Ajustado para dar mais peso a pontuações menores e chegar em 90+ com pontos de Top 10
    return _clamp(58 + math.log10(pontos + 1) * 9.5, 58, 98)


def ajustar_atributo_duplas(jogador: dict) -> bool:
    atributos = jogador.setdefault("atributos", {})
    mudou = False

    if "duplas" not in atributos:
        atributos["duplas"] = 60
        mudou = True

    pontos_duplas = max(
        _int(jogador.get("pontos_ranking_duplas"), 0),
        _int(jogador.get("pontos_duplas"), 0),
    )
    posicao_duplas = _int(jogador.get("rank_duplas") or jogador.get("posicao_duplas"), 0)

    alvo_por_pontos = overall_por_pontos(pontos_duplas)
    alvo_por_rank = overall_por_posicao(posicao_duplas)
    alvo = max(
        atributos.get("duplas", 60),
        (alvo_por_pontos + 3) if alvo_por_pontos is not None else 0,
        (alvo_por_rank + 4) if alvo_por_rank is not None else 0,
    )
    alvo = min(99, int(alvo))

    if atributos.get("duplas", 60) < alvo:
        atributos["duplas"] = alvo
        mudou = True

    return mudou


# ---------------------------------------------------------------------------
# Sistema de bônus de carta (EA FC) — fonte de verdade compartilhada
# entre api/routes/_carta.py e src/jogar_partida.py
# ---------------------------------------------------------------------------

_BONUS_CARTA: dict[str, dict[str, int]] = {
    "lenda": {"concentracao": 5, "determinacao": 5, "leitura_de_jogo": 5},
    "gs": {"concentracao": 3, "determinacao": 3, "saque": 2, "forehand": 2},
    "if": {"forehand": 3, "backhand": 3, "movimento": 2, "concentracao": 2},
    "ds": {"voleio": 5, "duplas": 5, "movimento": 2, "fisico": 2},
    "wk": {"forehand": 3, "backhand": 3, "movimento": 3, "fisico": 3},
}

# Cartas cujo bônus só vale em determinado contexto de modalidade
_CONTEXTO_CARTA: dict[str, str] = {"ds": "duplas"}


def _detectar_tipo_carta(j: dict, ranking_pos: int = 9999) -> str:
    """Retorna o tipo de carta do jogador para fins de bônus de simulação."""
    idade = _int(j.get("idade", 0), 0)
    atributos = j.get("atributos", {}) or {}
    duplas_attr = _int(atributos.get("duplas", 0), 0)

    if idade >= 35 and ranking_pos <= 50:
        return "lenda"
    trofeus = j.get("trofeus", []) or []
    if any("Grand Slam" in str(t.get("categoria", "")) for t in trofeus):
        return "gs"
    historico = j.get("historico_torneios", []) or []
    if any(
        str(e.get("fase", "") or e.get("resultado", "")).lower() == "campeao"
        for e in historico[-8:]
    ):
        return "if"
    if duplas_attr >= 80:
        return "ds"
    if idade <= 21 and ranking_pos <= 200:
        return "wk"
    return "base"


def aplicar_bonus_carta(
    j: dict, ranking_pos: int = 9999, modalidade: str = "simples"
) -> dict:
    """Retorna uma cópia do dict do jogador com os atributos boosted pela carta.

    Não modifica o dict original.  Se não houver bônus aplicável, retorna o
    mesmo objeto sem cópia (fast-path).
    """
    tipo = _detectar_tipo_carta(j, ranking_pos)
    bonus = dict(_BONUS_CARTA.get(tipo, {}))

    contexto = _CONTEXTO_CARTA.get(tipo)
    if contexto and contexto != modalidade:
        bonus = {}

    if not bonus:
        return j

    atributos = dict(j.get("atributos", {}) or {})
    psi = dict(j.get("atributos_psicologicos", {}) or {})
    for k, v in bonus.items():
        if k in atributos:
            atributos[k] = min(99, atributos[k] + v)
        elif k in psi:
            psi[k] = min(99, psi[k] + v)

    j_boosted = dict(j)
    j_boosted["atributos"] = atributos
    j_boosted["atributos_psicologicos"] = psi
    return j_boosted


def calcular_overall_contextual(jogador: dict, ranking_pos: int | None = None) -> int:
    atributos = jogador.get("atributos", {}) or {}
    base = calcular_overall_base(atributos)

    target_rank = overall_por_posicao(_int(ranking_pos, 0))
    pontos_simples = max(
        _int(jogador.get("pontos_ranking"), 0),
        _int(jogador.get("pontos"), 0),
    )
    target_points = overall_por_pontos(pontos_simples)

    targets = [v for v in (target_rank, target_points) if v is not None]
    if not targets:
        return base

    target = max(targets)
    
    # Se o jogador é Top 250, o ranking (target) deve ter muito mais peso que a média técnica (base)
    # Isso evita que jogadores com atributos incompletos pareçam amadores no overall
    if _int(ranking_pos, 9999) <= 250:
        blended = round(base * 0.25 + target * 0.75)
    else:
        blended = round(base * 0.40 + target * 0.60)
        
    return max(target - 2, min(target + 3, blended))
