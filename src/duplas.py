import random
from src.jogador import normalizar_nome


def fundir_dupla(jogador1, jogador2, nome_equipe=None, vinculo=None):
    """
    Funde os atributos de dois jogadores em uma única 'Equipe'
    para ser simulada no motor de partida 1v1.
    """
    attr1 = (
        jogador1.get("atributos", {})
        if isinstance(jogador1, dict)
        else getattr(jogador1, "atributos", {})
    )
    attr2 = (
        jogador2.get("atributos", {})
        if isinstance(jogador2, dict)
        else getattr(jogador2, "atributos", {})
    )

    psico1 = (
        jogador1.get("atributos_psicologicos", {})
        if isinstance(jogador1, dict)
        else getattr(jogador1, "atributos_psicologicos", {})
    )
    psico2 = (
        jogador2.get("atributos_psicologicos", {})
        if isinstance(jogador2, dict)
        else getattr(jogador2, "atributos_psicologicos", {})
    )

    # Regras de Sinergia de Duplas
    atributos_equipe = {
        # Em duplas, cada jogador serve metade dos games — o melhor sacador dita o ritmo
        "saque": max(attr1.get("saque", 50), attr2.get("saque", 50)),
        "forehand": (attr1.get("forehand", 50) + attr2.get("forehand", 50)) // 2,
        "backhand": (attr1.get("backhand", 50) + attr2.get("backhand", 50)) // 2,
        "topspin": (attr1.get("topspin", 50) + attr2.get("topspin", 50)) // 2,
        "voleio": max(attr1.get("voleio", 50), attr2.get("voleio", 50))
        + 5,  # Bônus de cobertura de rede
        "slice": (attr1.get("slice", 50) + attr2.get("slice", 50)) // 2,
        "movimento": (attr1.get("movimento", 50) + attr2.get("movimento", 50)) // 2,
        "lob": max(attr1.get("lob", 50), attr2.get("lob", 50)),
        "winner": (attr1.get("winner", 50) + attr2.get("winner", 50)) // 2,
        "fisico": (attr1.get("fisico", 50) + attr2.get("fisico", 50)) // 2,
        "duplas": (attr1.get("duplas", 60) + attr2.get("duplas", 60)) // 2,
    }

    psico_equipe = {
        "concentracao": max(
            psico1.get("concentracao", 50), psico2.get("concentracao", 50)
        ),
        "agressividade": (
            psico1.get("agressividade", 50) + psico2.get("agressividade", 50)
        )
        // 2,
        "leitura_de_jogo": max(
            psico1.get("leitura_de_jogo", 50), psico2.get("leitura_de_jogo", 50)
        ),
        "determinacao": max(
            psico1.get("determinacao", 50), psico2.get("determinacao", 50)
        ),
    }

    if not nome_equipe:
        nome1 = (
            jogador1.get("nome", "J1")
            if isinstance(jogador1, dict)
            else getattr(jogador1, "nome", "J1")
        )
        nome2 = (
            jogador2.get("nome", "J2")
            if isinstance(jogador2, dict)
            else getattr(jogador2, "nome", "J2")
        )
        nome_equipe = f"{nome1.split()[-1]} / {nome2.split()[-1]}"

    # Overall base exclui duplas e voleio (ambos têm peso próprio)
    atributos_base = {
        k: v for k, v in atributos_equipe.items() if k not in ("duplas", "voleio")
    }
    overall_base = sum(atributos_base.values()) // max(1, len(atributos_base))

    # Bônus de especialidade em duplas: cada ponto acima de 60 vale 0.5 no overall
    duplas_media = atributos_equipe.get("duplas", 60)
    bonus_duplas_attr = int((duplas_media - 60) * 0.5)

    # Bônus de voleio: fundamental em duplas — melhor dos dois, cada ponto acima de 60 vale 0.4
    voleio_melhor = max(
        attr1.get("voleio", 50),
        attr2.get("voleio", 50),
    )
    bonus_voleio = int(max(0, (voleio_melhor - 60) * 0.4))

    # Bônus de Sinergia
    nac1 = (
        jogador1.get("nacionalidade", "")
        if isinstance(jogador1, dict)
        else getattr(jogador1, "nacionalidade", "")
    )
    nac2 = (
        jogador2.get("nacionalidade", "")
        if isinstance(jogador2, dict)
        else getattr(jogador2, "nacionalidade", "")
    )
    bonus_nac = 5 if (nac1[:4] == nac2[:4] and nac1) else 0

    bonus_vinculo = 0
    partes_sinergia = []
    if bonus_nac:
        partes_sinergia.append("compatriotas")
    if bonus_voleio >= 4:
        partes_sinergia.append(f"voleio de rede ({voleio_melhor})")

    if isinstance(vinculo, dict):
        partidas = vinculo.get("partidas", 0)
        vitorias = vinculo.get("vitorias", 0)
        win_rate = vitorias / partidas if partidas > 0 else 0.0

        if partidas >= 10:
            bonus_vinculo = 6
        elif partidas >= 5:
            bonus_vinculo = 4
        elif partidas >= 1:
            bonus_vinculo = 2

        if win_rate >= 0.60 and partidas >= 1:
            bonus_vinculo += 2

        if bonus_vinculo:
            partes_sinergia.append(f"{partidas} partidas juntos")

    descricao_sinergia = " | ".join(partes_sinergia)

    overall = min(
        99, overall_base + bonus_duplas_attr + bonus_voleio + bonus_nac + bonus_vinculo
    )

    # Energia e lesão: usa o pior dos dois (qualquer parceiro inapto = dupla inapta)
    energia1 = int(
        jogador1.get("energia", 100)
        if isinstance(jogador1, dict)
        else getattr(jogador1, "energia", 100) or 100
    )
    energia2 = int(
        jogador2.get("energia", 100)
        if isinstance(jogador2, dict)
        else getattr(jogador2, "energia", 100) or 100
    )
    lesao1 = (
        jogador1.get("status_lesao", {})
        if isinstance(jogador1, dict)
        else getattr(jogador1, "status_lesao", {})
    )
    lesao2 = (
        jogador2.get("status_lesao", {})
        if isinstance(jogador2, dict)
        else getattr(jogador2, "status_lesao", {})
    )
    lesionado = (isinstance(lesao1, dict) and bool(lesao1.get("lesionado"))) or (
        isinstance(lesao2, dict) and bool(lesao2.get("lesionado"))
    )

    nacionalidade_equipe = nac1 if (bonus_nac and nac1) else "Mix"

    return {
        "nome": nome_equipe,
        "nacionalidade": nacionalidade_equipe,
        "atributos": atributos_equipe,
        "atributos_psicologicos": psico_equipe,
        "overall": overall,
        "bonus_aplicado": bonus_nac + bonus_vinculo,
        "descricao_sinergia": descricao_sinergia,
        "is_dupla": True,
        "jogadores": [jogador1, jogador2],
        "energia": min(energia1, energia2),
        "status_lesao": {"lesionado": lesionado},
    }


