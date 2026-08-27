import json

from src.dados import (
    carregar_temporada,
    get_caminho_ranking_save,
    get_caminho_torneio_save,
)
from src.jogador import carregar_jogador, normalizar_nome
from src.utils.json_utils import salvar_json_seguro
from src.utils.log_jogo import log_simulacao
from src.ranking import SistemaRanking
from src.save import salvar_jogo
from src.constants.wta_constants import (
    PONTOS_WTA_1000,
    PONTOS_WTA_250,
    PONTOS_WTA_500,
    PONTOS_WTA_GRAND_SLAM,
)
from src.constants.pontuacao_tabelas import (
    FATORES_PRIZE_POR_FASE,
    PONTOS_ATP_1000,
    PONTOS_ATP_250,
    PONTOS_ATP_500,
    PONTOS_ATP_FINALS,
    PONTOS_CHALLENGER_125,
    PONTOS_DAVIS_CUP,
    PONTOS_DUPLAS,
    PONTOS_GRAND_SLAM,
    PONTOS_ITF_100,
    PONTOS_ITF_25,
    SEMANAS_POR_ANO,
)

# Re-exports para compatibilidade com importadores externos
__all__ = [
    "FATORES_PRIZE_POR_FASE",
    "PONTOS_ATP_1000",
    "PONTOS_ATP_250",
    "PONTOS_ATP_500",
    "PONTOS_ATP_FINALS",
    "PONTOS_CHALLENGER_125",
    "PONTOS_DAVIS_CUP",
    "PONTOS_DUPLAS",
    "PONTOS_GRAND_SLAM",
    "PONTOS_ITF_100",
    "PONTOS_ITF_25",
    "SEMANAS_POR_ANO",
    "aplicar_penalidade_ausencia",
    "distribuir_pontos_davis",
    "distribuir_pontos_torneio",
    "obter_pontos_map",
]


def _calcular_expiracao_pontos(semana_atual, ano_atual):
    semana_expiracao = ((semana_atual - 1) % SEMANAS_POR_ANO) + 1
    ano_expiracao = int(ano_atual) + 1 if ano_atual is not None else None
    return semana_expiracao, ano_expiracao


def _eh_torneio_obrigatorio(tournament_type):
    return tournament_type in ("Grand Slam", "ATP 1000", "WTA 1000")


def aplicar_penalidade_ausencia(
    nome_save, nome_torneio, tipo_torneio, semana, ano, genero="masculino"
):
    """Injeta bloco de 0 pts para torneio obrigatorio que o jogador pulou.

    Idempotente: se o jogador ja tem qualquer bloco registrado para este
    torneio na semana em questao (ou seja, jogou pelo menos a 1a rodada),
    a funcao retorna sem fazer nada.
    """
    if not _eh_torneio_obrigatorio(tipo_torneio):
        return

    jogador_humano = carregar_jogador(nome_save)
    if not jogador_humano:
        return

    nome_jogador_norm = normalizar_nome(jogador_humano.nome)

    ranking = SistemaRanking(
        get_caminho_ranking_save(nome_save, genero=genero), modalidade="simples"
    )
    jogador_entry = ranking.buscar_jogador_por_nome(nome_jogador_norm)
    if jogador_entry is None:
        return

    det = jogador_entry.get("pontos_detalhados") or []
    ja_participou = any(
        isinstance(b, dict)
        and b.get("torneio") == nome_torneio
        and abs(int(b.get("semana_origem", 0) or 0) - semana) <= 2
        for b in det
    )
    if ja_participou:
        return

    sem_exp, ano_exp = _calcular_expiracao_pontos(semana, ano)
    ranking.adicionar_pontos(
        nome_jogador_norm,
        0,
        sem_exp,
        modalidade="simples",
        ano_exp=ano_exp,
        metadados={
            "torneio": nome_torneio,
            "tipo": tipo_torneio,
            "semana_origem": semana,
            "ano_origem": ano,
            "fase": "ausente",
            "penalidade": True,
        },
    )
    ranking.salvar_ranking()
    log_simulacao(
        f"Penalidade de ausencia registrada: {nome_torneio} ({tipo_torneio}), sem {semana}.",
        nome_save,
    )


