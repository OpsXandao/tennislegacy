"""
Módulo de simulação de partidas de tênis com suporte a modos rápido e detalhado.
"""

import random
from enum import Enum
from dataclasses import dataclass
from typing import Optional

from src.staff_constants import PROFISSIONAIS_DISPONIVEIS
from src.entidade_utils import (
    obter_atributos,
    obter_atributos_psicologicos,
)
from src.superficie_utils import normalizar_superficie
from src.match_constants import (
    TipoSaque,
    EstrategiaSaque,
    IntencaoPonto,
    MatchPointStats,
)
from src.simulacao_effects import (
    multiplicador_lesao as fx_multiplicador_lesao,
    multiplicador_doenca as fx_multiplicador_doenca,
    aplicar_multiplicador_atributos as fx_aplicar_multiplicador_atributos,
    calcular_mod_ambiente as fx_calcular_mod_ambiente,
)


@dataclass
class EstatisticasPartida:
    """Estatísticas coletadas durante uma partida."""

    # Saque
    aces: int = 0
    duplas_faltas: int = 0
    primeiro_saque_in: int = 0
    primeiro_saque_total: int = 0

    # Pontos
    winners: int = 0
    erros_nao_forcados: int = 0
    pontos_ganhos_saque: int = 0
    pontos_total_saque: int = 0
    pontos_ganhos_devolucao: int = 0
    pontos_total_devolucao: int = 0

    # Break points
    break_points_convertidos: int = 0
    break_points_total: int = 0
    break_points_salvos: int = 0
    break_points_enfrentados: int = 0

    # Rally profile
    rallies_curtos: int = 0
    rallies_medios: int = 0
    rallies_longos: int = 0

    def percentual_primeiro_saque(self) -> str:
        """Retorna o percentual de primeiro saque in."""
        if self.primeiro_saque_total == 0:
            return "0%"
        pct = (self.primeiro_saque_in / self.primeiro_saque_total) * 100
        return f"{pct:.0f}%"

    def percentual_pontos_saque(self) -> str:
        """Retorna o percentual de pontos ganhos no saque."""
        if self.pontos_total_saque == 0:
            return "0%"
        pct = (self.pontos_ganhos_saque / self.pontos_total_saque) * 100
        return f"{pct:.0f}%"

    def percentual_pontos_devolucao(self) -> str:
        """Retorna o percentual de pontos ganhos na devolução."""
        if self.pontos_total_devolucao == 0:
            return "0%"
        pct = (self.pontos_ganhos_devolucao / self.pontos_total_devolucao) * 100
        return f"{pct:.0f}%"

    def merge(self, other: "EstatisticasPartida"):
        """Acumula estatísticas de outra instância."""
        self.aces += other.aces
        self.duplas_faltas += other.duplas_faltas
        self.primeiro_saque_in += other.primeiro_saque_in
        self.primeiro_saque_total += other.primeiro_saque_total
        self.winners += other.winners
        self.erros_nao_forcados += other.erros_nao_forcados
        self.pontos_ganhos_saque += other.pontos_ganhos_saque
        self.pontos_total_saque += other.pontos_total_saque
        self.pontos_ganhos_devolucao += other.pontos_ganhos_devolucao
        self.pontos_total_devolucao += other.pontos_total_devolucao
        self.break_points_convertidos += other.break_points_convertidos
        self.break_points_total += other.break_points_total
        self.break_points_salvos += other.break_points_salvos
        self.break_points_enfrentados += other.break_points_enfrentados
        self.rallies_curtos += other.rallies_curtos
        self.rallies_medios += other.rallies_medios
        self.rallies_longos += other.rallies_longos

    def exibir(
        self,
        nome_jogador: str,
        nome_adversario: str,
        stats_adversario: "EstatisticasPartida",
    ) -> str:
        """Retorna estatísticas comparativas formatadas para a UI imprimir."""
        bp_j = f"{self.break_points_convertidos}/{self.break_points_total}"
        bp_a = f"{stats_adversario.break_points_convertidos}/{stats_adversario.break_points_total}"
        linhas = [
            f"\n{'='*55}",
            f"{'ESTATISTICAS':^55}",
            f"{'='*55}",
            f"{'':25} {'Voce':>12} {'Adversario':>15}",
            f"{'-'*55}",
            f"{'Aces':<25} {self.aces:>12} {stats_adversario.aces:>15}",
            f"{'Duplas Faltas':<25} {self.duplas_faltas:>12} {stats_adversario.duplas_faltas:>15}",
            f"{'1o Saque %':<25} {self.percentual_primeiro_saque():>12} {stats_adversario.percentual_primeiro_saque():>15}",
            f"{'Winners':<25} {self.winners:>12} {stats_adversario.winners:>15}",
            f"{'Erros Nao Forcados':<25} {self.erros_nao_forcados:>12} {stats_adversario.erros_nao_forcados:>15}",
            f"{'Pontos no Saque %':<25} {self.percentual_pontos_saque():>12} {stats_adversario.percentual_pontos_saque():>15}",
            f"{'Pontos na Devolucao %':<25} {self.percentual_pontos_devolucao():>12} {stats_adversario.percentual_pontos_devolucao():>15}",
            f"{'Break Points':<25} {bp_j:>12} {bp_a:>15}",
            f"{'='*55}",
        ]
        return "\n".join(linhas)


class TipoGolpe(Enum):
    ACE = "ace"
    DUPLA_FALTA = "dupla_falta"
    WINNER_FOREHAND = "winner_forehand"
    WINNER_BACKHAND = "winner_backhand"
    WINNER_VOLEIO = "winner_voleio"
    ERRO_NAO_FORCADO = "erro_nao_forcado"
    PONTO_CONSTRUIDO = "ponto_construido"
    DROP_SHOT = "drop_shot"
    LOB_WINNER = "lob_winner"
    SAQUE_EM_JOGO = "saque_em_jogo"


@dataclass
class ContextoPonto:
    """Contexto do ponto atual na partida."""

    sacador: str  # "j" (jogador) ou "a" (adversário)
    placar_game: tuple  # (pontos_j, pontos_a) em formato 0-4
    placar_set: tuple  # (games_j, games_a)
    placar_partida: tuple  # (sets_j, sets_a)
    sets_para_vencer: int = 2
    is_tiebreak: bool = False
    tiebreak_alvo: int = 7

    def is_break_point(self) -> bool:
        """Verifica se é break point (quem recebe pode quebrar)."""
        if self.is_tiebreak:
            return False
        pj, pa = self.placar_game
        if self.sacador == "j":
            # Adversário tem break point se pode ganhar o game
            return pa >= 3 and pa > pj
        else:
            # Jogador tem break point se pode ganhar o game
            return pj >= 3 and pj > pa

    def is_set_point(self) -> bool:
        """Verifica se é set point para algum jogador."""
        pj, pa = self.placar_game
        if self.is_tiebreak:
            alvo = max(2, int(self.tiebreak_alvo or 7))
            # Jogador tem set point se atingir alvo-1 e estiver na frente
            if pj >= alvo - 1 and pj > pa:
                return True
            # Adversário tem set point se atingir alvo-1 e estiver na frente
            if pa >= alvo - 1 and pa > pj:
                return True
            return False

        gj, ga = self.placar_set
        # Jogador pode fechar o set
        if gj >= 5 and gj > ga and pj >= 3 and pj > pa:
            return True
        # Adversário pode fechar o set
        if ga >= 5 and ga > gj and pa >= 3 and pa > pj:
            return True
        return False

    def is_match_point(self) -> bool:
        """Verifica se é match point para algum jogador."""
        sj, sa = self.placar_partida
        pj, pa = self.placar_game

        if self.is_tiebreak:
            alvo = max(2, int(self.tiebreak_alvo or 7))
            jogador_tem_set_point = pj >= alvo - 1 and pj > pa
            adversario_tem_set_point = pa >= alvo - 1 and pa > pj

            # É match point se for set point e estiver no set decisivo
            if sj == self.sets_para_vencer - 1 and jogador_tem_set_point:
                return True
            if sa == self.sets_para_vencer - 1 and adversario_tem_set_point:
                return True
            return False

        gj, ga = self.placar_set
        # Jogador pode fechar a partida
        if (
            sj == self.sets_para_vencer - 1
            and gj >= 5
            and gj > ga
            and pj >= 3
            and pj > pa
        ):
            return True
        # Adversário pode fechar a partida
        if (
            sa == self.sets_para_vencer - 1
            and ga >= 5
            and ga > gj
            and pa >= 3
            and pa > pj
        ):
            return True
        return False

    def jogador_perdendo(self) -> bool:
        """Verifica se o jogador está perdendo por 2+ games no set atual."""
        gj, ga = self.placar_set
        return ga >= gj + 2

    def adversario_perdendo(self) -> bool:
        """Verifica se o adversário está perdendo por 2+ games no set atual."""
        gj, ga = self.placar_set
        return gj >= ga + 2


