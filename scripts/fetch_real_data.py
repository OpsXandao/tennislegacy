from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.append(os.getcwd())

from src.utils.nome_utils import normalizar_nome

ROOT = Path(__file__).resolve().parents[1]
DB_MASTER = ROOT / "db" / "master"
CACHE_DIR = ROOT / "tmp" / "scraping_cache"
LOCAL_SACKMANN_DIRS = {
    "atp": ROOT / "JeffSackmann" / "tennis_atp-master",
    "wta": ROOT / "JeffSackmann" / "tennis_wta-master",
}
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_PARSE = "https://en.wikipedia.org/w/api.php"
RAW_GITHUB = "https://raw.githubusercontent.com/JeffSackmann"
USER_AGENT = "tennislegacy-scraper/1.0"

TITLE_FIELDS = ("height", "weight", "plays")

ATP_500_NAMES = {
    "acapulco",
    "barcelona",
    "basel",
    "beijing",
    "dubai",
    "halle",
    "hamburg",
    "london",
    "queens club",
    "queen's club",
    "rio de janeiro",
    "tokyo",
    "vienna",
    "washington",
    "astana",
    "rotterdam",
    "dallas",
    "mexican open",
    "china open",
    "japan open",
    "rio open",
}

WTA_1000_NAMES = {
    "indian wells",
    "miami",
    "madrid",
    "rome",
    "canadian open",
    "rogers cup",
    "national bank open",
    "cincinnati",
    "beijing",
    "china open",
    "wuhan",
    "doha",
    "dubai",
}

WTA_500_NAMES = {
    "adelaide",
    "abu dhabi",
    "berlin",
    "brisbane",
    "charleston",
    "eastbourne",
    "guadalajara",
    "linz",
    "monterrey",
    "san diego",
    "seoul",
    "strasbourg",
    "stuttgart",
    "tokyo",
    "washington",
    "zhengzhou",
    "pan pacific open",
    "toronto",
    "montreal",
}

WTA_250_NAMES = {
    "auckland",
    "austin",
    "bogota",
    "cleveland",
    "cluj-napoca",
    "hong kong",
    "hobart",
    "hua hin",
    "istanbul",
    "lyon",
    "monastir",
    "nottingham",
    "palermo",
    "parma",
    "rabat",
    "rouen",
    "prague",
    "budapest",
    "hamburg",
    "lausanne",
}


def slugify_nome(nome: str) -> str:
    bruto = normalizar_nome(nome)
    limpo = re.sub(r"[^a-z0-9]+", "_", bruto)
    return limpo.strip("_")


def ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def resolve_local_sackmann_dir(tour: str) -> Path | None:
    directory = LOCAL_SACKMANN_DIRS[tour]
    if directory.exists():
        return directory
    return None


def cached_get_text(session: Any, url: str, refresh: bool = False) -> str:
    ensure_cache_dir()
    filename = slugify_nome(url)
    cache_path = CACHE_DIR / f"{filename}.cache"
    if cache_path.exists() and not refresh:
        return cache_path.read_text(encoding="utf-8")

    response = session.get(url, timeout=30)
    response.raise_for_status()
    cache_path.write_text(response.text, encoding="utf-8")
    return response.text


def fetch_csv_rows(session: Any, url: str, refresh: bool = False) -> list[dict[str, str]]:
    text = cached_get_text(session, url, refresh=refresh)
    return list(csv.DictReader(text.splitlines()))


def fetch_csv_rows_from_source(
    session: Any,
    source: str | Path,
    refresh: bool = False,
) -> list[dict[str, str]]:
    if isinstance(source, Path):
        return list(csv.DictReader(source.read_text(encoding="utf-8").splitlines()))
    if session is None:
        raise FileNotFoundError(f"Arquivo local ausente e sessão HTTP indisponível para: {source}")
    return fetch_csv_rows(session, source, refresh=refresh)


def parse_height_cm(raw: str | None) -> int | None:
    if not raw:
        return None
    text = raw.replace(",", ".")
    match_cm = re.search(r"(\d{3})\s*cm", text, re.IGNORECASE)
    if match_cm:
        return int(match_cm.group(1))
    match_m = re.search(r"(\d(?:\.\d+)?)\s*m", text, re.IGNORECASE)
    if match_m:
        return int(round(float(match_m.group(1)) * 100))
    match_ft = re.search(r"(\d)\s*ft\s*(\d{1,2})", text, re.IGNORECASE)
    if match_ft:
        feet = int(match_ft.group(1))
        inches = int(match_ft.group(2))
        return int(round(((feet * 12) + inches) * 2.54))
    return None


