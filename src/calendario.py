import json
import os
import random
from src.dados import (
    carregar_calendario,
    carregar_estado_torneio,
    get_caminho_ranking_save,
    get_caminho_temporada,
    get_caminho_jogador_save,
)
from src.jogador import carregar_jogador, normalizar_nome
from src.ranking import SistemaRanking
from src.save import salvar_jogo

# --- Constantes ---
FADIGA_RECUPERACAO_SEMANAL = 25


def _torneio_prioridade(info_torneio):
    tipo = info_torneio.get("tipo", "")
    if tipo == "Grand Slam":
        return 0
    if tipo == "ATP 1000":
        return 1
    if tipo == "ATP 500":
        return 2
    if tipo == "ATP 250":
        return 3
    return 4


def _extrair_codigo_pais(valor):
    if not valor or not isinstance(valor, str):
        return ""
    if valor.startswith("[") and "]" in valor:
        return valor[1:valor.find("]")].upper()
    return ""


def _prob_participacao(tipo, rank, is_home=False):
    if tipo == "Grand Slam":
        if is_home:
            if rank <= 50:
                return 0.99
            if rank <= 100:
                return 0.92
            return 0.75
        if rank <= 50:
            return 0.98
        if rank <= 100:
            return 0.9
        return 0.7
    if tipo == "ATP 1000":
        if is_home:
            if rank <= 50:
                return 0.9
            if rank <= 100:
                return 0.7
            return 0.5
        if rank <= 50:
            return 0.85
        if rank <= 100:
            return 0.65
        return 0.4
    if tipo == "ATP 500":
        if is_home:
            if rank <= 5:
                return 0.9
            if rank <= 20:
                return 0.8
            if rank <= 50:
                return 0.7
            if rank <= 100:
                return 0.6
            return 0.5
        if rank <= 20:
            return 0.45
        if rank <= 50:
            return 0.55
        if rank <= 100:
            return 0.5
        return 0.35
    if tipo == "ATP 250":
        if is_home:
            if rank <= 20:
                return 0.45
            if rank <= 50:
                return 0.55
            if rank <= 100:
                return 0.7
            return 0.85
        if rank <= 5:
            return 0.1
        if rank <= 20:
            return 0.2
        if rank <= 50:
            return 0.35
        if rank <= 100:
            return 0.5
        return 0.6
    return 0.4


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
                nome_a = jogador_a.get("nome") if isinstance(jogador_a, dict) else str(jogador_a)
                nome_b = jogador_b.get("nome") if isinstance(jogador_b, dict) else str(jogador_b)
            nomes.add(normalizar_nome(nome_a))
            nomes.add(normalizar_nome(nome_b))
    return nomes


def _selecionar_participantes_para_torneio(info_torneio, ranking_ordenado, disponiveis_set):
    tipo = info_torneio.get("tipo", "")
    torneio_pais = _extrair_codigo_pais(info_torneio.get("pais_sede", ""))
    if tipo == "Grand Slam":
        num_top_diretos = 112
        num_jogadores_qualy = 128
    else:
        num_top_diretos = 28
        num_jogadores_qualy = 16
    total_necessario = num_top_diretos + num_jogadores_qualy

    selecionados = []
    for idx, jogador in enumerate(ranking_ordenado, 1):
        nome_norm = normalizar_nome(jogador.get("nome", ""))
        if nome_norm not in disponiveis_set:
            continue
        jogador_pais = _extrair_codigo_pais(jogador.get("nacionalidade", ""))
        is_home = torneio_pais and jogador_pais == torneio_pais
        if random.random() < _prob_participacao(tipo, idx, is_home=is_home):
            selecionados.append(jogador)
            if len(selecionados) >= total_necessario:
                break

    if len(selecionados) < total_necessario:
        # Prioriza wildcards locais (baixo ranking) para completar a lista
        for jogador in reversed(ranking_ordenado):
            nome_norm = normalizar_nome(jogador.get("nome", ""))
            if nome_norm not in disponiveis_set or jogador in selecionados:
                continue
            jogador_pais = _extrair_codigo_pais(jogador.get("nacionalidade", ""))
            if torneio_pais and jogador_pais == torneio_pais:
                selecionados.append(jogador)
                if len(selecionados) >= total_necessario:
                    break

    if len(selecionados) < total_necessario:
        for jogador in ranking_ordenado:
            nome_norm = normalizar_nome(jogador.get("nome", ""))
            if nome_norm not in disponiveis_set or jogador in selecionados:
                continue
            selecionados.append(jogador)
            if len(selecionados) >= total_necessario:
                break

    for jogador in selecionados:
        disponiveis_set.discard(normalizar_nome(jogador.get("nome", "")))
    return selecionados



