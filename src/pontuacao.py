import json
from src.dados import (
    get_caminho_ranking_save,
    get_caminho_torneio_save,
    carregar_temporada,
)
from src.json_utils import salvar_json_seguro
from src.log_jogo import log_simulacao
from src.ranking import SistemaRanking
from src.jogador import normalizar_nome
from src.jogador import carregar_jogador
from src.wta_constants import (
    PONTOS_WTA_250,
    PONTOS_WTA_500,
    PONTOS_WTA_1000,
    PONTOS_WTA_GRAND_SLAM,
)
from src.save import salvar_jogo

PONTOS_ATP_250 = {
    "campeao": 250,
    "final": 150,
    "semifinal": 90,
    "quartas": 45,
    "oitavas": 20,
    "r16": 20,
    "pre_oitavas": 10,  # Rodada de 32
    "r32": 10,
    "qualy_2": 5,  # Classificado
    "qualy_1": 0,
}

PONTOS_GRAND_SLAM = {
    "campeao": 2000,
    "final": 1200,
    "semifinal": 720,
    "quartas": 360,
    "r16": 180,  # Round of 16
    "oitavas": 180,
    "r32": 90,  # Round of 32
    "r64": 45,  # Round of 64
    "r128": 10,  # Round of 128 (first round loss)
    "qualy_r3": 30,  # Final round of qualifying
    "qualy_r2": 16,  # Second round of qualifying
    "qualy_r1": 7,  # First round of qualifying
}

PONTOS_ATP_500 = {
    "campeao": 500,
    "final": 300,
    "semifinal": 180,
    "quartas": 90,
    "oitavas": 45,  # Round of 16
    "r16": 45,
    "pre_oitavas": 20,  # Round of 32
    "r32": 20,
    "qualy_2": 10,  # Qualificado
    "qualy_1": 0,
}

PONTOS_ATP_1000 = {
    "campeao": 1000,
    "final": 600,
    "semifinal": 360,
    "quartas": 180,
    "oitavas": 90,  # Round of 16
    "r16": 90,
    "r32": 45,  # Round of 32
    "r64": 25,  # Round of 64
    "r96": 10,  # Round of 96
    "qualy_2": 16,  # Qualificado
    "qualy_1": 0,
}

PONTOS_CHALLENGER_125 = {
    "campeao": 125,
    "final": 85,
    "semifinal": 55,
    "quartas": 25,
    "oitavas": 13,
    "r16": 13,
    "pre_oitavas": 3,
    "r32": 3,
    "qualy_2": 0,
    "qualy_1": 0,
}

PONTOS_ITF_100 = {
    "campeao": 100,
    "final": 70,
    "semifinal": 40,
    "quartas": 20,
    "oitavas": 10,
    "r16": 10,
    "pre_oitavas": 2,
    "r32": 2,
    "qualy_2": 0,
    "qualy_1": 0,
}

PONTOS_ITF_25 = {
    "campeao": 25,
    "final": 18,
    "semifinal": 12,
    "quartas": 8,
    "oitavas": 4,
    "r16": 4,
    "pre_oitavas": 1,
    "r32": 1,
    "qualy_2": 0,
    "qualy_1": 0,
}

PONTOS_DAVIS_CUP = {
    "vitoria_simples_grupo": 50,
    "vitoria_simples_final8": 80,
    "vitoria_duplas_grupo": 20,
    "vitoria_duplas_final8": 30,
    "campeao_bonus": 150,
    "finalista_bonus": 80,
    "semifinalista_bonus": 40,
}

PONTOS_ATP_FINALS = {
    "campeao": 1500,
    "final": 1000,
    "semifinal": 500,
    "quartas": 200,
}

