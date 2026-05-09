from __future__ import annotations
from typing import Any, List, Dict, Optional
from src.jogador import normalizar_nome
from src.dados import obter_torneios_da_semana
from src.tournament_manager import WeekTournamentManager

def _campeao_exibivel(nome_campeao: Any) -> bool:
    """Verifica se o nome do campeão é válido para exibição."""
    nome = str(nome_campeao or "").strip()
    if not nome:
        return False
    nome_norm = normalizar_nome(nome)
    # Filtra nomes de bots e placeholders de sistema
    invalidos = {"---", "tbd", "none", "null", "na", "n/a", "cancelado"}
    if nome_norm in invalidos or nome_norm.startswith("bot ") or nome_norm.startswith("n/a "):
        return False
    return True

def simular_torneios_semanais_npc(
    nome_save: str, 
    semana_atual: int, 
    jogador: Any, 
    player_active_tournament_state: Optional[Dict] = None
) -> List[Dict]:
    """
    Encapsula a simulação de torneios onde o jogador não participa, em ambos os tours.
    Retorna uma lista de resumos dos campeões.
    """
    # Gerenciadores para ambos os tours
    manager_atp = WeekTournamentManager(nome_save, semana_atual, genero="masculino")
    manager_wta = WeekTournamentManager(nome_save, semana_atual, genero="feminino")

    # 1. Inicializa os torneios
    for gen, manager in [("masculino", manager_atp), ("feminino", manager_wta)]:
        torneios_info = obter_torneios_da_semana(semana_atual, genero=gen)
        # Marca qual torneio o jogador está participando para evitar conflito de simulação
        for info in torneios_info:
            if player_active_tournament_state and gen == jogador.genero:
                if info["nome"] == player_active_tournament_state.get("torneio"):
                    info["participando"] = True

        manager.inicializar_torneios(torneios_info, jogador_nome=jogador.nome)

    # 2. Simula todos os torneios até o fim (máximo de 7 rodadas para um Grand Slam)
    for manager in [manager_atp, manager_wta]:
        for _ in range(7):
            manager.simular_rodada_para_todos(
                fase_alvo="finalizado", jogador_nome=jogador.nome
            )

    # 3. Coleta os campeões
    campeoes_da_semana = []
    for manager in [manager_atp, manager_wta]:
        resumos = manager.obter_resumo_semanal()
        t_label = "ATP" if manager.genero == "masculino" else "WTA"
        for r in resumos:
            campeao_simples = r.get("campeao")
            campeao_duplas = r.get("campeao_duplas")

            if _campeao_exibivel(campeao_simples):
                campeoes_da_semana.append(
                    {
                        "tour": t_label,
                        "torneio": r.get("nome"),
                        "simples": campeao_simples,
                        "duplas": (
                            campeao_duplas
                            if _campeao_exibivel(campeao_duplas)
                            else None
                        ),
                    }
                )

    return campeoes_da_semana
