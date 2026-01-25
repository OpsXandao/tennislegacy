import random

# --- Regional and Global Name Lists ---
NOMES_GLOBAL = [
    "Carlos", "Pedro", "Luiz", "João", "Rafael", "Felipe", "Daniel", "Lucas", "Mateus", "Gabriel",
    "André", "Bruno", "Eduardo", "Gustavo", "Henrique", "Leonardo", "Marcelo", "Thiago", "Vinicius",
    "Antônio", "Francisco", "José", "Ricardo", "Fernando", "Diego", "Miguel", "Arthur", "Davi",
    "Bernardo", "Nicolas", "Samuel", "Guilherme", "Lorenzo", "Enzo", "Valentim", "Joaquim", "Manuel",
    "Alexandre", "Rodrigo", "Paulo", "Sergio", "Vitor", "Rui", "Gonçalo", "Diogo", "Tomás", "Santiago",
    "Afonso", "Salvador", "Martim", "Lourenço", "Francisco", "João", "Tiago", "Miguel", "Duarte",
    "Vicente", "Vasco", "Gabriel", "Artur", "Matias", "Simão", "Caetano", "Gaspar", "Clemente", "Xavier"
]

SOBRENOMES_GLOBAL = [
    "Silva", "Santos", "Oliveira", "Souza", "Lima", "Costa", "Pereira", "Ferreira", "Rodrigues", "Alves",
    "Martins", "Gomes", "Nunes", "Carvalho", "Melo", "Dias", "Fernandes", "Moreira", "Barbosa", "Ribeiro",
    "Guerra", "Rocha", "Pinto", "Freitas", "Reis", "Pires", "Cunha", "Moraes", "Castro", "Machado",
    "Vasconcelos", "Mendes", "Godinho", "Monteiro", "Cardoso", "Correia", "Nogueira", "Sanches", "Teixeira",
    "Almeida", "Azevedo", "Borges", "Campos", "Duarte", "Esteves", "Franco", "Guerreiro", "Inacio", "Jesus",
    "Leal", "Marques", "Neves", "Pacheco", "Queiros", "Ramalho", "Salgado", "Tavares", "Vieira", "Xavier"
]

# Australian Names
NOMES_AUS = ["Liam", "Noah", "Oliver", "Lucas", "Ethan", "Jack", "William", "James", "Benjamin", "Henry"]
SOBRENOMES_AUS = ["Smith", "Jones", "Williams", "Brown", "Wilson", "Davies", "Evans", "Thomas", "Ryan", "Walker"]

# French Names
NOMES_FRA = ["Louis", "Gabriel", "Raphaël", "Léo", "Arthur", "Jules", "Adam", "Hugo", "Lucas", "Paul"]
SOBRENOMES_FRA = ["Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Dubois", "Moreau", "Laurent"]

# UK Names (England)
NOMES_GBR = ["Oliver", "George", "Arthur", "Freddie", "Harry", "Noah", "Leo", "Oscar", "Charlie", "Jack"]
SOBRENOMES_GBR = ["Smith", "Jones", "Williams", "Brown", "Wilson", "Johnson", "Davies", "Robinson", "Wright", "Thompson"]

# USA Names
NOMES_EUA = ["Liam", "Noah", "Oliver", "James", "Elijah", "William", "Henry", "Lucas", "Benjamin", "Theodore"]
SOBRENOMES_EUA = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

# Mapping nationalities to regional lists
NOMES_POR_NACIONALIDADE = {
    "AUS": NOMES_AUS,
    "FRA": NOMES_FRA,
    "GBR": NOMES_GBR,
    "EUA": NOMES_EUA,
    "GLOBAL": NOMES_GLOBAL # Fallback
}

SOBRENOMES_POR_NACIONALIDADE = {
    "AUS": SOBRENOMES_AUS,
    "FRA": SOBRENOMES_FRA,
    "GBR": SOBRENOMES_GBR,
    "EUA": SOBRENOMES_EUA,
    "GLOBAL": SOBRENOMES_GLOBAL # Fallback
}


def gerar_nome_completo(nacionalidade="GLOBAL"):
    nomes = NOMES_POR_NACIONALIDADE.get(nacionalidade, NOMES_GLOBAL)
    sobrenomes = SOBRENOMES_POR_NACIONALIDADE.get(nacionalidade, SOBRENOMES_GLOBAL)
    
    nome = random.choice(nomes)
    sobrenome = random.choice(sobrenomes)
    return f"{nome} {sobrenome}"

def gerar_nacionalidade_aleatoria(pais_sede=None):
    nacionalidades_comuns = ["BRA", "ARG", "EUA", "GBR", "ESP", "FRA", "GER", "AUS", "CAN", "ITA", "SRB", "RUS", "SUI", "GRE", "POL", "JPN", "CHN"]
    
    if pais_sede:
        # Extrai o código do país se estiver no formato "[XX] Nome"
        if pais_sede.startswith("[") and "]" in pais_sede:
            codigo_pais = pais_sede[1:pais_sede.find("]")].upper()
            if codigo_pais in nacionalidades_comuns:
                # 70% de chance de ser da nacionalidade do país sede
                if random.random() < 0.70:
                    return codigo_pais
        
        # Fallback se pais_sede não for válido ou não escolhido
        return random.choice(nacionalidades_comuns)
    else:
        return random.choice(nacionalidades_comuns)

def gerar_jogador_fraco(id_bot, pais_sede=None):
    nacionalidade = gerar_nacionalidade_aleatoria(pais_sede)
    nome = gerar_nome_completo(nacionalidade) # Pass nationality to get a region-appropriate name
    
    # Define atributos de um jogador fraco (valores baixos)
    atributos = {
        "saque": random.randint(30, 50),
        "forehand": random.randint(30, 50),
        "backhand": random.randint(30, 50),
        "topspin": random.randint(30, 50),
        "voleio": random.randint(30, 50),
        "slice": random.randint(30, 50),
        "movimento": random.randint(30, 50),
        "lob": random.randint(30, 50),
        "winner": random.randint(30, 50),
    }
    
    # Atributos psicológicos também baixos
    atributos_psicologicos = {
        "concentracao": random.randint(30, 50),
        "agressividade": random.randint(30, 50),
        "leitura_de_jogo": random.randint(30, 50),
        "determinacao": random.randint(30, 50),
    }
    
    overall = round(sum(atributos.values()) / len(atributos))
    
    return {
        "nome": nome,
        "nacionalidade": nacionalidade,
        "overall": overall,
        "pontos": random.randint(0, 50), # Pontos baixos para jogadores fracos
        "pontos_detalhados": [],
        "atributos": atributos,
        "atributos_psicologicos": atributos_psicologicos
    }