import random
from src.dados import (
    carregar_estado_torneio,
    carregar_temporada as carregar_temporada_dados,
    salvar_temporada as salvar_temporada_dados,
    obter_torneio_por_nome as obter_torneio_por_nome_dados,
    obter_torneios_da_semana as obter_torneios_da_semana_dados,
)
from src.jogador import carregar_jogador, normalizar_nome
from src.management import (
    processar_gastos_equipe,
    processar_expiracoes_contratos,
    processar_expiracoes_empresario,
    processar_despesas_operacionais,
    obter_profissional_da_equipe,
)
from src.patrocinios import (
    PATROCINADORES_DISPONIVEIS,
    gerar_convites_midia_email,
    gerar_propostas_carreira_email,
    processar_pagamentos_patrocinio,
)
from src.ranking import SistemaRanking
from src.save import salvar_jogo
from src.calendario_participacao import (
    ajustar_prob_participacao_por_contexto,
    prob_participacao,
)
from src.io_utils import print_green
from src.staff_constants import PROFISSIONAIS_DISPONIVEIS

# --- Constantes ---
FADIGA_RECUPERACAO_SEMANAL = 30
ENERGIA_RECUPERACAO_SEMANAL_BASE = 18
ENERGIA_RECUPERACAO_SEMANAL_POR_FISICO = 0.5

DOENCAS_DISPONIVEIS = {
    "gripe": {
        "duracao": (1, 2),
        "penalidade_atributos": 0.08,
        "penalidade_energia": 0.18,
        "peso": 4,
    },
    "virose": {
        "duracao": (1, 2),
        "penalidade_atributos": 0.10,
        "penalidade_energia": 0.22,
        "peso": 3,
    },
    "intoxicacao": {
        "duracao": (1, 1),
        "penalidade_atributos": 0.12,
        "penalidade_energia": 0.25,
        "peso": 2,
    },
    "resfriado": {
        "duracao": (1, 1),
        "penalidade_atributos": 0.05,
        "penalidade_energia": 0.12,
        "peso": 5,
    },
}


def _normalizar_status_doenca(status):
    padrao = {
        "doente": False,
        "tipo": None,
        "nivel": "saudavel",
        "semanas_restantes": 0,
        "penalidade_atributos": 0.0,
        "penalidade_recuperacao_energia": 0.0,
    }
    status = status if isinstance(status, dict) else {}
    normalizado = padrao.copy()
    normalizado.update(status)
    if not normalizado.get("doente"):
        normalizado["tipo"] = None
        normalizado["nivel"] = "saudavel"
        normalizado["semanas_restantes"] = 0
        normalizado["penalidade_atributos"] = 0.0
        normalizado["penalidade_recuperacao_energia"] = 0.0
    else:
        normalizado["semanas_restantes"] = max(
            1, int(normalizado.get("semanas_restantes", 1))
        )
    return normalizado


def _chance_doenca(jogador, info_torneio=None):
    base = 0.03
    fadiga = int(getattr(jogador, "fadiga", 0) or 0)
    energia = int(getattr(jogador, "energia", 100) or 100)
    base += max(0.0, (fadiga - 40) / 600.0)
    base += max(0.0, (55 - energia) / 650.0)
    if info_torneio:
        base += 0.02
    return max(0.01, min(0.20, base))


def _tentar_disparar_doenca(jogador, info_torneio=None):
    """Retorna (status_doenca, eventos: list[str])."""
    eventos: list = []
    status_doenca = _normalizar_status_doenca(getattr(jogador, "status_doenca", {}))
    if status_doenca.get("doente"):
        return status_doenca, eventos

    if random.random() > _chance_doenca(jogador, info_torneio=info_torneio):
        return status_doenca, eventos

    nomes = list(DOENCAS_DISPONIVEIS.keys())
    pesos = [DOENCAS_DISPONIVEIS[n]["peso"] for n in nomes]
    tipo = random.choices(nomes, weights=pesos, k=1)[0]
    cfg = DOENCAS_DISPONIVEIS[tipo]
    semanas = random.randint(cfg["duracao"][0], cfg["duracao"][1])
    nivel = (
        "grave"
        if cfg["penalidade_atributos"] >= 0.11
        else ("moderada" if cfg["penalidade_atributos"] >= 0.08 else "leve")
    )

    status_doenca.update(
        {
            "doente": True,
            "tipo": tipo,
            "nivel": nivel,
            "semanas_restantes": semanas,
            "penalidade_atributos": cfg["penalidade_atributos"],
            "penalidade_recuperacao_energia": cfg["penalidade_energia"],
        }
    )
    impacto_energia = int(round(12 + cfg["penalidade_energia"] * 30))
    jogador.energia = max(0, jogador.energia - impacto_energia)
    jogador.fadiga = min(100, jogador.fadiga + 8)
    eventos.append(f"🤒 Você ficou doente ({tipo}). Impacto temporário no desempenho.")
    return status_doenca, eventos


def _recuperar_energia_semana(jogador, eventos=None):
    fisico = jogador.atributos.get("fisico", 50)
    recuperacao = int(
        round(
            ENERGIA_RECUPERACAO_SEMANAL_BASE
            + fisico * ENERGIA_RECUPERACAO_SEMANAL_POR_FISICO
        )
    )
    if recuperacao <= 0:
        return
    status_doenca = _normalizar_status_doenca(getattr(jogador, "status_doenca", {}))
    penalidade_rec = float(status_doenca.get("penalidade_recuperacao_energia", 0.0))
    if penalidade_rec > 0:
        recuperacao = int(round(recuperacao * max(0.4, 1.0 - penalidade_rec)))
    fadiga_atual = int(getattr(jogador, "fadiga", 0) or 0)
    if fadiga_atual <= 20:
        # Descanso com baixa fadiga acelera reposição energética.
        recuperacao += int(round((20 - fadiga_atual) * 0.5))
    elif fadiga_atual >= 70:
        # Fadiga alta limita recuperação eficiente na semana.
        recuperacao = int(round(recuperacao * 0.88))
    energia_antes = jogador.energia
    jogador.energia = min(100, jogador.energia + recuperacao)

    status_lesao = (
        jogador.status_lesao
        if isinstance(getattr(jogador, "status_lesao", {}), dict)
        else {}
    )
    esta_limitado = bool(status_lesao.get("lesionado")) or status_lesao.get(
        "nivel"
    ) in (
        "limitado",
        "desconforto",
    )
    doente = bool(status_doenca.get("doente"))
    # Quando a fadiga está baixa (< 20) e saudável, garante um piso mínimo de energia.
    if fadiga_atual <= 20 and not esta_limitado and not doente:
        piso_fadiga_baixa = 78
        if jogador.energia < piso_fadiga_baixa:
            jogador.energia = piso_fadiga_baixa
    # Com fadiga zerada e sem limitações, garante energia alta para o próximo torneio.
    if jogador.fadiga <= 0 and not esta_limitado and not doente:
        piso_descanso_total = 92
        if jogador.energia < piso_descanso_total:
            jogador.energia = piso_descanso_total

    if eventos is not None:
        eventos.append(
            f"😌 Energia recuperada com o descanso semanal: {energia_antes}% -> {jogador.energia}%."
        )


