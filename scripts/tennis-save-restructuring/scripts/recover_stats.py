import os
import json
from pathlib import Path
from src.utils.nome_utils import normalizar_nome


def recover_save_stats(save_name):
    save_path = Path("saves") / save_name
    if not save_path.exists():
        print(f"❌ Save {save_name} not found.")
        return

    print(f"🛠️ Recovering stats for save: {save_name}")

    db_dir = Path("db")

    for tour in ["atp", "wta"]:
        genero = "masculino" if tour == "atp" else "feminino"
        global_ranking_file = db_dir / f"ranking_{tour}.json"

        if not global_ranking_file.exists():
            continue

        with open(global_ranking_file, "r", encoding="utf-8") as f:
            global_ranking = json.load(f)

        global_map = {normalizar_nome(j): j for j in global_ranking}

        players_dir = save_path / "jogadores" / tour
        if not players_dir.exists():
            continue

        recovered_count = 0
        for player_file in players_dir.glob("*.json"):
            with open(player_file, "r", encoding="utf-8") as f:
                player_data = json.load(f)

            nome_norm = normalizar_nome(player_data.get("nome", ""))

            # Se o jogador no save está corrompido (is_lean=True ou overall baixo/faltando atributos reais)
            # ou simplesmente se queremos garantir que todos os que estão no global tenham seus stats originais
            if player_data.get("is_lean") or player_data.get("overall", 0) < 65:
                if nome_norm in global_map:
                    global_data = global_map[nome_norm]

                    # Preserva campos dinâmicos do save
                    campos_preservar = [
                        "pontos",
                        "pontos_ranking",
                        "pontos_detalhados",
                        "pontos_ytd",
                        "dinheiro",
                        "historico_torneios",
                        "trofeus",
                        "moral",
                        "fadiga",
                        "energia",
                        "status_lesao",
                    ]

                    # Restaura atributos e dados base do global
                    for k, v in global_data.items():
                        if k not in campos_preservar:
                            player_data[k] = v

                    # Garante que não é mais lean
                    player_data["is_lean"] = False

                    # Recalcula overall real
                    from src.constants.constantes import DEFAULT_ATRIBUTOS_PSICOLOGICOS

                    tec = player_data.get("atributos", {}).values()
                    psi = player_data.get(
                        "atributos_psicologicos", DEFAULT_ATRIBUTOS_PSICOLOGICOS
                    ).values()
                    avg_tec = sum(tec) / len(tec) if tec else 50
                    avg_psi = sum(psi) / len(psi) if psi else 50
                    player_data["overall"] = round((avg_tec * 0.8) + (avg_psi * 0.2))

                    with open(player_file, "w", encoding="utf-8") as pf:
                        json.dump(player_data, pf, indent=2, ensure_ascii=False)

                    recovered_count += 1

        print(f"✅ Recovered {recovered_count} {tour.upper()} players.")

    # Agora atualiza o índice do ranking para refletir os novos overalls
    for tour in ["atp", "wta"]:
        ranking_file = save_path / f"ranking_{tour}.json"
        if ranking_file.exists():
            with open(ranking_file, "r", encoding="utf-8") as f:
                ranking = json.load(f)

            for entry in ranking:
                nome_norm = normalizar_nome(entry.get("nome", ""))
                safe_name = (
                    entry["nome"]
                    .lower()
                    .replace(" ", "_")
                    .replace("'", "")
                    .replace(".", "")
                )
                shard_file = save_path / "jogadores" / tour / f"{safe_name}.json"

                if shard_file.exists():
                    with open(shard_file, "r", encoding="utf-8") as f:
                        shard_data = json.load(f)
                    # Remove o overall do índice, ele deve viver só no shard
                    if "overall" in entry:
                        del entry["overall"]

            with open(ranking_file, "w", encoding="utf-8") as f:
                json.dump(ranking, f, indent=2, ensure_ascii=False)
            print(f"📊 Updated {tour.upper()} ranking index (removed overall).")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        recover_save_stats(sys.argv[1])
    else:
        print("Usage: python recover_stats.py <save_name>")
