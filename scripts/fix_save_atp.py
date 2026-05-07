import json

SAVE_NAME = "aaa"
RANKING_FILE = f"saves/{SAVE_NAME}/ranking_atp.json"

with open(RANKING_FILE, "r") as f:
    ranking = json.load(f)

for j in ranking:
    if j["nome"] == "Alexandre Paiva":
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

with open(RANKING_FILE, "w") as f:
    json.dump(ranking, f, indent=2)

print("ranking_atp fixed.")
