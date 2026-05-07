import os
import json
from pathlib import Path


def shard_players_in_save(save_name):
    save_path = Path("saves") / save_name
    if not save_path.exists():
        print(f"❌ Save {save_name} not found.")
        return

    print(f"🚀 Sharding players for save: {save_name}")

    for genero in ["masculino", "feminino"]:
        tour = "atp" if genero == "masculino" else "wta"
        ranking_file = save_path / f"ranking_{tour}.json"
        if not ranking_file.exists():
            continue

        with open(ranking_file, "r", encoding="utf-8") as f:
            ranking = json.load(f)

        if not ranking or not isinstance(ranking, list):
            continue

        # Se já estiver sharded (checa o primeiro elemento), pula
        if ranking[0].get("is_lean"):
            print(f"⏩ {tour.upper()} ranking already sharded.")
            continue

        players_dir = save_path / "jogadores" / tour
        os.makedirs(players_dir, exist_ok=True)

        ranking_lean = []
        for j in ranking:
            if not isinstance(j, dict):
                continue

            # Salva detalhado
            safe_name = (
                j["nome"].lower().replace(" ", "_").replace("'", "").replace(".", "")
            )
            player_file = players_dir / f"{safe_name}.json"
            with open(player_file, "w", encoding="utf-8") as pf:
                json.dump(j, pf, indent=2, ensure_ascii=False)

            # Cria lean
            lean = {
                "nome": j.get("nome"),
                "nacionalidade": j.get("nacionalidade"),
                "pontos": j.get("pontos", 0),
                "pontos_ranking": j.get("pontos_ranking", 0),
                "overall": j.get("overall", 50),
                "is_lean": True,
            }
            if "pontos_ranking_duplas" in j:
                lean["pontos_ranking_duplas"] = j["pontos_ranking_duplas"]

            ranking_lean.append(lean)

        # Sobrescreve ranking principal com a versão lean
        with open(ranking_file, "w", encoding="utf-8") as f:
            json.dump(ranking_lean, f, indent=2, ensure_ascii=False)

        print(f"✅ Sharded {len(ranking)} {tour.upper()} players.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        shard_players_in_save(sys.argv[1])
    else:
        print("Usage: python shard_players.py <save_name>")