def _e_torneio_especial(tipo_torneio):
    return tipo_torneio in ("Davis Cup", "Billie Jean King Cup", "United Cup")


def _normalizar_superficie_torneio(quadra):
    if not quadra:
        return "dura"
    q = str(quadra).strip().lower()
    if "saibro" in q or "clay" in q or "terra" in q:
        return "saibro"
    if "grama" in q or "grass" in q:
        return "grama"
    return "dura"


def _superficie_preferida_jogador(jogador):
    attrs = jogador.get("atributos", {}) if isinstance(jogador, dict) else {}
    saque = attrs.get("saque", 50)
    voleio = attrs.get("voleio", 50)
    topspin = attrs.get("topspin", 50)
    if topspin > 70:
        return "saibro"
    if saque > 70 and voleio > 60:
        return "grama"
    return "dura"


def _torneio_prioridade(info_torneio):
    tipo = info_torneio.get("tipo", "")
    if tipo == "Grand Slam":
        return 0
    if tipo in {"ATP 1000", "WTA 1000"}:
        return 1
    if tipo in {"ATP 500", "WTA 500"}:
        return 2
    if tipo in {"ATP 250", "WTA 250"}:
        return 3
    if tipo == "Challenger 125":
        return 4
    if tipo in {"ITF 100", "ITF 25"}:
        return 5
    return 6


def _extrair_codigo_pais(valor):
    if not valor or not isinstance(valor, str):
        return ""
    if valor.startswith("[") and "]" in valor:
        fechamento = valor.find("]")
        return valor[1:fechamento].upper()
    return ""


def _prob_participacao(tipo, rank, is_home=False, superficie_match=False):
    return prob_participacao(
        tipo=tipo,
        rank=rank,
        is_home=is_home,
        superficie_match=superficie_match,
    )


def _coletar_participantes_estado(estado):
    nomes = set()
    if not estado:
        return nomes
    for jogador in estado.get("direct_entries", []):
        if isinstance(jogador, dict):
            nomes.add(normalizar_nome(jogador.get("nome", "")))
        else:
            nomes.add(normalizar_nome(str(jogador)))
    for confrontos in estado.get("rodadas", {}).values():
        for confronto in confrontos:
            if isinstance(confronto, dict):
                nome_a = confronto.get("jogador_a", {}).get("nome", "")
                nome_b = confronto.get("jogador_b", {}).get("nome", "")
            else:
                jogador_a, jogador_b = confronto
                nome_a = (
                    jogador_a.get("nome")
                    if isinstance(jogador_a, dict)
                    else str(jogador_a)
                )
                nome_b = (
                    jogador_b.get("nome")
                    if isinstance(jogador_b, dict)
                    else str(jogador_b)
                )
            nomes.add(normalizar_nome(nome_a))
            nomes.add(normalizar_nome(nome_b))
    return nomes


def _marcar_historico_expirado(
    jogador, blocos_expirando, ano_novo=None, semana_nova=None
):
    """
    Marca entradas de historico_torneios como expiradas, priorizando identidade do torneio.
    """
    historico = (
        jogador.get("historico_torneios", [])
        if isinstance(jogador, dict)
        else getattr(jogador, "historico_torneios", [])
    )
    if not isinstance(historico, list) or not isinstance(blocos_expirando, list):
        return 0

    marcados = 0
    for bloco in blocos_expirando:
        if not isinstance(bloco, dict):
            continue

        nome_ref = normalizar_nome(bloco.get("torneio", ""))
        tipo_ref = str(bloco.get("tipo", "") or "")
        semana_ref = bloco.get("semana_origem")
        ano_ref = bloco.get("ano_origem")
        pontos_ref = bloco.get("pontos")

        alvo = None

        # 1) Prioriza identidade completa do torneio de origem.
        for item in historico:
            if not isinstance(item, dict) or item.get("expirado"):
                continue
            if (
                nome_ref
                and normalizar_nome(item.get("nome", "")) == nome_ref
                and (not tipo_ref or str(item.get("tipo", "")) == tipo_ref)
                and (semana_ref is None or item.get("semana") == semana_ref)
                and (ano_ref is None or item.get("ano") == ano_ref)
            ):
                alvo = item
                break

        # 2) Fallback por origem (tipo/semana/ano/pontos), quando nome não existir.
        if alvo is None:
            for item in historico:
                if not isinstance(item, dict) or item.get("expirado"):
                    continue
                if (
                    (not tipo_ref or str(item.get("tipo", "")) == tipo_ref)
                    and (semana_ref is None or item.get("semana") == semana_ref)
                    and (ano_ref is None or item.get("ano") == ano_ref)
                    and (pontos_ref is None or item.get("pontos") == pontos_ref)
                ):
                    alvo = item
                    break

        # 3) Último fallback por pontos (mantém compatibilidade de saves legados).
        if alvo is None and pontos_ref is not None:
            for item in historico:
                if not isinstance(item, dict) or item.get("expirado"):
                    continue
                if item.get("pontos") == pontos_ref:
                    alvo = item
                    break

        if alvo is not None:
            alvo["expirado"] = True
            if ano_novo is not None:
                alvo["ano_expiracao_processado"] = int(ano_novo)
            if semana_nova is not None:
                alvo["semana_expiracao_processado"] = int(semana_nova)
            marcados += 1

    return marcados


