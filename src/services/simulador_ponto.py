import random
from typing import Any
from src.constants.staff_constants import PROFISSIONAIS_DISPONIVEIS
from src.utils.entidade_utils import (
    obter_atributos,
    obter_atributos_psicologicos,
)
from src.utils.superficie_utils import normalizar_superficie
from src.constants.match_constants import (
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
from src.fadiga import calcular_penalidade_energia, calcular_multiplicador_condicao
from src.match_state import (
    ContextoPartida,
    ContextoPonto,
    TipoGolpe,
)
from src.utils.match_sim_utils import calcular_bonus_psicologico, SUPERFICIE_MODS
from src.utils.match_doubles_utils import (
    perfil_duplas_entidade,
    ajuste_duplas_saque_devolucao,
    ajuste_duplas_rally,
)
from .simulador_saque import SimuladorSaque
from .ponto_narrativa import (
    pn_append_insight,
    pn_momento_do_ponto,
    pn_rotulo_estilo,
    pn_padronizar_descricoes,
    pn_registrar_narrativa_ponto,
)


class SimuladorPonto:
    """
    Simula pontos baseado em confronto direto de atributos.
    """

    FATOR_SORTE = 0.15

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
        return pn_padronizar_descricoes(descricoes)

    @staticmethod
    def _entidade_nome(entidade) -> str:
        if isinstance(entidade, dict):
            return str(entidade.get("nome", "Equipe")).strip() or "Equipe"
        return str(getattr(entidade, "nome", "Equipe")).strip() or "Equipe"

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

    def _ajuste_duplas_saque_devolucao(
        self,
        contexto,
        estrategia_sacador,
        poder_saque,
        chance_ace,
        poder_devolucao,
        stats_info,
    ):
        sacador = self.jogador if contexto.sacador == "j" else self.adversario
        receptor = self.adversario if contexto.sacador == "j" else self.jogador
        return ajuste_duplas_saque_devolucao(
            contexto,
            sacador,
            receptor,
            estrategia_sacador,
            poder_saque,
            chance_ace,
            poder_devolucao,
            stats_info,
        )

    def _confronto(self, valor_atacante: float, valor_defensor: float) -> bool:
        atk = valor_atacante / 100.0
        def_ = valor_defensor / 100.0
        vantagem = atk - def_
        prob_base = 0.5 + (vantagem * 0.7)
        prob_base = max(0.1, min(0.9, prob_base))
        sorte = (random.random() - 0.5) * 2 * self.FATOR_SORTE
        prob_final = prob_base + sorte
        prob_final = max(0.05, min(0.95, prob_final))
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
        sup = normalizar_superficie(superficie)
        bases = {"saibro": 5.5, "dura": 3.5, "grama": 2.0}
        media = bases.get(sup, 3.5)

        def _peso_estilo(e: str) -> float:
            if e == "atacar_do_fundo":
                return 1.0
            if e == "atacar_pelo_meio":
                return 0.80
            return 0.45

        media *= (_peso_estilo(estilo_j) + _peso_estilo(estilo_a)) / 2.0
        resistencia = (
            atributos_j.get("resistencia", 50) + atributos_a.get("resistencia", 50)
        ) / 2
        velocidade = (
            atributos_j.get("velocidade", 50) + atributos_a.get("velocidade", 50)
        ) / 2
        media += (resistencia - 50) / 50.0
        media += (velocidade - 50) / 100.0
        avg_stamina = (stamina_j + stamina_a) / 2
        if avg_stamina < 35:
            media *= 0.60
        elif avg_stamina < 55:
            media *= 0.78
        media = max(1.0, media)
        n = round(random.gauss(media, media * 0.55))
        return max(1, min(n, 18))

    @staticmethod
    def _n_trocas_para_intensidade(n: int) -> str:
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
            escala = 1.0 + i * 0.025
            p_j = poder_j * (1.0 + (leitura_j - 50) * 0.002 * escala)
            p_a = poder_a * (1.0 + (leitura_a - 50) * 0.002 * escala)
            if self._confronto(p_j, p_a):
                vantagem += 0.1
            else:
                vantagem -= 0.1
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
        insights: list[str] | None = None,
    ) -> float:
        stamina = max(0.0, min(100.0, stamina))
        atributos = atributos or {}
        resistencia = atributos.get("resistencia", 50)
        agilidade = atributos.get("agilidade", 50)
        stamina_efetiva = stamina + (resistencia - 50) * 0.4
        stamina_efetiva = max(0.0, min(100.0, stamina_efetiva))
        mod = 0.7 + (stamina_efetiva / 100.0) * 0.3
        if estilo == "atacar_do_fundo" and stamina < 55:
            mod += (agilidade - 50) / 800.0
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

    def _aplicar_mod_superficie(
        self, atributos: dict, superficie: str, entidade: Any = None
    ) -> dict:
        superficie = normalizar_superficie(superficie)
        mods = SUPERFICIE_MODS.get(superficie, SUPERFICIE_MODS["dura"])

        # Especialização Individual (O Toque de Mestre)
        pref = getattr(entidade, "superficie_preferida", "dura") if entidade else "dura"
        bonus_pref = 1.0
        if pref == superficie:
            bonus_pref = 1.10  # +10% em tudo na superfície favorita
        elif (pref == "saibro" and superficie == "grama") or (
            pref == "grama" and superficie == "saibro"
        ):
            bonus_pref = 0.85  # -15% se for a superfície oposta ao seu estilo natural

        return {k: v * mods.get(k, 1.0) * bonus_pref for k, v in atributos.items()}

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

    @staticmethod
    def _append_insight(insights: list[str] | None, texto: str) -> None:
        pn_append_insight(insights, texto)

    @staticmethod
    def _momento_do_ponto(contexto: ContextoPonto) -> tuple[str, str]:
        return pn_momento_do_ponto(contexto)

    @staticmethod
    def _rotulo_estilo(estilo: str) -> str:
        return pn_rotulo_estilo(estilo)

    def _registrar_narrativa_ponto(
        self,
        stats_info: MatchPointStats,
        contexto: ContextoPonto,
        vencedor: str,
        estrategia_j: dict,
        estrategia_a: dict,
        poder_saque: float,
        poder_devolucao: float,
        poder_rally_j: float,
        poder_rally_a: float,
    ) -> None:
        pn_registrar_narrativa_ponto(
            stats_info,
            contexto,
            vencedor,
            estrategia_j,
            estrategia_a,
            poder_saque,
            poder_devolucao,
            poder_rally_j,
            poder_rally_a,
        )

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
        insights: list[str] = None,
        eh_jogador: bool = True,
        energia: float = 100.0,
        condicao: int = 100,
    ) -> tuple:
        vel_saque = atributos.get("vel_saque", 50)
        pre_saque = atributos.get("pre_saque", 50)
        segundo_saque = atributos.get("segundo_saque", 50)
        forca = atributos.get("forca", 50)
        clutch = psico.get("clutch", 55)
        compostura = psico.get("compostura", 55)
        # Primeiro saque: vel_saque*0.65 + pre_saque*0.25 + forca*0.10
        poder_primeiro = vel_saque * 0.65 + pre_saque * 0.25 + forca * 0.10
        # Segundo saque: segundo_saque*0.55 + pre_saque*0.30 + vel_saque*0.15
        poder_segundo = segundo_saque * 0.55 + pre_saque * 0.30 + vel_saque * 0.15
        # Penalidade compostura baixa no segundo saque
        if compostura < 50:
            poder_segundo *= 1.0 - (50 - compostura) * 0.004
        if tipo_saque == TipoSaque.AGRESSIVO:
            poder = poder_primeiro * 1.15
            chance_falta = 0.35 - (vel_saque / 500)
            chance_ace = 0.12 + (vel_saque / 500)
        elif tipo_saque == TipoSaque.SEGURO:
            poder = poder_segundo * 0.85
            chance_falta = 0.08 - (segundo_saque / 1000)
            chance_ace = 0.02 + (segundo_saque / 1000)
        else:
            poder = poder_primeiro
            chance_falta = 0.20 - (vel_saque / 500)
            chance_ace = 0.06 + (vel_saque / 500)
        # Bonus clutch em pontos criticos
        momento, _ = self._momento_do_ponto(contexto)
        if momento in ("break_point", "match_point", "set_point", "deuce"):
            bonus_clutch = (clutch - 50) * 0.04
            poder += bonus_clutch * 3
            chance_ace += bonus_clutch * 0.005
            chance_falta -= bonus_clutch * 0.01
        bonus, psico_insights = calcular_bonus_psicologico(
            psico, contexto, eh_jogador=eh_jogador
        )
        poder += bonus * 5
        chance_falta -= bonus * 0.02
        chance_ace += bonus * 0.01
        if insights is not None:
            for pi in psico_insights:
                if pi not in insights:
                    insights.append(pi)
        mod_stamina = self._stamina_mod(
            stamina,
            atributos=atributos,
            superficie=superficie,
            insights=insights if eh_jogador else None,
        )
        poder = self._aplicar_modificadores(
            poder,
            0.0,
            mod_stamina,
            fator_estado=fator_estado,
            energia=energia,
            condicao=condicao,
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
        insights: list[str] = None,
        eh_jogador: bool = True,
        energia: float = 100.0,
        condicao: int = 100,
    ) -> float:
        retorno = atributos.get("retorno", 50)
        backhand = atributos.get("backhand", 50)
        velocidade = atributos.get("velocidade", 50)
        agilidade = atributos.get("agilidade", 50)
        slice_ = atributos.get("slice", 50)
        bonus, psico_insights = calcular_bonus_psicologico(
            psico, contexto, eh_jogador=eh_jogador
        )
        if insights is not None:
            for pi in psico_insights:
                if pi not in insights:
                    insights.append(pi)
        # retorno*0.40 + backhand*0.25 + velocidade*0.15 + agilidade*0.10 + slice*0.10
        base = (
            retorno * 0.40
            + backhand * 0.25
            + velocidade * 0.15
            + agilidade * 0.10
            + slice_ * 0.10
        )
        poder = self._aplicar_modificadores(
            base,
            bonus * 5,
            self._stamina_mod(
                stamina,
                atributos=atributos,
                superficie=superficie,
                insights=insights if eh_jogador else None,
            ),
            fator_estado=fator_estado,
            energia=energia,
            condicao=condicao,
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
        insights: list[str] = None,
        eh_jogador: bool = True,
        energia: float = 100.0,
        condicao: int = 100,
    ) -> float:
        forehand = atributos.get("forehand", 50)
        backhand = atributos.get("backhand", 50)
        velocidade = atributos.get("velocidade", 50)
        agilidade = atributos.get("agilidade", 50)
        voleio = atributos.get("voleio", 50)
        smash = atributos.get("smash", 50)
        topspin = atributos.get("topspin", 50)
        slice_ = atributos.get("slice", 50)
        winner = atributos.get("winner", 50)
        estilo = estrategia.get("estilo", "atacar_do_fundo")
        lob = atributos.get("lob", 50)
        if estilo == "atacar_na_rede":
            # voleio*0.42 + velocidade*0.18 + forehand*0.16 + smash*0.12 + slice*0.08 + lob*0.04
            base = (
                voleio * 0.42
                + velocidade * 0.18
                + forehand * 0.16
                + smash * 0.12
                + slice_ * 0.08
                + lob * 0.04
            )
        elif estilo == "atacar_do_fundo":
            # forehand*0.30 + backhand*0.30 + topspin*0.18 + agilidade*0.12 + slice*0.05 + winner*0.05
            base = (
                forehand * 0.30
                + backhand * 0.30
                + topspin * 0.18
                + agilidade * 0.12
                + slice_ * 0.05
                + winner * 0.05
            )
        else:
            base = (
                forehand * 0.24
                + backhand * 0.24
                + velocidade * 0.18
                + voleio * 0.14
                + topspin * 0.09
                + winner * 0.05
                + slice_ * 0.04
                + lob * 0.02
            )
        bonus, psico_insights = calcular_bonus_psicologico(
            psico, contexto, eh_jogador=eh_jogador
        )
        if insights is not None:
            for pi in psico_insights:
                if pi not in insights:
                    insights.append(pi)
        poder = self._aplicar_modificadores(
            base,
            bonus * 8,
            self._stamina_mod(
                stamina,
                atributos=atributos,
                estilo=estilo,
                superficie=superficie,
                insights=insights if eh_jogador else None,
            ),
            fator_estado=fator_estado,
            energia=energia,
            condicao=condicao,
        )
        leitura = psico.get("leitura_de_jogo", 50)
        poder += (leitura - 50) * 0.15
        return poder

    def _aplicar_modificadores(
        self,
        valor_base: float,
        bonus_psico: float,
        stamina_mod: float,
        fator_estado: float = 1.0,
        energia: float = 100.0,
        condicao: int = 100,
    ) -> float:
        valor = (valor_base + bonus_psico) * stamina_mod * fator_estado
        valor *= 1.0 - calcular_penalidade_energia(energia)
        valor *= calcular_multiplicador_condicao(condicao)
        return valor

    def _get_fator_estado(self, moral: float, ritmo: float) -> float:
        """
        Retorna multiplicador de performance baseado em moral e ritmo de jogo.
        O ritmo de jogo (0-100) tem um impacto crucial na consistência.
        """
        f_moral = 1.0 + (moral - 70) / 400.0  # Mais impacto que antes
        f_ritmo = 1.0 + (ritmo - 50) / 250.0  # Drasticamente aumentado (era /1000)
        return max(0.75, min(1.20, f_moral * f_ritmo))

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
        entidade: object = None,
    ) -> tuple:
        agressividade = psico.get("agressividade", 50)
        clutch = psico.get("clutch", 55)
        compostura = psico.get("compostura", 55)
        forehand = atributos.get("forehand", 50)
        backhand = atributos.get("backhand", 50)
        voleio = atributos.get("voleio", 50)
        duplas = atributos.get("duplas", 60)
        estilo = estrategia.get("estilo", "atacar_do_fundo")
        p_duplas = (
            perfil_duplas_entidade(entidade)
            if entidade is not None
            else {"ativa": False, "quimica": 0.0}
        )
        winner_attr = atributos.get("winner", 50)
        chance_winner = (
            agressividade * 0.35 + winner_attr * 0.40 + vantagem_rally * 50.0 * 0.25
        ) / 100.0
        superficie_norm = str(superficie).lower()
        if "grama" in superficie_norm:
            chance_winner *= 1.25
        elif "saibro" in superficie_norm:
            chance_winner *= 0.78
        if stamina < 40:
            chance_winner *= 0.70
        elif stamina < 60:
            chance_winner *= 0.88
        if intencao == IntencaoPonto.ARRISCAR:
            chance_winner *= 1.40
        elif intencao == IntencaoPonto.DEFENSIVO:
            chance_winner *= 0.0
        if p_duplas.get("ativa"):
            chance_winner *= 1.0 + min(
                0.14,
                p_duplas.get("quimica", 0.0) / 140.0
                + max(0.0, (duplas - 60.0) / 240.0),
            )
        chance_winner = min(0.82, chance_winner)
        if random.random() < chance_winner:
            # clutch em pontos criticos, compostura em pressao continua
            foco = (clutch + compostura) / 2.0
            if random.random() < foco / 100.0:
                if (
                    p_duplas.get("ativa")
                    and estilo == "atacar_na_rede"
                    and voleio > 60
                    and duplas >= 72
                ):
                    return (
                        "Poach agressivo na rede e voleio limpo para matar o ponto!",
                        True,
                        False,
                    )
                elif estilo == "atacar_na_rede" and voleio > 60:
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
                golpe = "Forehand" if forehand > backhand else "Backhand"
                local = random.choice(["na rede", "pra fora"])
                return (f"{golpe} {local}!", False, True)
        else:
            return ("Adversário força o erro, ponto ganho!", False, False)

    def simular_ponto_estrategista(
        self,
        estrategia: dict,
        contexto: ContextoPonto,
        tipo_saque: TipoSaque = None,
        contexto_partida: ContextoPartida = None,
        estrategia_adversario: dict = None,
    ) -> tuple:
        descricoes = []
        atributos_j = self._get_atributos_jogador()
        atributos_a = self._get_atributos_adversario()
        psico_j = self._get_psico_jogador()
        psico_a = self._get_psico_adversario()
        stats_info = MatchPointStats.novo(contexto.sacador)
        contexto_partida = contexto_partida or ContextoPartida()
        superficie = normalizar_superficie(contexto_partida.superficie)
        energia_j = float(contexto_partida.stamina_j)
        energia_a = float(contexto_partida.stamina_a)
        condicao_j = int(getattr(contexto_partida, "condicao_j", 100))
        condicao_a = int(getattr(contexto_partida, "condicao_a", 100))
        if contexto.sacador == "j":
            attr_sacador, psico_sacador = atributos_j, psico_j
            attr_receptor, psico_receptor = atributos_a, psico_a
            nome_receptor = self.adversario.get("nome", "Adversario")
            stamina_sacador = contexto_partida.stamina_j
            stamina_receptor = contexto_partida.stamina_a
            energia_sacador, energia_receptor = energia_j, energia_a
            condicao_sacador, condicao_receptor = condicao_j, condicao_a
        else:
            attr_sacador, psico_sacador = atributos_a, psico_a
            attr_receptor, psico_receptor = atributos_j, psico_j
            nome_receptor = (
                self.jogador.nome if hasattr(self.jogador, "nome") else "Jogador"
            )
            stamina_sacador = contexto_partida.stamina_a
            stamina_receptor = contexto_partida.stamina_j
            energia_sacador, energia_receptor = energia_a, energia_j
            condicao_sacador, condicao_receptor = condicao_a, condicao_j
        status_j = self._get_status_lesao_jogador()
        status_a = self._get_status_lesao_adversario()
        doenca_j = self._get_status_doenca_jogador()
        doenca_a = self._get_status_doenca_adversario()
        atributos_j = self._aplicar_efeito_lesao(atributos_j, status_j)
        atributos_a = self._aplicar_efeito_lesao(atributos_a, status_a)
        atributos_j = self._aplicar_efeito_doenca(atributos_j, doenca_j)
        atributos_a = self._aplicar_efeito_doenca(atributos_a, doenca_a)
        atributos_j_mod = self._aplicar_mod_superficie(
            atributos_j, superficie, entidade=self.jogador
        )
        atributos_a_mod = self._aplicar_mod_superficie(
            atributos_a, superficie, entidade=self.adversario
        )
        if contexto.sacador == "j":
            attr_sacador, attr_receptor = atributos_j_mod, atributos_a_mod
        else:
            attr_sacador, attr_receptor = atributos_a_mod, atributos_j_mod
        mod_ambiente = self._mod_ambiente(contexto_partida)
        fator_j = self._get_fator_estado(
            contexto_partida.moral_j, contexto_partida.ritmo_j
        )
        fator_a = self._get_fator_estado(
            contexto_partida.moral_a, contexto_partida.ritmo_a
        )
        if contexto.sacador == "j":
            fator_sacador = fator_j
            fator_receptor = fator_a
        else:
            fator_sacador = fator_a
            fator_receptor = fator_j
        estrategia_sacador, estrategia_receptor = self._resolver_estrategias_lado(
            contexto, estrategia, estrategia_adversario
        )
        if contexto.sacador == "j":
            estrategia_j, estrategia_adv = estrategia_sacador, estrategia_receptor
        else:
            estrategia_j, estrategia_adv = estrategia_receptor, estrategia_sacador
        tipo = tipo_saque or estrategia_sacador.get("saque_tipo", TipoSaque.VARIADO)
        stats_info.momento, stats_info.pressao = self._momento_do_ponto(contexto)
        poder_saque, chance_ace, chance_falta = self._calcular_poder_saque(
            attr_sacador,
            psico_sacador,
            tipo,
            contexto,
            superficie,
            stamina_sacador,
            fator_estado=fator_sacador,
            insights=stats_info.insights,
            eh_jogador=(contexto.sacador == "j"),
            energia=energia_sacador,
            condicao=condicao_sacador,
        )
        poder_devolucao = self._calcular_poder_devolucao(
            attr_receptor,
            psico_receptor,
            contexto,
            superficie,
            stamina_receptor,
            fator_estado=fator_receptor,
            insights=stats_info.insights,
            eh_jogador=(contexto.sacador == "a"),
            energia=energia_receptor,
            condicao=condicao_receptor,
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
        poder_saque, chance_ace, poder_devolucao = ajuste_duplas_saque_devolucao(
            contexto,
            self.jogador if contexto.sacador == "j" else self.adversario,
            self.adversario if contexto.sacador == "j" else self.jogador,
            estrategia_sacador,
            poder_saque,
            chance_ace,
            poder_devolucao,
            stats_info,
        )
        if random.random() < chance_falta:
            descricoes.append("1o saque: Falta!")
            estrategia_saque = estrategia_sacador.get("saque", EstrategiaSaque.SEGURO)
            if self.segundo_saque(estrategia_saque, contexto)[0]:
                descricoes.append("2o saque: Em jogo.")
            else:
                descricoes.append("2o saque: Dupla falta!")
                stats_info.dupla_falta = True
                stats_info.intensidade = "curto"
                vencedor = "a" if contexto.sacador == "j" else "j"
                self._registrar_narrativa_ponto(
                    stats_info,
                    contexto,
                    vencedor,
                    estrategia_j,
                    estrategia_adv,
                    poder_saque,
                    poder_devolucao,
                    0.0,
                    0.0,
                )
                return (vencedor, self._padronizar_descricoes(descricoes), stats_info)
        else:
            stats_info.primeiro_saque_in = True
            if random.random() < chance_ace and self._confronto(
                poder_saque * 1.3, poder_devolucao
            ):
                descricoes.append(
                    f"1o saque: Ace {random.choice(['no T', 'aberto', 'no corpo'])}!"
                )
                stats_info.ace = True
                stats_info.intensidade = "curto"
                self._registrar_narrativa_ponto(
                    stats_info,
                    contexto,
                    contexto.sacador,
                    estrategia_j,
                    estrategia_adv,
                    poder_saque,
                    poder_devolucao,
                    0.0,
                    0.0,
                )
                return (
                    contexto.sacador,
                    self._padronizar_descricoes(descricoes),
                    stats_info,
                )
            else:
                descricoes.append(
                    f"1o saque: Saque {'potente' if poder_saque > 60 else 'preciso' if poder_saque > 45 else 'seguro'}, em jogo."
                )
        descricoes.append(f"Rally: {random.choice(self.DESCRICOES_RALLY)}")
        if contexto.sacador == "j":
            poder_rally_j = self._calcular_poder_rally(
                atributos_j_mod,
                psico_j,
                estrategia_j,
                contexto,
                superficie,
                contexto_partida.stamina_j,
                fator_estado=fator_j,
                insights=stats_info.insights,
                eh_jogador=True,
                energia=energia_j,
                condicao=condicao_j,
            )
            poder_rally_a = self._calcular_poder_rally(
                atributos_a_mod,
                psico_a,
                estrategia_adv,
                contexto,
                superficie,
                contexto_partida.stamina_a,
                fator_estado=fator_a,
                insights=stats_info.insights,
                eh_jogador=False,
                energia=energia_a,
                condicao=condicao_a,
            )
        else:
            poder_rally_a = self._calcular_poder_rally(
                atributos_a_mod,
                psico_a,
                estrategia_adv,
                contexto,
                superficie,
                contexto_partida.stamina_a,
                fator_estado=fator_a,
                insights=stats_info.insights,
                eh_jogador=False,
                energia=energia_a,
                condicao=condicao_a,
            )
            poder_rally_j = self._calcular_poder_rally(
                atributos_j_mod,
                psico_j,
                estrategia_j,
                contexto,
                superficie,
                contexto_partida.stamina_j,
                fator_estado=fator_j,
                insights=stats_info.insights,
                eh_jogador=True,
                energia=energia_j,
                condicao=condicao_j,
            )
        poder_rally_j *= mod_ambiente["rally"]
        poder_rally_a *= mod_ambiente["rally"]
        poder_rally_j *= 1.0 + (contexto_partida.momentum_j * 0.02)
        poder_rally_a *= 1.0 + (contexto_partida.momentum_a * 0.02)
        poder_rally_j, poder_rally_a = ajuste_duplas_rally(
            self.jogador,
            self.adversario,
            poder_rally_j,
            poder_rally_a,
            estrategia_j,
            estrategia_adv,
            stats_info,
            descricoes,
        )
        _venceu_rally_j, _vantagem_rally, _n_trocas_rally = self._simular_rally_trocas(
            poder_rally_j,
            poder_rally_a,
            psico_j,
            psico_a,
            stamina_j=contexto_partida.stamina_j,
            stamina_a=contexto_partida.stamina_a,
            superficie=contexto_partida.superficie,
            estilo_j=estrategia_j.get("estilo"),
            estilo_a=estrategia_adv.get("estilo"),
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
                entidade=self.jogador,
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
                entidade=self.adversario,
            )
        descricoes.append(desc_final)
        stats_info.winner = eh_winner
        stats_info.erro_nao_forcado = eh_erro
        stats_info.intensidade = self._n_trocas_para_intensidade(_n_trocas_rally)
        self._registrar_narrativa_ponto(
            stats_info,
            contexto,
            vencedor,
            estrategia_j,
            estrategia_adv,
            poder_saque,
            poder_devolucao,
            poder_rally_j,
            poder_rally_a,
        )
        return (vencedor, self._padronizar_descricoes(descricoes), stats_info)

    def simular_ponto_rapido(
        self,
        estrategia: dict,
        contexto: ContextoPonto = None,
        contexto_partida: ContextoPartida = None,
        estrategia_adversario: dict = None,
    ) -> tuple:
        contexto = contexto or self._contexto_padrao_saque()
        vencedor, _, stats = self.simular_ponto_estrategista(
            estrategia,
            contexto,
            contexto_partida=contexto_partida,
            estrategia_adversario=estrategia_adversario,
        )
        return vencedor, stats

    def simular_ponto_detalhado(
        self,
        estrategia: dict,
        contexto: ContextoPonto,
        tipo_saque: TipoSaque = None,
        contexto_partida: ContextoPartida = None,
        estrategia_adversario: dict = None,
    ) -> tuple:
        return self.simular_ponto_estrategista(
            estrategia,
            contexto,
            tipo_saque=tipo_saque,
            contexto_partida=contexto_partida,
            estrategia_adversario=estrategia_adversario,
        )
