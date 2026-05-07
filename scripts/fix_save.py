import json

SAVE_NAME = "aaa"
JOGADOR_FILE = f"saves/{SAVE_NAME}/jogador.json"
RANKING_DUPLAS_FILE = f"saves/{SAVE_NAME}/ranking_atp_duplas.json"

# Fix jogador.json
with open(JOGADOR_FILE, "r") as f:
    jogador = json.load(f)

# He won a 250 tournament probably (in Week 1). Let's give him 250 points and 250 YTD points.
jogador["seguidores"] += 500  # Champion bonus
jogador["pontos_ytd"] += 250

if "pontos_detalhados_duplas" not in jogador:
    jogador["pontos_detalhados_duplas"] = []

jogador["pontos_detalhados_duplas"].append(
    {
        "pontos": 250,
        "semana_expiracao": 1,
        "ano_expiracao": 2027,
        "torneio": "Brisbane International",  # Example week 1 tournament
        "tipo": "ATP 250",
        "semana_origem": 1,
        "ano_origem": 2026,
        "fase": "campeao",
        "modalidade": "duplas",
    }
)

with open(JOGADOR_FILE, "w") as f:
    json.dump(jogador, f, indent=2)

# Fix ranking_atp_duplas.json
with open(RANKING_DUPLAS_FILE, "r") as f:
    ranking = json.load(f)

for j in ranking:
    if j["nome"] == "Alexandre Paiva":
        j["pontos"] = j.get("pontos", 0) + 250
        j["pontos_ranking_duplas"] = j.get("pontos_ranking_duplas", 0) + 250
        j["pontos_ytd"] = j.get("pontos_ytd", 0) + 250

        if "pontos_detalhados_duplas" not in j:
            j["pontos_detalhados_duplas"] = []

        j["pontos_detalhados_duplas"].append(
            {
                "pontos": 250,
                "semana_expiracao": 1,
                "ano_expiracao": 2027,
                "torneio": "Brisbane International",
                "tipo": "ATP 250",
                "semana_origem": 1,
                "ano_origem": 2026,
                "fase": "campeao",
                "modalidade": "duplas",
            }
        )
        break

# Sort ranking by points_ranking_duplas
ranking.sort(key=lambda x: x.get("pontos_ranking_duplas", 0), reverse=True)

with open(RANKING_DUPLAS_FILE, "w") as f:
    json.dump(ranking, f, indent=2)

print("Save fixed successfully.")