def _selecionar_participantes_para_torneio(
    info_torneio, ranking_ordenado, disponiveis_set, max_jogadores=None
):
    """
    Seleciona jogadores do ranking para um torneio.

    max_jogadores: quando fornecido, limita quantos são selecionados E removidos do
    pool. Usado por tournament_manager/world_tour_sync onde não há qualifying NPC —
    evita esgotar o pool desnecessariamente.
    """
    tipo = info_torneio.get("tipo", "")
    torneio_pais = _extrair_codigo_pais(info_torneio.get("pais_sede", ""))
    superficie_torneio = _normalizar_superficie_torneio(
        info_torneio.get("quadra", "dura")
    )

    # Cálculo dinâmico do total necessário (Main Draw + Qualy)
    if max_jogadores is not None:
        # Chamador sabe exatamente quantos precisa (ex: draw_size sem qualifying NPC)
        total_necessario = max_jogadores
    elif tipo == "Grand Slam":
        total_necessario = 128 + 128  # 256
    elif "1000" in tipo:
        total_necessario = 96 + 64  # 160
    elif tipo == "ATP Finals" or tipo == "WTA Finals":
        total_necessario = 8
    elif _e_torneio_especial(tipo):
        total_necessario = 64  # Valor base para simulação rápida
    else:
        # 250 e 500 (draw 32 + 16 qualy)
        total_necessario = 32 + 16  # 48

    def _eh_jogador_real(j):
        # "Bot Externo" / "Bot Leo Williams" → falso. "Botic van de Zandschulp" → real.
        return not bool(j.get("is_bot")) and not str(j.get("nome", "")).startswith(
            "Bot "
        )

    # Ranking base: prioriza jogadores reais para evitar placeholders em ATP/WTA.
    ranking_base = ranking_ordenado
    posicao_ranking = {
        normalizar_nome(j.get("nome", "")): idx
        for idx, j in enumerate(ranking_base, 1)
        if j.get("nome")
    }
    ranking_reais = [j for j in ranking_base if _eh_jogador_real(j)]
    ranking_bots = [j for j in ranking_base if not _eh_jogador_real(j)]

    selecionados = []
    # Primeira passada: seleciona jogadores reais por probabilidade de participação.
    for jogador in ranking_reais:
        nome_norm = normalizar_nome(jogador.get("nome", ""))
        if nome_norm not in disponiveis_set:
            continue

        # Pula jogadores lesionados
        status_lesao = jogador.get("status_lesao", {})
        if isinstance(status_lesao, dict) and status_lesao.get("lesionado"):
            continue

        jogador_pais = _extrair_codigo_pais(jogador.get("nacionalidade", ""))
        is_home = torneio_pais and jogador_pais == torneio_pais
        superficie_pref = _superficie_preferida_jogador(jogador)
        jogador["superficie_preferida"] = jogador.get(
            "superficie_preferida", superficie_pref
        )
        superficie_match = jogador.get("superficie_preferida") == superficie_torneio

        # Probabilidade base de participação
        idx = posicao_ranking.get(nome_norm, len(ranking_base))
        prob = _prob_participacao(
            tipo, idx, is_home=is_home, superficie_match=superficie_match
        )
        prob = ajustar_prob_participacao_por_contexto(
            prob,
            jogador,
            tipo=tipo,
            rank=idx,
            nome_torneio=info_torneio.get("nome", ""),
            semana_atual=info_torneio.get("semana"),
            ano_atual=info_torneio.get("ano"),
        )
        prob = min(0.99, prob * 1.2)  # viés pró-jogador real

        if random.random() < prob:
            selecionados.append(jogador)
            if len(selecionados) >= total_necessario:
                break

    # Segunda passada: completa com jogadores reais restantes, sem sorteio.
    if len(selecionados) < total_necessario:
        for jogador in ranking_reais:
            nome_norm = normalizar_nome(jogador.get("nome", ""))
            if nome_norm not in disponiveis_set or jogador in selecionados:
                continue
            selecionados.append(jogador)
            if len(selecionados) >= total_necessario:
                break

    # Terceira passada: só usa bots se realmente não houver reais suficientes.
    if len(selecionados) < total_necessario:
        for jogador in ranking_bots:
            nome_norm = normalizar_nome(jogador.get("nome", ""))
            if nome_norm not in disponiveis_set or jogador in selecionados:
                continue
            selecionados.append(jogador)
            if len(selecionados) >= total_necessario:
                break

    for jogador in selecionados:
        disponiveis_set.discard(normalizar_nome(jogador.get("nome", "")))
    return selecionados


def obter_torneios_da_semana(semana, genero="masculino"):
    return obter_torneios_da_semana_dados(semana, genero=genero)


def obter_torneio_por_nome(semana, nome_torneio, genero="masculino"):
    return obter_torneio_por_nome_dados(semana, nome_torneio, genero=genero)


def obter_info_torneio_e_fase(nome_save, genero="masculino"):
    estado = carregar_estado_torneio(nome_save, genero=genero)
    if not estado:
        return "Nenhum torneio em andamento", "sem_torneio"

    nome_torneio = estado.get("torneio", "Torneio Desconhecido")
    fase = estado.get("fase_atual", "fase_desconhecida")
    semana = estado.get("semana", 0)

    info = obter_torneio_por_nome(semana, nome_torneio, genero=genero)
    if info:
        pais = info.get("pais_sede", "??")
        tipo = info.get("tipo", "??")
        estrelas = "⭐" * info.get("popularidade", 0)
        premio = info.get("premiacao", 0)
        return (
            f"{nome_torneio} ({pais}) - {tipo} | Popularidade: {estrelas} | 💰 Premiação: ${premio}",
            fase,
        )

    return nome_torneio, fase


def carregar_temporada(nome_save):
    """Carrega o estado da temporada (ano e semana) do save."""
    return carregar_temporada_dados(nome_save)


def salvar_temporada(nome_save, data):
    """Salva o estado da temporada (ano e semana) no save."""
    salvar_temporada_dados(nome_save, data)


def _calcular_expiracao_pontos(semana_atual, ano_atual):
    semana_expiracao = ((semana_atual - 1) % 52) + 1
    return semana_expiracao, int(ano_atual) + 1


