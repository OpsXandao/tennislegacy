import random

from src.io_utils import safe_input


def escolher_estrategia():
    print("\n🎯 Escolha sua estratégia para este game:")
    print("🧭 Direção de ataque:")
    print("1. Pelo meio")
    print("2. Pelas laterais")
    direcao = safe_input("Escolha (1 ou 2): ").strip()
    if direcao not in {"1", "2"}:
        print("❌ Direção inválida. Usando 'meio'.")
        direcao = "1"

    print("\n⚔️ Estilo de jogo:")
    print("1. Atacar na rede")
    print("2. Atacar do fundo")
    print("3. Atacar pelo meio")
    estilo = safe_input("Escolha (1, 2 ou 3): ").strip()
    if estilo not in {"1", "2", "3"}:
        print("❌ Estilo inválido. Usando 'atacar do fundo'.")
        estilo = "2"

    return {
        "direcao": "meio" if direcao == "1" else "laterais",
        "estilo": {
            "1": "atacar_na_rede",
            "2": "atacar_do_fundo",
            "3": "atacar_pelo_meio",
        }[estilo],
    }


def calcular_bonus(estilo, atributo):
    bonus_map = {
        "atacar_na_rede": {"voleio", "reflexo"},
        "atacar_do_fundo": {"forehand", "backhand", "movimento"},
        "atacar_pelo_meio": {"saque", "forca", "precisao"},
    }
    return 2 if atributo in bonus_map.get(estilo, set()) else 0


def simular_ponto(jogador, adversario, estrategia):
    atributos_j = jogador.atributos
    atributos_a = adversario.get("atributos", {k: 50 for k in atributos_j})

    score_j = sum(
        atributos_j[k] + calcular_bonus(estrategia["estilo"], k) for k in atributos_j
    )
    score_a = sum(atributos_a[k] for k in atributos_a)

    return random.choices(["j", "a"], weights=[score_j, score_a])[0]


def simular_game(jogador, adversario, estrategia):
    pontos = {"j": 0, "a": 0}
    vantagem = None
    historico = []

    def placar_txt(p):
        return {0: "0", 1: "15", 2: "30", 3: "40"}.get(p, "40")

    while True:
        vencedor = simular_ponto(jogador, adversario, estrategia)
        historico.append(vencedor)

        if pontos["j"] >= 3 and pontos["a"] >= 3:
            if vantagem is None:
                if pontos["j"] == pontos["a"]:
                    print("Deuce!")
                    vantagem = vencedor
                    print(
                        f"Advantage {jogador.nome if vencedor == 'j' else adversario['nome']}"
                    )
                else:
                    vantagem = vencedor
                    print(
                        f"Advantage {jogador.nome if vencedor == 'j' else adversario['nome']}"
                    )
            else:
                if vencedor == vantagem:
                    return vencedor, historico
                else:
                    vantagem = None
                    print("Deuce!")
        else:
            pontos[vencedor] += 1
            if pontos[vencedor] >= 4 and abs(pontos["j"] - pontos["a"]) >= 2:
                return vencedor, historico
            print(
                f"Placar: {jogador.nome} {placar_txt(pontos['j'])} x {placar_txt(pontos['a'])} {adversario['nome']}"
            )


def jogar_partida(jogador, adversario, nome_save):
    print(f"\n🎾 Iniciando partida entre {jogador.nome} e {adversario['nome']}")
    estrategia = escolher_estrategia()

    sets = {"j": 0, "a": 0}
    resultado = []

    while sets["j"] < 2 and sets["a"] < 2:
        games = {"j": 0, "a": 0}
        while True:
            print(f"\n{jogador.nome} {games['j']} x {games['a']} {adversario['nome']}")

            vencedor, historico = simular_game(jogador, adversario, estrategia)
            games[vencedor] += 1

            if vencedor == "a":
                print("❌ Você perdeu este game.")
                escolha = safe_input("Deseja manter a estratégia? (s/n): ").strip().lower()
                if escolha == "n":
                    estrategia = escolher_estrategia()

            if (games["j"] >= 6 or games["a"] >= 6) and abs(
                games["j"] - games["a"]
            ) >= 2:
                winner = "j" if games["j"] > games["a"] else "a"
                sets[winner] += 1
                resultado.append((games["j"], games["a"]))
                print(
                    f"🏁 Fim do set: {jogador.nome} {games['j']} x {games['a']} {adversario['nome']}"
                )
                break

    # ✅ Agora fora do while principal
    print("\nPartida finalizada!")
    print("📋 Resultado por sets:")
    for idx, (sj, sa) in enumerate(resultado, 1):
        print(f"Set {idx}: {jogador.nome} {sj} x {sa} {adversario['nome']}")

    sets_vencidos_jogador = sets["j"]
    sets_vencidos_adversario = sets["a"]

    vencedor_final = (
        jogador.nome
        if sets_vencidos_jogador > sets_vencidos_adversario
        else adversario["nome"]
    )
    perdedor_final = (
        adversario["nome"] if vencedor_final == jogador.nome else jogador.nome
    )

    placar_final = f"{vencedor_final} {max(sets_vencidos_jogador, sets_vencidos_adversario)} x {min(sets_vencidos_jogador, sets_vencidos_adversario)} {perdedor_final}"

    print(f"\n✅ Vencedor da partida: {vencedor_final}")
    return vencedor_final, placar_final
