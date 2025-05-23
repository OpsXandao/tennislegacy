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
            "saque": 50,
            "forehand": 50,
            "backhand": 50,
            "topspin": 50,
            "voleio": 50,
            "slice": 50,
            "movimento": 50,
            "lob": 50,
            "winner": 50
        }
    
    def calcular_overall(self):
        media = sum(self.atributos.values()) / len(self.atributos)
        return round(min(100, max(0, media)))
        
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
        
    def carregar_adversario(self):
        caminho_base = os.path.dirname(os.path.abspath(__file__))
        caminho_json = os.path.join(caminho_base, "../save/jogador.json")
        with open(caminho_json, encoding="utf-8") as f:
            adversarios = json.load(f)
        return random.choice(adversarios)
        
    def jogar_partida(self):
        def media_atributos(atributos):
            return sum(atributos.values()) / len(atributos)

        vantagens = {
            "forehand": "backhand", "backhand": "slice", "slice": "forehand",
            "topspin": "lob", "lob": "voleio", "voleio": "topspin",
            "saque": "movimento", "movimento": "winner", "winner": "saque"
        }

        adversario = self.carregar_adversario()
        nome_adversario = adversario["nome"]
        nacionalidade_adversario = adversario["nacionalidade"]
        atributos_adversario = adversario["atributos"]
        overall_adversario = adversario["overall"]

        sets_jogador = 0
        sets_adversario = 0 

        while sets_jogador < 2 and sets_adversario < 2:
            games_jogador = 0
            games_adversario = 0
            numero_set = sets_jogador + sets_adversario + 1

            print(f"\n🎾 {numero_set}º Set — {self.nome} {self.nacionalidade} vs {nome_adversario} {nacionalidade_adversario}")
            print(f"🟦 Sets: {sets_jogador} x {sets_adversario}")

            while True:
                atributo_jogador = random.choice(list(self.atributos.keys()))
                atributo_adversario = random.choice(list(atributos_adversario.keys()))

                bonus_jogador = 0
                bonus_adv = 0

                if vantagens.get(atributo_jogador) == atributo_adversario:
                    bonus_jogador += 5
                elif vantagens.get(atributo_adversario) == atributo_jogador:
                    bonus_adv += 5

                perfil_jogador = (
                    media_atributos(self.atributos) * 0.6 +
                    self.energia * 0.2 +
                    self.ritmo_jogo * 0.2 +
                    bonus_jogador +
                    random.uniform(-3, 3)
                )

                energia_adversario = random.randint(60, 90)
                ritmo_adversario = random.randint(50, 80)

                perfil_adversario = (
                    media_atributos(atributos_adversario) * 0.6 +
                    energia_adversario * 0.2 +
                    ritmo_adversario * 0.2 +
                    bonus_adv +
                    random.uniform(-3, 3)
                )

                if perfil_jogador >= perfil_adversario:
                    games_jogador += 1
                    print(f"✅ Game seu! ({games_jogador} x {games_adversario})")
                else:
                    games_adversario += 1
                    print(f"❌ Game do {nome_adversario}. ({games_jogador} x {games_adversario})")

                if (games_jogador >= 6 or games_adversario >= 6) and abs(games_jogador - games_adversario) >= 2:
                    if games_jogador > games_adversario:
                        sets_jogador += 1
                        print(f"🏆 Você venceu o {numero_set}º set!")
                    else:
                        sets_adversario += 1
                        print(f"📉 {nome_adversario} venceu o {numero_set}º set.")
                    break

        total_games = games_jogador + games_adversario
        energia_gasta = int(total_games * 0.8)
        xp_ganho = int((overall_adversario / 100) * total_games * 4)

        if sets_jogador > sets_adversario:
            print(f"\n🏁 Fim da partida: Vitória de {self.nome} {self.nacionalidade} sobre {nome_adversario} {nacionalidade_adversario}")
            print("🏆 Parabéns! Você venceu a partida!")
            self.xp += xp_ganho
            self.moral = min(100, self.moral + 10)
            self.dinheiro += total_games * 10
            self.ritmo_jogo = min(100, self.ritmo_jogo + 15)
        else:
            print(f"\n🏁 Fim da partida: Derrota para {nome_adversario} {nacionalidade_adversario}")
            print("❌ Não foi dessa vez... continue treinando!")
            self.xp += int(xp_ganho * 0.5)
            self.moral = max(0, self.moral - 10)
            self.ritmo_jogo = max(0, self.ritmo_jogo + 15)

        self.energia = max(0, self.energia - energia_gasta)
        print(f"⚡ Energia gasta: {energia_gasta}")
        print(f"⭐ XP ganho: {xp_ganho}")