def _migrar_pontuacao(ranking_obj, semana_atual, ano_atual):
    """Migra a estrutura de pontos antiga para a nova (pontos_detalhados)."""
    print(
        "ℹ️ Migrando estrutura de pontuação para o novo sistema de ranking contínuo..."
    )
    semana_expiracao, ano_expiracao = _calcular_expiracao_pontos(
        semana_atual, ano_atual
    )
    for jogador in ranking_obj.ranking:
        pontos_antigos = jogador.get("pontos", 0)
        pontos_detalhados = jogador.get("pontos_detalhados")
        if pontos_antigos > 0 and (
            pontos_detalhados is None or pontos_detalhados == []
        ):
            jogador["pontos_detalhados"] = [
                {
                    "pontos": pontos_antigos,
                    "semana_expiracao": semana_expiracao,
                    "ano_expiracao": ano_expiracao,
                }
            ]
            jogador["pontos"] = pontos_antigos  # Mantém o campo total
    ranking_obj.salvar_ranking()
    print("✅ Migração concluída!")
    return True


def _simular_torneios_semanais_npc(
    nome_save, semana_atual, ranking_principal, jogador, player_active_tournament_state
):
    """Encapsula a simulação de torneios onde o jogador não participa, em ambos os tours."""
    from src.tournament_manager import WeekTournamentManager

    # Gerenciadores para ambos os tours
    manager_atp = WeekTournamentManager(nome_save, semana_atual, genero="masculino")
    manager_wta = WeekTournamentManager(nome_save, semana_atual, genero="feminino")

    jogador_em_torneio_ativo = _estado_torneio_ativo(
        player_active_tournament_state, semana_referencia=semana_atual
    )

    # 1. Inicializa os torneios se ainda não foram (cria as chaves)
    for gen, manager in [("masculino", manager_atp), ("feminino", manager_wta)]:
        torneios_info = obter_torneios_da_semana(semana_atual, genero=gen)
        # Marca qual torneio o jogador está participando
        for info in torneios_info:
            if jogador_em_torneio_ativo and gen == jogador.genero:
                if info["nome"] == player_active_tournament_state.get("torneio"):
                    info["participando"] = True

        manager.inicializar_torneios(torneios_info, jogador_nome=jogador.nome)

    # 2. Simula todos os torneios até o fim (pois estamos avançando a semana)
    # O manager irá simular rodada por rodada
    for manager in [manager_atp, manager_wta]:
        # Simula até 7 rodadas (máximo de um Grand Slam)
        for _ in range(7):
            manager.simular_rodada_para_todos(
                fase_alvo="finalizado", jogador_nome=jogador.nome
            )

    # 3. Coleta e exibe os campeões
    def _campeao_exibivel(nome_campeao):
        nome = str(nome_campeao or "").strip()
        if not nome:
            return False
        nome_norm = normalizar_nome(nome)
        return not (
            nome_norm.startswith("bot externo")
            or nome_norm.startswith("bot ")
            or nome_norm in {"---", "tbd", "none", "null", "na", "n/a", "cancelado"}
            or nome_norm.startswith("n/a ")
            or nome_norm.startswith("cancelado")
        )

    campeoes_da_semana = []
    oficiais_semana = {}
    for gen, label in [("masculino", "ATP"), ("feminino", "WTA")]:
        oficiais_semana[label] = {}
        for info in obter_torneios_da_semana(semana_atual, genero=gen):
            if not isinstance(info, dict):
                continue
            oficiais_semana[label][info.get("nome")] = {
                "simples": info.get("ultimo_campeao"),
                "duplas": info.get("ultimo_campeao_duplas"),
            }

    for manager in [manager_atp, manager_wta]:
        resumos = manager.obter_resumo_semanal()
        t_label = "ATP" if manager.genero == "masculino" else "WTA"
        for r in resumos:
            nome_torneio = r.get("nome")
            oficial = oficiais_semana.get(t_label, {}).get(nome_torneio, {})
            campeao_simples = r.get("campeao")
            campeao_duplas = r.get("campeao_duplas")
            if not _campeao_exibivel(campeao_simples):
                campeao_simples = oficial.get("simples")
            if not _campeao_exibivel(campeao_duplas):
                campeao_duplas = oficial.get("duplas")

            if _campeao_exibivel(campeao_simples):
                campeoes_da_semana.append(
                    {
                        "tour": t_label,
                        "torneio": nome_torneio,
                        "simples": campeao_simples,
                        "duplas": (
                            campeao_duplas
                            if _campeao_exibivel(campeao_duplas)
                            else None
                        ),
                    }
                )

    if campeoes_da_semana:
        from src.io_utils import safe_input

        width = 75
        print("\n" + "=" * width)
        print(f"{'🏆 CAMPEÕES DA SEMANA':^75}")
        print("=" * width)

        tours_ordem = ["WTA", "ATP"] if jogador.genero == "feminino" else ["ATP", "WTA"]
        for tour in tours_ordem:
            lista_tour = [c for c in campeoes_da_semana if c["tour"] == tour]
            if lista_tour:
                print(f"\n📢 TOUR {tour}:")
                for c in lista_tour:
                    label = "Campeã" if tour == "WTA" else "Campeão"
                    print(f"  🎾 {c['torneio']}:")
                    print(f"     └─ {label}: {c['simples']}")
                    if c.get("duplas"):
                        print(f"     └─ Duplas: {c['duplas']}")

        print("\n" + "=" * width)

    return campeoes_da_semana


