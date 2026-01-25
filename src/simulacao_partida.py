"""
Módulo de simulação de partidas de tênis com suporte a modos rápido e detalhado.
"""

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ModoSimulacao(Enum):
    RAPIDO = "rapido"
    DETALHADO = "detalhado"


class TipoSaque(Enum):
    AGRESSIVO = "agressivo"
    SEGURO = "seguro"
    VARIADO = "variado"


class EstrategiaAtaque(Enum):
    REDE = "rede"           # Subir a rede após golpes fortes
    FUNDO = "fundo"         # Winners do baseline
    VARIADO = "variado"     # Alternar padrões


class EstrategiaDefesa(Enum):
    CONTRA_ATAQUE = "contra_ataque"   # Virar com winners
    CONSISTENCIA = "consistencia"      # Bolas altas, esperar erro
    NEUTRALIZAR = "neutralizar"        # Slice para resetar


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

    def merge(self, other: 'EstatisticasPartida'):
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

    def exibir(self, nome_jogador: str, nome_adversario: str, stats_adversario: 'EstatisticasPartida'):
        """Exibe estatísticas comparativas formatadas."""
        print(f"\n{'='*55}")
        print(f"{'ESTATISTICAS':^55}")
        print(f"{'='*55}")
        print(f"{'':25} {'Voce':>12} {'Adversario':>15}")
        print(f"{'-'*55}")
        print(f"{'Aces':<25} {self.aces:>12} {stats_adversario.aces:>15}")
        print(f"{'Duplas Faltas':<25} {self.duplas_faltas:>12} {stats_adversario.duplas_faltas:>15}")
        print(f"{'1o Saque %':<25} {self.percentual_primeiro_saque():>12} {stats_adversario.percentual_primeiro_saque():>15}")
        print(f"{'Winners':<25} {self.winners:>12} {stats_adversario.winners:>15}")
        print(f"{'Erros Nao Forcados':<25} {self.erros_nao_forcados:>12} {stats_adversario.erros_nao_forcados:>15}")
        print(f"{'Pontos no Saque %':<25} {self.percentual_pontos_saque():>12} {stats_adversario.percentual_pontos_saque():>15}")
        print(f"{'Pontos na Devolucao %':<25} {self.percentual_pontos_devolucao():>12} {stats_adversario.percentual_pontos_devolucao():>15}")
        bp_j = f"{self.break_points_convertidos}/{self.break_points_total}"
        bp_a = f"{stats_adversario.break_points_convertidos}/{stats_adversario.break_points_total}"
        print(f"{'Break Points':<25} {bp_j:>12} {bp_a:>15}")
        print(f"{'='*55}")


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
        if self.is_tiebreak:
            return False
        gj, ga = self.placar_set
        pj, pa = self.placar_game
        # Jogador pode fechar o set
        if gj >= 5 and gj > ga and pj >= 3 and pj > pa:
            return True
        # Adversário pode fechar o set
        if ga >= 5 and ga > gj and pa >= 3 and pa > pj:
            return True
        return False

    def is_match_point(self) -> bool:
        """Verifica se é match point para algum jogador."""
        if self.is_tiebreak:
            return False
        sj, sa = self.placar_partida
        gj, ga = self.placar_set
        pj, pa = self.placar_game
        # Jogador pode fechar a partida
        if sj == self.sets_para_vencer - 1 and gj >= 5 and gj > ga and pj >= 3 and pj > pa:
            return True
        # Adversário pode fechar a partida
        if sa == self.sets_para_vencer - 1 and ga >= 5 and ga > gj and pa >= 3 and pa > pj:
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
    momentum_j: int = 0
    momentum_a: int = 0


def normalizar_superficie(superficie: str) -> str:
    """Normaliza a superficie para um conjunto conhecido."""
    if not superficie:
        return "dura"
    superficie = superficie.strip().lower()
    mapa = {
        "hard": "dura",
        "dura": "dura",
        "rapida": "dura",
        "clay": "saibro",
        "saibro": "saibro",
        "terra": "saibro",
        "grass": "grama",
        "grama": "grama",
    }
    return mapa.get(superficie, "dura")


