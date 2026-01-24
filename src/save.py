import json
import os

from src.dados import (
    SAVES_DIR,
    get_caminho_jogador_save,
    get_caminho_ranking_save,
    get_caminho_torneio_save,
)
from src.jogador import normalizar_nome


def criar_pasta_save(nome_save):
    caminho = os.path.join(SAVES_DIR, nome_save)
    os.makedirs(caminho, exist_ok=True)
    return caminho


def salvar_jogo(nome_save, jogador_inst):
    try:
        # Salvar jogador.json
        if hasattr(jogador_inst, "to_dict"):
            dados = jogador_inst.to_dict()
        elif isinstance(jogador_inst, dict):
            dados = jogador_inst
        else:
            raise ValueError("Tipo de jogador não suportado!")

        criar_pasta_save(nome_save)
        jogador_path = get_caminho_jogador_save(nome_save)
        with open(jogador_path, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

        # Atualizar ranking_atp.json (opcional)
        ranking_path = get_caminho_ranking_save(nome_save)
        if os.path.exists(ranking_path):
            with open(ranking_path, encoding="utf-8") as f:
                ranking = json.load(f)

            # Atualiza informações do jogador no ranking, se existir
            for j in ranking:
                if normalizar_nome(j.get("nome", "")) == normalizar_nome(
                    dados.get("nome", "")
                ):
                    j.update(
                        {
                            "idade": dados.get("idade"),
                            "xp": dados.get("xp"),
                            "nivel": dados.get("nivel"),
                            "energia": dados.get("energia"),
                            "ritmo_jogo": dados.get("ritmo_jogo"),
                            "moral": dados.get("moral"),
                            "dinheiro": dados.get("dinheiro"),
                            "atributos": dados.get("atributos"),
                        }
                    )

            with open(ranking_path, "w", encoding="utf-8") as f:
                json.dump(ranking, f, indent=2, ensure_ascii=False)

        print("💾 Jogo salvo automaticamente")

    except Exception as e:
        print(f"❌ Erro ao salvar jogo: {e}")


def salvar_estado_atual_torneio(
    nome_save, fase_atual, confrontos, resultados, jogador_vivo=True
):
    try:
        caminho = get_caminho_torneio_save(nome_save)

        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                estado = json.load(f)
        else:
            estado = {
                "rodadas": {},
                "resultados": {},
                "fase_atual": fase_atual,
                "jogador_vivo": jogador_vivo,
            }

        estado["rodadas"][fase_atual] = [
            (
                a["nome"] if isinstance(a, dict) else a,
                b["nome"] if isinstance(b, dict) else b,
            )
            for a, b in confrontos
        ]

        estado["resultados"][fase_atual] = resultados
        estado["jogador_vivo"] = jogador_vivo
        estado["fase_atual"] = fase_atual

        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(estado, f, indent=2, ensure_ascii=False)

        print("💾 Estado do torneio salvo com sucesso")

    except Exception as e:
        print(f"❌ Erro ao salvar estado atual do torneio: {e}")


def carregar_estado_torneio(caminho):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            estado = json.load(f)

        fase = estado.get("fase_atual")
        rodadas = estado.get("rodadas", {}).get(fase, [])
        resultados = estado.get("resultados", {}).get(fase, [])
        jogador_vivo = estado.get("jogador_vivo", True)

        if fase is None:
            print("⚠️ Erro: Fase atual não definida no estado do torneio.")
        if not isinstance(rodadas, list):
            print("⚠️ Erro: Confrontos malformados. Esperado lista.")
            rodadas = []
        if not isinstance(resultados, list):
            print("⚠️ Erro: Resultados malformados. Esperado lista.")
            resultados = []

        return {
            "fase_atual": fase or "fase_indefinida",
            "confrontos": rodadas,
            "resultados": resultados,
            "jogador_vivo": jogador_vivo,
        }

    except (FileNotFoundError, json.JSONDecodeError, TypeError) as e:
        print(f"⚠️ Estado inválido ou ausente ({e.__class__.__name__}): {e}")
    except Exception as e:
        print(f"❌ Erro inesperado ao carregar estado do torneio: {e}")

    return {
        "fase_atual": "fase_indefinida",
        "confrontos": [],
        "resultados": [],
        "jogador_vivo": True,
    }


def atualizar_estado_jogador(caminho, vivo=True, fase_finalizada=False):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            estado = json.load(f)
        estado["jogador_vivo"] = vivo
        if fase_finalizada:
            estado["fase_atual"] = "finalizado"
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(estado, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Erro ao atualizar status do jogador: {e}")
