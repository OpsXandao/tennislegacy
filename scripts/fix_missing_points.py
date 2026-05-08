import os
import sys
import json

# Adiciona o diretório raiz ao sys.path para importar módulos do src
sys.path.append(os.getcwd())

from src.ranking import SistemaRanking
from src.dados import get_caminho_ranking_save, carregar_temporada
from src.utils.nome_utils import normalizar_nome


def fix_points(nome_save, nome_jogador, pontos, torneio, fase, semana, ano):
    genero = "masculino"
    path_ranking = get_caminho_ranking_save(nome_save, genero=genero)
    ranking = SistemaRanking(path_ranking, modalidade="simples")

    # Expiração em 52 semanas
    sem_exp = ((semana - 1 + 52) % 52) + 1
    ano_exp = ano + (1 if semana + 52 > 52 else 0)
    if semana == 1:  # Caso especial para simplificar
        ano_exp = ano + 1
        sem_exp = 1

    print(f"🔧 Adicionando {pontos} pts para {nome_jogador} no save '{nome_save}'...")

    ranking.adicionar_pontos(
        nome_jogador,
        pontos,
        sem_exp,
        modalidade="simples",
        ano_exp=ano_exp,
        metadados={
            "torneio": torneio,
            "tipo": "ATP 250",
            "semana_origem": semana,
            "ano_origem": ano,
            "fase": fase,
            "modalidade": "simples",
        },
    )

    ranking.salvar_ranking()
    print("✅ Pontos adicionados e ranking salvo!")


if __name__ == "__main__":
    # Parametros para o seu caso específico
    fix_points(
        nome_save="aaa",
        nome_jogador="Alexandre Paiva",
        pontos=20,  # Oitavas de ATP 250
        torneio="Brisbane International",
        fase="oitavas",
        semana=1,
        ano=2026,
    )
