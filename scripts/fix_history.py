import json

SAVE_NAME = "aaa"
JOGADOR_FILE = f"saves/{SAVE_NAME}/jogador.json"

with open(JOGADOR_FILE, "r") as f:
    jogador = json.load(f)

# Add to historico_torneios for the dashboard
if "historico_torneios" not in jogador:
    jogador["historico_torneios"] = []

jogador["historico_torneios"].append(
    {
        "ano": 2026,
        "semana": 1,
        "nome": "Brisbane International",
        "tipo": "ATP 250",
        "fase": "campeao",
        "pontos": 250,
        "modalidade": "duplas",
        "obrigatorio": False,
    }
)

with open(JOGADOR_FILE, "w") as f:
    json.dump(jogador, f, indent=2)

print("historico_torneios fixed.")
