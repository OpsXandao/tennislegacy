import os
import json

class Jogador:
    def __init__(self, nome, idade, nacionalidade, save_name="default"):
        self.nome = nome
        self.idade = idade
        self.xp = 0
        self.nacionalidade = nacionalidade
        self.nivel = 1
        self.energia = 100
        self.ritmo_jogo = 50
        self.moral = 70
        self.dinheiro = 500
        self.save_name = save_name
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

    def to_dict(self):
        return {
            "nome": self.nome,
            "idade": self.idade,
            "nacionalidade": self.nacionalidade,
            "xp": self.xp,
            "nivel": self.nivel,
            "energia": self.energia,
            "ritmo_jogo": self.ritmo_jogo,
            "moral": self.moral,
            "dinheiro": self.dinheiro,
            "atributos": self.atributos
        }
        
def adicionar_jogador_ao_ranking(jogador_instancia):
    ranking_path = os.path.join("saves", jogador_instancia.save_name, "ranking_atp.json")

    if os.path.exists(ranking_path):
        with open(ranking_path, "r", encoding="utf-8") as f:
            ranking = json.load(f)
    else:
        ranking = []

    nomes_existentes = [j["nome"].strip().lower() for j in ranking]

    if jogador_instancia.nome.strip().lower() not in nomes_existentes:
        novo = {
            "nome": jogador_instancia.nome,
            "nacionalidade": jogador_instancia.nacionalidade,
            "overall": jogador_instancia.calcular_overall(),
            "atributos": jogador_instancia.atributos,
            "pontos": 0
        }
        ranking.append(novo)
        with open(ranking_path, "w", encoding="utf-8") as f:
            json.dump(ranking, f, indent=2, ensure_ascii=False)
        print(f"✅ Jogador '{novo['nome']}' adicionado ao ranking local com 0 pontos.")
    else:
        print(f"ℹ️ Jogador '{jogador_instancia.nome}' já está presente no ranking.")

def carregar_jogador(nome_save):
    from jogador import reidratar_jogador  # ← garante que a função será usada

    caminho = os.path.join("saves", nome_save, "jogador.json")
    if not os.path.exists(caminho):
        print("❌ Save não encontrado.")
        exit()

    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)

    return reidratar_jogador(dados, nome_save)


def criar_jogador(nome_save):
    from save import criar_pasta_save, salvar_jogo
    from dados import escolher_nacionalidade
    import builtins
    from shutil import copyfile

    print("🎾 Criação do Jogador")
    nome = input("Nome: ")
    while True:
        idade_str = input("Idade: ").strip()
        if idade_str.isdigit():
            idade = int(idade_str)
            break
        print("❌ Idade inválida. Digite apenas números inteiros.")

    nacionalidade = escolher_nacionalidade()

    print("\n📌 Escolha o tipo de jogador:")
    print("1. Técnico — mais controle e precisão")
    print("2. Físico — mais força e movimentação")
    print("3. Equilibrado — tudo balanceado")
    tipo = input("Escolha (1, 2 ou 3): ").strip()

    atributos_por_tipo = {
        "1": {
            "saque": 60, "forehand": 75, "backhand": 75, "topspin": 72,
            "voleio": 65, "slice": 72, "movimento": 68, "lob": 74, "winner": 65
        },
        "2": {
            "saque": 75, "forehand": 72, "backhand": 70, "topspin": 68,
            "voleio": 60, "slice": 62, "movimento": 78, "lob": 60, "winner": 75
        },
        "3": {
            "saque": 70, "forehand": 70, "backhand": 70, "topspin": 70,
            "voleio": 70, "slice": 70, "movimento": 70, "lob": 70, "winner": 70
        }
    }

    atributos = atributos_por_tipo.get(tipo, atributos_por_tipo["3"])

    jogador_instancia = Jogador(nome, idade, nacionalidade, save_name=nome_save)
    jogador_instancia.atributos = atributos
    builtins.jogador = jogador_instancia

    criar_pasta_save(nome_save)

    ranking_origem = os.path.join("db", "ranking_atp.json")
    ranking_destino = os.path.join("saves", nome_save, "ranking_atp.json")
    if not os.path.exists(ranking_destino):
        copyfile(ranking_origem, ranking_destino)

    salvar_jogo(nome_save, jogador_instancia)

    adicionar_jogador_ao_ranking(jogador_instancia)

    return jogador_instancia

def reidratar_jogador(dados, nome_save):
            jogador = Jogador(
                nome=dados["nome"],
                idade=dados["idade"],
                nacionalidade=dados["nacionalidade"],
                save_name=nome_save
            )
            jogador.xp = dados["xp"]
            jogador.nivel = dados["nivel"]
            jogador.energia = dados["energia"]
            jogador.ritmo_jogo = dados["ritmo_jogo"]
            jogador.moral = dados["moral"]
            jogador.dinheiro = dados["dinheiro"]
            jogador.atributos = dados["atributos"]
            return jogador