def tentar_convidar_parceiro(
    jogador, npc, ranking_pos=999, torneio_tipo="ATP 250", vinculo=None
):
    """
    Calcula a chance de um NPC aceitar o convite.
    Tops (Top 30) raramente aceitam duplas fora de GS ou Davis.
    """
    ovr_jogador = (
        jogador.calcular_overall()
        if hasattr(jogador, "calcular_overall")
        else jogador.get("overall", 50)
    )
    ovr_npc = npc.get("overall", 50)

    # 1. Regra de Elite (Realismo)
    if ranking_pos <= 30 and torneio_tipo not in [
        "Grand Slam",
        "Davis Cup",
        "Billie Jean King Cup",
        "United Cup",
    ]:
        # Só aceita se for compatriota e olhe lá
        nac_j = (
            jogador.nacionalidade
            if hasattr(jogador, "nacionalidade")
            else jogador.get("nacionalidade", "")
        )
        if nac_j[:4] != npc["nacionalidade"][:4]:
            return (
                False,
                f"{npc['nome']} está focado 100% no quadro de simples este ano.",
            )
        else:
            if random.random() > 0.2:  # 20% de chance mesmo sendo compatriota
                return (
                    False,
                    f"{npc['nome']} prefere poupar o físico para a chave individual.",
                )

    # 2. Diferença de Nível
    diff = abs(ovr_jogador - ovr_npc)
    if ovr_npc > 80 and diff > 8:
        return False, f"{npc['nome']} busca um parceiro com ranking mais alto."

    # 3. Chance Base
    chance = 0.5

    # Bônus Nacionalidade
    mesmo_pais = False
    nac_j = (
        jogador.nacionalidade
        if hasattr(jogador, "nacionalidade")
        else jogador.get("nacionalidade", "")
    )
    if nac_j[:4] == npc["nacionalidade"][:4]:
        chance += 0.3
        mesmo_pais = True

    # Bônus Ranking
    if diff < 5:
        chance += 0.2

    # Bônus Vínculo
    if isinstance(vinculo, dict):
        partidas = vinculo.get("partidas", 0)
        vitorias = vinculo.get("vitorias", 0)
        win_rate = vitorias / partidas if partidas > 0 else 0.0

        if partidas >= 10:
            chance += 0.20
        elif partidas >= 5:
            chance += 0.15
        elif partidas >= 1:
            chance += 0.10

        if win_rate >= 0.60 and partidas >= 1:
            chance += 0.10

    chance = min(0.95, chance)

    # Sorteio
    sucesso = random.random() < chance

    if sucesso:
        msg = (
            f"{npc['nome']} aceitou! 'Bora pra quadra, parceiro!'"
            if mesmo_pais
            else f"{npc['nome']} aceitou seu convite."
        )
        return True, msg
    else:
        return False, f"{npc['nome']} já fechou com outro parceiro para esta semana."


