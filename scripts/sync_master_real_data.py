#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.append(os.getcwd())

from scripts.fetch_real_data import (
    build_local_player_bio_index,
    build_titles_index,
    iter_player_files,
    process_player,
)
from src.json_utils import salvar_json_seguro

ROOT = Path(__file__).resolve().parents[1]
DB_DIR = ROOT / "db"
TEMPLATES_DIR = DB_DIR / "templates"


def build_lean_index_entry(player: dict) -> dict:
    trofeus = player.get("trofeus") or []
    ultimo_titulo = trofeus[-1] if trofeus else None
    return {
        "nome": player.get("nome"),
        "nacionalidade": player.get("nacionalidade", "??"),
        "pontos": int(player.get("pontos", 0) or 0),
        "pontos_ranking": int(player.get("pontos_ranking", player.get("pontos", 0)) or 0),
        "pontos_duplas": int(player.get("pontos_duplas", 0) or 0),
        "pontos_ranking_duplas": int(player.get("pontos_ranking_duplas", 0) or 0),
        "pontos_ytd": int(player.get("pontos_ytd", 0) or 0),
        "idade": int(player.get("idade", 0) or 0),
        "titulos_total": len(trofeus),
        "ultimo_titulo_ano": ultimo_titulo.get("ano") if ultimo_titulo else None,
        "is_lean": True,
    }


def rebuild_template_index(tour: str) -> tuple[Path, int]:
    files = iter_player_files(tour)
    entries = []
    for path in files:
        player = json.loads(path.read_text(encoding="utf-8"))
        entries.append(build_lean_index_entry(player))

    entries.sort(key=lambda item: item.get("pontos_ranking", 0), reverse=True)
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = TEMPLATES_DIR / f"npc_index_{tour}.json"
    salvar_json_seguro(str(out_path), entries)
    return out_path, len(entries)


def build_coverage_summary(tour: str) -> dict:
    files = iter_player_files(tour)
    bio_fields = ("altura", "peso", "mao_dominante", "reves", "estilo_jogo")
    bio_complete = 0
    players_with_titles = 0
    titles_total = 0

    for path in files:
        player = json.loads(path.read_text(encoding="utf-8"))
        if all(player.get(field) not in (None, "", 0, []) for field in bio_fields):
            bio_complete += 1

        trophies = player.get("trofeus") or []
        if trophies:
            players_with_titles += 1
            titles_total += len(trophies)

    return {
        "bio_complete": bio_complete,
        "players_with_titles": players_with_titles,
        "titles_total": titles_total,
    }


def sync_tour(
    tour: str,
    include_local_bio: bool,
    include_titles: bool,
    start_year: int,
    end_year: int,
    dry_run: bool,
) -> dict:
    local_bio_index = build_local_player_bio_index(tour) if include_local_bio else {}
    titles_index = (
        build_titles_index(None, tour, start_year, end_year)
        if include_titles
        else {}
    )
    if include_local_bio and include_titles:
        mode = "all-local"
    elif include_local_bio:
        mode = "bio-local"
    else:
        mode = "trofeus"

    changed_total = 0
    files = iter_player_files(tour)
    for path in files:
        changed, _ = process_player(
            session=None,
            path=path,
            tour=tour,
            mode=mode,
            local_bio_index=local_bio_index,
            titles_index=titles_index,
            refresh=False,
            dry_run=dry_run,
        )
        if changed:
            changed_total += 1

    template_path = None
    template_count = 0
    if not dry_run:
        template_path, template_count = rebuild_template_index(tour)

    coverage = build_coverage_summary(tour)

    return {
        "tour": tour,
        "players": len(files),
        "changed": changed_total,
        "template_path": str(template_path) if template_path else None,
        "template_count": template_count,
        "bio_complete": coverage["bio_complete"],
        "players_with_titles": coverage["players_with_titles"],
        "titles_total": coverage["titles_total"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sincroniza db/master com dados locais do Jeff Sackmann e recria índices lean."
    )
    parser.add_argument("--tour", choices=["atp", "wta", "ambos"], default="ambos")
    parser.add_argument("--skip-bio-local", action="store_true")
    parser.add_argument("--skip-titles", action="store_true")
    parser.add_argument("--start-year", type=int, default=2000)
    parser.add_argument("--end-year", type=int, default=2024)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    tours = ["atp", "wta"] if args.tour == "ambos" else [args.tour]
    for tour in tours:
        result = sync_tour(
            tour=tour,
            include_local_bio=not args.skip_bio_local,
            include_titles=not args.skip_titles,
            start_year=args.start_year,
            end_year=args.end_year,
            dry_run=args.dry_run,
        )
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
