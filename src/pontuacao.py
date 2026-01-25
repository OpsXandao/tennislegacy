import json
from src.dados import get_caminho_ranking_save, get_caminho_torneio_save
from src.calendario import carregar_temporada
from src.ranking import SistemaRanking
from src.jogador import normalizar_nome

PONTOS_ATP_250 = {
    "campeao": 250,
    "final": 150,
    "semifinal": 90,
    "quartas": 45,
    "oitavas": 20,
    "pre_oitavas": 10,  # Rodada de 32
    "qualy_2": 5,  # Classificado
    "qualy_1": 0,
}

PONTOS_GRAND_SLAM = {
    "campeao": 2000,
    "final": 1200,
    "semifinal": 720,
    "quartas": 360,
    "r16": 180, # Round of 16
    "r32": 90,  # Round of 32
    "r64": 45,  # Round of 64
    "r128": 10, # Round of 128 (first round loss)
    "qualy_r3": 30, # Final round of qualifying
    "qualy_r2": 16, # Second round of qualifying
    "qualy_r1": 7,  # First round of qualifying
}

PONTOS_ATP_500 = {
    "campeao": 500,
    "final": 300,
    "semifinal": 180,
    "quartas": 90,
    "oitavas": 45,  # Round of 16
    "pre_oitavas": 20, # Round of 32
    "qualy_2": 10,  # Qualificado
    "qualy_1": 0,
}

PONTOS_ATP_1000 = {
    "campeao": 1000,
    "final": 600,
    "semifinal": 360,
    "quartas": 180,
    "oitavas": 90,  # Round of 16
    "r32": 45, # Round of 32
    "r64": 25, # Round of 64
    "qualy_2": 16,  # Qualificado
    "qualy_1": 0,
}

PONTOS_DAVIS_CUP = {
    "campeao": 750,  # Example points for winning the whole Davis Cup
    "final": 500,    # Losing finalist
    "semifinal": 350,
    "quartas": 200,
    # Davis Cup has a different format, points for individual matches might be complex
    # For simplicity, I'll assign points based on team progression.
}


def distribuir_pontos_torneio(nome_save):
    """
    Lê o resultado de um torneio finalizado, calcula e distribui os pontos
    para os jogadores no ranking do save usando a estrutura de pontos detalhados.
    """
    caminho_torneio = get_caminho_torneio_save(nome_save)
    try:
        with open(caminho_torneio, "r", encoding="utf-8") as f:
            estado_torneio = json.load(f)
    except FileNotFoundError:
        print(f"ℹ️ Arquivo de torneio para o save '{nome_save}' não encontrado. Nenhum ponto a distribuir.")
        return

    ranking = SistemaRanking(get_caminho_ranking_save(nome_save))
    temporada = carregar_temporada(nome_save)
    semana_atual = temporada["semana"]
    
    resultados = estado_torneio.get("resultados", {})
    
    # Get tournament type and select appropriate point structure
    tournament_type = estado_torneio.get("tournament_data", {}).get("tipo", "ATP 250")
    nome_torneio = estado_torneio.get("torneio", "Torneio Desconhecido")

    pontos_map = PONTOS_ATP_250 # Default
    fases_ordem = ["qualy_1", "qualy_2", "pre_oitavas", "oitavas", "quartas", "semifinal", "final"]

    if tournament_type == "Grand Slam":
        pontos_map = PONTOS_GRAND_SLAM
        fases_ordem = ["qualy_r1", "qualy_r2", "qualy_r3", "r128", "r64", "r32", "r16", "quartas", "semifinal", "final"]
    elif tournament_type == "ATP 500":
        pontos_map = PONTOS_ATP_500
        fases_ordem = ["qualy_1", "qualy_2", "pre_oitavas", "oitavas", "quartas", "semifinal", "final"] # ATP 500 can have 32 or 48 players
    elif tournament_type == "ATP 1000":
        pontos_map = PONTOS_ATP_1000
        fases_ordem = ["qualy_1", "qualy_2", "r64", "r32", "r16", "quartas", "semifinal", "final"] # ATP 1000 main draw starts often at R96 or R128 with byes
    elif tournament_type == "Davis Cup":
        pontos_map = PONTOS_DAVIS_CUP
        # Davis Cup points are different, likely awarded to all team members based on team's final position
        # For simplicity, we'll award points to the winning player for now if individual results are recorded.
        # This will need further refinement for proper team event scoring.
        print(f"ℹ️ Pontuação da Davis Cup ({nome_torneio}) será implementada em breve. Nenhum ponto individual distribuído no momento.")
        return # Skip point distribution for Davis Cup for now

    # Mapeia o quão longe cada jogador foi
    progresso_jogador = {}
    for fase in fases_ordem:
        for partida in resultados.get(fase, []):
            try:
                # Ensure players are dictionaries with 'nome'
                player_a_dict = partida.get('jogador_a', {})
                player_b_dict = partida.get('jogador_b', {})
                vencedor_dict = partida.get('vencedor', {})

                player_a_name = normalizar_nome(player_a_dict.get('nome', ''))
                player_b_name = normalizar_nome(player_b_dict.get('nome', ''))
                vencedor_name = normalizar_nome(vencedor_dict.get('nome', ''))
            except (KeyError, AttributeError):
                continue # Skip if data is malformed

            # Set current phase for both players
            if player_a_name:
                progresso_jogador[player_a_name] = fase
            if player_b_name:
                progresso_jogador[player_b_name] = fase
            
            # Advance winner to the next phase for further point calculation
            try:
                indice_fase_atual = fases_ordem.index(fase)
                if indice_fase_atual + 1 < len(fases_ordem):
                    if vencedor_name:
                        progresso_jogador[vencedor_name] = fases_ordem[indice_fase_atual + 1]
            except ValueError:
                pass # This happens if fase is not in fases_ordem, which shouldn't happen with dynamic list

    # Special handling for the champion (ensures 'campeao' phase is correctly assigned)
    if "final" in resultados and resultados["final"]:
        try:
            vencedor_final_dict = resultados["final"][0].get('vencedor', {})
            vencedor_final_name = normalizar_nome(vencedor_final_dict.get('nome', ''))
            if vencedor_final_name:
                progresso_jogador[vencedor_final_name] = "campeao"
        except (KeyError, IndexError, AttributeError):
            pass

    # Calcula e adiciona os pontos
    pontos_distribuidos = {}
    for jogador_nome, progresso_fase in progresso_jogador.items():
        pontos = pontos_map.get(progresso_fase, 0)
        if pontos > 0:
            pontos_distribuidos[jogador_nome] = pontos

    if not pontos_distribuidos:
        print(f"ℹ️ Nenhum ponto a ser distribuído para o torneio '{nome_torneio}'.")
        return

    print(f"\n🏆 Pontuação do Torneio: {nome_torneio} ({tournament_type})")
    # Ordena para mostrar do maior para o menor
    for nome, pontos in sorted(pontos_distribuidos.items(), key=lambda item: item[1], reverse=True):
        semana_expiracao = (semana_atual + 51) % 52 + 1 # Expira na mesma semana do próximo ano
        ranking.adicionar_pontos(nome, pontos, semana_expiracao)
        fase_atingida_str = progresso_jogador.get(nome, "desconhecida").replace("_", " ").title()
        print(f"'{nome}' ganhou {pontos} pontos por chegar em: {fase_atingida_str}.")

    ranking.ordenar()
    ranking.salvar_ranking()
    print("✅ Ranking atualizado com sucesso!")
