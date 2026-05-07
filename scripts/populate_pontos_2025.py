#!/usr/bin/env python3
"""
populate_pontos_2025.py

Popula o campo pontos_detalhados nos JSONs de db/master/ com dados REAIS
da temporada 2025 (ATP e WTA), extraídos dos repositórios públicos de
Jeff Sackmann (https://github.com/JeffSackmann/).

Uso:
    python3 scripts/populate_pontos_2025.py --tour atp
    python3 scripts/populate_pontos_2025.py --tour wta
    python3 scripts/populate_pontos_2025.py --tour atp --dry-run
    python3 scripts/populate_pontos_2025.py --tour atp --top 500
"""

import argparse
import csv
import io
import json
import os
import re
import sys
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

# ─────────────────────────────────────────────────────────────────────────────
# TABELAS DE PONTOS (espelham pontuacao.py / wta_constants.py)
# ─────────────────────────────────────────────────────────────────────────────

PONTOS = {
    "atp": {
        "Grand Slam": {
            "campeao": 2000,
            "final": 1300,
            "semifinal": 800,
            "quartas": 400,
            "oitavas": 200,
            "r16": 200,
            "r32": 90,
            "r64": 50,
            "r128": 10,
        },
        "ATP 1000": {
            "campeao": 1000,
            "final": 650,
            "semifinal": 400,
            "quartas": 200,
            "oitavas": 100,
            "r16": 100,
            "r32": 50,
            "r64": 30,
        },
        "ATP 500": {
            "campeao": 500,
            "final": 330,
            "semifinal": 200,
            "quartas": 100,
            "oitavas": 50,
            "r16": 50,
            "r32": 25,
        },
        "ATP 250": {
            "campeao": 250,
            "final": 165,
            "semifinal": 100,
            "quartas": 50,
            "oitavas": 25,
            "r16": 25,
            "r32": 13,
        },
        "ATP Finals": {
            "campeao": 1500,
            "final": 1000,
            "semifinal": 500,
            "quartas": 200,
        },
    },
    "wta": {
        "Grand Slam": {
            "campeao": 2000,
            "final": 1300,
            "semifinal": 780,
            "quartas": 430,
            "oitavas": 240,
            "r16": 240,
            "r32": 130,
            "r64": 70,
            "r128": 10,
        },
        "WTA 1000": {
            "campeao": 1000,
            "final": 650,
            "semifinal": 390,
            "quartas": 215,
            "oitavas": 120,
            "r16": 120,
            "r32": 65,
            "r64": 35,
        },
        "WTA 500": {
            "campeao": 500,
            "final": 325,
            "semifinal": 195,
            "quartas": 108,
            "oitavas": 60,
            "r16": 60,
            "r32": 32,
        },
        "WTA 250": {
            "campeao": 250,
            "final": 163,
            "semifinal": 98,
            "quartas": 54,
            "oitavas": 30,
            "r16": 30,
            "r32": 1,
        },
        "WTA Finals": {
            "campeao": 1500,
            "final": 1000,
            "semifinal": 500,
            "quartas": 200,
        },
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# HIERARQUIA DE RODADAS (maior índice = rodada mais avançada)
# ─────────────────────────────────────────────────────────────────────────────

ROUND_ORDER = {
    "R128": 1,
    "R64": 2,
    "R32": 3,
    "R16": 4,
    "QF": 5,
    "SF": 6,
    "F": 7,
    # Round Robin (ATP/WTA Finals) — tratado separadamente
    "RR": 3,
    "SF": 6,  # noqa: F811
}

# Mapeamento de round Sackmann → fase do jogo
ROUND_TO_FASE = {
    "F": {"winner": "campeao", "loser": "final"},
    "SF": {"winner": "semifinal", "loser": "semifinal"},
    "QF": {"winner": "quartas", "loser": "quartas"},
    "R16": {"winner": "oitavas", "loser": "oitavas"},
    "R32": {"winner": "r32", "loser": "r32"},
    "R64": {"winner": "r64", "loser": "r64"},
    "R128": {"winner": "r128", "loser": "r128"},
    "RR": {"winner": "quartas", "loser": "quartas"},
}

# ─────────────────────────────────────────────────────────────────────────────
# MAPEAMENTO: nome Sackmann → {nome_jogo, semana, tipo}
# ─────────────────────────────────────────────────────────────────────────────

ATP_TOURNAMENT_MAP = {
    # Semana 1
    "Brisbane International": {
        "nome": "Brisbane International",
        "semana": 1,
        "tipo": "ATP 250",
    },
    "Hong Kong Open": {"nome": "Hong Kong Open", "semana": 1, "tipo": "ATP 250"},
    # Semana 2
    "ASB Classic": {"nome": "ASB Classic", "semana": 2, "tipo": "ATP 250"},
    "Adelaide International": {
        "nome": "Adelaide International",
        "semana": 2,
        "tipo": "ATP 250",
    },
    # Semana 3
    "Australian Open": {"nome": "Australian Open", "semana": 3, "tipo": "Grand Slam"},
    # Semana 5
    "Open Sud de France": {
        "nome": "Open Sud de France",
        "semana": 5,
        "tipo": "ATP 250",
    },
    "Montpellier": {"nome": "Open Sud de France", "semana": 5, "tipo": "ATP 250"},
    # Semana 6
    "Cordoba Open": {"nome": "Cordoba Open", "semana": 6, "tipo": "ATP 250"},
    "Dallas Open": {"nome": "Dallas Open", "semana": 6, "tipo": "ATP 250"},
    "Open 13": {"nome": "Open 13", "semana": 6, "tipo": "ATP 250"},
    "Marseille": {"nome": "Open 13", "semana": 6, "tipo": "ATP 250"},
    # Semana 7
    "Rotterdam": {"nome": "Rotterdam Open", "semana": 7, "tipo": "ATP 500"},
    "ABN AMRO World Tennis Tournament": {
        "nome": "Rotterdam Open",
        "semana": 7,
        "tipo": "ATP 500",
    },
    "Argentina Open": {"nome": "Argentina Open", "semana": 7, "tipo": "ATP 250"},
    "Delray Beach Open": {
        "nome": "Delray Beach Open",
        "semana": 7,
        "tipo": "ATP 250",
    },
    "Delray Beach": {"nome": "Delray Beach Open", "semana": 7, "tipo": "ATP 250"},
    # Semana 8
    "Rio Open": {"nome": "Rio Open", "semana": 8, "tipo": "ATP 500"},
    "Qatar ExxonMobil Open": {
        "nome": "Qatar Open",
        "semana": 8,
        "tipo": "ATP 250",
    },
    "Doha": {"nome": "Qatar Open", "semana": 8, "tipo": "ATP 250"},
    "Los Cabos Open": {"nome": "Los Cabos Open", "semana": 8, "tipo": "ATP 250"},
    # Semana 9
    "Mexican Open": {"nome": "Mexican Open", "semana": 9, "tipo": "ATP 500"},
    "Acapulco": {"nome": "Mexican Open", "semana": 9, "tipo": "ATP 500"},
    "Dubai": {"nome": "Dubai Tennis Championships", "semana": 9, "tipo": "ATP 500"},
    "Dubai Tennis Championships": {
        "nome": "Dubai Tennis Championships",
        "semana": 9,
        "tipo": "ATP 500",
    },
    "Chile Open": {"nome": "Chile Open", "semana": 9, "tipo": "ATP 250"},
    # Semana 10
    "Indian Wells Masters": {
        "nome": "Indian Wells Open",
        "semana": 10,
        "tipo": "ATP 1000",
    },
    "BNP Paribas Open": {
        "nome": "Indian Wells Open",
        "semana": 10,
        "tipo": "ATP 1000",
    },
    # Semana 12
    "Miami Open": {"nome": "Miami Open", "semana": 12, "tipo": "ATP 1000"},
    # Semana 14
    "US Men's Clay Court Championships": {
        "nome": "U.S. Men's Clay Court Championships",
        "semana": 14,
        "tipo": "ATP 250",
    },
    "Grand Prix Hassan II": {
        "nome": "Grand Prix Hassan II",
        "semana": 14,
        "tipo": "ATP 250",
    },
    "Estoril": {"nome": "Estoril Open", "semana": 14, "tipo": "ATP 250"},
    "Millennium Estoril Open": {
        "nome": "Estoril Open",
        "semana": 14,
        "tipo": "ATP 250",
    },
    # Semana 15
    "Monte Carlo Masters": {
        "nome": "Monte-Carlo Masters",
        "semana": 15,
        "tipo": "ATP 1000",
    },
    "Monte-Carlo Masters": {
        "nome": "Monte-Carlo Masters",
        "semana": 15,
        "tipo": "ATP 1000",
    },
    # Semana 16
    "Barcelona": {"nome": "Barcelona Open", "semana": 16, "tipo": "ATP 500"},
    "Barcelona Open Banc Sabadell": {
        "nome": "Barcelona Open",
        "semana": 16,
        "tipo": "ATP 500",
    },
    "Munich": {"nome": "Bavarian International", "semana": 16, "tipo": "ATP 250"},
    "Bucharest": {"nome": "Romanian Open", "semana": 16, "tipo": "ATP 250"},
    # Semana 17
    "Madrid": {"nome": "Madrid Open", "semana": 17, "tipo": "ATP 1000"},
    "Mutua Madrid Open": {
        "nome": "Madrid Open",
        "semana": 17,
        "tipo": "ATP 1000",
    },
    # Semana 19
    "Rome": {"nome": "Italian Open", "semana": 19, "tipo": "ATP 1000"},
    "Internazionali BNL d'Italia": {
        "nome": "Italian Open",
        "semana": 19,
        "tipo": "ATP 1000",
    },
    # Semana 21
    "Geneva": {"nome": "Geneva Open", "semana": 21, "tipo": "ATP 250"},
    "Lyon": {"nome": "Lyon Open", "semana": 21, "tipo": "ATP 250"},
    # Semana 22
    "Roland Garros": {"nome": "French Open", "semana": 22, "tipo": "Grand Slam"},
    # Semana 24
    "Stuttgart": {"nome": "Stuttgart Open", "semana": 24, "tipo": "ATP 250"},
    "Rosmalen": {
        "nome": "Rosmalen Championships",
        "semana": 24,
        "tipo": "ATP 250",
    },
    # Semana 25
    "Halle": {"nome": "Halle Open", "semana": 25, "tipo": "ATP 500"},
    "Queen's Club": {
        "nome": "Queen's Club Championships",
        "semana": 25,
        "tipo": "ATP 500",
    },
    # Semana 26
    "Mallorca": {
        "nome": "Mallorca Championships",
        "semana": 26,
        "tipo": "ATP 250",
    },
    "Eastbourne": {
        "nome": "Eastbourne International",
        "semana": 26,
        "tipo": "ATP 250",
    },
    # Semana 27
    "Wimbledon": {"nome": "Wimbledon", "semana": 27, "tipo": "Grand Slam"},
    # Semana 29
    "Hamburg": {"nome": "Hamburg Open", "semana": 29, "tipo": "ATP 500"},
    "Bastad": {"nome": "Swedish Open", "semana": 29, "tipo": "ATP 250"},
    "Gstaad": {"nome": "Swiss Open", "semana": 29, "tipo": "ATP 250"},
    "Newport": {"nome": "Hall of Fame Open", "semana": 29, "tipo": "ATP 250"},
    # Semana 30
    "Kitzbuhel": {"nome": "Austrian Open", "semana": 30, "tipo": "ATP 250"},
    "Umag": {"nome": "Croatia Open", "semana": 30, "tipo": "ATP 250"},
    "Atlanta": {"nome": "Atlanta Open", "semana": 30, "tipo": "ATP 250"},
    # Semana 31
    "Washington": {"nome": "Washington Open", "semana": 31, "tipo": "ATP 500"},
    "Citi Open": {"nome": "Washington Open", "semana": 31, "tipo": "ATP 500"},
    # Semana 32
    "Canadian Open": {
        "nome": "Canadian Open",
        "semana": 32,
        "tipo": "ATP 1000",
    },
    "Rogers Cup": {"nome": "Canadian Open", "semana": 32, "tipo": "ATP 1000"},
    "National Bank Open": {
        "nome": "Canadian Open",
        "semana": 32,
        "tipo": "ATP 1000",
    },
    # Semana 33
    "Cincinnati": {
        "nome": "Cincinnati Open",
        "semana": 33,
        "tipo": "ATP 1000",
    },
    "Western & Southern Open": {
        "nome": "Cincinnati Open",
        "semana": 33,
        "tipo": "ATP 1000",
    },
    # Semana 34
    "Winston-Salem": {
        "nome": "Winston-Salem Open",
        "semana": 34,
        "tipo": "ATP 250",
    },
    # Semana 35
    "US Open": {"nome": "US Open", "semana": 35, "tipo": "Grand Slam"},
    # Semana 38
    "Chengdu": {"nome": "Chengdu Open", "semana": 38, "tipo": "ATP 250"},
    "Hangzhou": {"nome": "Hangzhou Open", "semana": 38, "tipo": "ATP 250"},
    # Semana 39
    "China Open": {"nome": "China Open", "semana": 39, "tipo": "ATP 500"},
    "Japan Open": {"nome": "Japan Open", "semana": 39, "tipo": "ATP 500"},
    # Semana 40
    "Shanghai": {"nome": "Shanghai Masters", "semana": 40, "tipo": "ATP 1000"},
    "Shanghai Masters": {
        "nome": "Shanghai Masters",
        "semana": 40,
        "tipo": "ATP 1000",
    },
    # Semana 42
    "Antwerp": {"nome": "European Open", "semana": 42, "tipo": "ATP 250"},
    "Almaty": {"nome": "Almaty Open", "semana": 42, "tipo": "ATP 250"},
    "Stockholm": {"nome": "Stockholm Open", "semana": 42, "tipo": "ATP 250"},
    # Semana 43
    "Basel": {"nome": "Swiss Indoors", "semana": 43, "tipo": "ATP 500"},
    "Vienna": {"nome": "Vienna Open", "semana": 43, "tipo": "ATP 500"},
    # Semana 44
    "Paris Masters": {"nome": "Paris Masters", "semana": 44, "tipo": "ATP 1000"},
    "Paris Indoors": {"nome": "Paris Masters", "semana": 44, "tipo": "ATP 1000"},
    "Rolex Paris Masters": {
        "nome": "Paris Masters",
        "semana": 44,
        "tipo": "ATP 1000",
    },
    # Semana 45
    "Belgrade": {"nome": "Belgrade Open", "semana": 45, "tipo": "ATP 250"},
    "Metz": {"nome": "Moselle Open", "semana": 45, "tipo": "ATP 250"},
    # Semana 46
    "Nitto ATP Finals": {
        "nome": "ATP Finals",
        "semana": 46,
        "tipo": "ATP Finals",
    },
    "ATP Finals": {"nome": "ATP Finals", "semana": 46, "tipo": "ATP Finals"},
}

WTA_TOURNAMENT_MAP = {
    # Semana 1-2
    "Brisbane International": {
        "nome": "Brisbane International",
        "semana": 1,
        "tipo": "WTA 250",
    },
    "Auckland Classic": {"nome": "ASB Classic", "semana": 2, "tipo": "WTA 250"},
    "ASB Classic": {"nome": "ASB Classic", "semana": 2, "tipo": "WTA 250"},
    "Adelaide International": {
        "nome": "Adelaide International",
        "semana": 2,
        "tipo": "WTA 500",
    },
    "Hobart International": {
        "nome": "Hobart International",
        "semana": 2,
        "tipo": "WTA 250",
    },
    # Grand Slams
    "Australian Open": {"nome": "Australian Open", "semana": 3, "tipo": "Grand Slam"},
    "Roland Garros": {"nome": "French Open", "semana": 22, "tipo": "Grand Slam"},
    "Wimbledon": {"nome": "Wimbledon", "semana": 27, "tipo": "Grand Slam"},
    "US Open": {"nome": "US Open", "semana": 35, "tipo": "Grand Slam"},
    # WTA 1000
    "Indian Wells Masters": {
        "nome": "Indian Wells Open",
        "semana": 10,
        "tipo": "WTA 1000",
    },
    "BNP Paribas Open": {
        "nome": "Indian Wells Open",
        "semana": 10,
        "tipo": "WTA 1000",
    },
    "Miami Open": {"nome": "Miami Open", "semana": 12, "tipo": "WTA 1000"},
    "Madrid": {"nome": "Madrid Open", "semana": 17, "tipo": "WTA 1000"},
    "Mutua Madrid Open": {
        "nome": "Madrid Open",
        "semana": 17,
        "tipo": "WTA 1000",
    },
    "Rome": {"nome": "Italian Open", "semana": 19, "tipo": "WTA 1000"},
    "Internazionali BNL d'Italia": {
        "nome": "Italian Open",
        "semana": 19,
        "tipo": "WTA 1000",
    },
    "Canadian Open": {
        "nome": "Canadian Open",
        "semana": 32,
        "tipo": "WTA 1000",
    },
    "Rogers Cup": {"nome": "Canadian Open", "semana": 32, "tipo": "WTA 1000"},
    "National Bank Open": {
        "nome": "Canadian Open",
        "semana": 32,
        "tipo": "WTA 1000",
    },
    "Cincinnati": {"nome": "Cincinnati Open", "semana": 33, "tipo": "WTA 1000"},
    "Western & Southern Open": {
        "nome": "Cincinnati Open",
        "semana": 33,
        "tipo": "WTA 1000",
    },
    "Wuhan Open": {"nome": "Wuhan Open", "semana": 39, "tipo": "WTA 1000"},
    "China Open": {"nome": "China Open", "semana": 39, "tipo": "WTA 1000"},
    # WTA 500
    "Dubai": {"nome": "Dubai Tennis Championships", "semana": 9, "tipo": "WTA 500"},
    "Dubai Tennis Championships": {
        "nome": "Dubai Tennis Championships",
        "semana": 9,
        "tipo": "WTA 500",
    },
    "Stuttgart": {"nome": "Stuttgart Open", "semana": 24, "tipo": "WTA 500"},
    "Eastbourne": {
        "nome": "Eastbourne International",
        "semana": 26,
        "tipo": "WTA 500",
    },
    "Washington": {"nome": "Washington Open", "semana": 31, "tipo": "WTA 500"},
    "Citi Open": {"nome": "Washington Open", "semana": 31, "tipo": "WTA 500"},
    "Seoul": {"nome": "Seoul Open", "semana": 38, "tipo": "WTA 500"},
    "Tokyo": {"nome": "Japan Open", "semana": 39, "tipo": "WTA 500"},
    "Pan Pacific Open": {"nome": "Japan Open", "semana": 39, "tipo": "WTA 500"},
    "Vienna": {"nome": "Vienna Open", "semana": 43, "tipo": "WTA 500"},
    # WTA 250 (outras)
    "Doha": {"nome": "Qatar Open", "semana": 8, "tipo": "WTA 250"},
    "Hua Hin": {"nome": "Hua Hin Open", "semana": 5, "tipo": "WTA 250"},
    # WTA Finals
    "WTA Finals": {"nome": "WTA Finals", "semana": 46, "tipo": "WTA Finals"},
    "Nitto WTA Finals": {"nome": "WTA Finals", "semana": 46, "tipo": "WTA Finals"},
}

# ─────────────────────────────────────────────────────────────────────────────
# URLS DOS DADOS SACKMANN
# ─────────────────────────────────────────────────────────────────────────────

SACKMANN_URLS = {
    "atp": (
        "https://raw.githubusercontent.com/JeffSackmann/"
        "tennis_atp/master/atp_matches_2025.csv"
    ),
    "wta": (
        "https://raw.githubusercontent.com/JeffSackmann/"
        "tennis_wta/master/wta_matches_2025.csv"
    ),
}

# ─────────────────────────────────────────────────────────────────────────────
# UTILITÁRIOS
# ─────────────────────────────────────────────────────────────────────────────


def _remover_acentos(texto):
    """Remove acentos e diacríticos de uma string."""
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalizar_lookup(nome):
    """Normaliza nome para lookup: sem acentos, lowercase, espaços simples."""
    sem_acento = _remover_acentos(nome)
    limpo = re.sub(r"[\s\-\.']+", " ", sem_acento).strip().lower()
    return limpo


def nome_para_chave(nome):
    """Converte nome em chave de dicionário (mesma lógica do filename)."""
    return re.sub(r"\s+", "_", normalizar_lookup(nome))


def _match_tourney(tourney_name, tour):
    """Tenta encontrar o torneio no mapa correspondente ao tour."""
    mapa = ATP_TOURNAMENT_MAP if tour == "atp" else WTA_TOURNAMENT_MAP
    # Tentativa exata primeiro
    if tourney_name in mapa:
        return mapa[tourney_name]
    # Normalizado
    norm = normalizar_lookup(tourney_name)
    for key, val in mapa.items():
        if normalizar_lookup(key) == norm:
            return val
    # Substring (tourney_name contém a chave do mapa)
    for key, val in mapa.items():
        if normalizar_lookup(key) in norm or norm in normalizar_lookup(key):
            return val
    return None


# ─────────────────────────────────────────────────────────────────────────────
# ÍNDICE DE JOGADORES (nome → caminho do arquivo JSON)
# ─────────────────────────────────────────────────────────────────────────────


def construir_indice_jogadores(tour):
    """
    Lê todos os JSONs em db/master/<tour>/ e constrói um dict:
      normalized_name → filepath
    """
    dir_path = os.path.join("db", "master", tour)
    if not os.path.isdir(dir_path):
        raise FileNotFoundError(f"Diretório não encontrado: {dir_path}")

    indice = {}
    for filename in os.listdir(dir_path):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(dir_path, filename)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            nome = data.get("nome", "")
            if nome:
                chave = normalizar_lookup(nome)
                indice[chave] = path
        except (json.JSONDecodeError, OSError):
            pass
    return indice


def buscar_arquivo_jogador(nome_sackmann, indice):
    """Tenta localizar o arquivo JSON do jogador pelo nome do Sackmann."""
    chave = normalizar_lookup(nome_sackmann)
    if chave in indice:
        return indice[chave]
    # Tenta sem sufixo de número (ex: "Novak Djokovic" vs "N. Djokovic")
    # Tenta match parcial com sobrenome
    partes = chave.split()
    if len(partes) >= 2:
        sobrenome = partes[-1]
        candidatos = [k for k in indice if k.endswith(sobrenome)]
        if len(candidatos) == 1:
            return indice[candidatos[0]]
    return None


# ─────────────────────────────────────────────────────────────────────────────
# DOWNLOAD E PARSING DOS DADOS SACKMANN
# ─────────────────────────────────────────────────────────────────────────────


def baixar_csv(tour):
    """Baixa o CSV de matches 2025 do repositório Sackmann."""
    url = SACKMANN_URLS[tour]
    print(f"Baixando dados de: {url}")
    try:
        with urlopen(url, timeout=30) as resp:
            content = resp.read()
            status = getattr(resp, "status", 200)
    except HTTPError as exc:
        raise RuntimeError(f"Falha ao baixar CSV (HTTP {exc.code}): {url}") from exc
    except URLError as exc:
        raise RuntimeError(f"Falha ao baixar CSV ({exc.reason}): {url}") from exc

    if status != 200:
        raise RuntimeError(f"Falha ao baixar CSV (HTTP {status}): {url}")

    print(f"  → {len(content):,} bytes recebidos")
    return content.decode("utf-8")


def parsear_matches(csv_text, tour, top=500):
    """
    Parseia o CSV e retorna um dict:
      player_name → {
          tourney_key → {
              "tourney_info": {...},
              "melhor_round_idx": int,
              "melhor_round": str,
              "is_campeao": bool,
          }
      }
    """
    resultados = {}  # nome → {tourney_key → dados}

    reader = csv.DictReader(io.StringIO(csv_text))
    linhas = list(reader)
    print(f"  → {len(linhas):,} partidas encontradas no CSV")

    for row in linhas:
        tourney_name = row.get("tourney_name", "").strip()
        round_code = row.get("round", "").strip()
        winner_name = row.get("winner_name", "").strip()
        loser_name = row.get("loser_name", "").strip()

        if not tourney_name or not round_code or not winner_name:
            continue

        tourney_info = _match_tourney(tourney_name, tour)
        if tourney_info is None:
            continue  # torneio não mapeado (Davis Cup, challenger, etc.)

        tourney_key = f"{tourney_info['nome']}_{tourney_info['semana']}"
        round_idx = ROUND_ORDER.get(round_code, 0)
        if round_idx == 0:
            continue  # round desconhecido

        # Atualiza o resultado do vencedor
        for nome in [winner_name, loser_name]:
            if not nome:
                continue
            if nome not in resultados:
                resultados[nome] = {}
            if tourney_key not in resultados[nome]:
                resultados[nome][tourney_key] = {
                    "tourney_info": tourney_info,
                    "melhor_round_idx": 0,
                    "melhor_round": "",
                    "is_campeao": False,
                }

        # Vencedor: avança para a próxima rodada — só atualiza se for maior
        atual_w = resultados[winner_name][tourney_key]
        if round_idx > atual_w["melhor_round_idx"]:
            atual_w["melhor_round_idx"] = round_idx
            atual_w["melhor_round"] = round_code
        if round_code == "F":
            atual_w["is_campeao"] = True

        # Perdedor: marca a rodada em que perdeu (se for maior que atual)
        if loser_name:
            atual_l = resultados[loser_name][tourney_key]
            if round_idx > atual_l["melhor_round_idx"]:
                atual_l["melhor_round_idx"] = round_idx
                atual_l["melhor_round"] = round_code

    print(f"  → {len(resultados):,} jogadores únicos encontrados")
    return resultados


# ─────────────────────────────────────────────────────────────────────────────
# CÁLCULO DE PONTOS
# ─────────────────────────────────────────────────────────────────────────────


def calcular_fase(round_code, is_campeao, tipo_torneio, tour):
    """Retorna a fase do jogo correspondente à rodada Sackmann."""
    if round_code == "F" and is_campeao:
        return "campeao"

    mapa = ROUND_TO_FASE.get(round_code)
    if mapa is None:
        return None

    fase = mapa["winner"] if is_campeao else mapa["loser"]

    # Ajuste para torneios menores que não têm r64/r128
    tabela = PONTOS.get(tour, {}).get(tipo_torneio, {})
    if fase not in tabela:
        # Tenta versões alternativas
        for alt in ["oitavas", "r16", "r32", "quartas"]:
            if alt in tabela:
                return alt
        return None

    return fase


def calcular_pontos(fase, tipo_torneio, tour):
    """Retorna os pontos para uma fase/tipo de torneio/tour."""
    tabela = PONTOS.get(tour, {}).get(tipo_torneio, {})
    return tabela.get(fase, 0)


# ─────────────────────────────────────────────────────────────────────────────
# GERAÇÃO DA ENTRADA pontos_detalhados
# ─────────────────────────────────────────────────────────────────────────────


def gerar_entradas_pontos(resultados_jogador, tour):
    """
    Recebe o dict de resultados de um jogador e gera a lista
    de pontos_detalhados no formato do jogo.
    """
    entradas = []
    for tourney_key, dados in resultados_jogador.items():
        info = dados["tourney_info"]
        tipo = info["tipo"]
        semana = info["semana"]
        nome_torneio = info["nome"]
        round_code = dados["melhor_round"]
        is_campeao = dados["is_campeao"]

        fase = calcular_fase(round_code, is_campeao, tipo, tour)
        if fase is None:
            continue

        pts = calcular_pontos(fase, tipo, tour)
        if pts <= 0:
            continue

        entradas.append(
            {
                "pontos": pts,
                "semana_expiracao": semana,
                "ano_expiracao": 2026,
                "semana_origem": semana,
                "ano_origem": 2025,
                "torneio": nome_torneio,
                "tipo": tipo,
                "fase": fase,
                "modalidade": "simples",
            }
        )

    return entradas


# ─────────────────────────────────────────────────────────────────────────────
# PROCESSAMENTO PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────


def processar(tour, top=500, dry_run=False):
    """Fluxo principal: baixa dados, processa, atualiza JSONs."""
    print(f"\n{'='*60}")
    print(f"Processando circuito: {tour.upper()}")
    print(f"{'='*60}")

    # 1. Baixar e parsear CSV
    csv_text = baixar_csv(tour)
    resultados = parsear_matches(csv_text, tour, top=top)

    # 2. Construir índice de jogadores
    print("\nConstruindo índice de jogadores...")
    indice = construir_indice_jogadores(tour)
    print(f"  → {len(indice):,} arquivos JSON indexados")

    # 3. Atualizar JSONs
    atualizados = 0
    nao_encontrados = []
    sem_pontos = 0

    for nome_sackmann, res_torneios in resultados.items():
        filepath = buscar_arquivo_jogador(nome_sackmann, indice)
        if filepath is None:
            nao_encontrados.append(nome_sackmann)
            continue

        entradas = gerar_entradas_pontos(res_torneios, tour)
        if not entradas:
            sem_pontos += 1
            continue

        total_pontos = sum(e["pontos"] for e in entradas)

        if dry_run:
            print(
                f"  [DRY-RUN] {nome_sackmann}: "
                f"{len(entradas)} torneios, {total_pontos} pts"
            )
            atualizados += 1
            continue

        # Lê o arquivo existente
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"  ERRO ao ler {filepath}: {e}")
            continue

        # Atualiza apenas os campos de pontos 2025
        data["pontos_detalhados"] = entradas
        data["pontos_ranking"] = total_pontos
        data["pontos"] = total_pontos

        # Escreve de volta
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            atualizados += 1
        except OSError as e:
            print(f"  ERRO ao escrever {filepath}: {e}")

    print(f"\n{'─'*40}")
    print(f"Resultado {tour.upper()}:")
    print(f"  Atualizados:      {atualizados}")
    print(f"  Sem pontos:       {sem_pontos}")
    print(f"  Não encontrados:  {len(nao_encontrados)}")
    if nao_encontrados[:20]:
        print("  Exemplos não encontrados:")
        for n in nao_encontrados[:20]:
            print(f"    - {n}")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Popula pontos_detalhados com dados reais da temporada 2025."
    )
    parser.add_argument(
        "--tour",
        choices=["atp", "wta", "ambos"],
        default="atp",
        help="Circuito: atp, wta ou ambos (padrão: atp)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=500,
        help="Limite de jogadores pelo ranking (padrão: 500)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula sem escrever arquivos",
    )
    args = parser.parse_args()

    tours = ["atp", "wta"] if args.tour == "ambos" else [args.tour]
    for t in tours:
        processar(tour=t, top=args.top, dry_run=args.dry_run)

    print("\nConcluído!")