SUPERFICIE_MODS = {
    "dura": {
        "saque": 1.0,
        "forehand": 1.0,
        "backhand": 1.0,
        "topspin": 1.0,
        "voleio": 1.0,
        "slice": 1.0,
        "movimento": 1.0,
        "lob": 1.0,
        "winner": 1.0,
    },
    "saibro": {
        "saque": 0.94,
        "forehand": 1.02,
        "backhand": 1.02,
        "topspin": 1.08,
        "voleio": 0.95,
        "slice": 1.02,
        "movimento": 1.06,
        "lob": 1.04,
        "winner": 0.95,
    },
    "grama": {
        "saque": 1.08,
        "forehand": 1.03,
        "backhand": 1.01,
        "topspin": 0.94,
        "voleio": 1.08,
        "slice": 1.06,
        "movimento": 0.96,
        "lob": 0.95,
        "winner": 1.04,
    },
}


def calcular_bonus_psicologico(atributos_psicologicos: dict, contexto: ContextoPonto, eh_jogador: bool = True) -> float:
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
    perdendo = contexto.jogador_perdendo() if eh_jogador else contexto.adversario_perdendo()
    if perdendo:
        bonus += (psico.get("determinacao", 50) - 50) / 10

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

    def segundo_saque(self, contexto: ContextoPonto = None) -> tuple:
        """
        Simula o segundo saque (sempre mais conservador).

        Returns:
            (sucesso: bool, resultado: TipoGolpe, descricao: str)
        """
        saque_base = self.atributos.get("saque", 50)
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
        "Forehand cruzado... Backhand paralelo...",
        "Troca de bolas no fundo...",
        "Slice defensivo... Approach...",
        "Topspin pesado... Bola curta...",
        "Subida a rede... Passada...",
        "Bola alta... Smash...",
        "Variacao de ritmo...",
        "Jogo de fundo intenso...",
    ]

    def __init__(self, jogador, adversario: dict):
        self.jogador = jogador
        self.adversario = adversario

    def _get_atributos_jogador(self):
        if hasattr(self.jogador, 'atributos'):
            return self.jogador.atributos
        return self.jogador.get('atributos', {})

    def _get_psico_jogador(self):
        if hasattr(self.jogador, 'atributos_psicologicos'):
            return self.jogador.atributos_psicologicos
        return self.jogador.get('atributos_psicologicos', {})

    def _get_atributos_adversario(self):
        return self.adversario.get('atributos', {})

    def _get_psico_adversario(self):
        return self.adversario.get('atributos_psicologicos', {})

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

    def _stamina_mod(self, stamina: float) -> float:
        stamina = max(0.0, min(100.0, stamina))
        return 0.7 + (stamina / 100.0) * 0.3

    def _aplicar_mod_superficie(self, atributos: dict, superficie: str) -> dict:
        superficie = normalizar_superficie(superficie)
        mods = SUPERFICIE_MODS.get(superficie, SUPERFICIE_MODS["dura"])
        return {k: v * mods.get(k, 1.0) for k, v in atributos.items()}

    def _calcular_poder_saque(self, atributos: dict, psico: dict, tipo_saque: TipoSaque,
                               contexto: ContextoPonto, superficie: str, stamina: float) -> tuple:
        """
        Calcula o poder do saque baseado nos atributos.

        Returns:
            (poder: float, chance_ace: float, chance_falta: float)
        """
        saque = atributos.get("saque", 50)
        winner = atributos.get("winner", 50)
        forehand = atributos.get("forehand", 50)

        # Base do poder do saque
        poder = saque * 0.7 + winner * 0.2 + forehand * 0.1

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

        mod_stamina = self._stamina_mod(stamina)
        poder *= mod_stamina
        chance_falta += (1.0 - mod_stamina) * 0.15
        chance_ace *= mod_stamina

        return (poder, max(0.02, chance_ace), max(0.05, chance_falta))

    def _calcular_poder_devolucao(self, atributos: dict, psico: dict, contexto: ContextoPonto,
                                  superficie: str, stamina: float) -> float:
        """Calcula o poder de devolução do receptor."""
        # Devolução depende de movimento, backhand e slice
        movimento = atributos.get("movimento", 50)
        backhand = atributos.get("backhand", 50)
        slice_ = atributos.get("slice", 50)
        forehand = atributos.get("forehand", 50)

        poder = backhand * 0.35 + movimento * 0.3 + slice_ * 0.2 + forehand * 0.15

        # Bonus psicológico e stamina
        bonus = calcular_bonus_psicologico(psico, contexto)
        poder += bonus * 5
        poder *= self._stamina_mod(stamina)

        return poder

    def _calcular_poder_rally(self, atributos: dict, psico: dict, estrategia: dict,
                               contexto: ContextoPonto, superficie: str, stamina: float) -> float:
        """Calcula o poder no rally baseado na estratégia."""
        forehand = atributos.get("forehand", 50)
        backhand = atributos.get("backhand", 50)
        movimento = atributos.get("movimento", 50)
        voleio = atributos.get("voleio", 50)
        topspin = atributos.get("topspin", 50)
        slice_ = atributos.get("slice", 50)
        winner = atributos.get("winner", 50)

        estilo = estrategia.get("estilo", "atacar_do_fundo")

        if estilo == "atacar_na_rede":
            # Rede: voleio é principal, movimento para approach
            poder = voleio * 0.45 + movimento * 0.25 + forehand * 0.2 + slice_ * 0.1
        elif estilo == "atacar_do_fundo":
            # Fundo: forehand e backhand são principais
            poder = forehand * 0.32 + backhand * 0.32 + topspin * 0.18 + movimento * 0.18
        else:  # atacar_pelo_meio
            # Variado: mix equilibrado
            poder = forehand * 0.25 + backhand * 0.25 + movimento * 0.2 + voleio * 0.15 + topspin * 0.1 + winner * 0.05

        # Bonus psicológico e stamina
        bonus = calcular_bonus_psicologico(psico, contexto)
        poder += bonus * 8
        poder *= self._stamina_mod(stamina)

        # Leitura de jogo ajuda no rally
        leitura = psico.get("leitura_de_jogo", 50)
        poder += (leitura - 50) * 0.15

        return poder

    def _determinar_tipo_finalizacao(self, vencedor: str, atributos: dict, psico: dict,
                                      estrategia: dict) -> tuple:
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

        # Chance de winner baseada na agressividade
        chance_winner = agressividade / 100.0

        if random.random() < chance_winner:
            # Tentativa de winner - sucesso depende da concentração
            if random.random() < concentracao / 100.0:
                # Winner! Tipo depende do estilo e atributos
                if estilo == "atacar_na_rede" and voleio > 50:
                    return ("Voleio vencedor!", True, False)
                elif forehand >= backhand:
                    return ("Winner de forehand!", True, False)
                else:
                    return ("Winner de backhand!", True, False)
            else:
                # Errou tentando winner
                return ("Erro nao forcado!", False, True)
        else:
            # Ponto construído com paciência
            return ("Ponto construido com paciencia!", False, False)

    def _sortear_intensidade_rally(self, atributos: dict, estrategia: dict) -> str:
        movimento = atributos.get("movimento", 50)
        topspin = atributos.get("topspin", 50)
        estilo = estrategia.get("estilo", "atacar_do_fundo")
        base_longo = 0.25 if estilo == "atacar_do_fundo" else 0.18
        base_longo += (movimento - 50) / 300
        base_longo += (topspin - 50) / 400
        roll = random.random()
        if roll < max(0.1, base_longo):
            return "longo"
        if roll < 0.65:
            return "medio"
        return "curto"

    def simular_ponto_rapido(self, estrategia: dict, contexto: ContextoPonto = None,
                              contexto_partida: ContextoPartida = None,
                              estrategia_adversario: dict = None) -> tuple:
        """
        Simula um ponto no modo rápido usando confronto de atributos.

        Returns:
            (vencedor: str, stats_info: dict)
        """
        atributos_j = self._get_atributos_jogador()
        atributos_a = self._get_atributos_adversario()
        psico_j = self._get_psico_jogador()
        psico_a = self._get_psico_adversario()

        stats_info = {
            "sacador": contexto.sacador if contexto else "j",
            "primeiro_saque_in": False,
            "ace": False,
            "dupla_falta": False,
            "winner": False,
            "erro_nao_forcado": False,
            "intensidade": "medio",
        }

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

        attr_sacador = self._aplicar_mod_superficie(attr_sacador, superficie)
        attr_receptor = self._aplicar_mod_superficie(attr_receptor, superficie)

        # FASE 1: Saque
        poder_saque, chance_ace, chance_falta = self._calcular_poder_saque(
            attr_sacador, psico_sacador, TipoSaque.VARIADO, contexto, superficie, stamina_sacador
        )
        poder_devolucao = self._calcular_poder_devolucao(
            attr_receptor, psico_receptor, contexto, superficie, stamina_receptor
        )
        if contexto.sacador == "j":
            poder_saque *= 1.0 + (contexto_partida.momentum_j * 0.02)
            poder_devolucao *= 1.0 + (contexto_partida.momentum_a * 0.02)
        else:
            poder_saque *= 1.0 + (contexto_partida.momentum_a * 0.02)
            poder_devolucao *= 1.0 + (contexto_partida.momentum_j * 0.02)

        # Primeiro saque
        if random.random() < chance_falta:
            # Falta no primeiro saque
            # Segundo saque (mais seguro)
            chance_falta_2 = chance_falta * 0.3  # Muito menor chance de falta
            if random.random() < chance_falta_2:
                # Dupla falta!
                stats_info["dupla_falta"] = True
                stats_info["intensidade"] = "curto"
                vencedor = "a" if contexto.sacador == "j" else "j"
                return (vencedor, stats_info)
        else:
            stats_info["primeiro_saque_in"] = True
            # Verifica ace
            if random.random() < chance_ace:
                # Confronto saque vs devolução para ace
                if self._confronto(poder_saque * 1.3, poder_devolucao):
                    stats_info["ace"] = True
                    stats_info["intensidade"] = "curto"
                    return (contexto.sacador, stats_info)

        # FASE 2: Rally
        atributos_j_mod = self._aplicar_mod_superficie(atributos_j, superficie)
        atributos_a_mod = self._aplicar_mod_superficie(atributos_a, superficie)
        poder_rally_j = self._calcular_poder_rally(
            atributos_j_mod, psico_j, estrategia, contexto, superficie, contexto_partida.stamina_j
        )
        estrategia_adv = estrategia_adversario or {"estilo": "atacar_do_fundo"}
        poder_rally_a = self._calcular_poder_rally(
            atributos_a_mod, psico_a, estrategia_adv, contexto, superficie, contexto_partida.stamina_a
        )
        poder_rally_j *= 1.0 + (contexto_partida.momentum_j * 0.02)
        poder_rally_a *= 1.0 + (contexto_partida.momentum_a * 0.02)

        # Confronto no rally
        if self._confronto(poder_rally_j, poder_rally_a):
            vencedor = "j"
            _, eh_winner, eh_erro = self._determinar_tipo_finalizacao("j", atributos_j, psico_j, estrategia)
        else:
            vencedor = "a"
            _, eh_winner, eh_erro = self._determinar_tipo_finalizacao("a", atributos_a, psico_a, estrategia_adv)

        stats_info["winner"] = eh_winner
        stats_info["erro_nao_forcado"] = eh_erro

        stats_info["intensidade"] = self._sortear_intensidade_rally(
            atributos_j if vencedor == "j" else atributos_a,
            estrategia if vencedor == "j" else estrategia_adv,
        )

        return (vencedor, stats_info)

    def simular_ponto_detalhado(self, estrategia: dict, contexto: ContextoPonto,
                                 tipo_saque: TipoSaque = None,
                                 contexto_partida: ContextoPartida = None,
                                 estrategia_adversario: dict = None) -> tuple:
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

        stats_info = {
            "sacador": contexto.sacador,
            "primeiro_saque_in": False,
            "ace": False,
            "dupla_falta": False,
            "winner": False,
            "erro_nao_forcado": False,
            "intensidade": "medio",
        }
        contexto_partida = contexto_partida or ContextoPartida()
        superficie = normalizar_superficie(contexto_partida.superficie)

        # Determina sacador e receptor
        if contexto.sacador == "j":
            attr_sacador, psico_sacador = atributos_j, psico_j
            attr_receptor, psico_receptor = atributos_a, psico_a
            nome_sacador = self.jogador.nome if hasattr(self.jogador, 'nome') else "Jogador"
            nome_receptor = self.adversario.get("nome", "Adversario")
            stamina_sacador = contexto_partida.stamina_j
            stamina_receptor = contexto_partida.stamina_a
        else:
            attr_sacador, psico_sacador = atributos_a, psico_a
            attr_receptor, psico_receptor = atributos_j, psico_j
            nome_sacador = self.adversario.get("nome", "Adversario")
            nome_receptor = self.jogador.nome if hasattr(self.jogador, 'nome') else "Jogador"
            stamina_sacador = contexto_partida.stamina_a
            stamina_receptor = contexto_partida.stamina_j

        attr_sacador = self._aplicar_mod_superficie(attr_sacador, superficie)
        attr_receptor = self._aplicar_mod_superficie(attr_receptor, superficie)

        tipo = tipo_saque or TipoSaque.VARIADO

        # FASE 1: Saque
        poder_saque, chance_ace, chance_falta = self._calcular_poder_saque(
            attr_sacador, psico_sacador, tipo, contexto, superficie, stamina_sacador
        )
        poder_devolucao = self._calcular_poder_devolucao(
            attr_receptor, psico_receptor, contexto, superficie, stamina_receptor
        )
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
            chance_falta_2 = chance_falta * 0.3
            if random.random() < chance_falta_2:
                descricoes.append("2o saque: Dupla falta!")
                stats_info["dupla_falta"] = True
                stats_info["intensidade"] = "curto"
                vencedor = "a" if contexto.sacador == "j" else "j"
                return (vencedor, descricoes, stats_info)
            else:
                descricoes.append("2o saque: Em jogo.")
        else:
            stats_info["primeiro_saque_in"] = True

            # Verifica ace - confronto direto saque vs devolução
            if random.random() < chance_ace and self._confronto(poder_saque * 1.3, poder_devolucao):
                direcoes = ["no T", "aberto", "no corpo"]
                descricoes.append(f"1o saque: Ace {random.choice(direcoes)}!")
                stats_info["ace"] = True
                stats_info["intensidade"] = "curto"
                return (contexto.sacador, descricoes, stats_info)
            else:
                qualidade = "potente" if poder_saque > 60 else "preciso" if poder_saque > 45 else "seguro"
                descricoes.append(f"1o saque: Saque {qualidade}, em jogo.")

        # FASE 2: Rally
        descricoes.append(f"Rally: {random.choice(self.DESCRICOES_RALLY)}")

        atributos_j_mod = self._aplicar_mod_superficie(atributos_j, superficie)
        atributos_a_mod = self._aplicar_mod_superficie(atributos_a, superficie)
        poder_rally_j = self._calcular_poder_rally(
            atributos_j_mod, psico_j, estrategia, contexto, superficie, contexto_partida.stamina_j
        )
        estrategia_adv = estrategia_adversario or {"estilo": "atacar_do_fundo"}
        poder_rally_a = self._calcular_poder_rally(
            atributos_a_mod, psico_a, estrategia_adv, contexto, superficie, contexto_partida.stamina_a
        )
        poder_rally_j *= 1.0 + (contexto_partida.momentum_j * 0.02)
        poder_rally_a *= 1.0 + (contexto_partida.momentum_a * 0.02)

        # Mostra confronto de poder (para debug/feedback)
        diferenca = abs(poder_rally_j - poder_rally_a)
        if diferenca > 15:
            quem_domina = "Jogador" if poder_rally_j > poder_rally_a else nome_receptor
            descricoes.append(f"{quem_domina} domina o rally!")

        # Confronto no rally
        if self._confronto(poder_rally_j, poder_rally_a):
            vencedor = "j"
            desc_final, eh_winner, eh_erro = self._determinar_tipo_finalizacao("j", atributos_j, psico_j, estrategia)
        else:
            vencedor = "a"
            desc_final, eh_winner, eh_erro = self._determinar_tipo_finalizacao("a", atributos_a, psico_a, estrategia_adv)

        descricoes.append(desc_final)
        stats_info["winner"] = eh_winner
        stats_info["erro_nao_forcado"] = eh_erro

        stats_info["intensidade"] = self._sortear_intensidade_rally(
            atributos_j if vencedor == "j" else atributos_a,
            estrategia if vencedor == "j" else estrategia_adv,
        )

        return (vencedor, descricoes, stats_info)