def parse_weight_kg(raw: str | None) -> int | None:
    if not raw:
        return None
    text = raw.replace(",", ".")
    match_kg = re.search(r"(\d{2,3})\s*kg", text, re.IGNORECASE)
    if match_kg:
        return int(match_kg.group(1))
    match_lb = re.search(r"(\d{2,3})\s*lb", text, re.IGNORECASE)
    if match_lb:
        return int(round(int(match_lb.group(1)) * 0.453592))
    return None


def parse_plays(raw: str | None, genero: str = "masculino") -> tuple[str | None, str | None]:
    if not raw:
        return None, None
    text = raw.strip().lower()
    dominant = None
    backhand = None

    if "right" in text:
        dominant = "Destra" if genero == "feminino" else "Destro"
    elif "left" in text:
        dominant = "Canhota" if genero == "feminino" else "Canhoto"

    if "two-handed" in text or "two handed" in text:
        backhand = "Duas mãos"
    elif "one-handed" in text or "one handed" in text:
        backhand = "Uma mão"

    return dominant, backhand


def parse_hand_code(raw: str | None, genero: str = "masculino") -> str | None:
    text = (raw or "").strip().upper()
    if text == "R":
        return "Destra" if genero == "feminino" else "Destro"
    if text == "L":
        return "Canhota" if genero == "feminino" else "Canhoto"
    return None


def infer_style_from_summary(summary: str | None, current_style: str | None = None) -> str:
    text = (summary or "").lower()
    if "all-court" in text:
        return "All-court"
    if "aggressive baseliner" in text:
        return "Aggressive Baseliner"
    if "baseliner" in text:
        return "Baselines Aggressive"
    if "serve-and-volley" in text or "serve and volley" in text:
        return "Serve-and-volley"
    return current_style or "All-court"


def normalize_tourney_name(name: str) -> str:
    text = normalizar_nome(name or "")
    text = text.replace("atp masters 1000", "").replace("wta 1000", "")
    text = text.replace("presented by", "").replace("open", " open")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def classify_title_category(tour: str, row: dict[str, str]) -> str | None:
    level = (row.get("tourney_level") or "").strip().upper()
    name = normalize_tourney_name(row.get("tourney_name", ""))

    if "olympic" in name:
        return "Olympics"
    if level == "G":
        return "Grand Slam"
    if level == "M" or level == "PM":
        return f"{tour.upper()} 1000"
    if level == "F":
        return f"{tour.upper()} Finals"

    if tour == "atp":
        if any(alias in name for alias in ATP_500_NAMES):
            return "ATP 500"
        return "ATP 250"

    # WTA logic
    if any(alias in name for alias in WTA_1000_NAMES):
        return "WTA 1000"
    if level == "P" or any(alias in name for alias in WTA_500_NAMES):
        return "WTA 500"
    if level == "I" or any(alias in name for alias in WTA_250_NAMES):
        return "WTA 250"
    return "WTA 250"