PONTOS_DUPLAS = {
    "ATP 250": {"campeao": 250, "final": 150, "semifinal": 90, "quartas": 45},
    "ATP 500": {
        "campeao": 500,
        "final": 300,
        "semifinal": 180,
        "quartas": 90,
        "oitavas": 45,
        "r16": 45,  # alias para "oitavas" (fase usada no draw de duplas)
    },
    "ATP 1000": {
        "campeao": 1000,
        "final": 600,
        "semifinal": 360,
        "quartas": 180,
        "oitavas": 90,
        "r16": 90,  # alias para "oitavas"
    },
    "ATP Finals": {
        "campeao": 1000,
        "final": 600,
        "semifinal": 300,
        "quartas": 120,
    },
    "Challenger 125": {
        "campeao": 125,
        "final": 85,
        "semifinal": 55,
        "quartas": 25,
        "oitavas": 13,
        "r16": 13,
    },
    "ITF 100": {
        "campeao": 100,
        "final": 70,
        "semifinal": 40,
        "quartas": 20,
        "oitavas": 10,
        "r16": 10,
    },
    "ITF 25": {
        "campeao": 25,
        "final": 18,
        "semifinal": 12,
        "quartas": 8,
        "oitavas": 4,
        "r16": 4,
    },
    "WTA Finals": {
        "campeao": 1000,
        "final": 600,
        "semifinal": 300,
        "quartas": 120,
    },
    # WTA: tabelas reduzidas com apenas as fases geradas em duplas
    "WTA 250": {"campeao": 250, "final": 163, "semifinal": 98, "quartas": 54},
    "WTA 500": {
        "campeao": 500,
        "final": 325,
        "semifinal": 195,
        "quartas": 108,
        "oitavas": 60,
        "r16": 60,  # alias para "oitavas"
    },
    "WTA 1000": {
        "campeao": 1000,
        "final": 650,
        "semifinal": 390,
        "quartas": 215,
        "oitavas": 120,
        "r16": 120,  # alias para "oitavas"
    },
    "Grand Slam": {
        "campeao": 2000,
        "final": 1200,
        "semifinal": 720,
        "quartas": 360,
        "oitavas": 180,
        "r16": 180,  # alias para "oitavas" (3ª rodada no draw de 64 pares)
        "r32": 90,  # 2ª rodada do draw de 64 pares
        "r64": 0,  # 1ª rodada (eliminados na entrada)
    },
}

SEMANAS_POR_ANO = 52
FATORES_PRIZE_POR_FASE = {
    "qualy_r3": 0.0035,
    "qualy_r2": 0.0022,
    "qualy_r1": 0.0012,
    "qualy_2": 0.0015,
    "qualy_1": 0.0008,
    "campeao": 0.18,
    "final": 0.10,
    "semifinal": 0.06,
    "quartas": 0.03,
    "oitavas": 0.015,
    "r16": 0.015,
    "pre_oitavas": 0.009,
    "r32": 0.009,
    "r64": 0.0045,
    "r128": 0.0025,
}


def _calcular_expiracao_pontos(semana_atual, ano_atual):
    """
    Pontos expiram na mesma semana do ano seguinte.
    """
    semana_expiracao = ((semana_atual - 1) % SEMANAS_POR_ANO) + 1
    ano_expiracao = int(ano_atual) + 1 if ano_atual is not None else None
    return semana_expiracao, ano_expiracao


def _eh_torneio_obrigatorio(tournament_type):
    return tournament_type in ("Grand Slam", "ATP 1000")


def _calcular_prize_por_fase(premiacao_total, fase):
    if not premiacao_total:
        return 0
    fator = FATORES_PRIZE_POR_FASE.get(fase, 0.0)
    valor_bruto = int(float(premiacao_total) * fator)

    # Realismo financeiro: Dedução de impostos (retidos na fonte) e
    # comissões da equipe técnica (treinador, empresário, etc).
    # No tênis real, sobe ~60-65% do valor bruto para o jogador.
    impostos_e_comissoes = 0.35  # 35% de dedução total
    valor_liquido = int(valor_bruto * (1.0 - impostos_e_comissoes))

    return valor_liquido


def obter_pontos_map(tournament_type, genero="masculino"):
    """Retorna o dicionário de pontos correto para o tipo de torneio e gênero."""
    if genero == "feminino":
        if tournament_type == "Grand Slam":
            return PONTOS_WTA_GRAND_SLAM
        if "1000" in tournament_type:
            return PONTOS_WTA_1000
        if "500" in tournament_type:
            return PONTOS_WTA_500
        return PONTOS_WTA_250
    else:
        if tournament_type == "Grand Slam":
            return PONTOS_GRAND_SLAM
        if tournament_type == "ATP 1000":
            return PONTOS_ATP_1000
        if tournament_type == "ATP 500":
            return PONTOS_ATP_500
        if tournament_type == "ATP Finals":
            return PONTOS_ATP_FINALS
        if tournament_type == "Challenger 125":
            return PONTOS_CHALLENGER_125
        if tournament_type == "ITF 100":
            return PONTOS_ITF_100
        if tournament_type == "ITF 25":
            return PONTOS_ITF_25
        return PONTOS_ATP_250


