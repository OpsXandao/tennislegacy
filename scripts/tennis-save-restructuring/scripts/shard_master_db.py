import os
import json
from pathlib import Path


def shard_master_db():
    db_dir = Path("db")

    for tour in ["atp", "wta"]:
        ranking_file = db_dir / f"ranking_{tour}.json"
        if not ranking_file.exists():
            continue

        print(f"🚀 Sharding MASTER {tour.upper()} database...")
        with open(ranking_file, "r", encoding="utf-8") as f:
            ranking = json.load(f)

        players_dir = db_dir / "jogadores" / tour
        os.makedirs(players_dir, exist_ok=True)

        index_pure = []
        for j in ranking:
            if not isinstance(j, dict):
                continue

            # 1. Salva o arquivo detalhado completo na base master
            safe_name = (
                j["nome"].lower().replace(" ", "_").replace("'", "").replace(".", "")
            )
            player_file = players_dir / f"{safe_name}.json"

            # No Master, garantimos que is_lean é False
            j["is_lean"] = False

            with open(player_file, "w", encoding="utf-8") as pf:
                json.dump(j, pf, indent=2, ensure_ascii=False)

            # 2. Cria o índice PURO (sem overall, sem nada extra)
            index_entry = {
                "nome": j.get("nome"),
                "nacionalidade": j.get("nacionalidade"),
                "pontos": j.get("pontos", 0),
                "pontos_ranking": j.get("pontos_ranking", 0),
                "is_lean": True,
            }
            # Pontos de duplas permanecem no índice para permitir ordenação do ranking de duplas sem carregar tudo
            if "pontos_ranking_duplas" in j:
                index_entry["pontos_ranking_duplas"] = j["pontos_ranking_duplas"]

            index_pure.append(index_entry)

        # Sobrescreve a base global com o índice puro
        with open(ranking_file, "w", encoding="utf-8") as f:
            json.dump(index_pure, f, indent=2, ensure_ascii=False)

        print(f"✅ Sharded {len(ranking)} master players and updated index.")


if __name__ == "__main__":
    shard_master_db()
