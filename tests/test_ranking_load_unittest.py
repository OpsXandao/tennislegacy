import json
import os
import tempfile
import unittest
from unittest.mock import patch

from src.player_ratings import ajustar_atributo_duplas, calcular_overall_contextual
from src.ranking import SistemaRanking


class RankingLoadTests(unittest.TestCase):
    def test_overall_contextual_respeita_ranking_de_elite(self):
        jogador = {
            "nome": "Top Player",
            "pontos_ranking": 9350,
            "atributos": {
                "saque": 78,
                "forehand": 81,
                "backhand": 79,
                "topspin": 76,
                "voleio": 72,
                "slice": 74,
                "movimento": 80,
                "lob": 70,
                "fisico": 79,
                "winner": 78,
                "duplas": 62,
            },
        }

        overall = calcular_overall_contextual(jogador, ranking_pos=7)
        self.assertGreaterEqual(overall, 87)

    def test_ajustar_duplas_cria_atributo_com_base_no_ranking_de_duplas(self):
        jogador = {
            "nome": "Doubles Specialist",
            "pontos_duplas": 2800,
            "atributos": {
                "saque": 70,
                "forehand": 69,
                "backhand": 72,
            },
        }

        mudou = ajustar_atributo_duplas(jogador)

        self.assertTrue(mudou)
        self.assertIn("duplas", jogador["atributos"])
        self.assertGreaterEqual(jogador["atributos"]["duplas"], 89)

    def test_carga_nao_persiste_reparos_automaticamente(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump([{"nome": "Jogador Teste"}], tmp)
            caminho = tmp.name

        try:
            with patch("src.ranking.get_caminho_ranking_global", return_value="/tmp/inexistente"):
                ranking = SistemaRanking(caminho)

            self.assertTrue(ranking._mudou_na_carga)
            self.assertTrue(ranking.tem_reparos_pendentes)
            with open(caminho, "r", encoding="utf-8") as f:
                salvo = json.load(f)
            self.assertEqual(salvo, [{"nome": "Jogador Teste"}])
        finally:
            if os.path.exists(caminho):
                os.remove(caminho)


if __name__ == "__main__":
    unittest.main()
