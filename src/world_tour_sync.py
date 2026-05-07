import random

from src.log_jogo import log_erro
from src.tournament_manager import (
    WeekTournamentManager,
    fases_por_tipo_torneio,
    gerar_placar_fake,
)
from src.dados import get_caminho_ranking_save, get_caminho_ranking_global
from src.dados import carregar_ranking


def sincronizar_tour_mundial(nome_save, semana, fase_alvo, jogador_nome):
    """
    Sincroniza os torneios ATP/WTA da semana atual para a fase alvo.
    Mantém essa dependência fora de `torneio.py` para reduzir ciclos de import.
    """
    try:
        for gen in ["masculino", "feminino"]:
            manager = WeekTournamentManager(nome_save, semana, genero=gen)
            manager.simular_rodada_para_todos(fase_alvo, jogador_nome=jogador_nome)
    except Exception as e:
        log_erro(nome_save, "sincronizacao_tour_mundial", e, {"fase_alvo": fase_alvo})


def inicializar_andamento_outros_torneios(
    estado: dict,
    nome_save: str,
    semana: int,
    genero_jogador: str,
    nome_torneio_ativo: str,
) -> bool:
    """
    Cria o draw inicial de todos os torneios NPC da semana, excluindo o torneio
    do jogador. Os draws são armazenados em estado['outros_torneios_semana'].
    Retorna True se novos torneios foram inicializados.
    """
    if estado.get("outros_torneios_semana"):
        return False

    from src.calendario import obter_torneios_da_semana
    from src.calendario import _selecionar_participantes_para_torneio
    from src.jogador import normalizar_nome

    outros = []

    for gen in ("masculino", "feminino"):
        torneios_semana = obter_torneios_da_semana(semana, genero=gen)
        caminho_save = get_caminho_ranking_save(nome_save, genero=gen)
        ranking_save = carregar_ranking(caminho_save)
        ranking_global = carregar_ranking(get_caminho_ranking_global(genero=gen))
        if not ranking_save and not ranking_global:
            continue
        ranking_merge = []
        nomes_vistos = set()
        for j in ranking_save + ranking_global:
            nome_norm = normalizar_nome(j.get("nome", ""))
            if not nome_norm or nome_norm in nomes_vistos:
                continue
            ranking_merge.append(j)
            nomes_vistos.add(nome_norm)

        ranking_ord = sorted(
            ranking_merge,
            key=lambda j: int(j.get("pontos_ranking", j.get("pontos", 0)) or 0),
            reverse=True,
        )

        # Pool compartilhado: impede duplicatas entre torneios do mesmo gênero
        disponiveis = {
            normalizar_nome(j.get("nome", "")) for j in ranking_ord if j.get("nome")
        }

        for t_info in torneios_semana:
            nome_t = t_info.get("nome", "Torneio")
            tipo_t = t_info.get("tipo", "")
            if gen == genero_jogador and nome_t == nome_torneio_ativo:
                continue
            if tipo_t in ("Davis Cup", "Billie Jean King Cup", "United Cup"):
                continue

            fases, draw_size = fases_por_tipo_torneio(tipo_t)

            selecionados = _selecionar_participantes_para_torneio(
                t_info, ranking_ord, disponiveis, max_jogadores=draw_size
            )
            jogadores = [
                {"nome": j.get("nome", ""), "overall": int(j.get("overall", 50) or 50)}
                for j in selecionados[:draw_size]
            ]

            # Preenche o draw com reais restantes antes de qualquer fallback.
            nomes_draw = {normalizar_nome(j.get("nome", "")) for j in jogadores}
            for j in ranking_ord:
                if len(jogadores) >= draw_size:
                    break
                nome = j.get("nome", "")
                nome_norm = normalizar_nome(nome)
                if (
                    not nome_norm
                    or nome_norm in nomes_draw
                    or nome_norm.startswith("bot ")
                    or nome_norm.startswith("bot externo")
                    or bool(j.get("is_bot"))
                    or bool(j.get("e_ficticio"))
                ):
                    continue
                jogadores.append(
                    {"nome": nome, "overall": int(j.get("overall", 50) or 50)}
                )
                nomes_draw.add(nome_norm)

            if len(jogadores) < 2:
                continue

            from src.gerador_nomes import gerar_jogador_fraco

            while len(jogadores) < draw_size:
                bot = gerar_jogador_fraco(
                    len(jogadores) + 1,
                    pais_sede=t_info.get("pais_sede"),
                    genero=gen,
                )
                bot["e_ficticio"] = True
                jogadores.append({"nome": bot["nome"], "overall": bot["overall"]})
            random.shuffle(jogadores)
            confrontos = []
            for i in range(0, len(jogadores) - 1, 2):
                confrontos.append([jogadores[i], jogadores[i + 1]])

            outros.append(
                {
                    "tour": "ATP" if gen == "masculino" else "WTA",
                    "nome": nome_t,
                    "tipo": tipo_t,
                    "fases": fases,
                    "fase_idx": 0,
                    "rodadas": {fases[0]: confrontos},
                    "resultados": {},
                    "finalizado": False,
                    "campeao": None,
                }
            )

    estado["outros_torneios_semana"] = outros
    estado["outros_torneios_sim_dia"] = 1
    return True


