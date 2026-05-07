import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.ranking import SistemaRanking


class SistemaRankingSanitizacaoTests(unittest.TestCase):
    def test_ranking_simples_migra_pontos_de_duplas_gravados_no_campo_errado(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            singles_path = Path(tmpdir) / "singles_atp.json"

            singles_path.write_text(
                json.dumps(
                    [
                        {
                            "nome": "Carlos Alcaraz",
                            "nacionalidade": "[ES]",
                            "pontos": 13550,
                            "pontos_ranking": 13550,
                            "pontos_duplas": 0,
                            "pontos_ranking_duplas": 0,
                        },
                        {
                            "nome": "Neal Skupski",
                            "nacionalidade": "[RU] Rússia",
                            "pontos": 8280,
                            "pontos_ranking": 8280,
                            "pontos_duplas": 8280,
                            "pontos_ranking_duplas": 0,
                        },
                    ]
                ),
                encoding="utf-8",
            )

            ranking = SistemaRanking(str(singles_path), modalidade="simples")
            ranking.ordenar()

            self.assertEqual(ranking.ranking[0]["nome"], "Carlos Alcaraz")
            neal = next(j for j in ranking.ranking if j["nome"] == "Neal Skupski")
            self.assertEqual(neal["pontos"], 0)
            self.assertEqual(neal["pontos_ranking"], 0)
            self.assertEqual(neal["pontos_ranking_duplas"], 8280)

    @patch("src.ranking.carregar_npc_detalhado")
    def test_ranking_duplas_busca_nacionalidade_real_quando_feed_vem_corrompido(self, mock_carregar_npc):
        mock_carregar_npc.return_value = {"nacionalidade": "[GB] Grã-Bretanha"}
        with tempfile.TemporaryDirectory() as tmpdir:
            doubles_path = Path(tmpdir) / "doubles_atp.json"
            doubles_path.write_text(
                json.dumps(
                    [
                        {
                            "rank_duplas": idx + 1,
                            "nome": f"Jogador {idx}",
                            "pais3": "RUS",
                            "pontos_duplas": 1000 - idx,
                        }
                        for idx in range(25)
                    ]
                ),
                encoding="utf-8",
            )

            ranking = SistemaRanking(str(doubles_path), modalidade="duplas")
            jogador = ranking.ranking[0]

            self.assertEqual(jogador["nacionalidade"], "[GB] Grã-Bretanha")


if __name__ == "__main__":
    unittest.main()