def _ordem_fases_pontuacao(tournament_type, modalidade="simples"):
    if modalidade != "simples":
        return ["r64", "r32", "r16", "quartas", "semifinal", "final"]
    if tournament_type == "Grand Slam":
        return [
            "qualy_r1",
            "qualy_r2",
            "qualy_r3",
            "r128",
            "r64",
            "r32",
            "r16",
            "quartas",
            "semifinal",
            "final",
        ]
    if "1000" in tournament_type:
        return [
            "qualy_1",
            "qualy_2",
            "r96",
            "r64",
            "r32",
            "r16",
            "quartas",
            "semifinal",
            "final",
        ]
    if "Challenger" in tournament_type:
        return [
            "qualy_1",
            "qualy_2",
            "r48",
            "r32",
            "r16",
            "quartas",
            "semifinal",
            "final",
        ]
    return [
        "qualy_1",
        "qualy_2",
        "pre_oitavas",
        "oitavas",
        "quartas",
        "semifinal",
        "final",
    ]


def _fase_pontuacao_desistencia(fase_saida, tournament_type, modalidade="simples"):
    fase_norm = str(fase_saida or "").strip().lower()
    if not fase_norm:
        return None
    if fase_norm.startswith("qualy"):
        return None

    fases = _ordem_fases_pontuacao(tournament_type, modalidade=modalidade)
    fases_principais = [fase for fase in fases if not str(fase).startswith("qualy")]
    try:
        idx = fases.index(fase_norm)
    except ValueError:
        return None

    primeira_fase_main_draw = (
        fases.index(fases_principais[0]) if fases_principais else 0
    )
    if idx <= primeira_fase_main_draw:
        return None
    return fases[idx - 1]


def distribuir_pontos_davis(nome_save, target_save_name=None):
    """
    Distribui pontos para a Copa Davis com base no desempenho individual e da equipe.
    """
    from src.davis_cup import carregar_davis_cup

    alvo = target_save_name or nome_save
    jogador_humano = carregar_jogador(alvo)
    ranking = SistemaRanking(
        get_caminho_ranking_save(
            alvo, genero=getattr(jogador_humano, "genero", "masculino")
        )
    )
    temporada = carregar_temporada(alvo)
    semana_atual = temporada["semana"]
    ano_atual = temporada.get("ano")
    semana_expiracao, ano_expiracao = _calcular_expiracao_pontos(
        semana_atual, ano_atual
    )

    # Carrega a instância da competição por seleções para acessar o estado
    davis = carregar_davis_cup(alvo, jogador_humano)
    if not davis:
        return

    estado = davis._carregar_estado()
    resultados_confrontos = estado.get("resultados_confrontos", [])

    if not resultados_confrontos:
        return

    # Mapeia vitórias individuais
    vitorias_por_jogador = {}
    for confronto in resultados_confrontos:
        fase = str(confronto.get("fase", "") or "").lower()
        is_final8 = fase in {"quartas", "semifinal", "final"}

        for partida in confronto.get("partidas", []):
            vencedor = partida.get("vencedor")
            if not vencedor:
                continue

            tipo = partida.get("tipo", "simples")
            pts = 0
            if tipo == "simples":
                pts = PONTOS_DAVIS_CUP[
                    "vitoria_simples_final8" if is_final8 else "vitoria_simples_grupo"
                ]
            else:
                pts = PONTOS_DAVIS_CUP[
                    "vitoria_duplas_final8" if is_final8 else "vitoria_duplas_grupo"
                ]

            # Se o vencedor for um dict (NPC) ou o nome (Player)
            nome_v = (
                vencedor.get("nome") if isinstance(vencedor, dict) else str(vencedor)
            )
            nome_v = normalizar_nome(nome_v)
            vitorias_por_jogador[nome_v] = vitorias_por_jogador.get(nome_v, 0) + pts

    # Distribui os pontos de vitórias individuais
    for nome_norm, pontos in vitorias_por_jogador.items():
        if pontos > 0:
            ranking.adicionar_pontos(nome_norm, pontos, semana_expiracao)

            # Atualiza YTD do jogador no ranking
            jogador_reg = ranking.buscar_jogador_por_nome(nome_norm)
            if jogador_reg:
                jogador_reg["pontos_ytd"] = jogador_reg.get("pontos_ytd", 0) + pontos
                # Se for o jogador humano, atualiza o objeto também
                if nome_norm == normalizar_nome(jogador_humano.nome):
                    jogador_humano.pontos_ytd = (
                        getattr(jogador_humano, "pontos_ytd", 0) + pontos
                    )

    # Bônus de equipe (Finalistas e Campeão)
    if estado.get("fase_atual") == "finalizado":
        vencedor_final = estado.get("vencedor_torneio")
        finalista = estado.get("finalista_torneio")

        if vencedor_final:
            _distribuir_bonus_equipe(
                ranking,
                vencedor_final,
                PONTOS_DAVIS_CUP["campeao_bonus"],
                semana_expiracao,
            )
        if finalista:
            _distribuir_bonus_equipe(
                ranking,
                finalista,
                PONTOS_DAVIS_CUP["finalista_bonus"],
                semana_expiracao,
            )

    ranking.ordenar()
    ranking.salvar_ranking()
    salvar_jogo(alvo, jogador_humano)
    log_simulacao("Pontos da Copa Davis distribuídos.", nome_save)


