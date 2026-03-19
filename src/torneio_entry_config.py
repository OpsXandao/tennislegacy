from src.torneio_constants import (
    RANKING_TOP_20,
    RANKING_TOP_35,
    RANKING_TOP_50,
    RANKING_TOP_60,
)

ENTRY_DIRECT_CONFIGS = {
    "ATP 250": {
        "max_top20": 2,
        "min_top20": 0,
        "usa_top50": False,
        "fracao_top50": 0.0,
        "pesos_top20": lambda top20: [1.0 for _ in top20],
        "pesos_top50": lambda top50: [1.0 for _ in top50],
        "pesos_mid": lambda mid: [1.0 for _ in mid],
        "peso_mid_por_posicao": lambda pos: (
            1.0 if pos <= RANKING_TOP_35 else (1.3 if pos <= RANKING_TOP_60 else 1.6)
        ),
        "peso_pool80_por_posicao": lambda pos: (
            1.0 if pos <= RANKING_TOP_35 else (1.3 if pos <= RANKING_TOP_60 else 1.6)
        ),
    },
    "ATP 500": {
        "max_top20": 4,
        "min_top20": 1,
        "usa_top50": True,
        "fracao_top50": 0.7,
        "pesos_top20": lambda top20: [1.2 for _ in top20],
        "pesos_top50": lambda top50: [1.6 for _ in top50],
        "pesos_mid": lambda mid: [1.1 for _ in mid],
        "peso_mid_por_posicao": lambda pos: 1.1,
        "peso_pool80_por_posicao": lambda pos: (
            1.2 if pos <= RANKING_TOP_20 else (1.6 if pos <= RANKING_TOP_50 else 1.1)
        ),
    },
    "Challenger 125": {
        "max_top20": 0,
        "min_top20": 0,
        "usa_top50": False,
        "fracao_top50": 0.0,
        "pesos_top20": lambda top20: [0.2 for _ in top20],
        "pesos_top50": lambda top50: [0.5 for _ in top50],
        "pesos_mid": lambda mid: [1.0 for _ in mid],
        "peso_mid_por_posicao": lambda pos: (
            0.7 if pos <= RANKING_TOP_50 else (0.9 if pos <= RANKING_TOP_60 else 1.5)
        ),
        "peso_pool80_por_posicao": lambda pos: (
            0.4 if pos <= RANKING_TOP_50 else (0.8 if pos <= 100 else 1.7)
        ),
    },
    "ITF 100": {
        "max_top20": 0,
        "min_top20": 0,
        "usa_top50": False,
        "fracao_top50": 0.0,
        "pesos_top20": lambda top20: [0.0 for _ in top20],
        "pesos_top50": lambda top50: [0.1 for _ in top50],
        "pesos_mid": lambda mid: [1.0 for _ in mid],
        "peso_mid_por_posicao": lambda pos: (
            0.2 if pos <= RANKING_TOP_60 else (0.5 if pos <= 100 else 1.8)
        ),
        "peso_pool80_por_posicao": lambda pos: (
            0.1 if pos <= 100 else (0.8 if pos <= 200 else 1.9)
        ),
    },
    "ITF 25": {
        "max_top20": 0,
        "min_top20": 0,
        "usa_top50": False,
        "fracao_top50": 0.0,
        "pesos_top20": lambda top20: [0.0 for _ in top20],
        "pesos_top50": lambda top50: [0.0 for _ in top50],
        "pesos_mid": lambda mid: [1.0 for _ in mid],
        "peso_mid_por_posicao": lambda pos: (
            0.0 if pos <= 100 else (0.6 if pos <= 200 else 2.0)
        ),
        "peso_pool80_por_posicao": lambda pos: (
            0.0 if pos <= 100 else (0.5 if pos <= 200 else 2.1)
        ),
    },
}
