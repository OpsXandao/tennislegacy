# --- Atributos Padrão ---
DEFAULT_ATRIBUTOS = {
    "saque": 60,
    "forehand": 60,
    "backhand": 60,
    "topspin": 60,
    "voleio": 60,
    "slice": 60,
    "movimento": 60,
    "lob": 60,
    "fisico": 60,
    "winner": 60,
    "duplas": 60,
}

DEFAULT_ATRIBUTOS_PSICOLOGICOS = {
    "concentracao": 50,
    "agressividade": 50,
    "leitura_de_jogo": 50,
    "determinacao": 50,
}

# --- Arquétipos Mentais ---
MENTAL_ARCHETYPES = {
    "1": {
        "nome": "Gelo nas Veias",
        "descricao": "Foco imperturbável e calma sob pressão.",
        "atributos": {
            "concentracao": 75,
            "agressividade": 40,
            "leitura_de_jogo": 60,
            "determinacao": 65,
        },
    },
    "2": {
        "nome": "Guerreiro",
        "descricao": "Nunca desiste de uma bola e luta até o fim.",
        "atributos": {
            "concentracao": 55,
            "agressividade": 50,
            "leitura_de_jogo": 50,
            "determinacao": 85,
        },
    },
    "3": {
        "nome": "Agressivo",
        "descricao": "Busca o winner e dita o ritmo, mas corre riscos.",
        "atributos": {
            "concentracao": 50,
            "agressividade": 80,
            "leitura_de_jogo": 45,
            "determinacao": 65,
        },
    },
    "4": {
        "nome": "Estrategista",
        "descricao": "Lê o adversário perfeitamente e antecipa jogadas.",
        "atributos": {
            "concentracao": 60,
            "agressividade": 45,
            "leitura_de_jogo": 80,
            "determinacao": 55,
        },
    },
    "5": {
        "nome": "Equilibrado",
        "descricao": "Mentalidade sólida em todas as áreas.",
        "atributos": {
            "concentracao": 60,
            "agressividade": 60,
            "leitura_de_jogo": 60,
            "determinacao": 60,
        },
    },
}

# --- Arquétipos de Jogador ---
ARCHETYPES = {
    "1": {
        "nome": "Técnico",
        "descricao": "Mais controle e precisão",
        "atributos": {
            "saque": 65,
            "forehand": 75,
            "backhand": 75,
            "topspin": 72,
            "voleio": 65,
            "slice": 72,
            "movimento": 68,
            "lob": 74,
            "fisico": 64,
            "winner": 70,
            "duplas": 60,
        },
    },
    "2": {
        "nome": "Físico",
        "descricao": "Mais força e movimentação",
        "atributos": {
            "saque": 75,
            "forehand": 72,
            "backhand": 70,
            "topspin": 68,
            "voleio": 60,
            "slice": 62,
            "movimento": 78,
            "lob": 65,
            "fisico": 80,
            "winner": 70,
            "duplas": 60,
        },
    },
    "3": {
        "nome": "Equilibrado",
        "descricao": "Tudo balanceado",
        "atributos": {
            "saque": 70,
            "forehand": 70,
            "backhand": 70,
            "topspin": 70,
            "voleio": 70,
            "slice": 70,
            "movimento": 70,
            "lob": 70,
            "fisico": 70,
            "winner": 70,
            "duplas": 60,
        },
    },
}

# --- Fases de Torneio (T17) ---
FASES_NOMES = {
    "qualy_1": "1ª Rodada Quali",
    "qualy_2": "2ª Rodada Quali",
    "qualy_r1": "1ª Rodada Quali",
    "qualy_r2": "2ª Rodada Quali",
    "qualy_r3": "3ª Rodada Quali",
    "pre_oitavas": "32 avos",
    "oitavas": "Oitavas",
    "quartas": "Quartas",
    "semifinal": "Semifinal",
    "final": "Final",
    "campeao": "Campeão",
    "r128": "1ª Rodada",
    "r96": "1ª Rodada",
    "r64": "2ª Rodada",
    "r32": "3ª Rodada",
    "r16": "Oitavas",
}
