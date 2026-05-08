import json
import os
import random
import math
import sys

# Adiciona o diretório raiz ao sys.path para importar módulos do src
sys.path.append(os.getcwd())

from src.utils.nome_utils import normalizar_nome
from src.constants.constantes import DEFAULT_ATRIBUTOS, DEFAULT_ATRIBUTOS_PSICOLOGICOS


def gerar_json_basico(
    nome, nacionalidade, genero, rank_referencia=None, pontos_referencia=0
):
    # Estima um overall baseado no ranking ou pontos
    if rank_referencia:
        # Top 1: ~90, Top 100: ~80, Top 500: ~70, Top 1000: ~60
        base_ov = max(55, min(95, int(92 - math.log10(max(1, rank_referencia)) * 11)))
    elif pontos_referencia > 0:
        base_ov = max(55, min(95, int(50 + math.log10(max(1, pontos_referencia)) * 12)))
    else:
        base_ov = random.randint(55, 65)

    # Gera atributos aleatórios em torno da base_ov
    atributos = {}
    for k in DEFAULT_ATRIBUTOS.keys():
        atributos[k] = max(30, min(98, base_ov + random.randint(-8, 8)))

    # Se for especialista de duplas (baseado no contexto que estamos gerando), dá um bônus em duplas e voleio
    if "duplas" in atributos:
        atributos["duplas"] = max(atributos["duplas"], base_ov + random.randint(5, 15))
    if "voleio" in atributos:
        atributos["voleio"] = max(atributos["voleio"], base_ov + random.randint(0, 10))

    psico = {}
    for k in DEFAULT_ATRIBUTOS_PSICOLOGICOS.keys():
        psico[k] = random.randint(40, 75)

    # Recalcula overall real
    avg_tec = sum(v for k, v in atributos.items() if k != "duplas") / (
        len(atributos) - 1
    )
    avg_psi = sum(psico.values()) / len(psico)
    overall_real = round((avg_tec * 0.8) + (avg_psi * 0.2))

    return {
        "nome": nome,
        "nacionalidade": nacionalidade,
        "idade": random.randint(18, 35),
        "overall": overall_real,
        "pontos": pontos_referencia,
        "id": random.randint(10000, 99999),
        "atributos": atributos,
        "atributos_psicologicos": psico,
        "pontos_detalhados": [],
        "trofeus": [],
        "historico_torneios": [],
        "pontos_ytd": 0,
        "dinheiro": 1000,
        "pontos_duplas": pontos_referencia if "duplas" in atributos else 0,
        "pontos_detalhados_duplas": [],
        "pico_carreira": random.randint(26, 30),
        "pontos_ranking": pontos_referencia,
        "is_bot": False,
        "is_lean": False,
        "genero": genero,
    }


def processar():
    rankings_to_check = [
        ("db/templates/npc_index_atp.json", "atp", "masculino"),
        ("db/templates/npc_index_wta.json", "wta", "feminino"),
        ("db/templates/npc_index_atp_duplas.json", "atp", "masculino"),
        ("db/templates/npc_index_wta_duplas.json", "wta", "feminino"),
    ]

    count_created = 0

    for file_path, subfolder, genero in rankings_to_check:
        if not os.path.exists(file_path):
            print(f"⚠️ Arquivo {file_path} não encontrado.")
            continue

        print(f"🔍 Processando {file_path}...")
        with open(file_path, "r", encoding="utf-8") as f:
            ranking = json.load(f)

        for entry in ranking:
            nome = entry.get("nome")
            if not nome:
                continue

            safe_name = nome.lower().replace(" ", "_").replace("'", "").replace(".", "")
            path_jogador = os.path.join("db", "master", subfolder, f"{safe_name}.json")

            if not os.path.exists(path_jogador):
                # Criar o JSON
                nacionalidade = (
                    entry.get("nacionalidade") or entry.get("pais3") or "[??]"
                )
                # Se for código de 3 letras (como no novo ranking de duplas), tenta envolver em colchetes
                if len(nacionalidade) == 3 and not nacionalidade.startswith("["):
                    nacionalidade = f"[{nacionalidade}]"

                rank = entry.get("rank") or entry.get("rank_duplas")
                pontos = (
                    entry.get("pontos")
                    or entry.get("pontos_ranking")
                    or entry.get("pontos_duplas")
                    or 0
                )

                jogador_data = gerar_json_basico(
                    nome, nacionalidade, genero, rank, pontos
                )

                os.makedirs(os.path.dirname(path_jogador), exist_ok=True)
                with open(path_jogador, "w", encoding="utf-8") as fj:
                    json.dump(jogador_data, fj, ensure_ascii=False, indent=2)

                count_created += 1
                if count_created % 50 == 0:
                    print(f"... {count_created} jogadores gerados.")

    print(
        f"\n✅ Total de {count_created} novos arquivos JSON de jogadores criados na base global!"
    )


if __name__ == "__main__":
    processar()
