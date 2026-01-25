import random

import random
import json
import os

# Carrega o arquivo de nomes uma vez para evitar múltiplas leituras
with open(os.path.join("db", "nomes.json"), 'r', encoding='utf-8') as f:
    nomes_data = json.load(f)["countries"]

def gerar_nome_completo(nacionalidade="USA"):
    """
    Gera um nome completo (nome e sobrenome) com base na nacionalidade.
    Se a nacionalidade não for encontrada ou não tiver nomes/sobrenomes, usa 'USA' como fallback.
    """
    country_data = nomes_data.get(nacionalidade)
    
    # Fallback para USA se a nacionalidade não existir ou não tiver nomes/sobrenomes
    if not country_data or not country_data.get("names") or not country_data.get("surnames"):
        country_data = nomes_data.get("USA")

    nome = random.choice(country_data["names"])
    sobrenome = random.choice(country_data["surnames"])
    
    return f"{nome} {sobrenome}"

def gerar_nacionalidade_aleatoria(pais_sede=None):
    """
    Gera uma nacionalidade aleatória, com maior probabilidade de ser a do país sede.
    A lista de nacionalidades é extraída do arquivo nomes.json.
    """
    nacionalidades_disponiveis = list(nomes_data.keys())
    
    if pais_sede:
        if pais_sede.startswith("[") and "]" in pais_sede:
            codigo_pais = pais_sede[1:pais_sede.find("]")].upper()
            if codigo_pais in nacionalidades_disponiveis:
                # 70% de chance de ser da nacionalidade do país sede
                if random.random() < 0.70:
                    return codigo_pais
        
    return random.choice(nacionalidades_disponiveis)

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