def _distribuir_bonus_equipe(ranking, pais, pontos, semana_expiracao):
    """Da bonus para todos os jogadores principais do pais."""
    # Pega o top 4 do país no ranking para dar o bônus de equipe
    jogadores_pais = [
        j
        for j in ranking.ranking
        if normalizar_nome(j.get("nacionalidade", "")) == normalizar_nome(pais)
    ]
    jogadores_pais.sort(key=lambda x: x.get("pontos_ranking", 0), reverse=True)

    for j in jogadores_pais[:4]:
        nome_norm = normalizar_nome(j.get("nome", ""))
        ranking.adicionar_pontos(nome_norm, pontos, semana_expiracao)
        j["pontos_ytd"] = j.get("pontos_ytd", 0) + pontos


def distribuir_pontos_torneio(nome_save, target_save_name=None, genero="masculino"):
    """
    Lê o resultado de um torneio finalizado em 'nome_save' e distribui os pontos
    no ranking de 'target_save_name' (ou 'nome_save' se não fornecido).
    """
    from src.dados import get_caminho_ranking_duplas

    caminho_torneio = get_caminho_torneio_save(nome_save, genero=genero)
    try:
        with open(caminho_torneio, "r", encoding="utf-8") as f:
            estado_torneio = json.load(f)
    except FileNotFoundError:
        return (
            f"Arquivo de torneio para o save '{nome_save}' não encontrado. "
            "Nenhum ponto a distribuir."
        )

    if estado_torneio.get("pontos_distribuidos"):
        return "Pontos do torneio ja distribuidos anteriormente."

    # O ranking e temporada alvo (quem recebe os pontos)
    alvo = target_save_name or nome_save
    ranking_simples = SistemaRanking(
        get_caminho_ranking_save(alvo, genero=genero), modalidade="simples"
    )
    ranking_duplas = SistemaRanking(
        get_caminho_ranking_duplas(alvo, genero=genero), modalidade="duplas"
    )
    temporada = carregar_temporada(alvo)

    semana_atual = temporada["semana"]
    ano_atual = temporada.get("ano")
    semana_expiracao, ano_expiracao = _calcular_expiracao_pontos(
        semana_atual, ano_atual
    )

    jogador_humano_nome = normalizar_nome(estado_torneio.get("jogador", ""))
    genero_torneio = estado_torneio.get("genero", "masculino")
    tournament_type = estado_torneio.get("tournament_data", {}).get("tipo", "ATP 250")
    nome_torneio = estado_torneio.get("torneio", "Torneio Desconhecido")
    premiacao_total = estado_torneio.get("tournament_data", {}).get("premiacao", 0)

    # --- PARTE 1: SIMPLES ---
    _processar_pontos_modalidade(
        ranking_simples,
        estado_torneio,
        estado_torneio.get("resultados", {}),
        tournament_type,
        genero_torneio,
        "simples",
        semana_expiracao,
        ano_expiracao,
        nome_torneio,
        premiacao_total,
        semana_atual,
        ano_atual,
        nome_save,
        alvo,
    )

    # --- PARTE 2: DUPLAS ---
    _processar_pontos_modalidade(
        ranking_duplas,
        estado_torneio,
        estado_torneio.get("resultados_duplas", {}),
        tournament_type,
        genero_torneio,
        "duplas",
        semana_expiracao,
        ano_expiracao,
        nome_torneio,
        0,  # Premiação de duplas (pode ser expandido depois)
        semana_atual,
        ano_atual,
        nome_save,
        alvo,
    )

    ranking_simples.salvar_ranking()
    ranking_duplas.salvar_ranking()
    estado_torneio["pontos_distribuidos"] = True
    salvar_json_seguro(caminho_torneio, estado_torneio)