def _calcular_prize_por_fase(premiacao_total, fase):
    if not premiacao_total:
        return 0
    fator = FATORES_PRIZE_POR_FASE.get(fase, 0.0)
    valor_bruto = int(float(premiacao_total) * fator)
    impostos_e_comissoes = 0.35
    return int(valor_bruto * (1.0 - impostos_e_comissoes))


def obter_pontos_map(tournament_type, genero="masculino"):
    if genero == "feminino":
        if tournament_type == "Grand Slam":
            return PONTOS_WTA_GRAND_SLAM
        if "1000" in tournament_type:
            return PONTOS_WTA_1000
        if "500" in tournament_type:
            return PONTOS_WTA_500
        return PONTOS_WTA_250

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
    if not fase_norm or fase_norm.startswith("qualy"):
        return None

    fases = _ordem_fases_pontuacao(tournament_type, modalidade)
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

    davis = carregar_davis_cup(alvo, jogador_humano)
    if not davis:
        return

    estado = davis._carregar_estado()
    resultados_confrontos = estado.get("resultados_confrontos", [])
    if not resultados_confrontos:
        return

    vitorias_por_jogador = {}
    for confronto in resultados_confrontos:
        fase = str(confronto.get("fase", "") or "").lower()
        is_final8 = fase in {"quartas", "semifinal", "final"}
        for partida in confronto.get("partidas", []):
            vencedor = partida.get("vencedor")
            if not vencedor:
                continue
            tipo = partida.get("tipo", "simples")
            if tipo == "simples":
                pts = PONTOS_DAVIS_CUP[
                    "vitoria_simples_final8" if is_final8 else "vitoria_simples_grupo"
                ]
            else:
                pts = PONTOS_DAVIS_CUP[
                    "vitoria_duplas_final8" if is_final8 else "vitoria_duplas_grupo"
                ]

            nome_v = (
                vencedor.get("nome") if isinstance(vencedor, dict) else str(vencedor)
            )
            nome_v = normalizar_nome(nome_v)
            vitorias_por_jogador[nome_v] = vitorias_por_jogador.get(nome_v, 0) + pts

    for nome_norm, pontos in vitorias_por_jogador.items():
        if pontos <= 0:
            continue
        ranking.adicionar_pontos(
            nome_norm, pontos, semana_expiracao, ano_exp=ano_expiracao
        )
        jogador_reg = ranking.buscar_jogador_por_nome(nome_norm)
        if jogador_reg:
            jogador_reg["pontos_ytd"] = jogador_reg.get("pontos_ytd", 0) + pontos
            if nome_norm == normalizar_nome(jogador_humano.nome):
                jogador_humano.pontos_ytd = (
                    getattr(jogador_humano, "pontos_ytd", 0) + pontos
                )

    if estado.get("fase_atual") == "finalizado":
        vencedor_final = estado.get("vencedor_torneio")
        finalista = estado.get("finalista_torneio")
        if vencedor_final:
            _distribuir_bonus_equipe(
                ranking,
                vencedor_final,
                PONTOS_DAVIS_CUP["campeao_bonus"],
                semana_expiracao,
                ano_expiracao,
            )
        if finalista:
            _distribuir_bonus_equipe(
                ranking,
                finalista,
                PONTOS_DAVIS_CUP["finalista_bonus"],
                semana_expiracao,
                ano_expiracao,
            )

    ranking.ordenar()
    ranking.salvar_ranking()
    salvar_jogo(alvo, jogador_humano)
    log_simulacao("Pontos da Copa Davis distribuidos.", nome_save)


