import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.repositories import tournament_repository
from src.services import player_context_service
import src.torneio as torneio_module


class TournamentRepositoryTests(unittest.TestCase):
    def test_load_regular_tournament_hidrata_instancia_com_estado_existente(self):
        jogador = SimpleNamespace(nome="Alexandre", nacionalidade="BRA")
        estado = {
            "jogador": "Alexandre",
            "torneio": "Miami Open",
            "tipo": "Masters 1000",
            "semana": 12,
        }
        ranking_fake = object()
        instancia_fake = SimpleNamespace(caminho_json=None)

        with (
            patch.object(
                tournament_repository,
                "load_tournament_state",
                side_effect=[estado, None],
            ),
            patch.object(
                tournament_repository, "carregar_jogador", return_value=jogador
            ),
            patch.object(
                tournament_repository,
                "get_caminho_ranking_save",
                return_value="/tmp/ranking.json",
            ),
            patch.object(
                tournament_repository,
                "SistemaRanking",
                return_value=ranking_fake,
            ) as mock_ranking,
            patch.object(
                tournament_repository,
                "get_caminho_torneio_save",
                return_value="/tmp/torneio.json",
            ),
            patch.object(
                tournament_repository,
                "Torneio",
                return_value=instancia_fake,
            ) as mock_torneio,
        ):
            instancia = tournament_repository.load_regular_tournament("save_teste")

        self.assertIs(instancia, instancia_fake)
        mock_ranking.assert_called_once_with("/tmp/ranking.json", modalidade="simples")
        mock_torneio.assert_called_once_with(
            {"nome": "Miami Open", "tipo": "Masters 1000", "semana": 12},
            "Alexandre",
            "BRA",
            ranking_fake,
            nome_save="save_teste",
            genero="masculino",
        )
        self.assertEqual(instancia_fake.caminho_json, "/tmp/torneio.json")

    def test_carregar_torneio_delega_para_repository(self):
        instancia_fake = object()

        with patch.object(
            torneio_module,
            "load_regular_tournament",
            return_value=instancia_fake,
        ) as mock_load:
            instancia = torneio_module.carregar_torneio("save_teste", genero="feminino")

        self.assertIs(instancia, instancia_fake)
        mock_load.assert_called_once_with("save_teste", genero="feminino")

    def test_carregar_torneio_api_consulta_torneio_regular_antes_de_davis(self):
        instancia_fake = object()

        with (
            patch.object(
                player_context_service,
                "load_regular_tournament",
                return_value=instancia_fake,
            ) as mock_load,
            patch.object(player_context_service, "carregar_jogador") as mock_jogador,
        ):
            instancia = player_context_service.carregar_torneio_api("save_teste")

        self.assertIs(instancia, instancia_fake)
        mock_load.assert_called_once_with("save_teste")
        mock_jogador.assert_not_called()

    def test_extrair_nome_puro_preserva_formato_legado_de_resultado_dict(self):
        nome = torneio_module.extrair_nome_puro(
            {
                "vencedor": {"nome": "Alexandre Paiva"},
                "resultado": "6/4 6/3",
            }
        )

        self.assertEqual(nome, "Alexandre Paiva")

    def test_extrair_nome_puro_preserva_formato_legado_de_string(self):
        nome = torneio_module.extrair_nome_puro("Alexandre Paiva 2 x 1 Bruno Costa")

        self.assertEqual(nome, "Alexandre Paiva")

    def test_simular_partidas_npc_aceita_nome_jogador_explicito_por_compatibilidade(self):
        torneio_fake = SimpleNamespace(
            jogador_nome="Jogador Padrao",
            simular_npcs_na_fase_atual=lambda nome: chamadas.append(nome),
        )
        chamadas = []

        torneio_module.simular_partidas_npc(torneio_fake, nome_jogador="Outro Jogador")

        self.assertEqual(chamadas, ["Outro Jogador"])


if __name__ == "__main__":
    unittest.main()