@dataclass
class ContextoPartida:
    """Contexto geral da partida."""

    superficie: str = "dura"
    stamina_j: float = 100.0
    stamina_a: float = 100.0
    moral_j: float = 70.0
    moral_a: float = 70.0
    ritmo_j: float = 50.0
    ritmo_a: float = 50.0
    momentum_j: int = 0
    momentum_a: int = 0
    clima: str = "ameno"
    vento: int = 0
    umidade: int = 50
    altitude_m: int = 0
    indoor: bool = False
    sequencia_j: int = 0
    sequencia_a: int = 0
    ultimo_vencedor: Optional[str] = None


SUPERFICIE_MODS = {
    "dura": {
        "saque": 1.02,
        "forehand": 1.01,
        "backhand": 1.01,
        "topspin": 1.0,
        "voleio": 1.0,
        "slice": 1.0,
        "movimento": 1.0,
        "lob": 1.0,
        "winner": 1.01,
    },
    "saibro": {
        "saque": 0.92,
        "forehand": 1.03,
        "backhand": 1.03,
        "topspin": 1.12,
        "voleio": 0.93,
        "slice": 1.03,
        "movimento": 1.08,
        "lob": 1.06,
        "winner": 0.94,
    },
    "grama": {
        "saque": 1.12,
        "forehand": 1.02,
        "backhand": 1.0,
        "topspin": 1.04,
        "voleio": 1.12,
        "slice": 1.08,
        "movimento": 0.95,
        "lob": 0.93,
        "winner": 1.06,
    },
}


def calcular_bonus_psicologico(
    atributos_psicologicos: dict, contexto: ContextoPonto, eh_jogador: bool = True
) -> float:
    """
    Calcula o bônus psicológico baseado no contexto do ponto.

    Args:
        atributos_psicologicos: Dict com concentracao, agressividade, leitura_de_jogo, determinacao
        contexto: ContextoPonto atual
        eh_jogador: True se é o jogador do usuário, False se é adversário

    Returns:
        Bônus a ser aplicado no cálculo do ponto
    """
    if not atributos_psicologicos:
        return 0

    psico = atributos_psicologicos
    bonus = 0

    # Break point - concentração e determinação
    if contexto.is_break_point():
        bonus += (psico.get("concentracao", 50) - 50) / 10
        bonus += (psico.get("determinacao", 50) - 50) / 15

    # Set point - concentração e agressividade
    if contexto.is_set_point():
        bonus += (psico.get("concentracao", 50) - 50) / 10
        bonus += (psico.get("agressividade", 50) - 50) / 20

    # Match point - todos os 4 atributos
    if contexto.is_match_point():
        bonus += (psico.get("concentracao", 50) - 50) / 8
        bonus += (psico.get("agressividade", 50) - 50) / 15
        bonus += (psico.get("leitura_de_jogo", 50) - 50) / 12
        bonus += (psico.get("determinacao", 50) - 50) / 10

    # Perdendo por 2+ games - determinação
    perdendo = (
        contexto.jogador_perdendo() if eh_jogador else contexto.adversario_perdendo()
    )
    if perdendo:
        bonus += (psico.get("determinacao", 50) - 50) / 10

    # Penalidade base sempre ativa — nervosismo afeta até pontos normais
    concentracao = psico.get("concentracao", 50)
    if concentracao < 45:
        bonus -= (45 - concentracao) * 0.06  # até -2.7 por ponto normal
    agressividade_val = psico.get("agressividade", 50)
    if (
        agressividade_val > 80
        and not contexto.is_break_point()
        and not contexto.is_match_point()
    ):
        # Muito agressivo em momentos normais = mais erros
        bonus -= (agressividade_val - 80) * 0.04

    return bonus


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
            bonus = calcular_bonus_psicologico(self.atributos_psicologicos, contexto)
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
            bonus = calcular_bonus_psicologico(self.atributos_psicologicos, contexto)
            chance_in += bonus * 3

        roll = random.random() * 100

        if roll > chance_in:
            return (False, TipoGolpe.DUPLA_FALTA, "Falta! Dupla falta!")

        return (True, TipoGolpe.SAQUE_EM_JOGO, "Em jogo.")