def simular_rodada_outros_torneios(estado: dict) -> None:
    """Simula uma rodada de cada torneio NPC embarcado no estado do torneio."""
    outros = estado.get("outros_torneios_semana", [])
    for t in outros:
        if t.get("finalizado"):
            continue
        fases = t.get("fases", [])
        idx = int(t.get("fase_idx", 0) or 0)
        if idx >= len(fases):
            t["finalizado"] = True
            continue

        fase = fases[idx]
        confrontos = t.get("rodadas", {}).get(fase, [])
        if not confrontos:
            t["finalizado"] = True
            continue

        resultados = []
        vencedores = []
        for confronto in confrontos:
            a = (
                confronto[0]
                if isinstance(confronto[0], dict)
                else {"nome": str(confronto[0]), "overall": 50}
            )
            b = (
                confronto[1]
                if isinstance(confronto[1], dict)
                else {"nome": str(confronto[1]), "overall": 50}
            )
            oa = max(1, int(a.get("overall", 50) or 50))
            ob = max(1, int(b.get("overall", 50) or 50))
            # Fadiga acumulada: cada partida reduz efetividade em 4% (mín 82%)
            fator_a = max(0.82, 1.0 - a.get("_partidas", 0) * 0.04)
            fator_b = max(0.82, 1.0 - b.get("_partidas", 0) * 0.04)
            oa = max(1, int(oa * fator_a))
            ob = max(1, int(ob * fator_b))
            vencedor = random.choices([a, b], weights=[oa, ob], k=1)[0]
            resultados.append(
                {
                    "jogador_a": a.get("nome", "??"),
                    "jogador_b": b.get("nome", "??"),
                    "vencedor": vencedor.get("nome", "??"),
                    "placar": gerar_placar_fake(),
                }
            )
            # Incrementa contador de partidas do vencedor para rastrear desgaste
            vencedor = dict(vencedor)
            vencedor["_partidas"] = vencedor.get("_partidas", 0) + 1
            vencedores.append(vencedor)

        t.setdefault("resultados", {})[fase] = resultados
        t["fase_idx"] = idx + 1
        if len(vencedores) == 1 or t["fase_idx"] >= len(fases):
            t["finalizado"] = True
            t["campeao"] = vencedores[0].get("nome", "??") if vencedores else None
        else:
            prox_fase = fases[t["fase_idx"]]
            random.shuffle(vencedores)
            prox_confrontos = []
            for i in range(0, len(vencedores) - 1, 2):
                prox_confrontos.append([vencedores[i], vencedores[i + 1]])
            t.setdefault("rodadas", {})[prox_fase] = prox_confrontos


def sincronizar_outros_torneios_com_dia(
    estado: dict,
    nome_save: str,
    semana: int,
    genero_jogador: str,
    nome_torneio_ativo: str,
    dia_torneio: int,
) -> bool:
    """
    Garante que os torneios NPC embarcados no estado estão simulados até o
    dia_torneio. Retorna True se o estado foi modificado.
    """
    mudou = inicializar_andamento_outros_torneios(
        estado, nome_save, semana, genero_jogador, nome_torneio_ativo
    )
    dia_simulado = int(estado.get("outros_torneios_sim_dia", 1) or 1)
    dia_alvo = max(1, int(dia_torneio or 1))
    while dia_simulado < dia_alvo:
        simular_rodada_outros_torneios(estado)
        dia_simulado += 1
        mudou = True
    estado["outros_torneios_sim_dia"] = dia_simulado
    return mudou