def _extract_names(raw):
    """Extrai lista de nomes normalizados de uma entrada de partida (jogador, dupla ou string legada)."""
    if not raw:
        return []
    if isinstance(raw, dict):
        if "jogadores" in raw:
            return [
                normalizar_nome(j.get("nome", ""))
                for j in raw["jogadores"]
                if isinstance(j, dict)
            ]
        return [normalizar_nome(raw.get("nome", ""))]
    return [normalizar_nome(n.strip()) for n in str(raw).split("/")]


def _registrar_historico_torneio(destino, entrada: dict) -> None:
    if isinstance(destino, dict):
        historico = list(destino.get("historico_torneios", []) or [])
    else:
        historico = list(getattr(destino, "historico_torneios", []) or [])

    chave_entrada = (
        normalizar_nome(entrada.get("nome", "")),
        str(entrada.get("tipo", "") or ""),
        int(entrada.get("ano", 0) or 0),
        int(entrada.get("semana", 0) or 0),
        str(entrada.get("modalidade", "simples") or "simples"),
    )

    atualizado = False
    for idx, item in enumerate(historico):
        if not isinstance(item, dict):
            continue
        chave_item = (
            normalizar_nome(item.get("nome", item.get("torneio", ""))),
            str(item.get("tipo", "") or ""),
            int(item.get("ano", 0) or 0),
            int(item.get("semana", 0) or 0),
            str(item.get("modalidade", "simples") or "simples"),
        )
        if chave_item == chave_entrada:
            historico[idx] = {**item, **entrada}
            atualizado = True
            break

    if not atualizado:
        historico.append(entrada)

    if isinstance(destino, dict):
        destino["historico_torneios"] = historico
    else:
        destino.historico_torneios = historico