class SimuladorPonto:
    """
    Simula pontos baseado em confronto direto de atributos.

    O resultado de cada ponto é determinado pela comparação dos atributos
    relevantes de cada jogador, com um pequeno fator de sorte.
    """

    # Fator de sorte: 0 = 100% determinístico, 1 = 100% aleatório
    FATOR_SORTE = 0.15  # 15% de variância aleatória

    DESCRICOES_RALLY = [
        "Forehand cruzado... Backhand na paralela...",
        "Troca de bolas intensa no fundo de quadra...",
        "Slice defensivo profundo... Approach na rede...",
        "Topspin com muito efeito... Deixadinha inesperada...",
        "Subida à rede... Lob de cobertura...",
        "Bola alta e potente... Smash para definir!",
        "Variação de ritmo com slice e topspin...",
        "Jogo de pernas incrível para chegar na bola...",
        "Rally disputado, com ambos os jogadores se defendendo bem.",
        "Devolução agressiva que coloca pressão desde o início.",
    ]

    def __init__(self, jogador, adversario: dict):
        self.jogador = jogador
        self.adversario = adversario

    def _get_atributos_jogador(self):
        return obter_atributos(self.jogador)

    def _get_psico_jogador(self):
        psico = obter_atributos_psicologicos(self.jogador, copiar=True)

        # Bônus do Treinador
        if hasattr(self.jogador, "treinador") and self.jogador.treinador:
            t_data = PROFISSIONAIS_DISPONIVEIS.get(self.jogador.treinador)
            if t_data:
                bonus = t_data.get("bonus_tatico", 0)
                if bonus > 0:
                    for k in psico:
                        psico[k] += bonus
        return psico

    def _get_atributos_adversario(self):
        return obter_atributos(self.adversario)

    def _get_psico_adversario(self):
        return obter_atributos_psicologicos(self.adversario)

    def _padronizar_descricoes(self, descricoes):
        padronizadas = []
        for desc in descricoes:
            desc_str = str(desc).strip()
            lower = desc_str.lower()
            if lower.startswith("1o saque") or lower.startswith("2o saque"):
                padronizadas.append(f"[SAQUE] {desc_str}")
            elif lower.startswith("rally"):
                padronizadas.append(f"[RALLY] {desc_str}")
            elif "domina o rally" in lower:
                padronizadas.append(f"[MOMENTO] {desc_str}")
            else:
                padronizadas.append(f"[RESULTADO] {desc_str}")
        return padronizadas

    def _get_simulador_saque(self, contexto: ContextoPonto):
        if contexto.sacador == "j":
            atributos = self._get_atributos_jogador()
            psico = self._get_psico_jogador()
        else:
            atributos = self._get_atributos_adversario()
            psico = self._get_psico_adversario()
        return SimuladorSaque(atributos, psico)

    @staticmethod
    def _contexto_padrao_saque() -> ContextoPonto:
        return ContextoPonto(
            sacador="j",
            placar_game=(0, 0),
            placar_set=(0, 0),
            placar_partida=(0, 0),
        )

    def primeiro_saque(self, tipo: TipoSaque, contexto: ContextoPonto = None) -> tuple:
        contexto = contexto or self._contexto_padrao_saque()
        simulador = self._get_simulador_saque(contexto)
        return simulador.primeiro_saque(tipo, contexto)

    def segundo_saque(
        self,
        estrategia_saque: EstrategiaSaque = EstrategiaSaque.SEGURO,
        contexto: ContextoPonto = None,
    ) -> tuple:
        contexto = contexto or self._contexto_padrao_saque()
        simulador = self._get_simulador_saque(contexto)
        return simulador.segundo_saque(estrategia_saque, contexto)

    def _confronto(self, valor_atacante: float, valor_defensor: float) -> bool:
        """
        Realiza um confronto direto entre dois valores de atributo.

        A chance de vitória é proporcional à diferença de atributos.
        Quanto maior a diferença, mais previsível o resultado.

        Args:
            valor_atacante: Valor do atributo do atacante (0-100)
            valor_defensor: Valor do atributo do defensor (0-100)

        Returns:
            True se atacante vence, False se defensor vence
        """
        # Normaliza os valores para 0-1
        atk = valor_atacante / 100.0
        def_ = valor_defensor / 100.0

        # Calcula vantagem do atacante (-1 a 1)
        vantagem = atk - def_

        # Converte vantagem em probabilidade (0 a 1)
        # Vantagem de 0 = 50%, vantagem de 0.5 = ~85%, vantagem de -0.5 = ~15%
        prob_base = 0.5 + (vantagem * 0.7)  # Escala a vantagem
        prob_base = max(0.1, min(0.9, prob_base))  # Limita entre 10% e 90%

        # Aplica fator de sorte
        sorte = (random.random() - 0.5) * 2 * self.FATOR_SORTE  # -FATOR a +FATOR
        prob_final = prob_base + sorte
        prob_final = max(0.05, min(0.95, prob_final))  # Limita entre 5% e 95%

        return random.random() < prob_final

    @staticmethod
    def _calcular_n_trocas(
        superficie: str,
        estilo_j: str,
        estilo_a: str,
        atributos_j: dict,
        atributos_a: dict,
        stamina_j: float,
        stamina_a: float,
    ) -> int:
        """Calcula quantas trocas o rally terá baseado no contexto real da partida."""
        sup = normalizar_superficie(superficie)
        bases = {"saibro": 5.5, "dura": 3.5, "grama": 2.0}
        media = bases.get(sup, 3.5)

        # Dois baseliners = rallies mais longos; serve&volley encerra rápido
        def _peso_estilo(e: str) -> float:
            if e == "atacar_do_fundo":
                return 1.0
            if e == "atacar_pelo_meio":
                return 0.80
            return 0.45  # atacar_na_rede termina o ponto rápido

        media *= (_peso_estilo(estilo_j) + _peso_estilo(estilo_a)) / 2.0

        # Fisico e movimento prolongam rallies
        fisico = (atributos_j.get("fisico", 50) + atributos_a.get("fisico", 50)) / 2
        movimento = (
            atributos_j.get("movimento", 50) + atributos_a.get("movimento", 50)
        ) / 2
        media += (fisico - 50) / 50.0  # ±1 troca
        media += (movimento - 50) / 100.0  # ±0.5 troca

        # Stamina baixa encerra rallies mais cedo (erros por cansaço)
        avg_stamina = (stamina_j + stamina_a) / 2
        if avg_stamina < 35:
            media *= 0.60
        elif avg_stamina < 55:
            media *= 0.78

        media = max(1.0, media)
        # Distribuição com variância proporcional à média (rallies têm alta variância)
        n = round(random.gauss(media, media * 0.55))
        return max(1, min(n, 18))

    @staticmethod
    def _n_trocas_para_intensidade(n: int) -> str:
        """Converte número de trocas em categoria de intensidade para stamina."""
        if n <= 2:
            return "curto"
        if n <= 5:
            return "medio"
        if n <= 9:
            return "longo"
        return "muito_longo"

    def _simular_rally_trocas(
        self,
        poder_j: float,
        poder_a: float,
        psico_j: dict,
        psico_a: dict,
        stamina_j: float = 100.0,
        stamina_a: float = 100.0,
        superficie: str = "dura",
        estilo_j: str = "atacar_do_fundo",
        estilo_a: str = "atacar_do_fundo",
        atributos_j: dict = None,
        atributos_a: dict = None,
    ) -> tuple:
        """Simula N trocas contextuais antes da resolução final do rally.

        Retorna (venceu_j: bool, vantagem: float, n_trocas: int).
        - n_trocas determina o custo de stamina (conectado ao sistema de intensidade)
        - vantagem ∈ [0, ~0.5] indica dominância (usado em _determinar_tipo_finalizacao)
        - leitura_de_jogo pesa mais em rallies longos (accumulation effect)
        """
        atributos_j = atributos_j or {}
        atributos_a = atributos_a or {}

        n_trocas = self._calcular_n_trocas(
            superficie,
            estilo_j,
            estilo_a,
            atributos_j,
            atributos_a,
            stamina_j,
            stamina_a,
        )

        leitura_j = psico_j.get("leitura_de_jogo", 50)
        leitura_a = psico_a.get("leitura_de_jogo", 50)
        vantagem = 0.0

        for i in range(n_trocas - 1):
            # Leitura de jogo tem efeito cumulativo — mais impacto em rallies longos
            escala = 1.0 + i * 0.025
            p_j = poder_j * (1.0 + (leitura_j - 50) * 0.002 * escala)
            p_a = poder_a * (1.0 + (leitura_a - 50) * 0.002 * escala)
            if self._confronto(p_j, p_a):
                vantagem += 0.1
            else:
                vantagem -= 0.1

        # Troca decisiva com vantagem acumulada
        p_j_final = poder_j * (1.0 + vantagem)
        p_a_final = poder_a * (1.0 - vantagem)
        venceu_j = self._confronto(p_j_final, p_a_final)
        return venceu_j, abs(vantagem), n_trocas

    def _stamina_mod(
        self,
        stamina: float,
        atributos: dict = None,
        estilo: str = None,
        superficie: str = None,
    ) -> float:
        stamina = max(0.0, min(100.0, stamina))
        atributos = atributos or {}
        fisico = atributos.get("fisico", 50)
        movimento = atributos.get("movimento", 50)

        # Físico melhora a tolerância ao cansaço; baixo físico piora.
        stamina_efetiva = stamina + (fisico - 50) * 0.4
        stamina_efetiva = max(0.0, min(100.0, stamina_efetiva))
        mod = 0.7 + (stamina_efetiva / 100.0) * 0.3

        # Fundo de quadra + bom movimento segura melhor em rallys longos quando cansado.
        if estilo == "atacar_do_fundo" and stamina < 55:
            mod += (movimento - 50) / 800.0

        # Ajuste leve por superfície x estilo (preset ATP realista)
        if superficie and estilo:
            superficie = normalizar_superficie(superficie)
            estilo_mod = {
                "dura": {
                    "atacar_do_fundo": 1.0,
                    "atacar_pelo_meio": 1.01,
                    "atacar_na_rede": 1.0,
                },
                "saibro": {
                    "atacar_do_fundo": 1.02,
                    "atacar_pelo_meio": 1.0,
                    "atacar_na_rede": 0.98,
                },
                "grama": {
                    "atacar_do_fundo": 0.99,
                    "atacar_pelo_meio": 1.01,
                    "atacar_na_rede": 1.02,
                },
            }.get(superficie, {})
            mod *= estilo_mod.get(estilo, 1.0)

        return max(0.6, min(1.05, mod))

    def _aplicar_mod_superficie(self, atributos: dict, superficie: str) -> dict:
        superficie = normalizar_superficie(superficie)
        mods = SUPERFICIE_MODS.get(superficie, SUPERFICIE_MODS["dura"])
        return {k: v * mods.get(k, 1.0) for k, v in atributos.items()}

    @staticmethod
    def _resolver_estrategias_lado(
        contexto: ContextoPonto,
        estrategia: dict | None,
        estrategia_adversario: dict | None,
    ) -> tuple[dict, dict]:
        estrategia_j = estrategia or {"estilo": "atacar_do_fundo"}
        estrategia_a = estrategia_adversario or {"estilo": "atacar_do_fundo"}
        if contexto.sacador == "j":
            return estrategia_j, estrategia_a
        return estrategia_a, estrategia_j

    def _get_status_lesao_jogador(self):
        if hasattr(self.jogador, "status_lesao"):
            return getattr(self.jogador, "status_lesao", {}) or {}
        return (
            self.jogador.get("status_lesao", {})
            if isinstance(self.jogador, dict)
            else {}
        )

    def _get_status_lesao_adversario(self):
        return (
            self.adversario.get("status_lesao", {})
            if isinstance(self.adversario, dict)
            else {}
        )

    def _get_status_doenca_jogador(self):
        if hasattr(self.jogador, "status_doenca"):
            return getattr(self.jogador, "status_doenca", {}) or {}
        return (
            self.jogador.get("status_doenca", {})
            if isinstance(self.jogador, dict)
            else {}
        )

    def _get_status_doenca_adversario(self):
        return (
            self.adversario.get("status_doenca", {})
            if isinstance(self.adversario, dict)
            else {}
        )

    def _multiplicador_lesao(self, status_lesao) -> float:
        return fx_multiplicador_lesao(status_lesao)

    def _multiplicador_doenca(self, status_doenca) -> float:
        return fx_multiplicador_doenca(status_doenca)

    def _aplicar_efeito_lesao(self, atributos: dict, status_lesao) -> dict:
        return fx_aplicar_multiplicador_atributos(
            atributos, self._multiplicador_lesao(status_lesao)
        )

    def _aplicar_efeito_doenca(self, atributos: dict, status_doenca) -> dict:
        return fx_aplicar_multiplicador_atributos(
            atributos, self._multiplicador_doenca(status_doenca)
        )

    def _mod_ambiente(self, contexto_partida: ContextoPartida) -> dict:
        return fx_calcular_mod_ambiente(
            clima=contexto_partida.clima,
            vento=contexto_partida.vento,
            umidade=contexto_partida.umidade,
            altitude_m=contexto_partida.altitude_m,
            indoor=contexto_partida.indoor,
        )

    def _calcular_poder_saque(
        self,
        atributos: dict,
        psico: dict,
        tipo_saque: TipoSaque,
        contexto: ContextoPonto,
        superficie: str,
        stamina: float,
        fator_estado: float = 1.0,
    ) -> tuple:
        """
        Calcula o poder do saque baseado nos atributos.

        Returns:
            (poder: float, chance_ace: float, chance_falta: float)
        """
        saque = atributos.get("saque", 50)
        fisico = atributos.get("fisico", 50)

        # Base do poder do saque
        poder = saque * 0.80 + fisico * 0.20

        # Modificadores por tipo
        if tipo_saque == TipoSaque.AGRESSIVO:
            poder *= 1.15  # +15% poder
            chance_falta = 0.35 - (saque / 500)  # 25-35% falta
            chance_ace = 0.12 + (saque / 500)  # 12-22% ace
        elif tipo_saque == TipoSaque.SEGURO:
            poder *= 0.85  # -15% poder
            chance_falta = 0.08 - (saque / 1000)  # 3-8% falta
            chance_ace = 0.02 + (saque / 1000)  # 2-7% ace
        else:  # VARIADO
            chance_falta = 0.20 - (saque / 500)  # 10-20% falta
            chance_ace = 0.06 + (saque / 500)  # 6-16% ace

        # Bonus psicológico e stamina
        bonus = calcular_bonus_psicologico(psico, contexto)
        poder += bonus * 5
        chance_falta -= bonus * 0.02
        chance_ace += bonus * 0.01

        mod_stamina = self._stamina_mod(
            stamina, atributos=atributos, superficie=superficie
        )
        poder = self._aplicar_modificadores(
            poder, 0.0, mod_stamina, fator_estado=fator_estado
        )
        chance_falta += (1.0 - mod_stamina) * 0.15
        chance_ace *= mod_stamina

        return (poder, max(0.02, chance_ace), max(0.05, chance_falta))

    def _calcular_poder_devolucao(
        self,
        atributos: dict,
        psico: dict,
        contexto: ContextoPonto,
        superficie: str,
        stamina: float,
        fator_estado: float = 1.0,
    ) -> float:
        """Calcula o poder de devolução do receptor."""
        # Devolução depende de movimento, backhand e slice
        movimento = atributos.get("movimento", 50)
        backhand = atributos.get("backhand", 50)
        slice_ = atributos.get("slice", 50)
        forehand = atributos.get("forehand", 50)

        bonus = calcular_bonus_psicologico(psico, contexto)
        base = backhand * 0.35 + movimento * 0.3 + slice_ * 0.2 + forehand * 0.15
        poder = self._aplicar_modificadores(
            base,
            bonus * 5,
            self._stamina_mod(stamina, atributos=atributos, superficie=superficie),
            fator_estado=fator_estado,
        )

        return poder

    def _calcular_poder_rally(
        self,
        atributos: dict,
        psico: dict,
        estrategia: dict,
        contexto: ContextoPonto,
        superficie: str,
        stamina: float,
        fator_estado: float = 1.0,
    ) -> float:
        """Calcula o poder no rally baseado na estratégia."""
        forehand = atributos.get("forehand", 50)
        backhand = atributos.get("backhand", 50)
        movimento = atributos.get("movimento", 50)
        voleio = atributos.get("voleio", 50)
        topspin = atributos.get("topspin", 50)
        slice_ = atributos.get("slice", 50)
        winner = atributos.get("winner", 50)

        estilo = estrategia.get("estilo", "atacar_do_fundo")
        lob = atributos.get("lob", 50)

        if estilo == "atacar_na_rede":
            # Voleio + slice de aproximação; lob ajuda como contra-arma
            base = (
                voleio * 0.42
                + movimento * 0.22
                + forehand * 0.18
                + slice_ * 0.12
                + lob * 0.06
            )
        elif estilo == "atacar_do_fundo":
            # Slice defensivo é arma no fundo; lob como saída de dificuldade
            base = (
                forehand * 0.30
                + backhand * 0.30
                + topspin * 0.18
                + movimento * 0.14
                + slice_ * 0.05
                + lob * 0.03
            )
        else:  # atacar_pelo_meio
            base = (
                forehand * 0.24
                + backhand * 0.24
                + movimento * 0.18
                + voleio * 0.14
                + topspin * 0.09
                + winner * 0.05
                + slice_ * 0.04
                + lob * 0.02
            )

        bonus = calcular_bonus_psicologico(psico, contexto)
        poder = self._aplicar_modificadores(
            base,
            bonus * 8,
            self._stamina_mod(
                stamina, atributos=atributos, estilo=estilo, superficie=superficie
            ),
            fator_estado=fator_estado,
        )

        # Leitura de jogo ajuda no rally
        leitura = psico.get("leitura_de_jogo", 50)
        poder += (leitura - 50) * 0.15

        return poder

    def _aplicar_modificadores(
        self,
        valor_base: float,
        bonus_psico: float,
        stamina_mod: float,
        fator_estado: float = 1.0,
    ) -> float:
        """Aplica o padrão base+psico, multiplicador de stamina e fator de estado."""
        return (valor_base + bonus_psico) * stamina_mod * fator_estado

    def _get_fator_estado(self, moral: float, ritmo: float) -> float:
        """Calcula um multiplicador baseado na moral e ritmo de jogo."""
        # Moral: baseline 70. 100 -> ~+5%, 0 -> ~-12%
        f_moral = 1.0 + (moral - 70) / 600.0
        # Ritmo: baseline 50. 100 -> ~+5%, 0 -> ~-5%
        f_ritmo = 1.0 + (ritmo - 50) / 1000.0
        return max(0.8, min(1.15, f_moral * f_ritmo))

    def simular_ponto_estrategista(
        self,
        estrategia: dict,
        contexto: ContextoPonto,
        tipo_saque: TipoSaque = None,
        contexto_partida: ContextoPartida = None,
        estrategia_adversario: dict = None,
    ) -> tuple:
        """
        Simula um ponto com descrição detalhada usando confronto de atributos.

        Returns:
            (vencedor: str, descricoes: list[str], stats_info: dict)
        """
        descricoes = []
        atributos_j = self._get_atributos_jogador()
        atributos_a = self._get_atributos_adversario()
        psico_j = self._get_psico_jogador()
        psico_a = self._get_psico_adversario()

        stats_info = MatchPointStats.novo(contexto.sacador)
        contexto = contexto or self._contexto_padrao_saque()
        contexto_partida = contexto_partida or ContextoPartida()
        superficie = normalizar_superficie(contexto_partida.superficie)

        # Determina sacador e receptor
        if contexto.sacador == "j":
            attr_sacador, psico_sacador = atributos_j, psico_j
            attr_receptor, psico_receptor = atributos_a, psico_a
            nome_receptor = self.adversario.get("nome", "Adversario")
            stamina_sacador = contexto_partida.stamina_j
            stamina_receptor = contexto_partida.stamina_a
        else:
            attr_sacador, psico_sacador = atributos_a, psico_a
            attr_receptor, psico_receptor = atributos_j, psico_j
            nome_receptor = (
                self.jogador.nome if hasattr(self.jogador, "nome") else "Jogador"
            )
            stamina_sacador = contexto_partida.stamina_a
            stamina_receptor = contexto_partida.stamina_j

        status_j = self._get_status_lesao_jogador()
        status_a = self._get_status_lesao_adversario()
        doenca_j = self._get_status_doenca_jogador()
        doenca_a = self._get_status_doenca_adversario()
        atributos_j = self._aplicar_efeito_lesao(atributos_j, status_j)
        atributos_a = self._aplicar_efeito_lesao(atributos_a, status_a)
        atributos_j = self._aplicar_efeito_doenca(atributos_j, doenca_j)
        atributos_a = self._aplicar_efeito_doenca(atributos_a, doenca_a)
        if contexto.sacador == "j":
            attr_sacador, attr_receptor = atributos_j, atributos_a
        else:
            attr_sacador, attr_receptor = atributos_a, atributos_j
        attr_sacador = self._aplicar_mod_superficie(attr_sacador, superficie)
        attr_receptor = self._aplicar_mod_superficie(attr_receptor, superficie)
        mod_ambiente = self._mod_ambiente(contexto_partida)

        # Fatores de estado (Moral + Ritmo)
        if contexto.sacador == "j":
            fator_sacador = self._get_fator_estado(
                contexto_partida.moral_j, contexto_partida.ritmo_j
            )
            fator_receptor = self._get_fator_estado(
                contexto_partida.moral_a, contexto_partida.ritmo_a
            )
        else:
            fator_sacador = self._get_fator_estado(
                contexto_partida.moral_a, contexto_partida.ritmo_a
            )
            fator_receptor = self._get_fator_estado(
                contexto_partida.moral_j, contexto_partida.ritmo_j
            )

        estrategia_sacador, estrategia_adv = self._resolver_estrategias_lado(
            contexto, estrategia, estrategia_adversario
        )
        tipo = tipo_saque or estrategia_sacador.get("saque_tipo", TipoSaque.VARIADO)

        # FASE 1: Saque
        poder_saque, chance_ace, chance_falta = self._calcular_poder_saque(
            attr_sacador,
            psico_sacador,
            tipo,
            contexto,
            superficie,
            stamina_sacador,
            fator_estado=fator_sacador,
        )
        poder_devolucao = self._calcular_poder_devolucao(
            attr_receptor,
            psico_receptor,
            contexto,
            superficie,
            stamina_receptor,
            fator_estado=fator_receptor,
        )
        poder_saque *= mod_ambiente["saque"]
        chance_ace *= mod_ambiente["ace"]
        chance_falta *= mod_ambiente["falta"]
        if contexto.sacador == "j":
            poder_saque *= 1.0 + (contexto_partida.momentum_j * 0.02)
            poder_devolucao *= 1.0 + (contexto_partida.momentum_a * 0.02)
        else:
            poder_saque *= 1.0 + (contexto_partida.momentum_a * 0.02)
            poder_devolucao *= 1.0 + (contexto_partida.momentum_j * 0.02)

        # Primeiro saque
        if random.random() < chance_falta:
            descricoes.append("1o saque: Falta!")

            # Segundo saque
            estrategia_saque = estrategia_sacador.get("saque", EstrategiaSaque.SEGURO)
            if self.segundo_saque(estrategia_saque, contexto)[0]:
                descricoes.append("2o saque: Em jogo.")
            else:
                descricoes.append("2o saque: Dupla falta!")
                stats_info.dupla_falta = True
                stats_info.intensidade = "curto"
                vencedor = "a" if contexto.sacador == "j" else "j"
                descricoes = self._padronizar_descricoes(descricoes)
                return (vencedor, descricoes, stats_info)
        else:
            stats_info.primeiro_saque_in = True

            # Verifica ace - confronto direto saque vs devolução
            if random.random() < chance_ace and self._confronto(
                poder_saque * 1.3, poder_devolucao
            ):
                direcoes = ["no T", "aberto", "no corpo"]
                descricoes.append(f"1o saque: Ace {random.choice(direcoes)}!")
                stats_info.ace = True
                stats_info.intensidade = "curto"
                descricoes = self._padronizar_descricoes(descricoes)
                return (contexto.sacador, descricoes, stats_info)
            else:
                qualidade = (
                    "potente"
                    if poder_saque > 60
                    else "preciso" if poder_saque > 45 else "seguro"
                )
                descricoes.append(f"1o saque: Saque {qualidade}, em jogo.")

        # FASE 2: Rally
        descricoes.append(f"Rally: {random.choice(self.DESCRICOES_RALLY)}")

        atributos_j_mod = self._aplicar_mod_superficie(atributos_j, superficie)
        atributos_a_mod = self._aplicar_mod_superficie(atributos_a, superficie)

        # Fatores de rally
        fator_j = self._get_fator_estado(
            contexto_partida.moral_j, contexto_partida.ritmo_j
        )
        fator_a = self._get_fator_estado(
            contexto_partida.moral_a, contexto_partida.ritmo_a
        )

        estrategia_j, estrategia_adv = self._resolver_estrategias_lado(
            contexto, estrategia, estrategia_adversario
        )
        poder_rally_j = self._calcular_poder_rally(
            atributos_j_mod,
            psico_j,
            estrategia_j,
            contexto,
            superficie,
            contexto_partida.stamina_j,
            fator_estado=fator_j,
        )
        poder_rally_a = self._calcular_poder_rally(
            atributos_a_mod,
            psico_a,
            estrategia_adv,
            contexto,
            superficie,
            contexto_partida.stamina_a,
            fator_estado=fator_a,
        )
        poder_rally_j *= mod_ambiente["rally"]
        poder_rally_a *= mod_ambiente["rally"]
        poder_rally_j *= 1.0 + (contexto_partida.momentum_j * 0.02)
        poder_rally_a *= 1.0 + (contexto_partida.momentum_a * 0.02)

        # Mostra confronto de poder (para debug/feedback)
        diferenca = abs(poder_rally_j - poder_rally_a)
        if diferenca > 15:
            quem_domina = "Jogador" if poder_rally_j > poder_rally_a else nome_receptor
            descricoes.append(f"{quem_domina} domina o rally!")

        # Confronto no rally
        _venceu_rally_j, _vantagem_rally, _n_trocas_rally = self._simular_rally_trocas(
            poder_rally_j,
            poder_rally_a,
            psico_j,
            psico_a,
            stamina_j=contexto_partida.stamina_j,
            stamina_a=contexto_partida.stamina_a,
            superficie=contexto_partida.superficie,
            estilo_j=estrategia_j.get("estilo", "atacar_do_fundo"),
            estilo_a=estrategia_adv.get("estilo", "atacar_do_fundo"),
            atributos_j=atributos_j,
            atributos_a=atributos_a,
        )
        if _venceu_rally_j:
            vencedor = "j"
            desc_final, eh_winner, eh_erro = self._determinar_tipo_finalizacao(
                "j",
                atributos_j,
                psico_j,
                estrategia_j,
                estrategia_j.get("intencao"),
                vantagem_rally=_vantagem_rally,
                superficie=contexto_partida.superficie,
                stamina=contexto_partida.stamina_j,
            )
        else:
            vencedor = "a"
            desc_final, eh_winner, eh_erro = self._determinar_tipo_finalizacao(
                "a",
                atributos_a,
                psico_a,
                estrategia_adv,
                estrategia_adv.get("intencao"),
                vantagem_rally=_vantagem_rally,
                superficie=contexto_partida.superficie,
                stamina=contexto_partida.stamina_a,
            )

        descricoes.append(desc_final)
        stats_info.winner = eh_winner
        stats_info.erro_nao_forcado = eh_erro

        stats_info.intensidade = self._n_trocas_para_intensidade(_n_trocas_rally)
        if (
            mod_ambiente["erro"] > 1.05
            and not stats_info.winner
            and random.random() < 0.35
        ):
            stats_info.erro_nao_forcado = True

        descricoes = self._padronizar_descricoes(descricoes)
        return (vencedor, descricoes, stats_info)

    def _determinar_tipo_finalizacao(
        self,
        vencedor: str,
        atributos: dict,
        psico: dict,
        estrategia: dict,
        intencao: IntencaoPonto = None,
        vantagem_rally: float = 0.0,
        superficie: str = "",
        stamina: float = 100.0,
    ) -> tuple:
        """
        Determina como o ponto foi finalizado baseado nos atributos.

        Returns:
            (descricao: str, eh_winner: bool, eh_erro: bool)
        """
        agressividade = psico.get("agressividade", 50)
        concentracao = psico.get("concentracao", 50)
        forehand = atributos.get("forehand", 50)
        backhand = atributos.get("backhand", 50)
        voleio = atributos.get("voleio", 50)

        estilo = estrategia.get("estilo", "atacar_do_fundo")

        # Chance de winner baseada em agressividade, habilidade e vantagem posicional
        winner_attr = atributos.get("winner", 50)
        chance_winner = (
            agressividade * 0.35
            + winner_attr * 0.40
            + vantagem_rally
            * 50.0
            * 0.25  # vantagem_rally [0,0.3] → contribui até 3.75
        ) / 100.0

        # Modificador de superfície: grama/duro favorecem winners, saibro penaliza
        superficie_norm = str(superficie).lower()
        if "grama" in superficie_norm:
            chance_winner *= 1.25
        elif "saibro" in superficie_norm:
            chance_winner *= 0.78

        # Penalidade de stamina: jogadores cansados erram mais winners
        if stamina < 40:
            chance_winner *= 0.70
        elif stamina < 60:
            chance_winner *= 0.88

        # Modificador de intenção
        if intencao == IntencaoPonto.ARRISCAR:
            chance_winner *= 1.40
        elif intencao == IntencaoPonto.DEFENSIVO:
            chance_winner *= 0.45

        chance_winner = min(0.82, chance_winner)

        if random.random() < chance_winner:
            # Tentativa de winner - sucesso depende da concentração
            if random.random() < concentracao / 100.0:
                # Winner! Tipo depende do estilo e atributos
                if estilo == "atacar_na_rede" and voleio > 60:
                    return (
                        "Voleio curto na rede, sem chances para o adversário!",
                        True,
                        False,
                    )
                elif forehand >= backhand:
                    direcao = random.choice(["na cruzada", "na paralela"])
                    return (f"Winner de forehand {direcao}!", True, False)
                else:
                    direcao = random.choice(["na cruzada", "na paralela"])
                    return (f"Winner de backhand {direcao}!", True, False)
            else:
                # Errou tentando winner
                golpe = "Forehand" if forehand > backhand else "Backhand"
                local = random.choice(["na rede", "pra fora"])
                return (f"{golpe} {local}!", False, True)
        else:
            # Erro forçado não deve contar como erro não forçado.
            return ("Adversário força o erro, ponto ganho!", False, False)

    def _sortear_intensidade_rally(self, atributos: dict, estrategia: dict) -> str:
        movimento = atributos.get("movimento", 50)
        topspin = atributos.get("topspin", 50)
        estilo = estrategia.get("estilo", "atacar_do_fundo")

        if estilo == "atacar_na_rede":
            base_longo = 0.30
        elif estilo == "atacar_pelo_meio":
            base_longo = 0.22
        else:  # atacar_do_fundo
            base_longo = 0.25

        base_longo += (movimento - 50) / 400
        base_longo += (topspin - 50) / 500

        roll = random.random()
        if roll < max(0.1, base_longo):
            return "longo"
        if roll < 0.70:
            return "medio"
        return "curto"

    def simular_ponto_rapido(
        self,
        estrategia: dict,
        contexto: ContextoPonto = None,
        contexto_partida: ContextoPartida = None,
        estrategia_adversario: dict = None,
    ) -> tuple:
        """
        Simula um ponto no modo rápido usando confronto de atributos.

        Returns:
            (vencedor: str, stats_info: dict)
        """
        atributos_j = self._get_atributos_jogador()
        atributos_a = self._get_atributos_adversario()
        psico_j = self._get_psico_jogador()
        psico_a = self._get_psico_adversario()

        contexto = contexto or self._contexto_padrao_saque()
        stats_info = MatchPointStats.novo(contexto.sacador)
        contexto_partida = contexto_partida or ContextoPartida()
        superficie = normalizar_superficie(contexto_partida.superficie)

        # Determina sacador e receptor
        if contexto.sacador == "j":
            attr_sacador, psico_sacador = atributos_j, psico_j
            attr_receptor, psico_receptor = atributos_a, psico_a
            stamina_sacador = contexto_partida.stamina_j
            stamina_receptor = contexto_partida.stamina_a
        else:
            attr_sacador, psico_sacador = atributos_a, psico_a
            attr_receptor, psico_receptor = atributos_j, psico_j
            stamina_sacador = contexto_partida.stamina_a
            stamina_receptor = contexto_partida.stamina_j

        status_j = self._get_status_lesao_jogador()
        status_a = self._get_status_lesao_adversario()
        doenca_j = self._get_status_doenca_jogador()
        doenca_a = self._get_status_doenca_adversario()
        atributos_j = self._aplicar_efeito_lesao(atributos_j, status_j)
        atributos_a = self._aplicar_efeito_lesao(atributos_a, status_a)
        atributos_j = self._aplicar_efeito_doenca(atributos_j, doenca_j)
        atributos_a = self._aplicar_efeito_doenca(atributos_a, doenca_a)
        if contexto.sacador == "j":
            attr_sacador, attr_receptor = atributos_j, atributos_a
        else:
            attr_sacador, attr_receptor = atributos_a, atributos_j
        attr_sacador = self._aplicar_mod_superficie(attr_sacador, superficie)
        attr_receptor = self._aplicar_mod_superficie(attr_receptor, superficie)
        mod_ambiente = self._mod_ambiente(contexto_partida)

        # Fatores de estado (Moral + Ritmo)
        if contexto.sacador == "j":
            fator_sacador = self._get_fator_estado(
                contexto_partida.moral_j, contexto_partida.ritmo_j
            )
            fator_receptor = self._get_fator_estado(
                contexto_partida.moral_a, contexto_partida.ritmo_a
            )
        else:
            fator_sacador = self._get_fator_estado(
                contexto_partida.moral_a, contexto_partida.ritmo_a
            )
            fator_receptor = self._get_fator_estado(
                contexto_partida.moral_j, contexto_partida.ritmo_j
            )

        # FASE 1: Saque
        estrategia_sacador, _ = self._resolver_estrategias_lado(
            contexto, estrategia, estrategia_adversario
        )
        tipo_saque_efetivo = estrategia_sacador.get("saque_tipo", TipoSaque.VARIADO)
        poder_saque, chance_ace, chance_falta = self._calcular_poder_saque(
            attr_sacador,
            psico_sacador,
            tipo_saque_efetivo,
            contexto,
            superficie,
            stamina_sacador,
            fator_estado=fator_sacador,
        )
        poder_devolucao = self._calcular_poder_devolucao(
            attr_receptor,
            psico_receptor,
            contexto,
            superficie,
            stamina_receptor,
            fator_estado=fator_receptor,
        )
        poder_saque *= mod_ambiente["saque"]
        chance_ace *= mod_ambiente["ace"]
        chance_falta *= mod_ambiente["falta"]
        if contexto.sacador == "j":
            poder_saque *= 1.0 + (contexto_partida.momentum_j * 0.02)
            poder_devolucao *= 1.0 + (contexto_partida.momentum_a * 0.02)
        else:
            poder_saque *= 1.0 + (contexto_partida.momentum_a * 0.02)
            poder_devolucao *= 1.0 + (contexto_partida.momentum_j * 0.02)

        # Primeiro saque
        if random.random() < chance_falta:
            # Falta no primeiro saque
            estrategia_saque = estrategia_sacador.get("saque", EstrategiaSaque.SEGURO)
            if not self.segundo_saque(estrategia_saque, contexto)[0]:
                # Dupla falta!
                stats_info.dupla_falta = True
                stats_info.intensidade = "curto"
                vencedor = "a" if contexto.sacador == "j" else "j"
                return (vencedor, stats_info)
        else:
            stats_info.primeiro_saque_in = True
            # Verifica ace
            if random.random() < chance_ace:
                # Confronto saque vs devolução para ace
                if self._confronto(poder_saque * 1.3, poder_devolucao):
                    stats_info.ace = True
                    stats_info.intensidade = "curto"
                    return (contexto.sacador, stats_info)

        # FASE 2: Rally
        atributos_j_mod = self._aplicar_mod_superficie(atributos_j, superficie)
        atributos_a_mod = self._aplicar_mod_superficie(atributos_a, superficie)

        fator_j = self._get_fator_estado(
            contexto_partida.moral_j, contexto_partida.ritmo_j
        )
        fator_a = self._get_fator_estado(
            contexto_partida.moral_a, contexto_partida.ritmo_a
        )

        estrategia_j, estrategia_adv = self._resolver_estrategias_lado(
            contexto, estrategia, estrategia_adversario
        )
        poder_rally_j = self._calcular_poder_rally(
            atributos_j_mod,
            psico_j,
            estrategia_j,
            contexto,
            superficie,
            contexto_partida.stamina_j,
            fator_estado=fator_j,
        )
        poder_rally_a = self._calcular_poder_rally(
            atributos_a_mod,
            psico_a,
            estrategia_adv,
            contexto,
            superficie,
            contexto_partida.stamina_a,
            fator_estado=fator_a,
        )
        poder_rally_j *= mod_ambiente["rally"]
        poder_rally_a *= mod_ambiente["rally"]
        poder_rally_j *= 1.0 + (contexto_partida.momentum_j * 0.02)
        poder_rally_a *= 1.0 + (contexto_partida.momentum_a * 0.02)

        # Confronto no rally
        _venceu_rally_j, _vantagem_rally, _n_trocas_rally = self._simular_rally_trocas(
            poder_rally_j,
            poder_rally_a,
            psico_j,
            psico_a,
            stamina_j=contexto_partida.stamina_j,
            stamina_a=contexto_partida.stamina_a,
            superficie=contexto_partida.superficie,
            estilo_j=estrategia_j.get("estilo", "atacar_do_fundo"),
            estilo_a=estrategia_adv.get("estilo", "atacar_do_fundo"),
            atributos_j=atributos_j,
            atributos_a=atributos_a,
        )
        if _venceu_rally_j:
            vencedor = "j"
            _, eh_winner, eh_erro = self._determinar_tipo_finalizacao(
                "j",
                atributos_j,
                psico_j,
                estrategia_j,
                estrategia_j.get("intencao"),
                vantagem_rally=_vantagem_rally,
                superficie=contexto_partida.superficie,
                stamina=contexto_partida.stamina_j,
            )
        else:
            vencedor = "a"
            _, eh_winner, eh_erro = self._determinar_tipo_finalizacao(
                "a",
                atributos_a,
                psico_a,
                estrategia_adv,
                estrategia_adv.get("intencao"),
                vantagem_rally=_vantagem_rally,
                superficie=contexto_partida.superficie,
                stamina=contexto_partida.stamina_a,
            )

        stats_info.winner = eh_winner
        stats_info.erro_nao_forcado = eh_erro

        stats_info.intensidade = self._n_trocas_para_intensidade(_n_trocas_rally)
        if (
            mod_ambiente["erro"] > 1.05
            and not stats_info.winner
            and random.random() < 0.35
        ):
            stats_info.erro_nao_forcado = True

        return (vencedor, stats_info)

    def simular_ponto_detalhado(
        self,
        estrategia: dict,
        contexto: ContextoPonto,
        tipo_saque: TipoSaque = None,
        contexto_partida: ContextoPartida = None,
        estrategia_adversario: dict = None,
    ) -> tuple:
        """
        Simula um ponto com descrição detalhada usando confronto de atributos.

        Returns:
            (vencedor: str, descricoes: list[str], stats_info: dict)
        """
        descricoes = []
        atributos_j = self._get_atributos_jogador()
        atributos_a = self._get_atributos_adversario()
        psico_j = self._get_psico_jogador()
        psico_a = self._get_psico_adversario()

        stats_info = MatchPointStats.novo(contexto.sacador)
        contexto_partida = contexto_partida or ContextoPartida()
        superficie = normalizar_superficie(contexto_partida.superficie)

        # Determina sacador e receptor
        if contexto.sacador == "j":
            attr_sacador, psico_sacador = atributos_j, psico_j
            attr_receptor, psico_receptor = atributos_a, psico_a
            nome_receptor = self.adversario.get("nome", "Adversario")
            stamina_sacador = contexto_partida.stamina_j
            stamina_receptor = contexto_partida.stamina_a
        else:
            attr_sacador, psico_sacador = atributos_a, psico_a
            attr_receptor, psico_receptor = atributos_j, psico_j
            nome_receptor = (
                self.jogador.nome if hasattr(self.jogador, "nome") else "Jogador"
            )
            stamina_sacador = contexto_partida.stamina_a
            stamina_receptor = contexto_partida.stamina_j

        status_j = self._get_status_lesao_jogador()
        status_a = self._get_status_lesao_adversario()
        doenca_j = self._get_status_doenca_jogador()
        doenca_a = self._get_status_doenca_adversario()
        atributos_j = self._aplicar_efeito_lesao(atributos_j, status_j)
        atributos_a = self._aplicar_efeito_lesao(atributos_a, status_a)
        atributos_j = self._aplicar_efeito_doenca(atributos_j, doenca_j)
        atributos_a = self._aplicar_efeito_doenca(atributos_a, doenca_a)
        if contexto.sacador == "j":
            attr_sacador, attr_receptor = atributos_j, atributos_a
        else:
            attr_sacador, attr_receptor = atributos_a, atributos_j
        attr_sacador = self._aplicar_mod_superficie(attr_sacador, superficie)
        attr_receptor = self._aplicar_mod_superficie(attr_receptor, superficie)
        mod_ambiente = self._mod_ambiente(contexto_partida)

        # Fatores de estado (Moral + Ritmo)
        if contexto.sacador == "j":
            fator_sacador = self._get_fator_estado(
                contexto_partida.moral_j, contexto_partida.ritmo_j
            )
            fator_receptor = self._get_fator_estado(
                contexto_partida.moral_a, contexto_partida.ritmo_a
            )
        else:
            fator_sacador = self._get_fator_estado(
                contexto_partida.moral_a, contexto_partida.ritmo_a
            )
            fator_receptor = self._get_fator_estado(
                contexto_partida.moral_j, contexto_partida.ritmo_j
            )

        estrategia_sacador, estrategia_adv = self._resolver_estrategias_lado(
            contexto, estrategia, estrategia_adversario
        )
        tipo = tipo_saque or estrategia_sacador.get("saque_tipo", TipoSaque.VARIADO)

        # FASE 1: Saque
        poder_saque, chance_ace, chance_falta = self._calcular_poder_saque(
            attr_sacador,
            psico_sacador,
            tipo,
            contexto,
            superficie,
            stamina_sacador,
            fator_estado=fator_sacador,
        )
        poder_devolucao = self._calcular_poder_devolucao(
            attr_receptor,
            psico_receptor,
            contexto,
            superficie,
            stamina_receptor,
            fator_estado=fator_receptor,
        )
        poder_saque *= mod_ambiente["saque"]
        chance_ace *= mod_ambiente["ace"]
        chance_falta *= mod_ambiente["falta"]
        if contexto.sacador == "j":
            poder_saque *= 1.0 + (contexto_partida.momentum_j * 0.02)
            poder_devolucao *= 1.0 + (contexto_partida.momentum_a * 0.02)
        else:
            poder_saque *= 1.0 + (contexto_partida.momentum_a * 0.02)
            poder_devolucao *= 1.0 + (contexto_partida.momentum_j * 0.02)

        # Primeiro saque
        if random.random() < chance_falta:
            descricoes.append("1o saque: Falta!")

            # Segundo saque
            estrategia_saque = estrategia_sacador.get("saque", EstrategiaSaque.SEGURO)
            if self.segundo_saque(estrategia_saque, contexto)[0]:
                descricoes.append("2o saque: Em jogo.")
                stats_info.origem = (50, 0)
                stats_info.destino = (random.randint(30, 70), 75)
            else:
                descricoes.append("2o saque: Dupla falta!")
                stats_info.dupla_falta = True
                stats_info.intensidade = "curto"
                stats_info.origem = (50, 0)
                stats_info.destino = (
                    random.randint(10, 90),
                    40,
                )  # Fica na rede ou fora
                vencedor = "a" if contexto.sacador == "j" else "j"
                return (vencedor, descricoes, stats_info)
        else:
            stats_info.primeiro_saque_in = True

            # Verifica ace - confronto direto saque vs devolução
            if random.random() < chance_ace and self._confronto(
                poder_saque * 1.3, poder_devolucao
            ):
                direcoes = ["no T", "aberto", "no corpo"]
                dir_escolhida = random.choice(direcoes)
                descricoes.append(f"1o saque: Ace {dir_escolhida}!")
                stats_info.ace = True
                stats_info.intensidade = "curto"

                # Coordenadas do Ace
                lado_saque = random.choice([25, 75])
                stats_info.origem = (lado_saque, 0)
                if dir_escolhida == "no T":
                    stats_info.destino = (50, 65)
                elif dir_escolhida == "aberto":
                    stats_info.destino = (5 if lado_saque < 50 else 95, 65)
                else:
                    stats_info.destino = (lado_saque, 70)

                return (contexto.sacador, descricoes, stats_info)
            else:
                qualidade = (
                    "potente"
                    if poder_saque > 60
                    else "preciso" if poder_saque > 45 else "seguro"
                )
                descricoes.append(f"1o saque: Saque {qualidade}, em jogo.")
                stats_info.origem = (50, 0)
                stats_info.destino = (random.randint(20, 80), 75)

        # FASE 2: Rally
        descricoes.append(f"Rally: {random.choice(self.DESCRICOES_RALLY)}")

        atributos_j_mod = self._aplicar_mod_superficie(atributos_j, superficie)
        atributos_a_mod = self._aplicar_mod_superficie(atributos_a, superficie)

        # Fatores de rally
        fator_j = self._get_fator_estado(
            contexto_partida.moral_j, contexto_partida.ritmo_j
        )
        fator_a = self._get_fator_estado(
            contexto_partida.moral_a, contexto_partida.ritmo_a
        )

        estrategia_j, estrategia_adv = self._resolver_estrategias_lado(
            contexto, estrategia, estrategia_adversario
        )
        poder_rally_j = self._calcular_poder_rally(
            atributos_j_mod,
            psico_j,
            estrategia_j,
            contexto,
            superficie,
            contexto_partida.stamina_j,
            fator_estado=fator_j,
        )
        poder_rally_a = self._calcular_poder_rally(
            atributos_a_mod,
            psico_a,
            estrategia_adv,
            contexto,
            superficie,
            contexto_partida.stamina_a,
            fator_estado=fator_a,
        )
        poder_rally_j *= mod_ambiente["rally"]
        poder_rally_a *= mod_ambiente["rally"]
        poder_rally_j *= 1.0 + (contexto_partida.momentum_j * 0.02)
        poder_rally_a *= 1.0 + (contexto_partida.momentum_a * 0.02)

        # Mostra confronto de poder (para debug/feedback)
        diferenca = abs(poder_rally_j - poder_rally_a)
        if diferenca > 15:
            quem_domina = "Jogador" if poder_rally_j > poder_rally_a else nome_receptor
            descricoes.append(f"{quem_domina} domina o rally!")

        # Confronto no rally
        _venceu_rally_j, _vantagem_rally, _n_trocas_rally = self._simular_rally_trocas(
            poder_rally_j,
            poder_rally_a,
            psico_j,
            psico_a,
            stamina_j=contexto_partida.stamina_j,
            stamina_a=contexto_partida.stamina_a,
            superficie=contexto_partida.superficie,
            estilo_j=estrategia_j.get("estilo", "atacar_do_fundo"),
            estilo_a=estrategia_adv.get("estilo", "atacar_do_fundo"),
            atributos_j=atributos_j,
            atributos_a=atributos_a,
        )
        if _venceu_rally_j:
            vencedor = "j"
            desc_final, eh_winner, eh_erro = self._determinar_tipo_finalizacao(
                "j",
                atributos_j,
                psico_j,
                estrategia_j,
                estrategia_j.get("intencao"),
                vantagem_rally=_vantagem_rally,
                superficie=contexto_partida.superficie,
                stamina=contexto_partida.stamina_j,
            )
        else:
            vencedor = "a"
            desc_final, eh_winner, eh_erro = self._determinar_tipo_finalizacao(
                "a",
                atributos_a,
                psico_a,
                estrategia_adv,
                estrategia_adv.get("intencao"),
                vantagem_rally=_vantagem_rally,
                superficie=contexto_partida.superficie,
                stamina=contexto_partida.stamina_a,
            )

        descricoes.append(desc_final)
        stats_info.winner = eh_winner
        stats_info.erro_nao_forcado = eh_erro

        # Coordenadas da finalização (Winner ou Erro)
        if eh_winner:
            stats_info.origem = (random.randint(20, 80), 90 if vencedor == "a" else 10)
            stats_info.destino = (random.randint(0, 100), 10 if vencedor == "a" else 90)
        elif eh_erro:
            stats_info.origem = (random.randint(20, 80), 90 if vencedor == "a" else 10)
            stats_info.destino = (random.randint(0, 100), 50)  # Rede

        stats_info.intensidade = self._n_trocas_para_intensidade(_n_trocas_rally)
        if (
            mod_ambiente["erro"] > 1.05
            and not stats_info.winner
            and random.random() < 0.35
        ):
            stats_info.erro_nao_forcado = True

        return (vencedor, descricoes, stats_info)
