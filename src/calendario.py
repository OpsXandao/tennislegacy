import json
import os

def obter_torneios_da_semana(semana):
    caminho = os.path.join(os.path.dirname(__file__), "../save/calendario.json")
    with open(caminho, encoding="utf-8") as f:
        calendario = json.load(f)
    return calendario.get(str(semana), [])
