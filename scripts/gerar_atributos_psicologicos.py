"""
Script para adicionar atributos psicológicos a todos os jogadores no ranking_atp.json.
Os valores são baseados no overall existente com variação aleatória.
"""

import json
import random
import os

def gerar_atributos_psicologicos(overall):
    """
    Gera atributos psicológicos baseados no overall do jogador.
    Jogadores com maior overall tendem a ter melhores atributos psicológicos,
    mas com variação para criar personalidades distintas.
    """
    # Base é proporcional ao overall (escala 40-100 para overall)
    base = max(30, min(90, int(overall * 0.9)))

    # Adiciona variação aleatória (-15 a +15)
    def valor_com_variacao():
        valor = base + random.randint(-15, 15)
        return max(30, min(99, valor))

    return {
        "concentracao": valor_com_variacao(),
        "agressividade": valor_com_variacao(),
        "leitura_de_jogo": valor_com_variacao(),
        "determinacao": valor_com_variacao(),
    }


def main():
    caminho = os.path.join(os.path.dirname(__file__), "..", "db", "ranking_atp.json")

    with open(caminho, "r", encoding="utf-8") as f:
        jogadores = json.load(f)

    random.seed(42)  # Para reprodutibilidade

    jogadores_atualizados = 0
    for jogador in jogadores:
        if "atributos_psicologicos" not in jogador:
            overall = jogador.get("overall", 60)
            jogador["atributos_psicologicos"] = gerar_atributos_psicologicos(overall)
            jogadores_atualizados += 1

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(jogadores, f, indent=2, ensure_ascii=False)

    print(f"✅ Atributos psicológicos adicionados a {jogadores_atualizados} jogadores.")
    print(f"📁 Arquivo atualizado: {caminho}")


if __name__ == "__main__":
    main()
