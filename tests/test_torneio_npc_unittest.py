import random
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.torneio_npc import (
    limpar_nome_resultado,
    estimar_pontos_partida,
    estimar_games_partida,
    simular_partida_npc_basica,
)
from src.torneio_sim import simular_partida_npc


class TorneioNPCTests(unittest.TestCase):
    def test_limpar_nome_resultado_remove_sufixo_numerico(self):
        self.assertEqual(limpar_nome_resultado("Carlos Alcaraz 2"), "Carlos Alcaraz")
        self.assertEqual(
            limpar_nome_resultado("  Novak Djokovic99  "), "Novak Djokovic"
        )

    def test_estimativa_partida_best_of_3_respeita_intervalos(self):
        rng = random.Random(42)
        pontos = estimar_pontos_partida(best_of_sets=3, sets_d=1, rng=rng)
        games = estimar_games_partida(best_of_sets=3, sets_d=1, rng=rng)
        self.assertGreaterEqual(pontos, 102)
        self.assertLessEqual(pontos, 118)
        self.assertGreaterEqual(games, 18)
        self.assertLessEqual(games, 30)

    def test_estimativa_partida_best_of_5_respeita_intervalos(self):
        rng = random.Random(7)
        pontos = estimar_pontos_partida(best_of_sets=5, sets_d=2, rng=rng)
        games = estimar_games_partida(best_of_sets=5, sets_d=2, rng=rng)
        self.assertGreaterEqual(pontos, 180)
        self.assertLessEqual(pontos, 200)
        self.assertGreaterEqual(games, 30)
        self.assertLessEqual(games, 42)

    def test_simular_partida_npc_basica_formato_retorno(self):
        a = {"nome": "Jogador A 2"}
        b = {"nome": "Jogador B 1"}
        rng = random.Random(1)

        vencedor, perdedor, placar, pontos, games = simular_partida_npc_basica(
            a, b, best_of_sets=3, rng=rng
        )

        self.assertIn(vencedor, (a, b))
        self.assertIn(perdedor, (a, b))
        self.assertIsNot(vencedor, perdedor)
        self.assertNotIn("Jogador A 2 2 x", placar)
        self.assertNotIn("Jogador A 2 3 x", placar)
        self.assertNotIn("Jogador B 1", placar)
        self.assertIsInstance(pontos, int)
        self.assertGreater(pontos, 0)
        self.assertIsInstance(games, int)
        self.assertGreater(games, 0)

    def test_simular_partida_npc_repassa_superficie_e_usa_pontos_na_fadiga(self):
        torneio = SimpleNamespace(
            best_of_sets=3,
            tournament_data={"quadra": "saibro"},
            garantir_dados_completos=lambda jogador: jogador,
            _aplicar_fadiga_npc_por_nome=None,
            _aplicar_moral_npc_partida=lambda *_args: None,
        )
        chamadas_fadiga = []
        torneio._aplicar_fadiga_npc_por_nome = (
            lambda nome, carga: chamadas_fadiga.append((nome, carga))
        )

        with patch(
            "src.torneio_sim.simular_partida_npc_basica",
            return_value=(
                {"nome": "A"},
                {"nome": "B"},
                "A 2 x 1 B",
                123,
                28,
            ),
        ) as mock_basica:
            resultado = simular_partida_npc(
                torneio,
                {"nome": "A"},
                {"nome": "B"},
            )

        self.assertEqual(resultado["pontos_disputados"], 123)
        self.assertEqual(resultado["games_total"], 28)
        self.assertEqual(chamadas_fadiga, [("A", 123), ("B", 123)])
        self.assertEqual(mock_basica.call_args.kwargs["superficie"], "saibro")


if __name__ == "__main__":
    unittest.main()
