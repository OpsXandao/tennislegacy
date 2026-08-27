def serializar_participante_api(participante):
    if isinstance(participante, dict):
        return participante
    if hasattr(participante, "to_dict"):
        return participante.to_dict()
    if isinstance(participante, str):
        return {"nome": participante, "nacionalidade": "??"}
    return {"nome": str(participante), "nacionalidade": "??"}

def serializar_confronto_api(confronto, fase, indice, estado, ranking, jogador_nome, jogador_nacionalidade, modalidade="simples"):
    resultados_por_fase = estado.get(
        "resultados_duplas" if modalidade == "duplas" else "resultados",
        {},
    )
    resultados_fase = resultados_por_fase.get(fase, [])

    def _extrair_nome_resultado(valor):
        if isinstance(valor, dict):
            return str(valor.get("nome", ""))
        return str(valor or "")

    def _extrair_placar_resultado(resultado):
        return resultado.get("placar") or resultado.get("resultado")

    def _nome_participante(participante):
        if isinstance(participante, dict):
            return participante.get("nome", str(participante))
        return str(participante)

    def _nacionalidade_participante(participante, nome):
        if isinstance(participante, dict):
            return participante.get("nacionalidade", "??")
        if nome == jogador_nome:
            return jogador_nacionalidade
        jogador_ranking = ranking.buscar_jogador_por_nome(nome)
        if jogador_ranking:
            return jogador_ranking.get("nacionalidade", "??")
        return "??"

    def _buscar_resultado(jogador1, jogador2):
        nomes_alvo = {(str(jogador1), str(jogador2)), (str(jogador2), str(jogador1))}
        for resultado in resultados_fase:
            par = (
                _extrair_nome_resultado(resultado.get("jogador1", resultado.get("jogador_a"))),
                _extrair_nome_resultado(resultado.get("jogador2", resultado.get("jogador_b"))),
            )
            if par in nomes_alvo:
                return {
                    "vencedor": _extrair_nome_resultado(resultado.get("vencedor")),
                    "placar": _extrair_placar_resultado(resultado),
                }
        return {}

    if not isinstance(confronto, (list, tuple)) or len(confronto) != 2:
        return {
            "id": f"{modalidade}:{fase}:{indice}",
            "fase": fase,
            "jogador1": str(confronto),
            "jogador2": "",
            "vencedor": None,
            "placar": None,
        }

    j1 = _nome_participante(confronto[0])
    j2 = _nome_participante(confronto[1])
    return {
        "id": f"{modalidade}:{fase}:{indice}",
        "fase": fase,
        "jogador1": j1,
        "jogador2": j2,
        "jogador1_nacionalidade": _nacionalidade_participante(confronto[0], j1),
        "jogador2_nacionalidade": _nacionalidade_participante(confronto[1], j2),
        "vencedor": _buscar_resultado(j1, j2).get("vencedor"),
        "placar": _buscar_resultado(j1, j2).get("placar"),
    }

def to_api_state(torneio_inst):
    estado = torneio_inst._carregar_estado()
    bracket = []

    def _serializar_resultado_avulso(resultado, fase, indice, modalidade="simples"):
        j1 = resultado.get("jogador_a", resultado.get("jogador1", {}))
        j2 = resultado.get("jogador_b", resultado.get("jogador2", {}))
        return serializar_confronto_api(
            [j1, j2],
            fase,
            indice,
            {("resultados_duplas" if modalidade == "duplas" else "resultados"): {fase: [resultado]}},
            torneio_inst.ranking,
            torneio_inst.jogador_nome,
            torneio_inst.jogador_nacionalidade,
            modalidade=modalidade,
        )

    def _ordem_resultados_por_proxima_fase(fase, resultados, modalidade):
        if not hasattr(torneio_inst, "_fases_ordem"):
            return resultados
        try:
            fases = torneio_inst._fases_ordem()
        except Exception:
            return resultados
        if fase not in fases:
            return resultados
        idx = fases.index(fase)
        if idx + 1 >= len(fases):
            return resultados
        proxima_fase = fases[idx + 1]
        rodadas_chave = "rodadas_duplas" if modalidade == "duplas" else "rodadas"
        proximos = estado.get(rodadas_chave, {}).get(proxima_fase, [])
        if not proximos:
            return resultados

        ordem = []
        for confronto in proximos:
            if not isinstance(confronto, (list, tuple)) or len(confronto) != 2:
                continue
            for participante in confronto:
                if isinstance(participante, dict):
                    ordem.append(participante.get("nome", ""))
                else:
                    ordem.append(str(participante))

        def _nome_vencedor(resultado):
            vencedor = resultado.get("vencedor")
            if isinstance(vencedor, dict):
                return vencedor.get("nome", "")
            return str(vencedor or "")

        indice_por_nome = {nome: i for i, nome in enumerate(ordem)}
        return sorted(
            resultados,
            key=lambda resultado: indice_por_nome.get(_nome_vencedor(resultado), 9999),
        )

    def _adicionar_modalidade(modalidade):
        rodadas_chave = "rodadas_duplas" if modalidade == "duplas" else "rodadas"
        resultados_chave = (
            "resultados_duplas" if modalidade == "duplas" else "resultados"
        )

        fases = []
        for fase in estado.get(rodadas_chave, {}).keys():
            if fase not in fases:
                fases.append(fase)
        for fase in estado.get(resultados_chave, {}).keys():
            if fase not in fases:
                fases.append(fase)

        for fase in fases:
            confrontos = estado.get(rodadas_chave, {}).get(fase, [])
            if confrontos:
                for i, confronto in enumerate(confrontos, 1):
                    bracket.append(
                        serializar_confronto_api(
                            confronto,
                            fase,
                            i,
                            estado,
                            torneio_inst.ranking,
                            torneio_inst.jogador_nome,
                            torneio_inst.jogador_nacionalidade,
                            modalidade=modalidade,
                        )
                    )
                continue

            resultados = estado.get(resultados_chave, {}).get(fase, [])
            resultados = _ordem_resultados_por_proxima_fase(fase, resultados, modalidade)
            for i, resultado in enumerate(resultados, 1):
                bracket.append(_serializar_resultado_avulso(resultado, fase, i, modalidade))

    _adicionar_modalidade("simples")
    _adicionar_modalidade("duplas")

    return {
        "nome": torneio_inst.nome_torneio_atual,
        "tipo": torneio_inst.tournament_data.get("tipo"),
        "superficie": torneio_inst.tournament_data.get("quadra", "dura"),
        "fase_atual": estado.get("fase_atual"),
        "bracket": bracket,
        "jogador_ativo": bool(estado.get("jogador_vivo", False)),
        "campeao_simples": estado.get("campeao_simples"),
        "fase_atual_duplas": estado.get("fase_atual_duplas"),
        "jogador_ativo_duplas": bool(estado.get("jogador_vivo_duplas", False)),
        "entry_status": estado.get("entry_status", {}),
        "entry_list_summary": estado.get("entry_list_summary", {}),
        "cutoff_rank": estado.get("cutoff_rank"),
        "qualy_cutoff_rank": estado.get("qualy_cutoff_rank"),
        "entry_deadline_week": estado.get("entry_deadline_week"),
        "alternates": estado.get("alternates", []),
        "wildcards": estado.get("wildcards", []),
        "lucky_losers": estado.get("lucky_losers", []),
        "resultados": estado.get("resultados", {}),
        "resultados_duplas": estado.get("resultados_duplas", {}),
        "agenda_dia": estado.get("agenda_dia", {}),
        "estado": estado,
    }
