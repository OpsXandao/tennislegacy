def _atributos_ordenados(atributos):
    if not isinstance(atributos, dict):
        return []
    return sorted(atributos.items(), key=lambda item: item[1], reverse=True)


def _obter_record_ranking(ranking, nome):
    if not ranking or not nome:
        return None
    return ranking.buscar_jogador_por_nome(nome)


def _normalizar_jogador_dict(jogador, ranking):
    if isinstance(jogador, dict):
        nome = jogador.get("nome", "Desconhecido")
        nacionalidade = jogador.get("nacionalidade", "??")
        atributos = jogador.get("atributos", {})
        overall = jogador.get("overall")
    else:
        nome = getattr(jogador, "nome", "Desconhecido")
        nacionalidade = getattr(jogador, "nacionalidade", "??")
        atributos = getattr(jogador, "atributos", {})
        overall = getattr(jogador, "calcular_overall", lambda: None)()

    record = _obter_record_ranking(ranking, nome)
    if overall is None and record:
        overall = record.get("overall")
    if overall is None:
        overall = round(sum(atributos.values()) / len(atributos)) if atributos else 60

    posicao = ranking.obter_posicao(nome) if ranking else None
    pontos = record.get("pontos") if record else None
    trofeus = record.get("trofeus", []) if record else []

    return {
        "nome": nome,
        "nacionalidade": nacionalidade,
        "atributos": atributos,
        "overall": overall,
        "posicao": posicao,
        "pontos": pontos,
        "trofeus": trofeus,
    }


def _chance_vitoria(jogador_a, jogador_b):
    total = jogador_a["overall"] + jogador_b["overall"]
    if total <= 0:
        return 0.5, 0.5
    chance_a = jogador_a["overall"] / total
    return chance_a, 1.0 - chance_a


def _vantagem_superficie(atributos_j: dict, atributos_a: dict, superficie: str) -> str:
    """Retorna uma linha de texto sobre vantagem de superfície, ou '' se nenhuma."""
    mods = {
        "saibro": {"chave": ["topspin", "movimento"], "label": "saibro"},
        "grama": {"chave": ["saque", "voleio"], "label": "grama"},
        "dura": {"chave": ["forehand", "backhand"], "label": "quadra dura"},
    }
    info = mods.get(superficie)
    if not info:
        return ""
    chave = info["chave"]
    label = info["label"]
    media_j = sum(atributos_j.get(k, 50) for k in chave) / len(chave)
    media_a = sum(atributos_a.get(k, 50) for k in chave) / len(chave)
    diff = media_j - media_a
    if abs(diff) < 3:
        return f"  Superfície ({label}): equilibrado"
    quem = "Você" if diff > 0 else "Adversário"
    return f"  Superfície ({label}): vantagem para {quem} ({abs(diff):.0f} pts em {', '.join(chave)})"


def _formatar_lista_atributos(atributos, quantidade=2):
    ordenados = _atributos_ordenados(atributos)
    if not ordenados:
        return "N/A"
    nomes = [nome for nome, _ in ordenados[:quantidade]]
    return ", ".join(nomes)


def _formatar_lista_atributos_fracos(atributos, quantidade=2):
    ordenados = _atributos_ordenados(atributos)
    if not ordenados:
        return "N/A"
    nomes = [nome for nome, _ in list(reversed(ordenados))[:quantidade]]
    return ", ".join(nomes)


def _formatar_trofeus(trofeus):
    if not trofeus:
        return "Sem registros"
    ultimos = trofeus[-3:]
    linhas = []
    for t in ultimos:
        torneio = t.get("torneio", "Torneio")
        tipo = t.get("tipo", "")
        semana = t.get("semana")
        ano = t.get("ano")
        meta = []
        if tipo:
            meta.append(tipo)
        if semana and ano:
            meta.append(f"Semana {semana}/{ano}")
        elif semana:
            meta.append(f"Semana {semana}")
        info = f"{torneio} ({', '.join(meta)})" if meta else torneio
        linhas.append(info)
    return "; ".join(linhas)


def exibir_stats_adversario(jogador, adversario, ranking, superficie: str = ""):
    adversario_info = _normalizar_jogador_dict(adversario, ranking)

    print("\n" + "=" * 44)
    print(f"  📊  {adversario_info['nome']}")
    print("=" * 44)
    if adversario_info["posicao"]:
        print(f"  Ranking      : #{adversario_info['posicao']}")
    if adversario_info["pontos"] is not None:
        print(f"  Pontos ATP   : {adversario_info['pontos']}")
    print(f"  Nacionalidade: {adversario_info['nacionalidade']}")
    print(f"  Overall      : {adversario_info['overall']}")
    print(f"  Pontos fortes: {_formatar_lista_atributos(adversario_info['atributos'])}")
    print(
        f"  Pontos fracos: {_formatar_lista_atributos_fracos(adversario_info['atributos'])}"
    )
    print(f"  Títulos      : {_formatar_trofeus(adversario_info['trofeus'])}")
    print("=" * 44)


def exibir_review_partida(jogador, adversario, ranking, superficie: str = ""):
    jogador_info = _normalizar_jogador_dict(jogador, ranking)
    adversario_info = _normalizar_jogador_dict(adversario, ranking)

    chance_j, chance_a = _chance_vitoria(jogador_info, adversario_info)

    print("\n" + "=" * 44)
    print(f"  🧪  REVIEW — {jogador_info['nome']} vs {adversario_info['nome']}")
    print("=" * 44)

    # Barômetro visual de chance de vitória
    barras_j = round(chance_j * 20)
    barras_a = 20 - barras_j
    print("\n  Chance de vitória")
    print(
        f"  {jogador_info['nome'][:14]:<14} {'█' * barras_j}{'░' * barras_a} {chance_j:.0%}"
    )
    print(
        f"  {adversario_info['nome'][:14]:<14} {'░' * barras_j}{'█' * barras_a} {chance_a:.0%}"
    )

    print("\n  Adversário")
    if adversario_info["posicao"]:
        print(f"    Ranking      : #{adversario_info['posicao']}")
    print(f"    Overall      : {adversario_info['overall']}")
    print(
        f"    Pontos fortes: {_formatar_lista_atributos(adversario_info['atributos'])}"
    )
    print(
        f"    Pontos fracos: {_formatar_lista_atributos_fracos(adversario_info['atributos'])}"
    )
    print(f"    Títulos      : {_formatar_trofeus(adversario_info['trofeus'])}")

    # Vantagem de superfície
    if superficie:
        from src.simulacao_partida import normalizar_superficie

        sup = normalizar_superficie(superficie)
        linha_sup = _vantagem_superficie(
            jogador_info["atributos"], adversario_info["atributos"], sup
        )
        if linha_sup:
            print(f"\n{linha_sup}")

    print("=" * 44)