def _distribuir_bonus_equipe(
    ranking, pais, pontos, semana_expiracao, ano_expiracao=None
):
    jogadores_pais = [
        j
        for j in ranking.ranking
        if normalizar_nome(j.get("nacionalidade", "")) == normalizar_nome(pais)
    ]
    jogadores_pais.sort(key=lambda x: x.get("pontos_ranking", 0), reverse=True)

    for j in jogadores_pais[:4]:
        nome_norm = normalizar_nome(j.get("nome", ""))
        ranking.adicionar_pontos(
            nome_norm, pontos, semana_expiracao, ano_exp=ano_expiracao
        )
        j["pontos_ytd"] = j.get("pontos_ytd", 0) + pontos


def distribuir_pontos_torneio(nome_save, target_save_name=None, genero="masculino"):
    from src.dados import get_caminho_ranking_duplas

    caminho_torneio = get_caminho_torneio_save(nome_save, genero=genero)
    try:
        with open(caminho_torneio, "r", encoding="utf-8") as f:
            estado_torneio = json.load(f)
    except FileNotFoundError:
        return f"Arquivo de torneio para o save '{nome_save}' nao encontrado. Nenhum ponto a distribuir."

    if estado_torneio.get("pontos_distribuidos"):
        return "Pontos do torneio ja distribuidos anteriormente."

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

    genero_torneio = estado_torneio.get("genero", "masculino")
    tournament_type = estado_torneio.get("tournament_data", {}).get("tipo", "ATP 250")
    nome_torneio = estado_torneio.get("torneio", "Torneio Desconhecido")
    premiacao_total = estado_torneio.get("tournament_data", {}).get("premiacao", 0)

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
        0,
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

                idx = fases_ordem.index(fase)
                if idx + 1 < len(fases_ordem):
                    for n in nomes_v:
                        if n:
                            progresso_jogador[n] = fases_ordem[idx + 1]
            except Exception:
                continue

    if "final" in resultados and resultados["final"]:
        v_final = resultados["final"][0].get("vencedor", {})
        for n in _extract_names(v_final):
            if n:
                progresso_jogador[n] = "campeao"

    log_simulacao(
        f"Pontuacao do Torneio ({modalidade.upper()}): {nome_torneio} ({tournament_type})",
        nome_save,
    )

    jogador_humano = carregar_jogador(alvo)
    human_name_norm = normalizar_nome(jogador_humano.nome) if jogador_humano else ""
    jogador_humano_atualizado = False

    for jogador_nome_norm, progresso_fase in progresso_jogador.items():
        fase_historico = progresso_fase
        pontos_base = pontos_map.get(progresso_fase, 0)
        jogador_ranking = ranking.buscar_jogador_por_nome(jogador_nome_norm)

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

        prize = (
            _calcular_prize_por_fase(premiacao_total, fase_historico)
            if modalidade == "simples"
            else int(_calcular_prize_por_fase(premiacao_total, fase_historico) * 0.25)
        )

        # Bônus Lifestyle: Mansão em Monte Carlo (tax haven + prestige)
        if jogador_nome_norm == human_name_norm and jogador_humano:
            lifestyle = getattr(jogador_humano, "lifestyle", [])
            if isinstance(lifestyle, list) and "mansao_monte_carlo" in lifestyle:
                prize = int(prize * 1.10)

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
            if modalidade == "simples":
                if jogador_ranking:
                    jogador_ranking["pontos_ytd"] = (
                        jogador_ranking.get("pontos_ytd", 0) + pontos_base
                    )
                if jogador_nome_norm == human_name_norm and jogador_humano:
                    jogador_humano.pontos_ytd = (
                        getattr(jogador_humano, "pontos_ytd", 0) + pontos_base
                    )

        if prize > 0:
            ranking.adicionar_dinheiro(jogador_nome_norm, prize)
            if jogador_nome_norm == human_name_norm and jogador_humano:
                jogador_humano.dinheiro = getattr(jogador_humano, "dinheiro", 0) + prize

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
