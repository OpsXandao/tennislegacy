import os
import json
import shutil
from pathlib import Path


def migrate_ranking_to_doubles(save_path, gender="atp"):
    ranking_file = Path(save_path) / f"ranking_{gender}.json"
    if not ranking_file.exists():
        return

    with open(ranking_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    doubles_data = []
    for player in data:
        # Extract doubles info
        doubles_player = {
            "nome": player.get("nome"),
            "nacionalidade": player.get("nacionalidade"),
            "pontos": player.get("pontos_duplas", 0),
            "pontos_ranking": player.get("pontos_ranking_duplas", 0),
            "pontos_detalhados": player.get("pontos_detalhados_duplas", []),
            "overall": player.get("atributos", {}).get("duplas", 50),
        }
        doubles_data.append(doubles_player)

    doubles_file = Path(save_path) / f"ranking_{gender}_duplas.json"
    with open(doubles_file, "w", encoding="utf-8") as f:
        json.dump(doubles_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Created {doubles_file.name}")


def shard_calendar(save_path, gender="masculino"):
    world_file = Path(save_path) / f"world_tournaments_{gender}.json"
    if not world_file.exists():
        return

    with open(world_file, "r", encoding="utf-8") as f:
        tournaments = json.load(f)

    cal_dir = (
        Path(save_path) / "calendario" / ("atp" if gender == "masculino" else "wta")
    )
    os.makedirs(cal_dir, exist_ok=True)

    for name, data in tournaments.items():
        safe_name = name.lower().replace(" ", "_").replace("'", "").replace(".", "")
        t_file = cal_dir / f"{safe_name}.json"
        with open(t_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Sharded {len(tournaments)} tournaments into {cal_dir}")


def run_migration(save_name):
    save_path = Path("saves") / save_name
    if not save_path.exists():
        print(f"❌ Save {save_name} not found.")
        return

    print(f"🚀 Migrating save: {save_name}")
    migrate_ranking_to_doubles(save_path, "atp")
    migrate_ranking_to_doubles(save_path, "wta")
    shard_calendar(save_path, "masculino")
    shard_calendar(save_path, "feminino")
    print("✨ Migration complete!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        run_migration(sys.argv[1])
    else:
        print("Usage: python migrate_save.py <save_name>")
