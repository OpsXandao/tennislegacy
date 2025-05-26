calendario = {
    1: [  # Semana 1
        {
            "nome": "Brisbane International",
            "tipo": "ATP 250",
            "local": "Brisbane",
            "quadra": "dura",
            "premiacao": 661585,
            "dificuldade": 2,
            "popularidade": 2,
            "qualificacao": True,
            "pais_sede": "[AU] Austrália",
            "ultimo_campeao": "Jiří Lehečka"
        },
        {
            "nome": "Hong Kong Open",
            "tipo": "ATP 250",
            "local": "Hong Kong",
            "quadra": "dura",
            "premiacao": 661585,
            "dificuldade": 2,
            "popularidade": 2,
            "qualificacao": True,
            "pais_sede": "[CN] China",
            "ultimo_campeao": "Alexandre Müller"
        }
    ],
    2: [
        {
            "nome": "ASB Classic",
            "tipo": "ATP 250",
            "local": "Auckland",
            "quadra": "dura",
            "premiacao": 661585,
            "dificuldade": 2,
            "popularidade": 2,
            "qualificacao": True,
            "pais_sede": "[NZ] Nova Zelândia",
            "ultimo_campeao": "Gaël Monfils"
        },
        {
            "nome": "Adelaide International",
            "tipo": "ATP 250",
            "local": "Adelaide",
            "quadra": "dura",
            "premiacao": 661585,
            "dificuldade": 2,
            "popularidade": 2,
            "qualificacao": True,
            "pais_sede": "[AU] Austrália",
            "ultimo_campeao": "Félix Auger-Aliassime"
        }
    ],
    3: [
        {
            "nome": "Australian Open",
            "tipo": "Grand Slam",
            "local": "Melbourne",
            "quadra": "dura",
            "premiacao": 76340925,
            "dificuldade": 5,
            "popularidade": 5,
            "qualificacao": True,
            "pais_sede": "[AU] Austrália",
            "ultimo_campeao": "Jannik Sinner "
        }
    ],
    4: [
        {
            "nome": "Open Sud de France",
            "tipo": "ATP 250",
            "local": "Montpellier",
            "premiacao": 76340925,
            "dificuldade": 5,
            "popularidade": 5,
            "qualificacao": True,
            "pais_sede": "[FR] França",
            "ultimo_campeao": "Félix Auger-Aliassime"
        }
    ]
}

def obter_torneios_da_semana(semana):
    return calendario.get(semana, [])