def _atualizar_recuperacao_jogador(jogador, info_torneio=None) -> list:
    """
    Processa a recuperação física e médica do jogador ao avançar a semana.
    Retorna lista de strings com mensagens para o chamador exibir (API ou CLI).
    """
    eventos: list = []

    status = jogador.status_lesao if isinstance(jogador.status_lesao, dict) else {}
    status.setdefault("lesionado", False)
    status.setdefault("semanas_restantes", 0)
    status.setdefault("nivel", "limitado" if status.get("lesionado") else "saudavel")
    status.setdefault("penalidade_atributos", 0.18 if status.get("lesionado") else 0.0)
    if not status.get("lesionado") and status.get("nivel") == "lesionado":
        status["nivel"] = "limitado"
        status["penalidade_atributos"] = 0.12
        status["semanas_restantes"] = max(
            1, int(status.get("semanas_restantes", 0) or 0)
        )

    jogador.fadiga = max(
        0, int(getattr(jogador, "fadiga", 0) or 0) - FADIGA_RECUPERACAO_SEMANAL
    )
    _recuperar_energia_semana(jogador, eventos)

    fisio_fadiga = obter_profissional_da_equipe(
        getattr(jogador, "equipe", []), "fisioterapeuta"
    )
    if fisio_fadiga:
        bonus = fisio_fadiga.get("bonus_fadiga", 0)
        if bonus > 0:
            jogador.fadiga = max(0, jogador.fadiga - bonus)
            eventos.append(f"🩺 {fisio_fadiga['nome']}: -{bonus} fadiga extra.")

    eventos.append(f"😌 Sua fadiga atual: {jogador.fadiga}%.")

    if status["lesionado"]:
        status["semanas_restantes"] -= 1
        fisio = obter_profissional_da_equipe(
            getattr(jogador, "equipe", []), "fisioterapeuta"
        )
        if fisio:
            bonus_rec = fisio.get("bonus_recuperacao_lesao", 0)
            if bonus_rec > 0:
                status["semanas_restantes"] = max(
                    0, status["semanas_restantes"] - bonus_rec
                )
                eventos.append(
                    f"🩺 {fisio['nome']}: recuperação acelerada em {bonus_rec} semana(s)!"
                )
        eventos.append(
            f"❤️  Você está se recuperando da lesão. Semanas restantes: {status['semanas_restantes']}"
        )
        if status["semanas_restantes"] <= 0:
            status["lesionado"] = False
            status["nivel"] = "desconforto"
            status["semanas_restantes"] = 0
            status["penalidade_atributos"] = 0.06
            eventos.append(
                "🟠 Lesão fechada! Você ainda sente algum desconforto físico."
            )
    else:
        nivel = status.get("nivel", "saudavel")
        if nivel == "limitado":
            status["nivel"] = "desconforto"
            status["penalidade_atributos"] = 0.06
            eventos.append("🟠 Sua condição melhorou: de limitado para desconforto.")
        elif nivel == "desconforto":
            status["nivel"] = "saudavel"
            status["penalidade_atributos"] = 0.0
            eventos.append("✅ Você se recuperou totalmente!")

    jogador.status_lesao = status

    status_doenca = _normalizar_status_doenca(getattr(jogador, "status_doenca", {}))
    if status_doenca.get("doente"):
        status_doenca["semanas_restantes"] -= 1
        if status_doenca["semanas_restantes"] <= 0:
            status_doenca = _normalizar_status_doenca({"doente": False})
    else:
        status_doenca, ev_doenca = _tentar_disparar_doenca(
            jogador, info_torneio=info_torneio
        )
        eventos.extend(ev_doenca)

    jogador.status_doenca = _normalizar_status_doenca(status_doenca)
    return eventos


def _estado_torneio_ativo(estado_torneio, semana_referencia=None):
    if not isinstance(estado_torneio, dict):
        return False
    if not estado_torneio.get("torneio"):
        return False
    if str(estado_torneio.get("fase_atual", "")).lower() == "finalizado":
        return False
    if semana_referencia is not None:
        try:
            if int(estado_torneio.get("semana", semana_referencia)) != int(
                semana_referencia
            ):
                return False
        except (TypeError, ValueError):
            return False
    return True


def _semana_estado_torneio(estado_torneio):
    if not isinstance(estado_torneio, dict):
        return None
    try:
        return int(estado_torneio.get("semana"))
    except (TypeError, ValueError):
        return None


def _carregar_rankings_temporada(nome_save):
    from src.dados import get_caminho_ranking_duplas, get_caminho_ranking_save

    return {
        "simples_atp": SistemaRanking(
            get_caminho_ranking_save(nome_save, genero="masculino"),
            modalidade="simples",
        ),
        "duplas_atp": SistemaRanking(
            get_caminho_ranking_duplas(nome_save, genero="masculino"),
            modalidade="duplas",
        ),
        "simples_wta": SistemaRanking(
            get_caminho_ranking_save(nome_save, genero="feminino"),
            modalidade="simples",
        ),
        "duplas_wta": SistemaRanking(
            get_caminho_ranking_duplas(nome_save, genero="feminino"),
            modalidade="duplas",
        ),
    }


def _migrar_rankings_semana_se_preciso(rankings, semana_atual, ano_atual):
    for chave in ("simples_atp", "simples_wta"):
        rk = rankings[chave]
        if rk.ranking and "pontos_detalhados" not in rk.ranking[0]:
            _migrar_pontuacao(rk, semana_atual, ano_atual)


def _recuperar_npcs_semana(rankings):
    grupos = (
        [rankings["simples_atp"], rankings["duplas_atp"]],
        [rankings["simples_wta"], rankings["duplas_wta"]],
    )
    for lista_rk in grupos:
        jogadores_vistos = {}
        for rk in lista_rk:
            for j in rk.ranking:
                nome = j.get("nome")
                if nome not in jogadores_vistos:
                    _processar_recuperacao_npc(j)
                    jogadores_vistos[nome] = j
                    continue
                j_fonte = jogadores_vistos[nome]
                for campo in (
                    "fadiga",
                    "energia",
                    "moral",
                    "status_lesao",
                    "status_doenca",
                    "protected_ranking_semanas",
                ):
                    if campo in j_fonte:
                        j[campo] = j_fonte[campo]
        for rk in lista_rk:
            rk.salvar_ranking()


def _processar_virada_ano(temporada, jogador, rankings, eventos_api):
    if temporada["semana"] <= 52:
        return

    from src.progressao import processar_envelhecimento_anual

    temporada["semana"] = 1
    temporada["ano"] += 1
    eventos_api.append(f"Feliz Ano Novo! Bem-vindo a {temporada['ano']}!")

    processar_envelhecimento_anual(jogador)
    jogador.pontos_ytd = 0

    nome_humano_norm = normalizar_nome(jogador.nome)
    for rk_obj in (rankings["simples_atp"], rankings["simples_wta"]):
        for j in rk_obj.ranking:
            if normalizar_nome(j.get("nome", "")) == nome_humano_norm:
                j["pontos_ytd"] = 0
                continue
            processar_envelhecimento_anual(j)
            j["pontos_ytd"] = 0
        rk_obj.salvar_ranking()