def wikipedia_search_title(session: Any, nome: str, refresh: bool = False) -> str | None:
    ensure_cache_dir()
    cache_path = CACHE_DIR / f"wiki-search-{slugify_nome(nome)}.json"
    if cache_path.exists() and not refresh:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
        return payload.get("title")

    params = {
        "action": "query",
        "list": "search",
        "srsearch": f'"{nome}" tennis',
        "format": "json",
        "utf8": 1,
    }
    try:
        response = session.get(WIKIPEDIA_API, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        results = payload.get("query", {}).get("search", [])
        title = results[0]["title"] if results else None
    except Exception:
        title = None

    cache_path.write_text(json.dumps({"title": title}, ensure_ascii=False), encoding="utf-8")
    return title


def wikipedia_parse_infobox(session: Any, title: str, refresh: bool = False) -> dict[str, str]:
    from bs4 import BeautifulSoup

    ensure_cache_dir()
    cache_path = CACHE_DIR / f"wiki-parse-{slugify_nome(title)}.json"
    if cache_path.exists() and not refresh:
        return json.loads(cache_path.read_text(encoding="utf-8"))

    params = {
        "action": "parse",
        "page": title,
        "prop": "text",
        "format": "json",
    }
    try:
        response = session.get(WIKIPEDIA_PARSE, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        html = payload.get("parse", {}).get("text", {}).get("*", "")
    except Exception:
        html = ""

    soup = BeautifulSoup(html, "lxml")
    infobox = soup.select_one("table.infobox")
    result: dict[str, str] = {}
    summary_text = soup.get_text(" ", strip=True)

    if infobox:
        for row in infobox.select("tr"):
            header = row.find("th")
            value = row.find("td")
            if not header or not value:
                continue
            key = normalizar_nome(header.get_text(" ", strip=True))
            text = value.get_text(" ", strip=True)
            if any(field in key for field in TITLE_FIELDS):
                result[key] = text

    result["summary"] = summary_text[:2000]
    cache_path.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    return result


def fetch_bio_from_wikipedia(session: Any, nome: str, genero: str = "masculino", refresh: bool = False) -> dict[str, Any]:
    title = wikipedia_search_title(session, nome, refresh=refresh)
    if not title:
        return {}
    parsed = wikipedia_parse_infobox(session, title, refresh=refresh)
    dominant, backhand = parse_plays(parsed.get("plays"), genero=genero)
    return {
        "altura": parse_height_cm(parsed.get("height")),
        "peso": parse_weight_kg(parsed.get("weight")),
        "mao_dominante": dominant,
        "reves": backhand,
        "estilo_jogo": infer_style_from_summary(parsed.get("summary")),
        "fonte_bio": f"Wikipedia:{title}",
    }


def build_local_player_bio_index(tour: str) -> dict[str, dict[str, Any]]:
    local_dir = resolve_local_sackmann_dir(tour)
    if not local_dir:
        return {}

    players_path = local_dir / ("atp_players.csv" if tour == "atp" else "wta_players.csv")
    if not players_path.exists():
        return {}

    genero = "feminino" if tour == "wta" else "masculino"
    rows = fetch_csv_rows_from_source(None, players_path)
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        full_name = " ".join(
            part.strip()
            for part in (row.get("name_first", ""), row.get("name_last", ""))
            if part and part.strip()
        )
        if not full_name:
            continue
        result[normalizar_nome(full_name)] = {
            "altura": int(row["height"]) if (row.get("height") or "").isdigit() else None,
            "mao_dominante": parse_hand_code(row.get("hand"), genero=genero),
            "fonte_bio": f"Sackmann:{players_path.name}",
        }
    return result


def build_titles_index(
    session: Any,
    tour: str,
    start_year: int,
    end_year: int,
    refresh: bool = False,
) -> dict[str, list[dict[str, Any]]]:
    winners: dict[str, list[dict[str, Any]]] = defaultdict(list)
    prefix = "tennis_atp" if tour == "atp" else "tennis_wta"
    file_prefix = "atp" if tour == "atp" else "wta"
    local_dir = resolve_local_sackmann_dir(tour)

    for year in range(start_year, end_year + 1):
        filename = f"{file_prefix}_matches_{year}.csv"
        local_path = local_dir / filename if local_dir else None
        if local_path and local_path.exists():
            matches_source = local_path
        elif session is not None:
            matches_source = f"{RAW_GITHUB}/{prefix}/master/{filename}"
        else:
            print(f"Pulando {year} ({tour.upper()}): arquivo local ausente.")
            continue

        print(f"Indexando títulos: {year} ({tour.upper()})...")

        try:
            rows = fetch_csv_rows_from_source(session, matches_source, refresh=refresh)
        except Exception as e:
            print(f"Erro ao processar {year}: {e}")
            continue

        for row in rows:
            if (row.get("round") or "").strip().upper() != "F":
                continue
            winner_name = (row.get("winner_name") or "").strip()
            if not winner_name:
                continue
            category = classify_title_category(tour, row)
            if not category:
                continue
            winners[normalizar_nome(winner_name)].append(
                {
                    "nome": row.get("tourney_name", "").strip(),
                    "ano": year,
                    "categoria": category,
                }
            )

    for trophies in winners.values():
        trophies.sort(key=lambda item: (int(item["ano"]), item["nome"]))

    return winners


def update_player_bio(player_data: dict[str, Any], bio: dict[str, Any]) -> bool:
    changed = False
    for field in ("altura", "peso", "mao_dominante", "reves", "estilo_jogo"):
        value = bio.get(field)
        if value in (None, "", 0):
            continue
        # Se for mão dominante, aceita Destro/Destra como equivalentes se já existir um deles
        if field == "mao_dominante":
            curr = player_data.get(field)
            if curr and value[:4] == curr[:4]: # "Destr" match
                continue
        
        if player_data.get(field) != value:
            player_data[field] = value
            changed = True
    return changed


def update_player_titles(
    player_data: dict[str, Any], titles_index: dict[str, list[dict[str, Any]]]
) -> bool:
    nome_norm = normalizar_nome(player_data.get("nome", ""))
    trophies = titles_index.get(nome_norm, [])
    existing = player_data.get("trofeus") or []
    if existing == trophies:
        return False
    player_data["trofeus"] = trophies
    return True


def process_player(
    session: Any,
    path: Path,
    tour: str,
    mode: str,
    local_bio_index: dict[str, dict[str, Any]],
    titles_index: dict[str, list[dict[str, Any]]],
    refresh: bool,
    dry_run: bool,
) -> tuple[bool, list[str]]:
    player = json.loads(path.read_text(encoding="utf-8"))
    changes: list[str] = []
    genero = player.get("genero", "feminino" if tour == "wta" else "masculino")

    if mode in {"bio-local", "bio", "all-local", "all"}:
        local_bio = local_bio_index.get(normalizar_nome(player.get("nome", "")), {})
        if update_player_bio(player, local_bio):
            changes.append("bio_local")
    if mode in {"bio", "all"}:
        try:
            bio = fetch_bio_from_wikipedia(session, player.get("nome", ""), genero=genero, refresh=refresh)
        except Exception:
            bio = {}
        if update_player_bio(player, bio):
            changes.append("bio")

    if mode in {"trofeus", "all-local", "all"}:
        if update_player_titles(player, titles_index):
            changes.append("trofeus")

    if changes and not dry_run:
        path.write_text(json.dumps(player, ensure_ascii=False, indent=2), encoding="utf-8")

    return bool(changes), changes


def iter_player_files(tour: str) -> list[Path]:
    directory = DB_MASTER / tour
    if not directory.exists():
        raise FileNotFoundError(f"Diretório não encontrado: {directory}")
    return sorted(directory.glob("*.json"))


def run(
    tour: str,
    mode: str,
    limit: int | None,
    start_year: int,
    end_year: int,
    refresh: bool,
    dry_run: bool,
) -> None:
    session = None

    titles_index: dict[str, list[dict[str, Any]]] = {}
    local_bio_index: dict[str, dict[str, Any]] = {}
    if mode in {"bio-local", "bio", "all-local", "all"}:
        local_bio_index = build_local_player_bio_index(tour)
    if mode in {"bio", "all"}:
        try:
            import requests
        except ModuleNotFoundError as exc:
            raise SystemExit(
                "Dependência ausente: instale 'requests' para executar scraping de biografia."
            ) from exc
        session = requests.Session()
        session.headers.update({"User-Agent": USER_AGENT})
    if mode in {"trofeus", "all-local", "all"}:
        titles_index = build_titles_index(
            session,
            tour=tour,
            start_year=start_year,
            end_year=end_year,
            refresh=refresh,
        )

    files = iter_player_files(tour)
    if limit:
        files = files[:limit]

    changed_total = 0
    for path in files:
        changed, changes = process_player(
            session=session,
            path=path,
            tour=tour,
            mode=mode,
            local_bio_index=local_bio_index,
            titles_index=titles_index,
            refresh=refresh,
            dry_run=dry_run,
        )
        if changed:
            changed_total += 1
            print(f"[OK] {path.name}: {', '.join(changes)}")
        else:
            # print(f"[SKIP] {path.name}")
            pass

    print(f"Finalizado: {changed_total} arquivos alterados em {tour}.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extrai dados reais de biografia e troféus para db/master."
    )
    parser.add_argument("--tour", choices=["atp", "wta", "ambos"], default="atp")
    parser.add_argument(
        "--mode", choices=["bio-local", "bio", "trofeus", "all-local", "all"], default="all"
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--start-year", type=int, default=2000)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    tours = ["atp", "wta"] if args.tour == "ambos" else [args.tour]
    for tour in tours:
        run(
            tour=tour,
            mode=args.mode,
            limit=args.limit,
            start_year=args.start_year,
            end_year=args.end_year,
            refresh=args.refresh,
            dry_run=args.dry_run,
        )


if __name__ == "__main__":
    main()
