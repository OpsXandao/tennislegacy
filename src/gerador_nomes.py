import random
import json
import os

# Carrega o arquivo de nomes uma vez para evitar múltiplas leituras
with open(os.path.join("db", "nomes.json"), "r", encoding="utf-8") as f:
    nomes_data = json.load(f)["countries"]

_FALLBACK_SOBRENOMES = []
for _pais, _dados in nomes_data.items():
    sobrenomes = _dados.get("surnames") or []
    if sobrenomes:
        _FALLBACK_SOBRENOMES.extend(sobrenomes)

_MAPA_CODIGO_3_PARA_2 = {
    "BRA": "BR",
    "ARG": "AR",
    "EUA": "US",
    "USA": "US",
    "GER": "DE",
    "ITA": "IT",
    "ESP": "ES",
    "FRA": "FR",
    "GBR": "GB",
    "SUI": "CH",
    "SRB": "RS",
    "AUS": "AU",
    "POL": "PL",
    "JPN": "JP",
    "CHN": "CN",
    "CAN": "CA",
}


def _normalizar_codigo_pais(nacionalidade):
    if not nacionalidade:
        return ""
    if (
        isinstance(nacionalidade, str)
        and nacionalidade.startswith("[")
        and "]" in nacionalidade
    ):
        return nacionalidade[1 : nacionalidade.find("]")].upper()
    if isinstance(nacionalidade, str) and len(nacionalidade) == 3:
        return _MAPA_CODIGO_3_PARA_2.get(nacionalidade.upper(), nacionalidade.upper())
    return str(nacionalidade).upper()


def gerar_nome_completo(nacionalidade="US", genero="masculino"):
    """
    Gera um nome completo (nome e sobrenome) com base na nacionalidade e gênero.
    Se a nacionalidade não for encontrada ou não tiver nomes/sobrenomes, usa 'US' como fallback.
    """
    codigo = _normalizar_codigo_pais(nacionalidade)
    country_data = nomes_data.get(codigo)

    # Fallback para US se a nacionalidade não existir ou não tiver nomes/sobrenomes
    if not country_data or (
        not country_data.get("names") and not country_data.get("female_names")
    ):
        country_data = nomes_data.get("US", {})

    if genero == "feminino":
        nomes = (
            country_data.get("female_names") or country_data.get("names") or ["Player"]
        )
    else:
        nomes = country_data.get("names") or ["Player"]

    sobrenomes = country_data.get("surnames") or _FALLBACK_SOBRENOMES or ["Doe"]

    nome = random.choice(nomes)
    sobrenome = random.choice(sobrenomes)

    return f"{nome} {sobrenome}"


def gerar_nacionalidade_aleatoria(pais_sede=None):
    """
    Gera uma nacionalidade aleatória, com maior probabilidade de ser a do país sede.
    A lista de nacionalidades é extraída do arquivo nomes.json.
    """
    nacionalidades_disponiveis = list(nomes_data.keys())

    if pais_sede:
        if pais_sede.startswith("[") and "]" in pais_sede:
            codigo_pais = pais_sede[1 : pais_sede.find("]")].upper()
            if codigo_pais in nacionalidades_disponiveis:
                # 70% de chance de ser da nacionalidade do país sede
                if random.random() < 0.70:
                    return codigo_pais

    return random.choice(nacionalidades_disponiveis)


def gerar_jogador_fraco(id_bot, pais_sede=None, genero="masculino"):
    from src.constantes import DEFAULT_ATRIBUTOS, DEFAULT_ATRIBUTOS_PSICOLOGICOS

    codigo_pais = gerar_nacionalidade_aleatoria(pais_sede)
    nome = gerar_nome_completo(codigo_pais, genero)

    # Busca nome do país para o formato amigável [BR] Brasil
    from src.dados import carregar_nacionalidades

    nac_data = carregar_nacionalidades()
    nome_pais = "Desconhecido"
    for continente in nac_data.values():
        for p in continente:
            if p.startswith(f"[{codigo_pais}]"):
                nome_pais = p
                break
        if nome_pais != "Desconhecido":
            break

    if nome_pais == "Desconhecido":
        nome_pais = f"[{codigo_pais}] {codigo_pais}"

    # Arquétipos básicos para diversidade
    arquetipos = ["base", "sacador", "saibrista", "rede"]
    arq = random.choice(arquetipos)

    # Base de atributos baixos (30-50)
    atributos = {k: random.randint(30, 50) for k in DEFAULT_ATRIBUTOS.keys()}
    atributos["fisico"] = random.randint(35, 55)

    if arq == "sacador":
        atributos["saque"] += 15
        atributos["winner"] += 5
    elif arq == "saibrista":
        atributos["topspin"] += 12
        atributos["movimento"] += 10
        atributos["fisico"] += 8
    elif arq == "rede":
        atributos["voleio"] += 15
        atributos["movimento"] += 5

    # Atributos psicológicos
    psico = {k: random.randint(30, 55) for k in DEFAULT_ATRIBUTOS_PSICOLOGICOS.keys()}

    # Cálculo de Overall Real (Técnico + Físico + Mental)
    avg_tec = sum(atributos.values()) / len(atributos)
    avg_psi = sum(psico.values()) / len(psico)
    overall = round((avg_tec * 0.8) + (avg_psi * 0.2))

    return {
        "nome": nome,
        "nacionalidade": nome_pais,
        "overall": overall,
        "pontos": random.randint(0, 30),
        "pontos_ranking": 0,
        "pontos_ytd": 0,
        "pontos_detalhados": [],
        "trofeus": [],
        "historico_torneios": [],
        "dinheiro": 500,
        "atributos": atributos,
        "atributos_psicologicos": psico,
        "moral": random.randint(60, 80),
        "fadiga": random.randint(0, 20),
        "energia": random.randint(80, 100),
        "is_bot": True,
        "genero": genero,
    }
