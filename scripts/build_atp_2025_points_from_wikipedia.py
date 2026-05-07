#!/usr/bin/env python3
"""
Monta pontos detalhados de 2025 (ATP simples) a partir da Wikipedia.

Fontes:
- https://en.wikipedia.org/wiki/2025_ATP_Tour
- páginas "2025 <torneio> – Men's singles" linkadas a partir da página acima

Escopo:
- cobre ATP simples
- captura campeão, vice, semifinalistas e quartas diretamente da página da temporada
- complementa resultados de seeds com a seção "Seeds" da página de simples do torneio
- gera blocos `pontos_detalhados` por torneio com expiração em 2026

Uso:
    python3 scripts/build_atp_2025_points_from_wikipedia.py
    python3 scripts/build_atp_2025_points_from_wikipedia.py --output /tmp/atp_2025.json
    python3 scripts/build_atp_2025_points_from_wikipedia.py --apply
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup, Tag

BASE_URL = "https://en.wikipedia.org"
SEASON_URL = f"{BASE_URL}/wiki/2025_ATP_Tour"
DEFAULT_OUTPUT = "artifacts/atp_2025_points_wikipedia.json"
DB_MASTER_ATP_DIR = os.path.join("db", "master", "atp")

MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

POINTS = {
    "Grand Slam": {
        "campeao": 2000,
        "final": 1300,
        "semifinal": 800,
        "quartas": 400,
        "oitavas": 200,
        "r16": 200,
        "r32": 100,
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
        "r128": 10,
    },
    "ATP 500": {
        "campeao": 500,
        "final": 330,
        "semifinal": 200,
        "quartas": 100,
        "oitavas": 50,
        "r16": 50,
        "r32": 25,
        "r64": 10,
    },
    "ATP 250": {
        "campeao": 250,
        "final": 165,
        "semifinal": 100,
        "quartas": 50,
        "oitavas": 25,
        "r16": 25,
        "r32": 13,
        "r64": 5,
    },
    "ATP Finals": {
        "campeao": 1500,
        "final": 1000,
        "semifinal": 500,
        "quartas": 200,
    },
}

PHASE_WEIGHT = {
    "r128": 1,
    "r64": 2,
    "r32": 3,
    "r16": 4,
    "oitavas": 4,
    "quartas": 5,
    "semifinal": 6,
    "final": 7,
    "campeao": 8,
}

SKIP_CATEGORIES = {"Team event", "United Cup", "Davis Cup"}
VALID_CATEGORIES = {"Grand Slam", "ATP 1000", "ATP 500", "ATP 250", "ATP Finals"}


@dataclass
class TournamentResult:
    nome: str
    semana: int
    categoria: str
    singles_url: str | None
    resultados: dict[str, str]


def fetch_html(url: str) -> str:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 TennisLegacy/1.0"})
    try:
        with urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except HTTPError as exc:
        raise RuntimeError(f"Falha ao baixar {url} (HTTP {exc.code})") from exc
    except URLError as exc:
        raise RuntimeError(f"Falha ao baixar {url} ({exc.reason})") from exc


def normalizar_lookup(nome: str) -> str:
    texto = re.sub(r"\s+", " ", nome).strip().lower()
    return (
        texto.replace("’", "'")
        .replace("–", "-")
        .replace("á", "a")
        .replace("à", "a")
        .replace("ã", "a")
        .replace("â", "a")
        .replace("ä", "a")
        .replace("é", "e")
        .replace("è", "e")
        .replace("ê", "e")
        .replace("ë", "e")
        .replace("í", "i")
        .replace("ì", "i")
        .replace("î", "i")
        .replace("ï", "i")
        .replace("ó", "o")
        .replace("ò", "o")
        .replace("õ", "o")
        .replace("ô", "o")
        .replace("ö", "o")
        .replace("ú", "u")
        .replace("ù", "u")
        .replace("û", "u")
        .replace("ü", "u")
        .replace("ç", "c")
        .replace("ñ", "n")
    )


def nome_para_arquivo(nome: str) -> str:
    safe = nome.lower().replace(" ", "_").replace("'", "").replace(".", "")
    safe = safe.replace("-", "_")
    return f"{safe}.json"


def iso_week_from_label(label: str) -> int:
    match = re.search(r"(\d{1,2})\s+([A-Za-z]{3})", label)
    if not match:
        raise ValueError(f"Data semanal inválida: {label}")
    day = int(match.group(1))
    month = MONTHS[match.group(2).lower()]
    year = 2024 if month == 12 else 2025
    return date(year, month, day).isocalendar().week


def limpar_nome_jogador(texto: str) -> str:
    nome = re.sub(r"\[[^\]]+\]", "", texto)
    nome = re.sub(r"\([^)]*\)", "", nome)
    nome = re.sub(r"\s+", " ", nome).strip(" -\n\t")
    return nome


def anchors_to_names(anchors: Iterable[Tag]) -> list[str]:
    nomes = []
    for a in anchors:
        texto = limpar_nome_jogador(a.get_text(" ", strip=True))
        if not texto:
            continue
        if texto in {"Singles", "Doubles", "men", "women"}:
            continue
        nomes.append(texto)
    return nomes


def parse_category(cell_text: str) -> str | None:
    texto = " ".join(cell_text.split())
    if "Grand Slam" in texto:
        return "Grand Slam"
    match = re.search(r"(ATP\s+1000|ATP\s+500|ATP\s+250|ATP\s+Finals)", texto)
    if match:
        return re.sub(r"\s+", " ", match.group(1))
    return None


def merge_phase(resultados: dict[str, str], nome: str, fase: str) -> None:
    nome = limpar_nome_jogador(nome)
    if not nome or fase not in PHASE_WEIGHT:
        return
    atual = resultados.get(nome)
    if not atual or PHASE_WEIGHT[fase] > PHASE_WEIGHT.get(atual, 0):
        resultados[nome] = fase


def parse_season_page() -> list[TournamentResult]:
    soup = BeautifulSoup(fetch_html(SEASON_URL), "lxml")
    torneios: list[TournamentResult] = []

    for table in soup.select("table.wikitable"):
        for row in table.select("tr"):
            cells = row.find_all(["td", "th"])
            if len(cells) < 6:
                continue

            week_text = cells[0].get_text(" ", strip=True)
            if not re.search(r"\d{1,2}\s+[A-Za-z]{3}", week_text):
                continue

            categoria = parse_category(cells[1].get_text(" ", strip=True))
            if categoria in SKIP_CATEGORIES or categoria not in VALID_CATEGORIES:
                continue

            tournament_anchor = None
            singles_anchor = None
            for a in cells[1].find_all("a", href=True):
                label = a.get_text(" ", strip=True)
                href = a["href"]
                if label == "Singles":
                    singles_anchor = a
                elif (
                    not tournament_anchor
                    and href.startswith("/wiki/")
                    and "men%27s_singles" not in href.lower()
                    and "women%27s_singles" not in href.lower()
                    and label not in {"Doubles", "United Cup"}
                ):
                    tournament_anchor = a

            if not tournament_anchor:
                continue

            nome_torneio = limpar_nome_jogador(tournament_anchor.get_text(" ", strip=True))
            semana = iso_week_from_label(week_text)
            resultados: dict[str, str] = {}

            champions = anchors_to_names(cells[2].find_all("a", href=True))
            runners = anchors_to_names(cells[3].find_all("a", href=True))
            semis = anchors_to_names(cells[4].find_all("a", href=True))
            quarters = anchors_to_names(cells[5].find_all("a", href=True))

            if champions:
                merge_phase(resultados, champions[0], "campeao")
            if runners:
                merge_phase(resultados, runners[0], "final")
            for nome in semis[:2]:
                merge_phase(resultados, nome, "semifinal")
            for nome in quarters[:4]:
                merge_phase(resultados, nome, "quartas")

            torneios.append(
                TournamentResult(
                    nome=nome_torneio,
                    semana=semana,
                    categoria=categoria,
                    singles_url=urljoin(BASE_URL, singles_anchor["href"]) if singles_anchor else None,
                    resultados=resultados,
                )
            )

    return torneios


def effective_draw_size(draw_size: int) -> int:
    if draw_size >= 96:
        return 128
    if draw_size >= 48:
        return 64
    return 32


def parse_round_phase(label: str, draw_size: int) -> str | None:
    texto = label.lower()
    texto = texto.replace(", retired", "").replace(", withdrew", "").strip()

    if texto.startswith("champion"):
        return "campeao"
    if texto.startswith("final"):
        return "final"
    if texto.startswith("semifinal"):
        return "semifinal"
    if texto.startswith("quarterfinal"):
        return "quartas"

    slots = effective_draw_size(draw_size)
    mapa = {
        128: {
            "first round": "r128",
            "second round": "r64",
            "third round": "r32",
            "fourth round": "r16",
        },
        64: {
            "first round": "r64",
            "second round": "r32",
            "third round": "r16",
        },
        32: {
            "first round": "r32",
            "second round": "r16",
        },
    }

    for prefix, fase in mapa[slots].items():
        if texto.startswith(prefix):
            return fase
    return None


def enrich_with_seed_results(torneio: TournamentResult) -> None:
    if not torneio.singles_url:
        return

    soup = BeautifulSoup(fetch_html(torneio.singles_url), "lxml")
    draw_text = soup.get_text(" ", strip=True)
    draw_match = re.search(r"Draw\s+(\d+)", draw_text)
    draw_size = int(draw_match.group(1)) if draw_match else 32

    seed_header = None
    for header in soup.find_all(["h2", "h3"]):
        if "Seeds" in header.get_text(" ", strip=True):
            seed_header = header
            break
    if not seed_header:
        return

    node = seed_header.find_next_sibling()
    while node:
        if isinstance(node, Tag) and node.name in {"h2", "h3"}:
            break
        if isinstance(node, Tag) and node.name == "ul":
            for li in node.find_all("li", recursive=False):
                anchors = li.find_all("a", href=True)
                if not anchors:
                    continue
                nome = limpar_nome_jogador(anchors[-1].get_text(" ", strip=True))
                texto = li.get_text(" ", strip=True)
                match = re.search(r"\(([^()]*)\)\s*$", texto)
                if not match:
                    continue
                fase = parse_round_phase(match.group(1), draw_size)
                if fase:
                    merge_phase(torneio.resultados, nome, fase)
        node = node.find_next_sibling()


def build_player_points(torneios: list[TournamentResult]) -> dict[str, list[dict]]:
    por_jogador: dict[str, list[dict]] = defaultdict(list)
    for torneio in torneios:
        tabela = POINTS.get(torneio.categoria, {})
        for nome, fase in torneio.resultados.items():
            pontos = tabela.get(fase, 0)
            if pontos <= 0:
                continue
            por_jogador[nome].append(
                {
                    "pontos": int(pontos),
                    "torneio": torneio.nome,
                    "tipo": torneio.categoria,
                    "fase": fase,
                    "modalidade": "simples",
                    "semana_origem": int(torneio.semana),
                    "ano_origem": 2025,
                    "semana_expiracao": int(torneio.semana),
                    "ano_expiracao": 2026,
                }
            )
    return dict(por_jogador)


def aplicar_em_db_master(player_points: dict[str, list[dict]]) -> dict[str, int]:
    atualizados = 0
    nao_encontrados = 0

    for nome, entradas in player_points.items():
        path = os.path.join(DB_MASTER_ATP_DIR, nome_para_arquivo(nome))
        if not os.path.exists(path):
            nao_encontrados += 1
            continue
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        total = sum(item["pontos"] for item in entradas)
        data["pontos_detalhados"] = entradas
        data["pontos_ranking"] = total
        data["pontos"] = total

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        atualizados += 1

    return {"atualizados": atualizados, "nao_encontrados": nao_encontrados}


def write_output(path: str, torneios: list[TournamentResult], player_points: dict[str, list[dict]]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    payload = {
        "source": SEASON_URL,
        "scope": "ATP singles 2025",
        "method": "season page + singles seed pages",
        "tournaments": [
            {
                "nome": t.nome,
                "semana": t.semana,
                "categoria": t.categoria,
                "singles_url": t.singles_url,
                "resultados": t.resultados,
            }
            for t in torneios
        ],
        "player_points": player_points,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Monta pontos detalhados ATP 2025 a partir da Wikipedia."
    )
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Arquivo JSON de saída.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica os pontos diretamente em db/master/atp/*.json",
    )
    args = parser.parse_args()

    torneios = parse_season_page()
    for torneio in torneios:
        if torneio.singles_url:
            enrich_with_seed_results(torneio)

    player_points = build_player_points(torneios)
    write_output(args.output, torneios, player_points)

    print(f"Torneios processados: {len(torneios)}")
    print(f"Jogadores com blocos: {len(player_points)}")
    print(f"Saída escrita em: {args.output}")

    if args.apply:
        resumo = aplicar_em_db_master(player_points)
        print(f"Atualizados em db/master/atp: {resumo['atualizados']}")
        print(f"Não encontrados em db/master/atp: {resumo['nao_encontrados']}")


if __name__ == "__main__":
    main()