def _processar_rotinas_semanais_jogador(
    jogador, temporada, ranking, torneio_info_semana, jogador_participou, eventos_api
):
    processar_despesas_operacionais(
        jogador, temporada=temporada, info_torneio=torneio_info_semana
    )
    processar_expiracoes_empresario(jogador)
    processar_gastos_equipe(jogador)
    processar_expiracoes_contratos(jogador)
    processar_pagamentos_patrocinio(jogador)
    eventos_api.extend(processar_progressao_semanal(jogador))
    processar_seguidores(jogador, ranking, participou=jogador_participou)
    processar_avisos_patrocinio(jogador, ranking)

    caixa_antes = len(getattr(jogador, "caixa_email", []) or [])
    gerar_propostas_carreira_email(jogador, ranking)
    gerar_convites_midia_email(jogador, ranking)
    caixa_depois = len(getattr(jogador, "caixa_email", []) or [])
    novos_emails = max(0, caixa_depois - caixa_antes)
    if novos_emails > 0:
        eventos_api.append(f"{novos_emails} novo(s) email(s) de carreira recebido(s).")


def _inicializar_torneios_nova_semana(nome_save, semana_nova, jogador_nome):
    from src.tournament_manager import WeekTournamentManager

    for gen in ["masculino", "feminino"]:
        manager = WeekTournamentManager(nome_save, semana_nova, genero=gen)
        torneios_info = obter_torneios_da_semana(semana_nova, genero=gen)
        manager.inicializar_torneios(torneios_info, jogador_nome=jogador_nome)


def processar_progressao_semanal(jogador) -> list:
    """
    Aplica ganhos semanais de atributos mentais via psicólogo da equipe.
    Retorna lista de eventos para o chamador exibir.
    """
    eventos: list = []
    equipe = getattr(jogador, "equipe", [])
    for contrato in equipe:
        prof_id = contrato.get("id") if isinstance(contrato, dict) else contrato
        prof = PROFISSIONAIS_DISPONIVEIS.get(prof_id)
        if not prof or prof.get("categoria") != "psicologo":
            continue
        chance = float(prof.get("chance_mental", 0) or 0)
        if random.random() < chance:
            attrs_mentais = list(getattr(jogador, "atributos_psicologicos", {}).keys())
            if not attrs_mentais:
                continue
            attr = random.choice(attrs_mentais)
            bonus_max = int(prof.get("bonus_mental", 1) or 1)
            bonus = random.randint(1, bonus_max) if bonus_max > 1 else 1
            jogador.atributos_psicologicos[attr] = min(
                100, int(jogador.atributos_psicologicos.get(attr, 0)) + bonus
            )

            ganho_moral = int(prof.get("estrelas", 2)) * 1.5
            jogador.moral = min(100, jogador.moral + int(ganho_moral))

            nome_attr = attr.replace("_", " ").title()
            eventos.append(
                f"🧠 Sessão com {prof['nome']}: +{bonus} em {nome_attr} e moral subiu para {jogador.moral}!"
            )
    return eventos


def processar_seguidores(jogador, ranking, participou=True):
    """Aplica ganhos/perdas de seguidores na virada da semana."""
    posicao = ranking.obter_posicao(jogador.nome) or 9999

    # Ganho base por ranking (ex: Top 100 ganha mais que Top 1000)
    # 10000 / pos -> #1 ganha 10000, #100 ganha 100, #1000 ganha 10
    ganho_base = int(10000 / max(1, posicao))

    # Se não jogou torneio, o ganho de base (orgânico) é 90% menor
    if not participou:
        ganho_base = int(ganho_base * 0.1)
    else:
        # Bônus por título ou boa campanha (se ele jogou)
        from src.dados import carregar_estado_torneio

        estado_t = carregar_estado_torneio(jogador.save_name, genero=jogador.genero)
        if estado_t:
            # Campeão ganha bônus de 5x no ganho base da semana
            if str(estado_t.get("fase_atual", "")).lower() == "finalizado":
                # Verificamos se ele foi campeão (jogador_vivo continua True no fim se vencer)
                if estado_t.get("jogador_vivo"):
                    ganho_base *= 5
                    print_green("🏆 Bônus de popularidade por título!")
            elif (
                estado_t.get("jogador_vivo_duplas")
                and str(estado_t.get("fase_atual_duplas")).lower() == "finalizado"
            ):
                # Campeão de duplas ganha 3x
                ganho_base *= 3
                print_green("🏆 Bônus de popularidade por título de duplas!")

    equipe = getattr(jogador, "equipe", [])
    ganho_marketing = 0
    for contrato in equipe:
        prof_id = contrato.get("id") if isinstance(contrato, dict) else contrato
        prof = PROFISSIONAIS_DISPONIVEIS.get(prof_id)
        if prof and prof.get("categoria") == "marketing":
            ganho_marketing += random.randint(
                prof.get("seguidores_min", 0), prof.get("seguidores_max", 0)
            )

    total_ganho = ganho_base + ganho_marketing
    total = getattr(jogador, "seguidores", 0) + total_ganho

    # Penalidades por moral/psicológico baixos
    if getattr(jogador, "moral", 70) < 30:
        total = int(total * 0.90)
    psico = getattr(jogador, "atributos_psicologicos", {})
    if psico and sum(psico.values()) / len(psico) < 35:
        total = int(total * 0.95)

    jogador.seguidores = max(0, total)
    if total_ganho > 0:
        print(
            f"📱 Seguidores: +{total_ganho:,} (Base: {ganho_base}, Mkt: {ganho_marketing})"
        )


