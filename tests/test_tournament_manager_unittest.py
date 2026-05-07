import unittest
import types
import sys
from unittest.mock import patch

if "colorama" not in sys.modules:
    colorama_stub = types.SimpleNamespace(
        init=lambda *args, **kwargs: None,
        Fore=types.SimpleNamespace(
            RED="", GREEN="", BLUE="", YELLOW="", MAGENTA="", CYAN="", WHITE=""
        ),
        Style=types.SimpleNamespace(RESET_ALL="", BRIGHT=""),
    )
    sys.modules["colorama"] = colorama_stub

from src.tournament_manager import WeekTournamentManager, fases_por_tipo_torneio


class WeekTournamentManagerTests(unittest.TestCase):
    def test_init_usa_caminho_atual_de_ranking_do_save(self):
        with (
            patch("src.tournament_manager.os.makedirs"),
            patch(
                "src.tournament_manager.get_caminho_ranking_save",
                return_value="/tmp/rankings/singles_atp.json",
            ) as mock_path,
            patch("src.tournament_manager.SistemaRanking") as mock_ranking,
        ):
            mock_ranking.return_value.ranking = [{}]
            WeekTournamentManager("save_teste", 3, genero="masculino")

        mock_path.assert_called_once_with("save_teste", genero="masculino")
        mock_ranking.assert_called_once_with("/tmp/rankings/singles_atp.json")

    def test_fases_por_tipo_torneio_suporta_circuito_challenger_e_itf(self):
        self.assertEqual(
            fases_por_tipo_torneio("Challenger 125"),
            (["r32", "r16", "quartas", "semifinal", "final"], 32),
        )
        self.assertEqual(
            fases_por_tipo_torneio("ITF 100"),
            (["r32", "r16", "quartas", "semifinal", "final"], 32),
        )

    def test_obter_resumo_semanal_extrai_campeao_do_resultado_final(self):
        manager = WeekTournamentManager.__new__(WeekTournamentManager)
        manager.semana = 1
        manager.torneios = {
            "Brisbane International": {
                "fase_atual": "finalizado",
                "semana": 1,
                "tournament_data": {"tipo": "ATP 250"},
                "resultados": {"final": [{"vencedor": {"nome": "Tomas Machac"}}]},
            }
        }

        resumo = manager.obter_resumo_semanal()

        self.assertEqual(resumo[0]["campeao"], "Tomas Machac")

    def test_obter_resumo_semanal_nao_retorna_placeholder_como_campeao(self):
        manager = WeekTournamentManager.__new__(WeekTournamentManager)
        manager.semana = 1
        manager.torneios = {
            "Evento Teste": {
                "fase_atual": "finalizado",
                "semana": 1,
                "tournament_data": {"tipo": "ATP 250"},
                "campeao_simples": "---",
                "resultados": {"final": []},
            }
        }

        resumo = manager.obter_resumo_semanal()

        self.assertIsNone(resumo[0]["campeao"])

    def test_obter_resumo_semanal_filtra_torneios_de_outra_semana(self):
        manager = WeekTournamentManager.__new__(WeekTournamentManager)
        manager.semana = 3
        manager.torneios = {
            "Semana 2": {
                "fase_atual": "finalizado",
                "semana": 2,
                "tournament_data": {"tipo": "ATP 250"},
                "resultados": {"final": [{"vencedor": {"nome": "Jogador X"}}]},
            },
            "Semana 3": {
                "fase_atual": "finalizado",
                "semana": 3,
                "tournament_data": {"tipo": "ATP 250"},
                "resultados": {"final": [{"vencedor": {"nome": "Jogador Y"}}]},
            },
        }

        resumo = manager.obter_resumo_semanal()

        self.assertEqual(len(resumo), 1)
        self.assertEqual(resumo[0]["nome"], "Semana 3")


if __name__ == "__main__":
    unittest.main()
