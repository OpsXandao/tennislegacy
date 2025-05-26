import json
import random
import os

class jogador:
    def __init__(self, nome, idade, nacionalidade):
        self.nome = nome
        self.idade = idade
        self.xp = 0
        self.nacionalidade = nacionalidade
        self.nivel = 1
        self.energia = 100
        self.ritmo_jogo = 50
        self.moral = 70
        self.dinheiro = 500
        self.atributos = {
            "saque": 50, "forehand": 50, "backhand": 50, "topspin": 50,
            "voleio": 50, "slice": 50, "movimento": 50, "lob": 50, "winner": 50
        }

    def calcular_overall(self):
        return round(sum(self.atributos.values()) / len(self.atributos))

    def mostrar_status(self):
        print(f"\n🎾 Jogador: {self.nome} | {self.nacionalidade}")
        print(f"Overall: {self.calcular_overall()}")
        print(f"Idade: {self.idade} | Nível: {self.nivel} | XP: {self.xp}")
        print(f"Energia: {self.energia} | Ritmo de jogo: {self.ritmo_jogo}")
        print(f"Moral: {self.moral} | Dinheiro: ${self.dinheiro}")
        print("Atributos Técnicos:")
        for chave, valor in self.atributos.items():
            print(f"  {chave.capitalize()}: {valor}")

    def ajustar_energia(self, valor):
        self.energia = max(0, min(100, self.energia + valor))

    def ajustar_ritmo(self, valor):
        self.ritmo_jogo = max(0, min(100, self.ritmo_jogo + valor))

    def escolher_estrategia():
        print("\n🎯 Escolha sua estratégia para este game:")
        print("🧭 Direção de ataque:")
        print("1. Pelo meio")
        print("2. Pelas laterais")
        direcao = input("Escolha (1 ou 2): ").strip()
        print("\n⚔️ Estilo de jogo:")
        print("1. Atacar na rede")
        print("2. Atacar do fundo")
        print("3. Atacar do meio")
        estilo = input("Escolha (1, 2 ou 3): ").strip()
        return {
            "direcao": "meio" if direcao == "1" else "laterais",
            "estilo": {
                "1": "atacar_na_rede",
                "2": "atacar_do_fundo",
                "3": "atacar_pelo_meio"
            }.get(estilo, "atacar_do_fundo")
        }

    def carregar_adversario(self, nome_adversario=None):
        caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../save/atp.json")
        with open(caminho, encoding="utf-8") as f:
            jogadores = json.load(f)

        if nome_adversario:
            for j in jogadores:
                if j["nome"] == nome_adversario:
                    return j
            raise ValueError(f"Adversário '{nome_adversario}' não encontrado em atp.json.")
        else:
            return random.choice(jogadores)

    def calcular_bonus_por_estilo(self, estilo, atributo):
        estilo_bonus = {
            "atacar_na_rede": {"voleio", "winner"},
            "atacar_do_fundo": {"forehand", "backhand", "topspin"},
            "atacar_pelo_meio": {"saque", "slice", "movimento"}
        }
        return 2 if atributo in estilo_bonus.get(estilo, set()) else 0

    def jogar_partida(self, nome_adversario=None):
        media = lambda a: sum(a.values()) / len(a)
        vantagens = {
            "forehand": "backhand", "backhand": "slice", "slice": "forehand",
            "topspin": "lob", "lob": "voleio", "voleio": "topspin",
            "saque": "movimento", "movimento": "winner", "winner": "saque"
        }

        adversario = self.carregar_adversario(nome_adversario)
        nome_adversario = adversario["nome"]
        nacionalidade_adversario = adversario["nacionalidade"]
        atributos_adversario = adversario["atributos"]
        overall_adversario = adversario["overall"]

        sets_jogador, sets_adversario = 0, 0
        estrategia_atual = None

        while sets_jogador < 2 and sets_adversario < 2:
            games_jogador, games_adversario = 0, 0
            print(f"\n🎾 Set {sets_jogador + sets_adversario + 1} — {self.nome} {self.nacionalidade} vs {nome_adversario} {nacionalidade_adversario}")

            while True:
                if not estrategia_atual:
                    estrategia_atual = jogador.escolher_estrategia()
                pontos_jogador, pontos_adversario = 0, 0

                def placar(pj, pa):
                    if pj >= 3 and pa >= 3:
                        if pj == pa:
                            return "40 x 40"
                        elif pj > pa:
                            return "Ad x 40"
                        else:
                            return "40 x Ad"
                    else:
                        valores = ["0", "15", "30", "40"]
                        return f"{valores[min(pj, 3)]} x {valores[min(pa, 3)]}"

                while (pontos_jogador < 4 or pontos_adversario < 4) or abs(pontos_jogador - pontos_adversario) < 2:
                    print(f"🎾 Ponto! {placar(pontos_jogador, pontos_adversario)}")

                    atributo_jogador = random.choice(list(self.atributos))
                    atributo_adversario = random.choice(list(atributos_adversario))
                    bonus_jogador = (3 if vantagens.get(atributo_jogador) == atributo_adversario else 0) + self.calcular_bonus_por_estilo(estrategia_atual["estilo"], atributo_jogador)
                    bonus_adversario = 3 if vantagens.get(atributo_adversario) == atributo_jogador else 0

                    perfil_jogador = media(self.atributos) * 0.6 + self.energia * 0.2 + self.ritmo_jogo * 0.2 + bonus_jogador + random.uniform(-3, 3)
                    perfil_adversario = media(atributos_adversario) * 0.6 + random.randint(60, 90) * 0.2 + random.randint(50, 80) * 0.2 + bonus_adversario + random.uniform(-3, 3)

                    if perfil_jogador >= perfil_adversario:
                        pontos_jogador += 1
                    else:
                        pontos_adversario += 1

                    if (pontos_jogador >= 4 or pontos_adversario >= 4) and abs(pontos_jogador - pontos_adversario) >= 2:
                        break

                if pontos_jogador > pontos_adversario:
                    games_jogador += 1
                    print(f"✅ Game seu! ({games_jogador} x {games_adversario})")
                else:
                    games_adversario += 1
                    print(f"❌ Game do {nome_adversario}. ({games_jogador} x {games_adversario})")
                    mudar = input("⚙️ Deseja mudar sua estratégia? (s/n): ").strip().lower()
                    if mudar == "s":
                        estrategia_atual = jogador.escolher_estrategia()

                if (games_jogador >= 6 or games_adversario >= 6) and abs(games_jogador - games_adversario) >= 2:
                    sets_jogador += games_jogador > games_adversario
                    sets_adversario += games_adversario > games_jogador
                    print(f"{'🏆 Você venceu' if games_jogador > games_adversario else '📉'} o set!")
                    break

        total_games = games_jogador + games_adversario
        self.energia = max(0, self.energia - int(total_games * 0.8))
        experiencia = int((overall_adversario / 100) * total_games * 4)
        self.xp += experiencia if sets_jogador > sets_adversario else int(experiencia * 0.5)
        self.moral = min(100, self.moral + 10) if sets_jogador > sets_adversario else max(0, self.moral - 10)
        self.ritmo_jogo = min(100, self.ritmo_jogo + 15) if sets_jogador > sets_adversario else max(0, self.ritmo_jogo - 10)
        self.dinheiro += total_games * 10 if sets_jogador > sets_adversario else 0

        print(f"\n🏁 Fim da partida: {'Vitória' if sets_jogador > sets_adversario else 'Derrota'} de {self.nome} {self.nacionalidade} sobre {nome_adversario} {nacionalidade_adversario}")
        print("🏆 Parabéns! Você venceu!" if sets_jogador > sets_adversario else "❌ Não foi dessa vez!")
        print(f"🟦 Placar final: {sets_jogador} x {sets_adversario}")
        print(f"⚡ Energia gasta: {int(total_games * 0.8)}")
        print(f"⭐ XP ganho: {experiencia}")

        return sets_jogador, sets_adversario    
