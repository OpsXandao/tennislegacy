import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "db")
SAVES_DIR = os.path.join(BASE_DIR, "saves")

# --- Nacionalidades ---

def carregar_nacionalidades():
    """Carrega o dicionário de nacionalidades do arquivo JSON."""
    caminho_para_arquivo = os.path.join(DB_DIR, "nacionalidades.json")
    with open(caminho_para_arquivo, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- Caminhos (Paths) ---

def get_caminho_ranking_save(nome_save):
    """Retorna o caminho para o arquivo de ranking de um save específico."""
    return os.path.join(SAVES_DIR, nome_save, "ranking_atp.json")

def get_caminho_ranking_global():
    """Retorna o caminho para o arquivo de ranking global."""
    return os.path.join(DB_DIR, "ranking_atp.json")

def get_caminho_calendario():
    """Retorna o caminho para o arquivo de calendário."""
    return os.path.join(DB_DIR, "calendario.json")

def get_caminho_jogador_save(nome_save):
    """Retorna o caminho para o arquivo do jogador em um save específico."""
    return os.path.join(SAVES_DIR, nome_save, "jogador.json")

# --- Carregadores de Dados (Data Loaders) ---

def carregar_ranking(caminho):
    """Carrega um arquivo de ranking (JSON) de um caminho específico."""
    if not os.path.exists(caminho):
        return []  # Retorna uma lista vazia se o ranking não existir
    with open(caminho, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_caminho_torneio_save(nome_save):
    """Retorna o caminho para o arquivo de estado de um torneio de um save."""
    return os.path.join(SAVES_DIR, nome_save, "torneio_atp.json")

def carregar_estado_torneio(nome_save):
    """Carrega o estado de um torneio de um save específico."""
    caminho = get_caminho_torneio_save(nome_save)
    if not os.path.exists(caminho):
        return None  # Retorna None se o arquivo não existir
    with open(caminho, 'r', encoding='utf-8') as f:
        return json.load(f)

def carregar_calendario():
    """Carrega os dados do calendário do arquivo JSON."""
    caminho = get_caminho_calendario()
    with open(caminho, 'r', encoding='utf-8') as f:
        return json.load(f)