def _processar_pontos_modalidade(
    ranking,
    estado_torneio,
    resultados,
    tournament_type,
    genero_torneio,
    modalidade,
    semana_expiracao,
    ano_expiracao,
    nome_torneio,
    premiacao_total,
    semana_atual,
    ano_atual,
    nome_save,
    alvo,
):
    if not resultados:
        return

    if modalidade == "simples":
        pontos_map = obter_pontos_map(tournament_type, genero_torneio)
        fases_ordem = _ordem_fases_pontuacao(tournament_type, modalidade)
    else:
        pontos_map = PONTOS_DUPLAS.get(tournament_type, PONTOS_DUPLAS.get("ATP 250"))
        fases_ordem = _ordem_fases_pontuacao(tournament_type, modalidade)

    progresso_jogador = {}
    chave_a, chave_b = ("jogador_a", "jogador_b")

    for fase in fases_ordem:
        for partida in resultados.get(fase, []):
            try:
                p_a_raw = partida.get(chave_a, {})
                p_b_raw = partida.get(chave_b, {})
                v_raw = partida.get("vencedor", {})

                nomes_a = _extract_names(p_a_raw)
                nomes_b = _extract_names(p_b_raw)
                nomes_v = _extract_names(v_raw)

                for n in nomes_a:
                    if n:
                        progresso_jogador[n] = fase
                for n in nomes_b:
                    if n:
                        progresso_jogador[n] = fase

                try:
                    idx = fases_ordem.index(fase)
                    if idx + 1 < len(fases_ordem):
                        for n in nomes_v:
                            if n:
                                progresso_jogador[n] = fases_ordem[idx + 1]
                except ValueError:
                    pass
            except Exception:
                continue

    if "final" in resultados and resultados["final"]:
        v_final = resultados["final"][0].get("vencedor", {})
        for n in _extract_names(v_final):
            if n:
                progresso_jogador[n] = "campeao"

    log_simulacao(
        f"Pontuação do Torneio ({modalidade.upper()}): {nome_torneio} ({tournament_type})",
        nome_save,
    )

    # Carrega jogador humano para atualizar dinheiro se necessário
    jogador_humano = carregar_jogador(alvo)
    human_name_norm = normalizar_nome(jogador_humano.nome) if jogador_humano else ""
    jogador_humano_atualizado = False

    for jogador_nome_norm, progresso_fase in progresso_jogador.items():
        fase_historico = progresso_fase
        pontos_base = pontos_map.get(progresso_fase, 0)

        if (
            modalidade == "simples"
            and estado_torneio.get("desistencia_jogador")
            and jogador_nome_norm == normalizar_nome(estado_torneio.get("jogador", ""))
        ):
            fase_pontos = _fase_pontuacao_desistencia(
                estado_torneio.get("jogador_fase_saida"),
                tournament_type,
                modalidade=modalidade,
            )
            pontos_base = pontos_map.get(fase_pontos, 0) if fase_pontos else 0
            fase_historico = (
                str(estado_torneio.get("jogador_fase_saida") or progresso_fase)
                if estado_torneio.get("jogador_fase_saida")
                else progresso_fase
            )

        # Cálculo do Dinheiro
        prize = 0
        if modalidade == "simples":
            prize = _calcular_prize_por_fase(premiacao_total, fase_historico)
        else:
            # Em duplas o prêmio costuma ser ~25% do de simples por jogador
            prize = int(
                _calcular_prize_por_fase(premiacao_total, fase_historico) * 0.25
            )

        # 1. Adiciona pontos ao ranking
        if pontos_base > 0:
            ranking.adicionar_pontos(
                jogador_nome_norm,
                pontos_base,
                semana_expiracao,
                modalidade=modalidade,
                ano_exp=ano_expiracao,
                metadados={
                    "torneio": nome_torneio,
                    "tipo": tournament_type,
                    "semana_origem": semana_atual,
                    "ano_origem": ano_atual,
                    "fase": fase_historico,
                    "modalidade": modalidade,
                },
            )

        # 2. Credita dinheiro no ranking
        if prize > 0:
            ranking.adicionar_dinheiro(jogador_nome_norm, prize)

            # 3. Se for o jogador humano, atualiza o objeto Jogador
            if jogador_nome_norm == human_name_norm and jogador_humano:
                jogador_humano.dinheiro = getattr(jogador_humano, "dinheiro", 0) + prize

        jogador_ranking = ranking.buscar_jogador_por_nome(jogador_nome_norm)
        entrada_historico = {
            "nome": nome_torneio,
            "torneio": nome_torneio,
            "tipo": tournament_type,
            "semana": semana_atual,
            "ano": ano_atual,
            "fase": fase_historico,
            "fase_alcancada": fase_historico,
            "pontos": int(pontos_base),
            "premio": int(prize),
            "modalidade": modalidade,
            "obrigatorio": bool(_eh_torneio_obrigatorio(tournament_type)),
            "expirado": False,
        }

        if jogador_ranking:
            _registrar_historico_torneio(jogador_ranking, entrada_historico)

        if jogador_nome_norm == human_name_norm and jogador_humano:
            _registrar_historico_torneio(jogador_humano, entrada_historico)
            jogador_humano_atualizado = True

        log_simulacao(
            f"  {jogador_nome_norm}: {pontos_base} pts / ${prize} ({fase_historico})",
            nome_save,
        )

    if jogador_humano and jogador_humano_atualizado:
        salvar_jogo(alvo, jogador_humano)

    ranking.ordenar()
