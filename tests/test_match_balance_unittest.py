import random
import unittest

from src.jogar_partida import atualizar_estatisticas
from src.match_constants import EstrategiaSaque, IntencaoPonto, TipoSaque
from src.simulacao_partida import ContextoPartida, ContextoPonto, EstatisticasPartida, SimuladorPonto


class MatchBalanceTests(unittest.TestCase):
    def _player(self):
        return {
            "nome": "Player",
            "atributos": {
                "saque": 74,
                "devolucao": 66,
                "forehand": 72,
                "backhand": 69,
                "voleio": 68,
                "movimento": 70,
                "topspin": 67,
                "slice": 63,
                "fisico": 72,
                "lob": 58,
                "winner": 73,
            },
            "atributos_psicologicos": {
                "concentracao": 67,
                "agressividade": 68,
                "leitura_de_jogo": 64,
                "determinacao": 66,
            },
        }

    def _simulate_points(self, estrategia_j, estrategia_a, points=500):
        random.seed(42)
        jogador = self._player()
        adversario = {
            "nome": "Opponent",
            "atributos": dict(jogador["atributos"]),
            "atributos_psicologicos": dict(jogador["atributos_psicologicos"]),
        }
        simulador = SimuladorPonto(jogador, adversario)
        stats_j = EstatisticasPartida()
        stats_a = EstatisticasPartida()
        contexto_partida = ContextoPartida()

        for i in range(points):
            contexto = ContextoPonto(
                sacador="j" if i % 2 == 0 else "a",
                placar_game=(0, 0),
                placar_set=(0, 0),
                placar_partida=(0, 0),
            )
            vencedor, stats_info = simulador.simular_ponto_rapido(
                estrategia_j,
                contexto=contexto,
                contexto_partida=contexto_partida,
                estrategia_adversario=estrategia_a,
            )
            atualizar_estatisticas(stats_j, stats_a, vencedor, stats_info.to_dict(), contexto)

        return stats_j, stats_a

    def test_plano_agressivo_gera_mais_aces_e_rallies_curtos_que_plano_seguro(self):
        agressivo = {
            "estilo": "atacar_na_rede",
            "saque": EstrategiaSaque.FORCAR,
            "saque_tipo": TipoSaque.AGRESSIVO,
            "intencao": IntencaoPonto.ARRISCAR,
        }
        seguro = {
            "estilo": "atacar_do_fundo",
            "saque": EstrategiaSaque.SEGURO,
            "saque_tipo": TipoSaque.SEGURO,
            "intencao": IntencaoPonto.DEFENSIVO,
        }

        stats_agressivo, _ = self._simulate_points(agressivo, seguro)
        stats_seguro, _ = self._simulate_points(seguro, seguro)

        self.assertGreater(stats_agressivo.aces, stats_seguro.aces)
        self.assertGreater(stats_agressivo.rallies_curtos, stats_seguro.rallies_curtos)

    def test_plano_defensivo_gera_menos_winners_que_plano_ofensivo(self):
        ofensivo = {
            "estilo": "atacar_pelo_meio",
            "saque": EstrategiaSaque.FORCAR,
            "saque_tipo": TipoSaque.AGRESSIVO,
            "intencao": IntencaoPonto.ARRISCAR,
        }
        defensivo = {
            "estilo": "atacar_do_fundo",
            "saque": EstrategiaSaque.SEGURO,
            "saque_tipo": TipoSaque.SEGURO,
            "intencao": IntencaoPonto.DEFENSIVO,
        }

        stats_ofensivo, _ = self._simulate_points(ofensivo, defensivo)
        stats_defensivo, _ = self._simulate_points(defensivo, defensivo)

        self.assertGreater(stats_ofensivo.winners, stats_defensivo.winners)
        self.assertLessEqual(stats_defensivo.erros_nao_forcados, stats_ofensivo.erros_nao_forcados)

    def test_grama_premia_mais_aces_enquanto_saibro_puxa_rallies_longos(self):
        agressivo = {
            "estilo": "atacar_na_rede",
            "saque": EstrategiaSaque.FORCAR,
            "saque_tipo": TipoSaque.AGRESSIVO,
            "intencao": IntencaoPonto.ARRISCAR,
        }
        consistente = {
            "estilo": "atacar_do_fundo",
            "saque": EstrategiaSaque.SEGURO,
            "saque_tipo": TipoSaque.SEGURO,
            "intencao": IntencaoPonto.DEFENSIVO,
        }

        random.seed(7)
        jogador = self._player()
        adversario = {
            "nome": "Opponent",
            "atributos": dict(jogador["atributos"]),
            "atributos_psicologicos": dict(jogador["atributos_psicologicos"]),
        }
        simulador = SimuladorPonto(jogador, adversario)
        stats_grama = EstatisticasPartida()
        stats_saibro = EstatisticasPartida()

        for superficie, stats in (("grama", stats_grama), ("saibro", stats_saibro)):
            contexto_partida = ContextoPartida(superficie=superficie)
            for i in range(450):
                contexto = ContextoPonto(
                    sacador="j" if i % 2 == 0 else "a",
                    placar_game=(0, 0),
                    placar_set=(0, 0),
                    placar_partida=(0, 0),
                )
                estrategia_j = agressivo if superficie == "grama" else consistente
                vencedor, stats_info = simulador.simular_ponto_rapido(
                    estrategia_j,
                    contexto=contexto,
                    contexto_partida=contexto_partida,
                    estrategia_adversario=consistente,
                )
                atualizar_estatisticas(stats, EstatisticasPartida(), vencedor, stats_info.to_dict(), contexto)

        self.assertGreater(stats_grama.aces, stats_saibro.aces)
        self.assertGreater(stats_saibro.rallies_longos, stats_grama.rallies_longos)
