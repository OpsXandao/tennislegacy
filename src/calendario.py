import json
import os

def obter_torneios_da_semana(semana):
    caminho = os.path.join(os.path.dirname(__file__), "../db/calendario.json")
    with open(caminho, encoding="utf-8") as f:
        calendario = json.load(f)
    return calendario.get(str(semana), [])

def obter_torneio_por_nome(semana, nome_torneio):
    torneios = obter_torneios_da_semana(semana)
    for torneio in torneios:
        if torneio["nome"] == nome_torneio:
            return torneio
    return None

def distribuir_premio(total, porcentagem):
    return int(total * porcentagem)
