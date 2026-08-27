"""
Helpers de física/estado mental para partidas.

Contém as funções que aplicam efeitos de stamina, moral e momentum diretamente
nos objetos de contexto e no jogador — lógica que fica entre a orquestração
(jogar_partida.py) e os cálculos puros (match_dynamics.py).
"""

from __future__ import annotations

import logging

from src.match_dynamics import (
    calcular_impacto_moral_ranking,
    calcular_impacto_moral_sets,
)
from src.match_state import ContextoPartida

logger = logging.getLogger(__name__)


def aplicar_impacto_moral_por_sets(
    jogador, resultado_sets, venceu_partida: bool
) -> None:
    """Calcula e aplica ajuste de moral baseado na diferença de games por set."""
    if not hasattr(jogador, "moral"):
        return
    delta = calcular_impacto_moral_sets(jogador, resultado_sets, venceu_partida)
    if delta == 0:
        return
    moral_antes = int(getattr(jogador, "moral", 70))
    jogador.moral = max(0, min(100, moral_antes + delta))


def aplicar_impacto_mental_set_em_andamento(
    contexto_partida: ContextoPartida, games_j: int, games_a: int
) -> None:
    """Aplica impacto psicológico imediato no momentum após cada set."""
    diff = abs(int(games_j) - int(games_a))
    if diff < 3:
        return

    impacto = 2 if diff >= 5 else 1
    if games_j > games_a:
        contexto_partida.momentum_j = min(6, contexto_partida.momentum_j + impacto)
        contexto_partida.momentum_a = max(0, contexto_partida.momentum_a - impacto)
        logger.debug(
            f"Set dominante aumentou sua confiança para o próximo set (+{impacto} momentum)."
        )
    else:
        contexto_partida.momentum_a = min(6, contexto_partida.momentum_a + impacto)
        contexto_partida.momentum_j = max(0, contexto_partida.momentum_j - impacto)
        logger.debug(
            f"Set encaçapante abalou a confiança para o próximo set (-{impacto} momentum)."
        )


def aplicar_impacto_moral_por_resultado_ranking(
    jogador, adversario, venceu_partida: bool
) -> None:
    """Calcula e aplica ajuste de moral baseado no resultado relativo ao ranking."""
    if not hasattr(jogador, "moral"):
        return
    delta = calcular_impacto_moral_ranking(jogador, adversario, venceu_partida)
    if delta == 0:
        return
    moral_antes = int(getattr(jogador, "moral", 70))
    jogador.moral = max(0, min(100, moral_antes + delta))