def processar_avisos_patrocinio(jogador, ranking):
    """Verifica requisitos dos patrocinadores e emite avisos ou cancela contratos."""
    posicao = ranking.obter_posicao(jogador.nome) or 9999
    seguidores = getattr(jogador, "seguidores", 0)
    avisos = getattr(
        jogador, "avisos_patrocinio", {}
    )  # Agora mapeia pat_id -> semanas_insatisfeito (int)
    patrocinios = list(getattr(jogador, "patrocinios", []))

    for pat_id in patrocinios:
        pat = PATROCINADORES_DISPONIVEIS.get(pat_id)
        if not pat:
            continue
        req_ranking = pat.get("requisito_ranking", 9999)
        req_seg = pat.get("req_seguidores", 0)

        # Regra mais suave: Tolera até 50% de desvio no ranking e 30% nos seguidores antes de reclamar
        insatisfeito = posicao > req_ranking * 1.5 or (
            req_seg > 0 and seguidores < req_seg * 0.7
        )

        if insatisfeito:
            semanas = avisos.get(pat_id, 0) + 1
            avisos[pat_id] = semanas

            if semanas >= 3:
                # Cancelar contrato após 3 semanas de insatisfação
                if pat_id in jogador.patrocinios:
                    jogador.patrocinios.remove(pat_id)
                avisos.pop(pat_id, None)
                print(
                    f"❌ {pat['nome']} CANCELOU o contrato por falta de resultados/popularidade!"
                )
            else:
                prazo = 3 - semanas
                msg = "ranking" if posicao > req_ranking * 1.5 else "seguidores"
                print(
                    f"⚠️  {pat['nome']} está insatisfeito com seu {msg}. Você tem {prazo} semana(s) para melhorar!"
                )
        else:
            if pat_id in avisos:
                avisos.pop(pat_id)
                print(
                    f"✅ {pat['nome']} voltou a ficar satisfeito com sua performance."
                )

    jogador.avisos_patrocinio = avisos


def _processar_recuperacao_npc(j):
    """Lógica interna de recuperação física para um único NPC (dict)."""
    j.setdefault("fadiga", 0)
    j.setdefault("energia", 100)
    j.setdefault("moral", 70)

    # 1. Fadiga
    fadiga = int(j.get("fadiga", 0))
    j["fadiga"] = max(0, fadiga - FADIGA_RECUPERACAO_SEMANAL)

    # 2. Energia (com penalidade de doença e efeito da fadiga no descanso)
    fisico = j.get("fisico") or (j.get("atributos") or {}).get("fisico", 50)
    rec_energia = int(
        round(
            ENERGIA_RECUPERACAO_SEMANAL_BASE
            + fisico * ENERGIA_RECUPERACAO_SEMANAL_POR_FISICO
        )
    )
    status_doenca = _normalizar_status_doenca(j.get("status_doenca", {}))
    penalidade_rec = float(status_doenca.get("penalidade_recuperacao_energia", 0.0))
    if penalidade_rec > 0:
        rec_energia = int(round(rec_energia * max(0.4, 1.0 - penalidade_rec)))

    if j["fadiga"] <= 20:
        rec_energia += int(round((20 - j["fadiga"]) * 0.5))
    elif j["fadiga"] >= 70:
        rec_energia = int(round(rec_energia * 0.88))

    rec_energia = max(0, rec_energia)
    j["energia"] = min(100, int(j.get("energia", 100)) + rec_energia)

    status_lesao = (
        j.get("status_lesao", {}) if isinstance(j.get("status_lesao", {}), dict) else {}
    )
    esta_limitado = bool(status_lesao.get("lesionado")) or status_lesao.get(
        "nivel"
    ) in (
        "limitado",
        "desconforto",
    )
    doente = bool(status_doenca.get("doente"))
    if j["fadiga"] <= 20 and not esta_limitado and not doente and j["energia"] < 78:
        j["energia"] = 78
    if j["fadiga"] <= 0 and not esta_limitado and not doente and j["energia"] < 92:
        j["energia"] = 92

    # 2.1 Moral (impacto semanal de desgaste/recuperação)
    moral_atual = int(j.get("moral", 70) or 70)
    if moral_atual > 70:
        moral_atual = max(70, moral_atual - 2)
    elif moral_atual < 70:
        moral_atual = min(70, moral_atual + 2)

    if j["fadiga"] >= 80:
        moral_atual -= 3
    elif j["fadiga"] >= 60:
        moral_atual -= 1
    elif j["fadiga"] <= 30:
        moral_atual += 1
    if j["energia"] <= 40:
        moral_atual -= 1
    elif j["energia"] >= 85:
        moral_atual += 1
    j["moral"] = max(0, min(100, moral_atual))

    # 3. Lesão
    status = j.get("status_lesao", {})
    if status and status.get("semanas_restantes", 0) > 0:
        status["semanas_restantes"] -= 1
        if status["semanas_restantes"] <= 0:
            if status.get("lesionado"):
                status["lesionado"] = False
                status["nivel"] = "desconforto"
                status["semanas_restantes"] = 0
                status["penalidade_atributos"] = 0.06
            else:
                status["nivel"] = "saudavel"
                status["penalidade_atributos"] = 0.0
        j["status_lesao"] = status

    # 4. Protected Ranking
    if j.get("protected_ranking_semanas"):
        j["protected_ranking_semanas"] = max(0, int(j["protected_ranking_semanas"]) - 1)
        if j["protected_ranking_semanas"] == 0:
            j.pop("protected_ranking", None)


def _processar_recuperacao_ranking(ranking):
    """Atualiza fadiga, lesão e energia de todos os NPCs no ranking."""
    for j in ranking.ranking:
        if not isinstance(j, dict):
            continue
        _processar_recuperacao_npc(j)
    ranking.salvar_ranking()


def _processar_expiracao_ranking(nome_save, semana_atual, ano_atual):
    """Remove pontos que expiraram nesta semana (há 52 semanas) em todos os rankings."""
    from src.dados import get_caminho_ranking_save, get_caminho_ranking_duplas
    from src.ranking import SistemaRanking

    # Processa ATP e WTA, Simples e Duplas
    for genero in ["masculino", "feminino"]:
        # 1. Ranking de Simples
        path_s = get_caminho_ranking_save(nome_save, genero=genero)
        rk_s = SistemaRanking(path_s, modalidade="simples")
        _limpar_ranking_obj(rk_s, semana_atual, ano_atual)

        # 2. Ranking de Duplas
        path_d = get_caminho_ranking_duplas(nome_save, genero=genero)
        rk_d = SistemaRanking(path_d, modalidade="duplas")
        _limpar_ranking_obj(rk_d, semana_atual, ano_atual)


