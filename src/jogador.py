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