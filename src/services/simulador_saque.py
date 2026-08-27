import random
from src.constants.match_constants import TipoSaque, EstrategiaSaque
from src.match_state import ContextoPonto, TipoGolpe
from src.utils.match_sim_utils import calcular_bonus_psicologico

class SimuladorSaque:
    """Simula o saque de um jogador."""

    def __init__(self, atributos: dict, atributos_psicologicos: dict = None):
        self.atributos = atributos
        self.atributos_psicologicos = atributos_psicologicos or {}

    def primeiro_saque(self, tipo: TipoSaque, contexto: ContextoPonto = None) -> tuple:
        """
        Simula o primeiro saque.

        Returns:
            (sucesso: bool, resultado: TipoGolpe, descricao: str)
        """
        saque_base = self.atributos.get("saque", 50)

        # Modificadores por tipo de saque
        if tipo == TipoSaque.AGRESSIVO:
            chance_in = saque_base * 0.55  # Menos precisão
            chance_ace = 15 + (saque_base - 50) / 3
        elif tipo == TipoSaque.SEGURO:
            chance_in = saque_base * 0.85  # Mais precisão
            chance_ace = 3 + (saque_base - 50) / 10
        else:  # VARIADO
            chance_in = saque_base * 0.70
            chance_ace = 8 + (saque_base - 50) / 5

        # Aplica bônus psicológico
        if contexto:
            bonus, _ = calcular_bonus_psicologico(self.atributos_psicologicos, contexto)
            chance_in += bonus * 2
            chance_ace += bonus

        # Resultado
        roll = random.random() * 100

        if roll > chance_in:
            return (False, None, "Falta!")

        if roll < chance_ace:
            direcoes = ["no T", "aberto", "no corpo"]
            direcao = random.choice(direcoes)
            return (True, TipoGolpe.ACE, f"Ace {direcao}!")

        return (True, TipoGolpe.SAQUE_EM_JOGO, "Em jogo.")

    def segundo_saque(
        self,
        estrategia_saque: EstrategiaSaque = EstrategiaSaque.SEGURO,
        contexto: ContextoPonto = None,
    ) -> tuple:
        """
        Simula o segundo saque (sempre mais conservador).

        Returns:
            (sucesso: bool, resultado: TipoGolpe, descricao: str)
        """
        saque_base = self.atributos.get("saque", 50)

        if estrategia_saque == EstrategiaSaque.FORCAR:
            chance_in = saque_base * 0.75  # Mais arriscado
        else:  # SEGURO
            chance_in = saque_base * 0.90  # Muito mais conservador

        # Aplica bônus psicológico
        if contexto:
            bonus, _ = calcular_bonus_psicologico(self.atributos_psicologicos, contexto)
            chance_in += bonus * 3

        roll = random.random() * 100

        if roll > chance_in:
            return (False, TipoGolpe.DUPLA_FALTA, "Falta! Dupla falta!")

        return (True, TipoGolpe.SAQUE_EM_JOGO, "Em jogo.")
