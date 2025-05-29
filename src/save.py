import os
import json
from jogador import normalizar_nome

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "saves")
DB_DIR = os.path.join(os.path.dirname(__file__), "..", "db")


def criar_pasta_save(nome_save):
    caminho = os.path.join(BASE_DIR, nome_save)
    os.makedirs(caminho, exist_ok=True)
    return caminho


def salvar_jogo(nome_save, jogador_inst):
    try:
        caminho = criar_pasta_save(nome_save)
        ranking_path = os.path.join(caminho, "ranking_atp.json")

        with open(ranking_path, encoding="utf-8") as f:
            ranking = json.load(f)

        for j in ranking:
            if normalizar_nome(j) == normalizar_nome(jogador_inst):
                j.update(
                    {
                        "idade": jogador_inst.idade,
                        "xp": jogador_inst.xp,
                        "nivel": jogador_inst.nivel,
                        "energia": jogador_inst.energia,
                        "ritmo_jogo": jogador_inst.ritmo_jogo,
                        "moral": jogador_inst.moral,
                        "dinheiro": jogador_inst.dinheiro,
                        "atributos": jogador_inst.atributos,
                    }
                )

        with open(ranking_path, "w", encoding="utf-8") as f:
            json.dump(ranking, f, indent=2, ensure_ascii=False)

        jogador_path = os.path.join(caminho, "jogador.json")
        with open(jogador_path, "w", encoding="utf-8") as f:
            json.dump(jogador_inst.to_dict(), f, indent=2, ensure_ascii=False)

        print("💾 Jogo salvo automaticamente")

    except Exception as e:
        print(f"❌ Erro ao salvar jogo: {e}")


def salvar_estado_atual_torneio(
    nome_save, fase_atual, confrontos, resultados, jogador_vivo=True
):
    try:
        caminho = os.path.join(BASE_DIR, nome_save, "torneio_atp.json")

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