def obter_torneios_da_semana(semana):
    calendario = carregar_calendario()
    return calendario.get(str(semana), [])


def obter_torneio_por_nome(semana, nome_torneio):
    torneios = obter_torneios_da_semana(semana)
    for torneio in torneios:
        if torneio["nome"] == nome_torneio:
            return torneio
    return None


def distribuir_premio(total, porcentagem):
    return int(total * porcentagem)


def obter_info_torneio_e_fase(nome_save):
    estado = carregar_estado_torneio(nome_save)
    if not estado:
        return "Nenhum torneio em andamento", "sem_torneio"

    nome_torneio = estado.get("torneio", "Torneio Desconhecido")
    fase = estado.get("fase_atual", "fase_desconhecida")
    semana = estado.get("semana", 0)

    info = obter_torneio_por_nome(semana, nome_torneio)
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
    caminho = get_caminho_temporada(nome_save)
    if not os.path.exists(caminho):
        # Se não existir, cria um estado inicial
        return {"ano": 2026, "semana": 1}
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_temporada(nome_save, data):
    """Salva o estado da temporada (ano e semana) no save."""
    caminho = get_caminho_temporada(nome_save)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _migrar_pontuacao(ranking_obj, semana_atual):
    """Migra a estrutura de pontos antiga para a nova (pontos_detalhados)."""
    print("ℹ️ Migrando estrutura de pontuação para o novo sistema de ranking contínuo...")
    semana_expiracao = (semana_atual + 51) % 52 + 1
    for jogador in ranking_obj.ranking:
        pontos_antigos = jogador.get("pontos", 0)
        pontos_detalhados = jogador.get("pontos_detalhados")
        if pontos_antigos > 0 and (pontos_detalhados is None or pontos_detalhados == []):
            jogador["pontos_detalhados"] = [
                {"pontos": pontos_antigos, "semana_expiracao": semana_expiracao}
            ]
            jogador["pontos"] = pontos_antigos # Mantém o campo total
    ranking_obj.salvar_ranking()
    print("✅ Migração concluída!")
    return True

