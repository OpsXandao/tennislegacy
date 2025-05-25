calendario_janeiro = {
    1: [  # Semana 1
        {
            "nome": "Brisbane International",
            "tipo": "ATP 250",
            "local": "Brisbane, Austrália",
            "premiacao": 661585,
            "dificuldade": 2,
            "popularidade": 2,
            "qualificacao": True,
            "pais_sede": "[AU] Austrália"
        },
        {
            "nome": "Hong Kong Open",
            "tipo": "ATP 250",
            "local": "Hong Kong, China",
            "premiacao": 661585,
            "dificuldade": 2,
            "popularidade": 2,
            "qualificacao": True,
            "pais_sede": "[CN] China"
        },
        {
            "nome": "United Cup",
            "tipo": "Torneio Misto",
            "local": "Sydney, Perth, Brisbane (Austrália)",
            "premiacao": 10000000,
            "dificuldade": 4,
            "popularidade": 4,
            "qualificacao": False,
            "pais_sede": "[AU] Austrália"
        }
    ],
    2: [
        {
            "nome": "ASB Classic",
            "tipo": "ATP 250",
            "local": "Auckland, Nova Zelândia",
            "premiacao": 661585,
            "dificuldade": 2,
            "popularidade": 2,
            "qualificacao": True,
            "pais_sede": "[NZ] Nova Zelândia"
        },
        {
            "nome": "Adelaide International",
            "tipo": "ATP 250",
            "local": "Adelaide, Austrália",
            "premiacao": 661585,
            "dificuldade": 2,
            "popularidade": 2,
            "qualificacao": True,
            "pais_sede": "[AU] Austrália"
        }
    ],
    3: [
        {
            "nome": "Australian Open",
            "tipo": "Grand Slam",
            "local": "Melbourne, Austrália",
            "premiacao": 76340925,
            "dificuldade": 5,
            "popularidade": 5,
            "qualificacao": True,
            "pais_sede": "[AU] Austrália"
        }
    ],
    4: []  # Descanso ou eventos menores
}

def obter_torneios_da_semana(semana):
    return calendario_janeiro.get(semana, [])