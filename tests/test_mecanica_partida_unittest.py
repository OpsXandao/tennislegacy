import unittest
from unittest.mock import patch

from src.match_core import simular_game_rapido, atualizar_estatisticas
from src.constants.match_constants import TipoSaque, MatchPointStats, EstrategiaSaque, IntencaoPonto
from src.simulacao_partida import ContextoPartida, ContextoPonto, SimuladorPonto


class SimuladorSequencial:
    def __init__(self, vencedores):
        self.vencedores = list(vencedores)
        self.idx = 0
        self.contextos = []

    def simular_ponto_rapido(
        self, _estrategia, contexto, _contexto_partida, _estrategia_adversario
    ):
        self.contextos.append(contexto.placar_game)
        if self.idx < len(self.vencedores):
            vencedor = self.vencedores[self.idx]
        else:
            vencedor = self.vencedores[-1]
        self.idx += 1
        return vencedor, {"intensidade": "medio", "sacador": contexto.sacador}


class MecanicaPartidaTests(unittest.TestCase):
    def _jogador_base(self):
        return {
            "nome": "Jogador",
            "atributos": {
                "saque": 60,
                "devolucao": 60,
                "forehand": 60,
                "backhand": 60,
                "voleio": 50,
                "movimento": 60,
                "topspin": 55,
                "slice": 50,
                "fisico": 60,
                "lob": 50,
                "winner": 60,
            },
            "atributos_psicologicos": {
                "concentracao": 50,
                "agressividade": 50,
                "leitura_de_jogo": 50,
                "determinacao": 50,
            },
        }

    def test_contexto_tiebreak_reconhece_set_point(self):
        contexto = ContextoPonto(
            sacador="j",
            placar_game=(6, 5),
            placar_set=(6, 6),
            placar_partida=(0, 0),
            sets_para_vencer=2,
            is_tiebreak=True,
            tiebreak_alvo=7,
        )
        self.assertTrue(contexto.is_set_point())

    def test_contexto_tiebreak_reconhece_match_point(self):
        contexto = ContextoPonto(
            sacador="j",
            placar_game=(6, 5),
            placar_set=(6, 6),
            placar_partida=(1, 1),
            sets_para_vencer=2,
            is_tiebreak=True,
            tiebreak_alvo=7,
        )
        self.assertTrue(contexto.is_match_point())

    def test_game_rapido_avanca_placar_apos_deuce(self):
        jogador = {
            "nome": "Jogador",
            "atributos": {"fisico": 50, "movimento": 50, "topspin": 50},
            "atributos_psicologicos": {"agressividade": 50},
        }
        adversario = {
            "nome": "Adversario",
            "atributos": {"fisico": 50, "movimento": 50, "topspin": 50},
            "atributos_psicologicos": {"agressividade": 50},
        }
        simulador = SimuladorSequencial(
            ["j", "j", "j", "a", "a", "a", "j", "a", "j", "j"]
        )
        contexto_partida = ContextoPartida()

        vencedor, _historico, abandonou = simular_game_rapido(
            jogador,
            adversario,
            estrategia={"estilo": "atacar_do_fundo"},
            sacador="j",
            placar_set=(0, 0),
            placar_partida=(0, 0),
            simulador=simulador,
            contexto_partida=contexto_partida,
            estrategia_adversario={"estilo": "atacar_do_fundo"},
            silencioso=True,
            sets_para_vencer=2,
        )

        self.assertFalse(abandonou)
        self.assertEqual(vencedor, "j")
        self.assertIn((4, 3), simulador.contextos)
        self.assertIn((3, 3), simulador.contextos)

    def test_simulador_ponto_saque_sem_contexto_nao_quebra(self):
        jogador = self._jogador_base()
        adversario = {
            "nome": "Adversario",
            "atributos": dict(jogador["atributos"]),
            "atributos_psicologicos": dict(jogador["atributos_psicologicos"]),
        }
        simulador = SimuladorPonto(jogador, adversario)

        entrou_primeiro, _ace, _falta = simulador.primeiro_saque(TipoSaque.VARIADO)
        entrou_segundo, _resultado_segundo, _descricao_segundo = (
            simulador.segundo_saque()
        )

        self.assertIn(entrou_primeiro, (True, False))
        self.assertIn(entrou_segundo, (True, False))

    def test_simular_ponto_rapido_sem_contexto_nao_quebra(self):
        jogador = self._jogador_base()
        adversario = {
            "nome": "Adversario",
            "atributos": dict(jogador["atributos"]),
            "atributos_psicologicos": dict(jogador["atributos_psicologicos"]),
        }
        simulador = SimuladorPonto(jogador, adversario)

        vencedor, stats = simulador.simular_ponto_rapido({"estilo": "atacar_do_fundo"})

        self.assertIn(vencedor, ("j", "a"))
        self.assertIsInstance(stats, MatchPointStats)
        self.assertTrue(hasattr(stats, "get"))
        self.assertIn("sacador", stats)

    def test_modo_rapido_usa_saque_tipo_da_estrategia_do_sacador(self):
        jogador = self._jogador_base()
        adversario = {
            "nome": "Adversario",
            "atributos": dict(jogador["atributos"]),
            "atributos_psicologicos": dict(jogador["atributos_psicologicos"]),
        }
        simulador = SimuladorPonto(jogador, adversario)
        contexto = ContextoPonto(
            sacador="j",
            placar_game=(0, 0),
            placar_set=(0, 0),
            placar_partida=(0, 0),
        )

        tipos = []

        def fake_poder_saque(_attrs, _psico, tipo_saque, *_args, **_kwargs):
            tipos.append(tipo_saque)
            return (60.0, 0.0, 0.0)

        with patch.object(simulador, "_calcular_poder_saque", side_effect=fake_poder_saque), \
             patch.object(simulador, "_calcular_poder_devolucao", return_value=50.0), \
             patch.object(simulador, "_calcular_poder_rally", side_effect=[55.0, 45.0]), \
             patch.object(simulador, "_confronto", return_value=True), \
             patch.object(
                 simulador,
                 "_determinar_tipo_finalizacao",
                 return_value=("Winner de forehand na cruzada!", True, False),
             ):
            simulador.simular_ponto_rapido(
                {
                    "estilo": "atacar_do_fundo",
                    "saque_tipo": TipoSaque.AGRESSIVO,
                    "saque": EstrategiaSaque.FORCAR,
                    "intencao": IntencaoPonto.ARRISCAR,
                },
                contexto=contexto,
                contexto_partida=ContextoPartida(),
                estrategia_adversario={
                    "estilo": "atacar_na_rede",
                    "saque_tipo": TipoSaque.SEGURO,
                    "saque": EstrategiaSaque.SEGURO,
                    "intencao": IntencaoPonto.DEFENSIVO,
                },
            )

        self.assertEqual(tipos, [TipoSaque.AGRESSIVO])

    def test_segundo_saque_respeita_estrategia_do_adversario_quando_ele_saca(self):
        jogador = self._jogador_base()
        adversario = {
            "nome": "Adversario",
            "atributos": dict(jogador["atributos"]),
            "atributos_psicologicos": dict(jogador["atributos_psicologicos"]),
        }
        simulador = SimuladorPonto(jogador, adversario)
        contexto = ContextoPonto(
            sacador="a",
            placar_game=(0, 0),
            placar_set=(0, 0),
            placar_partida=(0, 0),
        )

        segundos_saques = []

        with patch.object(simulador, "_calcular_poder_saque", return_value=(60.0, 0.0, 1.0)), \
             patch.object(simulador, "_calcular_poder_devolucao", return_value=50.0), \
             patch.object(simulador, "segundo_saque", side_effect=lambda estrategia_saque, _ctx: (segundos_saques.append(estrategia_saque) or True, None, "Em jogo.")), \
             patch.object(simulador, "_calcular_poder_rally", side_effect=[45.0, 55.0]), \
             patch.object(simulador, "_confronto", return_value=False), \
             patch.object(
                 simulador,
                 "_determinar_tipo_finalizacao",
                 return_value=("Winner de backhand na paralela!", True, False),
             ):
            simulador.simular_ponto_rapido(
                {
                    "estilo": "atacar_do_fundo",
                    "saque_tipo": TipoSaque.AGRESSIVO,
                    "saque": EstrategiaSaque.FORCAR,
                    "intencao": IntencaoPonto.ARRISCAR,
                },
                contexto=contexto,
                contexto_partida=ContextoPartida(),
                estrategia_adversario={
                    "estilo": "atacar_na_rede",
                    "saque_tipo": TipoSaque.SEGURO,
                    "saque": EstrategiaSaque.SEGURO,
                    "intencao": IntencaoPonto.DEFENSIVO,
                },
            )

        self.assertEqual(segundos_saques, [EstrategiaSaque.SEGURO])

    def test_rally_usa_estrategia_do_adversario_quando_ele_saca(self):
        jogador = self._jogador_base()
        adversario = {
            "nome": "Adversario",
            "atributos": dict(jogador["atributos"]),
            "atributos_psicologicos": dict(jogador["atributos_psicologicos"]),
        }
        simulador = SimuladorPonto(jogador, adversario)
        contexto = ContextoPonto(
            sacador="a",
            placar_game=(0, 0),
            placar_set=(0, 0),
            placar_partida=(0, 0),
        )

        estilos = []

        def fake_poder_rally(_atributos, _psico, estrategia_usada, *_args, **_kwargs):
            estilos.append(estrategia_usada.get("estilo"))
            return 50.0

        with patch.object(simulador, "_calcular_poder_saque", return_value=(60.0, 0.0, 1.0)), \
             patch.object(simulador, "_calcular_poder_devolucao", return_value=50.0), \
             patch.object(simulador, "_calcular_poder_rally", side_effect=fake_poder_rally), \
             patch.object(simulador, "_simular_rally_trocas", return_value=(False, 0.1, 4)), \
             patch.object(
                 simulador,
                 "_determinar_tipo_finalizacao",
                 return_value=("Winner de backhand na paralela!", True, False),
             ):
            simulador.simular_ponto_rapido(
                {
                    "estilo": "atacar_do_fundo",
                    "saque_tipo": TipoSaque.AGRESSIVO,
                    "saque": EstrategiaSaque.FORCAR,
                    "intencao": IntencaoPonto.ARRISCAR,
                },
                contexto=contexto,
                contexto_partida=ContextoPartida(),
                estrategia_adversario={
                    "estilo": "atacar_na_rede",
                    "saque_tipo": TipoSaque.SEGURO,
                    "saque": EstrategiaSaque.SEGURO,
                    "intencao": IntencaoPonto.DEFENSIVO,
                },
            )

        self.assertEqual(estilos[0], "atacar_na_rede")
        self.assertEqual(estilos[1], "atacar_do_fundo")

    def test_estrategista_usa_tipo_saque_do_adversario_quando_ele_saca(self):
        jogador = self._jogador_base()
        adversario = {
            "nome": "Adversario",
            "atributos": dict(jogador["atributos"]),
            "atributos_psicologicos": dict(jogador["atributos_psicologicos"]),
        }
        simulador = SimuladorPonto(jogador, adversario)
        contexto = ContextoPonto(
            sacador="a",
            placar_game=(0, 0),
            placar_set=(0, 0),
            placar_partida=(0, 0),
        )

        tipos = []

        def fake_poder_saque(_attrs, _psico, tipo_saque, *_args, **_kwargs):
            tipos.append(tipo_saque)
            return (60.0, 0.0, 1.0)

        with patch.object(simulador, "_calcular_poder_saque", side_effect=fake_poder_saque), \
             patch.object(simulador, "_calcular_poder_devolucao", return_value=50.0), \
             patch.object(simulador, "segundo_saque", return_value=(True, None, "Em jogo.")), \
             patch.object(simulador, "_calcular_poder_rally", side_effect=[45.0, 55.0]), \
             patch.object(simulador, "_simular_rally_trocas", return_value=(False, 0.1, 4)), \
             patch.object(
                 simulador,
                 "_determinar_tipo_finalizacao",
                 return_value=("Winner de backhand na paralela!", True, False),
             ):
            simulador.simular_ponto_estrategista(
                {
                    "estilo": "atacar_do_fundo",
                    "saque_tipo": TipoSaque.AGRESSIVO,
                    "saque": EstrategiaSaque.FORCAR,
                    "intencao": IntencaoPonto.ARRISCAR,
                },
                contexto=contexto,
                contexto_partida=ContextoPartida(),
                estrategia_adversario={
                    "estilo": "atacar_na_rede",
                    "saque_tipo": TipoSaque.SEGURO,
                    "saque": EstrategiaSaque.SEGURO,
                    "intencao": IntencaoPonto.DEFENSIVO,
                },
            )

        self.assertEqual(tipos, [TipoSaque.SEGURO])

    def test_atualizar_estatisticas_trata_muito_longo_como_rally_longo(self):
        stats_j = MatchPointStats.novo("j")
        stats_a = MatchPointStats.novo("a")
        agg_j = type("Stats", (), {"aces":0,"duplas_faltas":0,"primeiro_saque_in":0,"primeiro_saque_total":0,"winners":0,"erros_nao_forcados":0,"pontos_ganhos_saque":0,"pontos_total_saque":0,"pontos_ganhos_devolucao":0,"pontos_total_devolucao":0,"break_points_convertidos":0,"break_points_total":0,"break_points_salvos":0,"break_points_enfrentados":0,"rallies_curtos":0,"rallies_medios":0,"rallies_longos":0})()
        agg_a = type("Stats", (), {"aces":0,"duplas_faltas":0,"primeiro_saque_in":0,"primeiro_saque_total":0,"winners":0,"erros_nao_forcados":0,"pontos_ganhos_saque":0,"pontos_total_saque":0,"pontos_ganhos_devolucao":0,"pontos_total_devolucao":0,"break_points_convertidos":0,"break_points_total":0,"break_points_salvos":0,"break_points_enfrentados":0,"rallies_curtos":0,"rallies_medios":0,"rallies_longos":0})()
        contexto = ContextoPonto(
            sacador="j",
            placar_game=(0, 0),
            placar_set=(0, 0),
            placar_partida=(0, 0),
        )

        atualizar_estatisticas(
            agg_j,
            agg_a,
            "j",
            {"sacador": "j", "intensidade": "muito_longo"},
            contexto,
        )

        self.assertEqual(agg_j.rallies_longos, 1)
        self.assertEqual(agg_a.rallies_longos, 1)

    def test_erro_forcado_nao_gera_erro_nao_forcado(self):
        jogador = {
            "nome": "Jogador",
            "atributos": {"forehand": 60, "backhand": 60, "voleio": 50},
            "atributos_psicologicos": {"agressividade": 50, "concentracao": 50},
        }
        adversario = {
            "nome": "Adversario",
            "atributos": dict(jogador["atributos"]),
            "atributos_psicologicos": dict(jogador["atributos_psicologicos"]),
        }
        simulador = SimuladorPonto(jogador, adversario)

        with patch("src.simulacao_partida.random.random", return_value=0.99):
            _desc, eh_winner, eh_erro_nao_forcado = (
                simulador._determinar_tipo_finalizacao(
                    "j",
                    atributos=jogador["atributos"],
                    psico=jogador["atributos_psicologicos"],
                    estrategia={"estilo": "atacar_do_fundo"},
                )
            )

        self.assertFalse(eh_winner)
        self.assertFalse(eh_erro_nao_forcado)


if __name__ == "__main__":
    unittest.main()