def avancar_semana(nome_save):
    """
    Avança uma semana na temporada, atualiza o ranking (point decay) e salva o estado.
    Simula também os torneios não selecionados pelo jogador.
    """
    from src.torneio import Torneio # Import here to avoid circular dependency
    from src.pontuacao import distribuir_pontos_torneio # Import here to avoid circular dependency
    from src.io_utils import safe_input # Import here for pause

    temporada = carregar_temporada(nome_save)
    ranking = SistemaRanking(get_caminho_ranking_save(nome_save))

    # Migração de dados (se necessário)
    if ranking.ranking and "pontos_detalhados" not in ranking.ranking[0]:
        _migrar_pontuacao(ranking, temporada["semana"])
        # Recarrega o ranking após a migração
        ranking = SistemaRanking(get_caminho_ranking_save(nome_save))

    # --- Simular outros torneios da semana atual ---
    semana_atual = temporada["semana"]
    torneios_da_semana = obter_torneios_da_semana(semana_atual)
    # Check if player is participating in a tournament this week (tournament state file exists and has data)
    player_active_tournament_state = carregar_estado_torneio(nome_save)
    player_active_tournament_name = player_active_tournament_state.get("torneio") if player_active_tournament_state else None
    jogador = carregar_jogador(nome_save)

    jogadores_disponiveis = list(ranking.ranking)
    disponiveis_set = {normalizar_nome(j.get("nome", "")) for j in jogadores_disponiveis}
    disponiveis_set.discard(normalizar_nome(jogador.nome))
    disponiveis_set -= _coletar_participantes_estado(player_active_tournament_state)

    participantes_por_torneio = {}
    torneios_para_alocacao = sorted(torneios_da_semana, key=_torneio_prioridade)
    for info_torneio in torneios_para_alocacao:
        if player_active_tournament_name and info_torneio["nome"] == player_active_tournament_name:
            continue
        if info_torneio["tipo"] in ("Davis Cup", "United Cup"):
            continue
        participantes_por_torneio[info_torneio["nome"]] = _selecionar_participantes_para_torneio(
            info_torneio, jogadores_disponiveis, disponiveis_set
        )


    campeoes_da_semana = []
    
    for info_torneio in torneios_da_semana:
        # Skip player's current tournament
        if player_active_tournament_name and info_torneio["nome"] == player_active_tournament_name:
            print(f"\n➡️ O jogador está participando do torneio: {info_torneio['nome']}. Não será simulado aqui.")
            continue
        
        # Skip Davis Cup and United Cup for NPC simulation for now, as their logic is not fully implemented
        if info_torneio["tipo"] == "Davis Cup" or info_torneio["tipo"] == "United Cup":
            print(f"\n➡️ Torneio {info_torneio['nome']} ({info_torneio['tipo']}) não será simulado para NPCs. Formato especial.")
            continue
        
        print(f"\n🌍 Simulando torneio para NPCs: {info_torneio['nome']} ({info_torneio['tipo']})...")
        
        # Create a dummy Torneio instance for simulation purposes
        # The 'jogador_nome' here is just a placeholder, as the actual player is not in this tournament
        # Pass the ranking object to the Torneio instance
        sim_torneio_instance = Torneio(
            tournament_data=info_torneio,
            jogador_nome="Simulador_NPC", # Dummy name for the instance
            jogador_nacionalidade="??",
            ranking=ranking,
            nome_save=nome_save # Use current save name to access ranking but temp files for tournament state
        )

        try:
            participantes = participantes_por_torneio.get(info_torneio["nome"])
            campeao_simulado = sim_torneio_instance.simular_torneio_npc(
                ranking.ranking,
                participantes_semana=participantes,
            )
            if campeao_simulado:
                campeoes_da_semana.append(f"{info_torneio['nome']}: {campeao_simulado['nome']}")
                # Distribute points for the simulated tournament
                # We need a dummy name_save for the simulated tournament state to be saved and loaded
                # sim_torneio_instance.nome_save holds the temp_save_name used in simular_torneio_npc
                distribuir_pontos_torneio(sim_torneio_instance.nome_save) 
        except Exception as e:
            print(f"❌ Erro ao simular {info_torneio['nome']} para NPCs: {e}")

    # Display champions of simulated tournaments
    if campeoes_da_semana:
        print("\n--- 🏆 Campeões da Semana ---")
        for campeao_info in campeoes_da_semana:
            print(f"- {campeao_info}")
        print("----------------------------")
        safe_input("Pressione Enter para continuar a temporada...") # Pause for display


    # Avança a semana/ano
    temporada["semana"] += 1
    if temporada["semana"] > 52:
        temporada["semana"] = 1
        temporada["ano"] += 1
        print(f"🎉 Feliz Ano Novo! Bem-vindo a {temporada['ano']}!")

    semana_nova = temporada["semana"]
    print(f"\n--- Avançando para a Semana {semana_nova} de {temporada['ano']} ---")

    # Recuperação de Fadiga e Lesão do jogador
    if jogador.status_lesao["lesionado"]:
        jogador.status_lesao["semanas_restantes"] -= 1
        print(f"❤️  Você está se recuperando da lesão. Semanas restantes: {jogador.status_lesao['semanas_restantes']}")
        if jogador.status_lesao["semanas_restantes"] <= 0:
            jogador.status_lesao["lesionado"] = False
            jogador.fadiga = 0 # Zera a fadiga após se recuperar
            print("✅ Você se recuperou da sua lesão!")
    else:
        # Recupera a fadiga se não estiver jogando
        jogador.fadiga = max(0, jogador.fadiga - FADIGA_RECUPERACAO_SEMANAL)
        print(f"😌 Sua fadiga diminuiu para {jogador.fadiga}%.")
    
    salvar_jogo(nome_save, jogador)

    # Lógica de point decay
    print("\n📉 Verificando pontos a expirar...")
    for jogador_ranking in ranking.ranking:
        pontos_originais = sum(p["pontos"] for p in jogador_ranking.get("pontos_detalhados", []))
        
        pontos_validos = [
            p for p in jogador_ranking.get("pontos_detalhados", []) if p["semana_expiracao"] >= semana_nova
        ]
        
        jogador_ranking["pontos_detalhados"] = pontos_validos
        novo_total = sum(p["pontos"] for p in pontos_validos)
        jogador_ranking["pontos"] = novo_total

        if novo_total < pontos_originais:
            print(f"  - {jogador_ranking['nome']} perdeu {pontos_originais - novo_total} pontos.")

    ranking.ordenar()
    ranking.salvar_ranking()
    salvar_temporada(nome_save, temporada)
    print("✅ Ranking semanal atualizado.")
    
    return temporada
