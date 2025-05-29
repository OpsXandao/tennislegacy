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


def obter_info_torneio_e_fase(nome_save):
    caminho = os.path.join("saves", nome_save, "torneio_atp.json")
    with open(caminho, encoding="utf-8") as f:
        estado = json.load(f)

    nome_torneio = estado.get("torneio", "Torneio Desconhecido")
    fase = estado.get("fase_atual", "fase_desconhecida")
    semana = estado.get("semana", 0)

    info = obter_torneio_por_nome(semana, nome_torneio)
    if info:
        pais = info.get("pais_sede", "??")
        tipo = info.get("tipo", "??")
        estrelas = "⭐" * info.get("popularidade", 0)
        premio = info.get("premiacao", 0)
        return (
            f"{nome_torneio} ({pais}) - {tipo} | Popularidade: {estrelas} | 💰 Premiação: ${premio}",
            fase,
        )

    return nome_torneio, fase

def avancar_semana(semana):
    return semana + 1
