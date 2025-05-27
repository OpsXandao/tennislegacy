import os
import json
import random


def escolher_estrategia():
    try:
        print("\n🎯 Escolha sua estratégia para este game:")
        print("🧭 Direção de ataque:")
        print("1. Pelo meio")
        print("2. Pelas laterais")
        direcao = input("Escolha (1 ou 2): ").strip()

        if direcao not in {"1", "2"}:
            raise ValueError("Direção inválida. Escolha 1 ou 2.")

        print("\n⚔️ Estilo de jogo:")
        print("1. Atacar na rede")
        print("2. Atacar do fundo")
        print("3. Atacar pelo meio")
        estilo = input("Escolha (1, 2 ou 3): ").strip()

        if estilo not in {"1", "2", "3"}:
            raise ValueError("Estilo inválido. Escolha 1, 2 ou 3.")

        return {
            "direcao": "meio" if direcao == "1" else "laterais",
            "estilo": {
                "1": "atacar_na_rede",
                "2": "atacar_do_fundo",
                "3": "atacar_pelo_meio"
            }[estilo]
        }

    except ValueError as ve:
        print(f"❌ Erro: {ve}")
        return escolher_estrategia()
    except Exception as e:
        print(f"❌ Erro inesperado na escolha de estratégia: {e}")
        return {"direcao": "meio", "estilo": "atacar_do_fundo"}


def carregar_adversario():
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../save/jogador.json")
    try:
        with open(caminho, encoding="utf-8") as f:
            jogadores = json.load(f)
            if not jogadores:
                raise ValueError("Lista de adversários vazia.")
            return random.choice(jogadores)
    except FileNotFoundError:
        print("❌ Arquivo de adversário não encontrado:", caminho)
    except json.JSONDecodeError:
        print("❌ Erro ao decodificar o JSON de adversários.")
    except ValueError as ve:
        print(f"❌ {ve}")
    except Exception as e:
        print(f"❌ Erro inesperado ao carregar adversário: {e}")
    return None


def calcular_bonus_por_estilo(estilo, atributo):
    estilo_bonus = {
        "atacar_na_rede": {"voleio", "winner"},
        "atacar_do_fundo": {"forehand", "backhand", "topspin"},
        "atacar_pelo_meio": {"saque", "slice", "movimento"}
    }
    try:
        bonus = 2 if atributo in estilo_bonus.get(estilo, set()) else 0
        return bonus
    except Exception as e:
        print(f"⚠️ Erro ao calcular bônus por estilo: {e}")
        return 0

def jogar_partida(jogador, adversario, nome_save):
    print(f"\n🎾 Iniciando partida entre {jogador.nome} e {adversario['nome']}")
    estrategia = escolher_estrategia()

    atributos_jogador = jogador.atributos
    atributos_adv = adversario.get("atributos", {k: 50 for k in atributos_jogador.keys()})

    score_jogador = sum(atributos_jogador[k] + calcular_bonus_por_estilo(estrategia["estilo"], k) for k in atributos_jogador)
    score_adv = sum(atributos_adv[k] for k in atributos_adv)

    score_jogador += random.randint(-5, 5)
    score_adv += random.randint(-5, 5)

    if score_jogador >= score_adv:
        sets_v, sets_d = 2, random.choice([0, 1])
        resultado = f"{jogador.nome} {sets_v} x {sets_d} {adversario['nome']}"
        return jogador.nome, resultado
    else:
        sets_d, sets_v = 0, random.choice([1, 2])
        resultado = f"{adversario['nome']} {sets_v} x {sets_d} {jogador.nome}"
        return adversario["nome"], resultado