def _limpar_ranking_obj(ranking_obj, semana_atual, ano_atual):
    """Lógica interna de limpeza de pontos expirados para um objeto SistemaRanking."""
    mudou_global = False
    is_duplas = ranking_obj.modalidade == "duplas"
    c_pts = "pontos_detalhados" if not is_duplas else "pontos_detalhados_duplas"

    for j in ranking_obj.ranking:
        # Se for um shard lean, precisamos carregar para limpar os pontos detalhados
        if j.get("is_lean"):
            ranking_obj.buscar_jogador_por_nome(j["nome"])

        detalhes = j.get(c_pts, [])
        if not detalhes:
            continue

        novos_detalhes = []
        mudou_jogador = False
        for p in detalhes:
            sem_exp = p.get("semana_expiracao")
            ano_exp = p.get("ano_expiracao")

            expirou = False
            if ano_exp is not None and sem_exp is not None:
                if ano_atual > ano_exp:
                    expirou = True
                elif ano_atual == ano_exp and semana_atual >= sem_exp:
                    expirou = True
            elif sem_exp is not None:
                # Fallback para quando ano_exp é None (considera o ano atual se semana_atual >= sem_exp)
                # Ou assume que expirou se a semana for igual/maior (legado)
                if semana_atual >= sem_exp:
                    expirou = True

            if expirou:
                mudou_jogador = True
            else:
                novos_detalhes.append(p)

        if mudou_jogador:
            j[c_pts] = novos_detalhes
            mudou_global = True

    if mudou_global:
        ranking_obj.ordenar(recalculate=True)
        ranking_obj.salvar_ranking()


def avancar_semana(nome_save, expected_week=None):
    from src.services.season_service import advance_week

    return advance_week(nome_save, expected_week=expected_week)


# ---------------------------------------------------------------------------
# Helpers de calendário/entry reutilizáveis pelos menus
# ---------------------------------------------------------------------------

_PESOS_FASE = {
    "qualy_1": 0,
    "qualy_2": 1,
    "qualy_r1": 0,
    "qualy_r2": 1,
    "qualy_r3": 2,
    "r128": 3,
    "r96": 3,
    "r64": 4,
    "r32": 5,
    "r16": 6,
    "oitavas": 6,
    "quartas": 7,
    "semifinal": 8,
    "final": 9,
    "campeao": 10,
}


def calcular_melhor_resultado_por_torneio(historico_torneios: list) -> dict:
    """
    Recebe uma lista de entradas de histórico de torneios do jogador e retorna
    um dict {nome_torneio: fase_melhor_resultado}.
    """
    melhor: dict = {}
    for h in historico_torneios:
        t_nome = h.get("torneio")
        fase = h.get("fase_alcancada", "r128")
        if t_nome not in melhor or _PESOS_FASE.get(fase, 0) > _PESOS_FASE.get(
            melhor[t_nome], 0
        ):
            melhor[t_nome] = fase
    return melhor


def badge_entry_status(ranking_pos, torneio: dict) -> str:
    """
    Retorna uma badge de status de inscrição para o torneio.
    Usa status_entry do torneio se disponível; caso contrário estima pelo ranking.
    """
    from src.torneio_constants import (
        NUM_TOP_DIRETOS_GRAND_SLAM,
        NUM_TOP_DIRETOS_ATP_1000,
        NUM_TOP_DIRETOS_PADRAO,
        DRAW_SIZE_GRAND_SLAM,
        DRAW_SIZE_ATP_1000,
        DRAW_SIZE_PADRAO,
        RANKING_LIMITE_CHALLENGER,
        RANKING_LIMITE_ITF,
    )

    def _limite_categoria(tipo_torneio: str):
        if tipo_torneio == "Challenger 125":
            return RANKING_LIMITE_CHALLENGER
        if tipo_torneio in {"ITF 100", "ITF 25"}:
            return RANKING_LIMITE_ITF
        return None

    status_real = torneio.get("status_entry")
    if status_real:
        badges = {
            "direct": "[Main Draw]",
            "wildcard": "[Wildcard ★]",
            "qualifier": "[Qualifying]",
            "lucky_loser": "[Lucky Loser]",
            "alternate": "[Alternate]",
        }
        return badges.get(status_real, "")

    if ranking_pos is None:
        return ""

    tipo = torneio.get("tipo", "")
    limite_categoria = _limite_categoria(tipo)
    if limite_categoria is not None and ranking_pos <= limite_categoria:
        return "[Ineligible]"

    cortes = {
        "Grand Slam": (NUM_TOP_DIRETOS_GRAND_SLAM, DRAW_SIZE_GRAND_SLAM),
        "ATP 1000": (NUM_TOP_DIRETOS_ATP_1000, DRAW_SIZE_ATP_1000),
        "WTA 1000": (NUM_TOP_DIRETOS_ATP_1000, DRAW_SIZE_ATP_1000),
        "ATP 500": (NUM_TOP_DIRETOS_PADRAO, DRAW_SIZE_PADRAO + 16),
        "WTA 500": (NUM_TOP_DIRETOS_PADRAO, DRAW_SIZE_PADRAO + 16),
        "ATP 250": (NUM_TOP_DIRETOS_PADRAO, DRAW_SIZE_PADRAO + 16),
        "WTA 250": (NUM_TOP_DIRETOS_PADRAO, DRAW_SIZE_PADRAO + 16),
        "Challenger 125": (
            RANKING_LIMITE_CHALLENGER + DRAW_SIZE_PADRAO,
            RANKING_LIMITE_CHALLENGER + DRAW_SIZE_PADRAO + 16,
        ),
        "ITF 100": (
            RANKING_LIMITE_ITF + DRAW_SIZE_PADRAO,
            RANKING_LIMITE_ITF + DRAW_SIZE_PADRAO + 16,
        ),
        "ITF 25": (
            RANKING_LIMITE_ITF + DRAW_SIZE_PADRAO,
            RANKING_LIMITE_ITF + DRAW_SIZE_PADRAO + 16,
        ),
        "ATP Finals": (None, None),
        "WTA Finals": (None, None),
        "Next Gen ATP Finals": (None, None),
        "United Cup": (None, None),
        "Davis Cup": (None, None),
        "Billie Jean King Cup": (None, None),
    }
    corte_md, corte_q = cortes.get(tipo, (NUM_TOP_DIRETOS_PADRAO, 64))
    if corte_md is None:
        return ""
    if ranking_pos <= corte_md:
        return "[Main Draw]"
    elif ranking_pos <= corte_q:
        return "[Qualifying]"
    else:
        return "[Alternates]"
