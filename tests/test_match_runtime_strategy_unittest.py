import importlib
import sys
import types
import unittest
from unittest.mock import patch

from src.match_config import ConfigPartida
from src.constants.match_constants import EstrategiaSaque, IntencaoPonto, TipoSaque
from src.match_state import ContextoPartida, EstatisticasPartida


class MatchRuntimeStrategyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fastapi = types.ModuleType("fastapi")

        class HTTPException(Exception):
            def __init__(self, status_code, detail):
                super().__init__(detail)
                self.status_code = status_code
                self.detail = detail

        def Header(default=None, alias=None):
            return default

        def Depends(dependency):
            return dependency

        fastapi.HTTPException = HTTPException
        fastapi.Header = Header
        fastapi.Depends = Depends
        sys.modules["fastapi"] = fastapi
        cls.MatchRuntime = importlib.import_module(
            "api.routes._match_runtime"
        ).MatchRuntime

    def _runtime_base(self):
        runtime = self.MatchRuntime.__new__(self.MatchRuntime)
        runtime.adversario = {
            "nome": "NPC",
            "atributos": {
                "saque": 74,
                "voleio": 66,
                "slice": 60,
                "forehand": 69,
                "backhand": 67,
                "topspin": 64,
                "movimento": 70,
                "winner": 72,
            },
            "atributos_psicologicos": {
                "agressividade": 67,
                "leitura_de_jogo": 61,
                "determinacao": 64,
            },
        }
        runtime.config = ConfigPartida(superficie="grama")
        runtime.contexto_partida = ContextoPartida(superficie="grama", stamina_a=70.0)
        runtime.stats_j = EstatisticasPartida()
        runtime.stats_a = EstatisticasPartida()
        runtime.estrategia_a = {
            "estilo": "atacar_do_fundo",
            "saque": EstrategiaSaque.SEGURO,
            "saque_tipo": TipoSaque.VARIADO,
            "intencao": IntencaoPonto.PACIENTE,
        }
        runtime.sets = [0, 0]
        return runtime

    def test_rival_fica_mais_agressivo_quando_perde_sets_e_winners(self):
        runtime = self._runtime_base()
        runtime.sets = [1, 0]
        runtime.stats_a.winners = 4
        runtime.stats_j.winners = 10
        runtime.stats_a.primeiro_saque_in = 28
        runtime.stats_a.primeiro_saque_total = 40

        runtime._ajustar_plano_adversario("set")

        self.assertEqual(runtime.estrategia_a["intencao"], IntencaoPonto.ARRISCAR)
        self.assertEqual(runtime.estrategia_a["saque"], EstrategiaSaque.FORCAR)

    def test_rival_fica_conservador_quando_primeiro_saque_e_stamina_caem(self):
        runtime = self._runtime_base()
        runtime.contexto_partida.stamina_a = 39.0
        runtime.stats_a.primeiro_saque_in = 18
        runtime.stats_a.primeiro_saque_total = 40

        runtime._ajustar_plano_adversario("game")

        self.assertEqual(runtime.estrategia_a["saque"], EstrategiaSaque.SEGURO)
        self.assertEqual(runtime.estrategia_a["saque_tipo"], TipoSaque.SEGURO)
        self.assertEqual(runtime.estrategia_a["intencao"], IntencaoPonto.DEFENSIVO)

    def test_serializar_reflete_fadiga_ao_vivo_com_base_na_energia_perdida(self):
        runtime = self._runtime_base()
        runtime.jogador = types.SimpleNamespace(fadiga=12, energia=92)
        runtime.adversario["fadiga"] = 18
        runtime.adversario["energia"] = 88
        runtime.contexto_partida.stamina_j = 61.0
        runtime.contexto_partida.stamina_a = 57.0
        runtime.total_pontos = 78
        runtime.energia_inicial = 92
        runtime.energia_inicial_a = 88
        runtime.fadiga_inicial_j = 12
        runtime.fadiga_inicial_a = 18
        runtime.stats_j = EstatisticasPartida()
        runtime.stats_a = EstatisticasPartida()
        runtime.last_point_snapshot = {}
        runtime.log = []
        runtime.sacador = "j"
        runtime.encerrado = False
        runtime.vencedor = None
        runtime.sets = [1, 0]
        runtime.games = [3, 2]
        runtime.pontos = [2, 1]
        runtime.estrategia_j = {
            "estilo": "atacar_do_fundo",
            "saque": EstrategiaSaque.SEGURO,
            "saque_tipo": TipoSaque.VARIADO,
            "intencao": IntencaoPonto.PACIENTE,
        }

        payload = runtime.serializar()

        self.assertGreater(payload["fadiga_j"], 12)
        self.assertGreater(payload["fadiga_a"], 18)
        self.assertIsInstance(payload["descricao_json"], dict)
        self.assertEqual(payload["descricao_json"]["kind"], "ponto")

    def test_runtime_recupera_stamina_apos_game_e_entre_sets(self):
        runtime = self._runtime_base()
        runtime.jogador = types.SimpleNamespace(
            nome="Jogador",
            atributos={"fisico": 72},
            atributos_psicologicos={},
            fadiga=10,
            energia=100,
        )
        runtime.adversario["atributos"]["fisico"] = 68
        runtime.contexto_partida.stamina_j = 61.0
        runtime.contexto_partida.stamina_a = 58.0
        runtime.games = [5, 4]
        runtime.pontos = [3, 2]
        runtime.set_scores = []
        runtime.sacador = "j"
        runtime.encerrado = False

        event_type, _ = runtime._atualizar_placar("j")

        self.assertEqual(event_type, "set")
        self.assertGreater(runtime.contexto_partida.stamina_j, 61.0)
        self.assertGreater(runtime.contexto_partida.stamina_a, 58.0)

    def test_runtime_aplica_bonus_inicial_quando_adversario_e_rival(self):
        runtime = self.MatchRuntime(
            partida_id="p1",
            save_name="save",
            modo="manual",
            jogador=types.SimpleNamespace(
                nome="Jogador",
                energia=100,
                moral=70,
                ritmo_jogo=50,
                rivalidades={
                    "npc": {
                        "nome": "NPC",
                        "confrontos": 4,
                        "vitorias": 1,
                        "ultima_semana": 12,
                    }
                },
            ),
            adversario={
                "nome": "NPC",
                "energia": 100,
                "moral": 70,
                "ritmo_jogo": 50,
                "atributos": {
                    "saque": 70,
                    "voleio": 65,
                    "slice": 60,
                    "forehand": 68,
                    "backhand": 66,
                    "topspin": 63,
                    "movimento": 69,
                    "winner": 71,
                },
                "atributos_psicologicos": {
                    "agressividade": 67,
                    "leitura_de_jogo": 61,
                    "determinacao": 64,
                },
            },
            torneio_info={"nome": "Roma"},
            config=ConfigPartida(superficie="saibro"),
        )

        self.assertEqual(runtime.contexto_partida.momentum_j, 5)
        self.assertEqual(runtime.contexto_partida.moral_j, 75.0)
        self.assertIn("Partida de rival", runtime.log[0])

    def test_jogar_ponto_restaura_metodos_do_simulador_se_houver_excecao(self):
        runtime = self._runtime_base()
        runtime.simulador = types.SimpleNamespace(
            _get_psico_jogador=lambda: {"concentracao": 50},
            _get_psico_adversario=lambda: {"concentracao": 50},
            simular_ponto_rapido=lambda *args, **kwargs: (_ for _ in ()).throw(
                RuntimeError("falha")
            ),
        )
        runtime._contexto_ponto = lambda: types.SimpleNamespace()
        runtime.estrategia_j = {
            "estilo": "atacar_do_fundo",
            "saque": EstrategiaSaque.SEGURO,
            "saque_tipo": TipoSaque.VARIADO,
            "intencao": IntencaoPonto.PACIENTE,
        }
        runtime.modo = "manual"
        original_j = runtime.simulador._get_psico_jogador
        original_a = runtime.simulador._get_psico_adversario

        with self.assertRaises(RuntimeError):
            runtime.jogar_ponto()

        self.assertIs(runtime.simulador._get_psico_jogador, original_j)
        self.assertIs(runtime.simulador._get_psico_adversario, original_a)

    def test_runtime_escolhe_tipo_saque_do_sacador_atual(self):
        runtime = self._runtime_base()
        runtime.sacador = "a"
        runtime.estrategia_j = {
            "estilo": "atacar_do_fundo",
            "saque": EstrategiaSaque.FORCAR,
            "saque_tipo": TipoSaque.AGRESSIVO,
            "intencao": IntencaoPonto.ARRISCAR,
        }
        runtime.estrategia_a = {
            "estilo": "atacar_na_rede",
            "saque": EstrategiaSaque.SEGURO,
            "saque_tipo": TipoSaque.SEGURO,
            "intencao": IntencaoPonto.DEFENSIVO,
        }

        self.assertEqual(runtime._tipo_saque_do_sacador(), TipoSaque.SEGURO)

    def test_runtime_de_duplas_funde_parceiro_e_dupla_adversaria_no_motor(self):
        class RankingFake:
            def __init__(self, ranking):
                self.ranking = ranking

        ranking_fake = RankingFake(
            [
                {
                    "nome": "Parceiro Silva",
                    "nacionalidade": "[BR]",
                    "energia": 84,
                    "moral": 72,
                    "ritmo_jogo": 58,
                    "atributos": {
                        "saque": 68,
                        "forehand": 67,
                        "backhand": 65,
                        "topspin": 61,
                        "voleio": 82,
                        "slice": 63,
                        "movimento": 74,
                        "lob": 58,
                        "winner": 66,
                        "fisico": 71,
                        "duplas": 89,
                    },
                    "atributos_psicologicos": {
                        "concentracao": 68,
                        "agressividade": 64,
                        "leitura_de_jogo": 78,
                        "determinacao": 70,
                    },
                },
                {
                    "nome": "Rival One",
                    "nacionalidade": "[US]",
                    "energia": 79,
                    "moral": 70,
                    "ritmo_jogo": 56,
                    "atributos": {
                        "saque": 73,
                        "forehand": 71,
                        "backhand": 69,
                        "topspin": 66,
                        "voleio": 78,
                        "slice": 65,
                        "movimento": 72,
                        "lob": 60,
                        "winner": 72,
                        "fisico": 69,
                        "duplas": 84,
                    },
                    "atributos_psicologicos": {
                        "concentracao": 67,
                        "agressividade": 69,
                        "leitura_de_jogo": 73,
                        "determinacao": 68,
                    },
                },
                {
                    "nome": "Rival Two",
                    "nacionalidade": "[US]",
                    "energia": 77,
                    "moral": 69,
                    "ritmo_jogo": 55,
                    "atributos": {
                        "saque": 70,
                        "forehand": 72,
                        "backhand": 68,
                        "topspin": 65,
                        "voleio": 76,
                        "slice": 67,
                        "movimento": 71,
                        "lob": 59,
                        "winner": 70,
                        "fisico": 68,
                        "duplas": 83,
                    },
                    "atributos_psicologicos": {
                        "concentracao": 65,
                        "agressividade": 66,
                        "leitura_de_jogo": 72,
                        "determinacao": 69,
                    },
                },
            ]
        )

        with patch("src.utils.match_doubles_utils.load_singles_ranking", return_value=ranking_fake):
            runtime = self.MatchRuntime(
                partida_id="dbl1",
                save_name="save",
                modo="manual",
                jogador=types.SimpleNamespace(
                    nome="Alexandre Paiva",
                    genero="masculino",
                    tipo_duplas_atual="mesmo_genero",
                    parceiro_duplas={"nome": "Parceiro Silva", "nacionalidade": "[BR]"},
                    vinculos_dupla={"Parceiro Silva": {"partidas": 8, "vitorias": 6}},
                    energia=88,
                    moral=74,
                    ritmo_jogo=62,
                    atributos={
                        "saque": 72,
                        "forehand": 70,
                        "backhand": 68,
                        "topspin": 64,
                        "voleio": 80,
                        "slice": 62,
                        "movimento": 73,
                        "lob": 57,
                        "winner": 69,
                        "fisico": 70,
                        "duplas": 87,
                    },
                    atributos_psicologicos={
                        "concentracao": 71,
                        "agressividade": 63,
                        "leitura_de_jogo": 75,
                        "determinacao": 72,
                    },
                    rivalidades={},
                ),
                adversario={"nome": "Rival One / Rival Two"},
                torneio_info={"nome": "Roma"},
                config=ConfigPartida(superficie="dura"),
                modalidade="duplas",
            )

        self.assertTrue(runtime.simulador.jogador["is_dupla"])
        self.assertTrue(runtime.simulador.adversario["is_dupla"])
        self.assertEqual(runtime.simulador.jogador["quimica"]["label"], "Entrosada")
        self.assertEqual(runtime.contexto_partida.stamina_j, 84.0)
        self.assertEqual(runtime.contexto_partida.stamina_a, 77.0)
        self.assertEqual(len(runtime.adversario["jogadores"]), 2)


if __name__ == "__main__":
    unittest.main()