def buscar_parceiro_por_ranking(ranking_completo, n=100, nome_jogador_excluir=None):
    """Retorna os top N jogadores do ranking para escolha manual."""
    nome_excluir_norm = (
        normalizar_nome(nome_jogador_excluir) if nome_jogador_excluir else ""
    )
    return [
        p
        for p in ranking_completo[:n]
        if normalizar_nome(p.get("nome", "")) != nome_excluir_norm
    ]


def buscar_parceiro_por_nacionalidade(
    ranking_completo, nacionalidade, nome_jogador_excluir=None
):
    """Filtra jogadores do ranking pela mesma nacionalidade, aceitando vários formatos."""
    if not nacionalidade:
        return []

    nome_excluir_norm = (
        normalizar_nome(nome_jogador_excluir) if nome_jogador_excluir else ""
    )

    # Normaliza a entrada da busca
    busca = nacionalidade.strip().upper()
    # Se o usuário digitou "BR", transforma em "[BR]" para o prefixo
    if len(busca) == 2 and not busca.startswith("["):
        busca_prefix = f"[{busca}]"
    elif busca.startswith("[") and "]" in busca:
        busca_prefix = busca[: busca.find("]") + 1]
    else:
        # Se digitou o nome do país (ex: Brasil), busca por substring na nacionalidade do jogador
        busca_prefix = busca

    candidatos = []
    for p in ranking_completo:
        if normalizar_nome(p.get("nome", "")) == nome_excluir_norm:
            continue

        nac_jogador = p.get("nacionalidade", "").upper()

        # Match por prefixo [BR] ou substring do nome do país
        if nac_jogador.startswith(busca_prefix) or busca_prefix in nac_jogador:
            candidatos.append(p)

    return candidatos


def _duplas_score(p):
    """Score para duplas: 60% overall de simples + 40% atributo duplas."""
    if hasattr(p, "calcular_overall"):
        ovr = p.calcular_overall()
        d = getattr(p, "atributos", {}).get("duplas", 60)
    else:
        ovr = p.get("overall", 50)
        atrs = p.get("atributos", {})
        d = atrs.get("duplas", 60) if isinstance(atrs, dict) else 60
    return round(ovr * 0.6 + d * 0.4)


def buscar_parceiros_disponiveis(jogador, pool_ranking, n=15, vinculos=None):
    """
    Retorna uma lista de jogadores com score de duplas próximo ao do jogador.
    Parceiros anteriores (presentes em vinculos) aparecem primeiro.
    Cada candidato terá o campo _vinculo injetado (dict ou None).
    O pool_ranking já deve vir filtrado pelo gênero correto (mesmo ou oposto).
    """
    score_j = _duplas_score(jogador)
    nome_jogador = jogador.nome if hasattr(jogador, "nome") else jogador.get("nome", "")
    nome_jogador_norm = normalizar_nome(nome_jogador)
    vinculos = vinculos or {}

    candidatos_raw = [
        p
        for p in pool_ranking
        if abs(_duplas_score(p) - score_j) <= 20
        and normalizar_nome(p.get("nome", "")) != nome_jogador_norm
    ]

    # Fallback: amplia para todo o ranking ordenado por proximidade de score.
    if not candidatos_raw:
        candidatos_raw = sorted(
            [
                p
                for p in pool_ranking
                if normalizar_nome(p.get("nome", "")) != nome_jogador_norm
            ],
            key=lambda p: abs(_duplas_score(p) - score_j),
        )

    nomes_vinculos = {normalizar_nome(k) for k in vinculos}

    anteriores = []
    novos = []
    for p in candidatos_raw:
        nome_norm = normalizar_nome(p.get("nome", ""))
        vinculo_entry = vinculos.get(p.get("nome", "")) or vinculos.get(
            next((k for k in vinculos if normalizar_nome(k) == nome_norm), ""), None
        )
        c = dict(p)
        c["_vinculo"] = vinculo_entry
        if nome_norm in nomes_vinculos:
            anteriores.append(c)
        else:
            novos.append(c)

    # Anteriores: ordenar por partidas desc
    anteriores.sort(key=lambda x: x["_vinculo"].get("partidas", 0), reverse=True)
    # Novos: embaralhar
    random.shuffle(novos)

    return (anteriores + novos)[:n]
