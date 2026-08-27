from __future__ import annotations

from typing import Any, List


class MilestoneService:
    """
    Detects significant career achievements (milestones) for narrative impact.
    Follows DRY by centralizing achievement logic.
    """

    @staticmethod
    def detect_match_milestones(jogador: Any, adversario_nome: str, adversario_ranking: int, jogador_venceu: bool) -> List[str]:
        milestones = []
        
        if not jogador_venceu:
            return milestones

        # 1. Top 10 Victory
        if adversario_ranking <= 10:
            milestones.append(f"VITÓRIA GIGANTE! {jogador.nome} derruba o Top 10 {adversario_nome} em uma partida memorável!")

        # 2. Victory Counts (Simplified)
        vitorias = len([p for p in getattr(jogador, "historico_partidas", []) if p.get("resultado") == "V"])
        if vitorias == 1:
            milestones.append("PRIMEIRA DE MUITAS: Sua primeira vitória no circuito profissional!")
        elif vitorias % 50 == 0:
            milestones.append(f"MARCO HISTÓRICO: {jogador.nome} alcança a incrível marca de {vitorias} vitórias na carreira!")

        return milestones

    @staticmethod
    def detect_ranking_milestones(jogador: Any, nova_posicao: int) -> List[str]:
        milestones = []
        pos_antiga = getattr(jogador, "_posicao_anterior", 9999)
        try:
            pos_antiga = int(pos_antiga)
        except (TypeError, ValueError):
            pos_antiga = 9999
        try:
            nova_posicao = int(nova_posicao)
        except (TypeError, ValueError):
            nova_posicao = 9999
        
        if nova_posicao < pos_antiga:
            if nova_posicao <= 1 and pos_antiga > 1:
                milestones.append("O NOVO REI: Você acaba de se tornar o Número 1 do Mundo!")
            elif nova_posicao <= 10 and pos_antiga > 10:
                milestones.append("ELITE MUNDIAL: Você entrou para o seleto grupo dos Top 10!")
            elif nova_posicao <= 100 and pos_antiga > 100:
                milestones.append("TOP 100: Você agora faz parte da elite que disputa os grandes torneios!")

        jogador._posicao_anterior = nova_posicao
        return milestones
