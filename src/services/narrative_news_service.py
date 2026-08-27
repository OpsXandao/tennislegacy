from __future__ import annotations

import random
from typing import Any, List

from src.jogador import normalizar_nome


class NarrativeNewsService:
    """
    Factory for dynamic, journalism-style headlines.
    Follows DRY and KISS by centralizing narrative templates.
    """

    @staticmethod
    def generate_player_news(jogador: Any, ranking_pos: int, tournament_state: dict | None) -> List[str]:
        noticias = []
        nome_up = jogador.nome.upper()

        # 1. Ranking Milestones
        if ranking_pos <= 1:
            noticias.append(f"NO TOPO DO MUNDO: {nome_up} assume a liderança do ranking e faz história!")
        elif ranking_pos <= 10:
            noticias.append(f"FENÔMENO: {nome_up} se consolida na elite do tênis mundial entre os Top 10!")
        elif ranking_pos <= 100:
            noticias.append(f"EM ASCENSÃO: O mundo do tênis começa a prestar atenção no talento de {nome_up}.")

        # 2. Tournament Success
        if tournament_state and tournament_state.get("fase_atual") == "finalizado":
            campeao = tournament_state.get("campeao_simples")
            torneio_nome = str(tournament_state.get("torneio", "Torneio")).upper()
            if campeao and normalizar_nome(campeao) == normalizar_nome(jogador.nome):
                noticias.append(f"CAMPEÃO INQUESTIONÁVEL! {nome_up} levanta o troféu em {torneio_nome}!")
            elif campeao:
                noticias.append(f"{campeao.upper()} conquista o título de {torneio_nome} após semana intensa.")

        # 3. Sponsorship
        if getattr(jogador, "patrocinios", []):
            noticias.append(f"MERCADO: {nome_up} atrai novos investidores e expande sua marca global.")

        # 4. Match Toughness (Ritmo)
        ritmo = getattr(jogador, "ritmo_jogo", 50)
        if ritmo < 30:
            noticias.append(f"PREOCUPAÇÃO: Analistas apontam que {nome_up} está sem ritmo de jogo e pode sofrer nas próximas rodadas.")
        elif ritmo > 85:
            noticias.append(f"EM ESTADO DE GRAÇA: {nome_up} exibe um ritmo de jogo avassalador e parece imbatível no momento.")

        return noticias

    @staticmethod
    def generate_circuit_news(tournament_manager: Any, active_tournament_name: str | None) -> List[str]:
        noticias = []
        try:
            for nome_t, estado in tournament_manager.torneios.items():
                if active_tournament_name and nome_t == active_tournament_name:
                    continue
                
                if estado.get("fase_atual") == "finalizado":
                    campeao = estado.get("campeao_simples")
                    if campeao:
                        noticias.append(f"CIRCUITO: {campeao.upper()} domina as quadras e vence em {nome_t.upper()}.")
                
                # Upset detection (Zebra)
                for fase in ["final", "semifinal", "quartas"]:
                    resultados = estado.get("resultados", {}).get(fase, [])
                    for res in resultados:
                        if random.random() < 0.10: # Upset probability
                            vencedor = str(res.get("vencedor", "")).upper()
                            noticias.append(f"SURPRESA EM {nome_t.upper()}: {vencedor} derruba favoritos e avança!")
        except Exception:
            pass
        return noticias

    @staticmethod
    def get_filler_news() -> str:
        _FRASES_MUNDO = [
            "AUDIÊNCIA DO TÊNIS SOBE 20% NESTA TEMPORADA COM NOVOS TALENTOS.",
            "NOVAS REGRAS DE QUADRA ESTÃO SENDO DISCUTIDAS PARA O PRÓXIMO ANO.",
            "TOUR MUNDIAL ANUNCIA EXPANSÃO PARA NOVOS MERCADOS EMERGENTES.",
            "RECORDE DE PÚBLICO EM GRAND SLAMS SUPERA EXPECTATIVAS.",
            "TECNOLOGIA EM RAQUETES: Nova geração promete golpes 15% mais rápidos.",
        ]
        return random.choice(_FRASES_MUNDO)
