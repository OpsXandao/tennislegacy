"""
Sistema de cartas estilo EA FC para TennisLegacy.

Tiers base (como ouro/prata/bronze do FIFA):
  iconic  — OVR >= 88
  gold    — OVR >= 75
  silver  — OVR >= 65
  bronze  — OVR < 65

Cartas especiais (override do tier, têm stats boosted):
  LENDA        — idade >= 35 e ranking <= 50       -> +5 concentracao, +5 determinacao, +5 leitura_de_jogo
  GS           — tem título de Grand Slam          -> +3 concentracao, +3 determinacao, +2 saque, +2 forehand
  IF (In Form) — "campeao" no historico_torneios recente (últimos 8) -> +3 forehand, +3 backhand, +2 movimento, +2 concentracao
  DS (Duplas)  — atributos.duplas >= 80            -> +5 voleio, +5 duplas, +2 movimento, +2 fisico
  WK (Wonder Kid) — idade <= 21 e ranking <= 200   -> +3 forehand, +3 backhand, +3 movimento, +3 fisico

Priority: LENDA > GS > IF > DS > WK > base tier
"""

_CORES = {
    "lenda": {
        "cor_primaria": "#C9A84C",
        "cor_secundaria": "#7A5C1E",
        "raridade": "iconic",
    },
    "gs": {
        "cor_primaria": "#FFD700",
        "cor_secundaria": "#B8860B",
        "raridade": "special",
    },
    "if": {
        "cor_primaria": "#00FF88",
        "cor_secundaria": "#007A3D",
        "raridade": "special",
    },
    "ds": {
        "cor_primaria": "#00E5FF",
        "cor_secundaria": "#006080",
        "raridade": "special",
    },
    "wk": {
        "cor_primaria": "#FF6B00",
        "cor_secundaria": "#8B3A00",
        "raridade": "special",
    },
    "iconic": {
        "cor_primaria": "#C9A84C",
        "cor_secundaria": "#7A5C1E",
        "raridade": "iconic",
    },
    "gold": {
        "cor_primaria": "#FFD700",
        "cor_secundaria": "#B8860B",
        "raridade": "gold",
    },
    "silver": {
        "cor_primaria": "#C0C0C0",
        "cor_secundaria": "#808080",
        "raridade": "silver",
    },
    "bronze": {
        "cor_primaria": "#CD7F32",
        "cor_secundaria": "#8B4513",
        "raridade": "bronze",
    },
}

_LABELS = {
    "lenda": "LENDA",
    "gs": "GS",
    "if": "IF",
    "ds": "DS",
    "wk": "WK",
    "iconic": "ICONIC",
    "gold": "GOLD",
    "silver": "SILVER",
    "bronze": "BRONZE",
}

from src.player_ratings import (
    _BONUS_CARTA,
    _CONTEXTO_CARTA,
    calcular_overall_contextual as _ovr_contextual,
)


_CONTEXTO = _CONTEXTO_CARTA


def _calcular_overall_simples(j: dict, ranking_pos: int = 9999) -> int:
    """OVR contextual (atributos + ancoragem por ranking), consistente com o exibido."""
    return _ovr_contextual(j, ranking_pos if ranking_pos < 9999 else None)


def _tier_base(ovr: int) -> str:
    if ovr >= 88:
        return "iconic"
    if ovr >= 75:
        return "gold"
    if ovr >= 65:
        return "silver"
    return "bronze"


def _tem_grand_slam(j: dict) -> bool:
    trofeus = j.get("trofeus", []) or []
    for t in trofeus:
        if "Grand Slam" in str(t.get("categoria", "")):
            return True
    return False


def _esta_in_form(j: dict) -> bool:
    historico = j.get("historico_torneios", []) or []
    recentes = historico[-8:]
    for entrada in recentes:
        fase = str(entrada.get("fase", "") or entrada.get("resultado", "")).lower()
        if fase == "campeao":
            return True
    return False


def carta_jogador(j: dict, ranking_pos: int = 9999) -> dict:
    """
    Retorna o dict de carta EA FC para um jogador.

    Returns:
    {
      "tipo": "lenda",          # lenda | gs | if | ds | wk | iconic | gold | silver | bronze
      "label": "LENDA",         # display label
      "raridade": "iconic",     # iconic | special | gold | silver | bronze
      "cor_primaria": "#C9A84C",
      "cor_secundaria": "#7A5C1E",
      "bonus": {"concentracao": 5, ...},   # dict vazio se tier base
      "contexto": None,          # None = always applies; "duplas" = only in doubles
    }
    """
    idade = int(j.get("idade", 0) or 0)
    atributos = j.get("atributos", {}) or {}
    duplas_attr = int(atributos.get("duplas", 0) or 0)

    # Determinar tipo especial por prioridade: LENDA > GS > IF > DS > WK
    tipo: str | None = None

    if idade >= 35 and ranking_pos <= 50:
        tipo = "lenda"
    elif _tem_grand_slam(j):
        tipo = "gs"
    elif _esta_in_form(j):
        tipo = "if"
    elif duplas_attr >= 80:
        tipo = "ds"
    elif idade <= 21 and ranking_pos <= 200:
        tipo = "wk"

    if tipo is None:
        ovr = _calcular_overall_simples(j, ranking_pos)
        tipo = _tier_base(ovr)
        bonus: dict = {}
    else:
        bonus = dict(_BONUS_CARTA.get(tipo, {}))

    cores = _CORES[tipo]
    return {
        "tipo": tipo,
        "label": _LABELS[tipo],
        "raridade": cores["raridade"],
        "cor_primaria": cores["cor_primaria"],
        "cor_secundaria": cores["cor_secundaria"],
        "bonus": bonus,
        "contexto": _CONTEXTO.get(tipo, None),
    }
