import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.services import player_context_service


class PlayerContextServiceTests(unittest.TestCase):
    def test_genero_oposto_inverte_genero(self):
        self.assertEqual(player_context_service._genero_oposto("masculino"), "feminino")
        self.assertEqual(player_context_service._genero_oposto("feminino"), "masculino")

    def test_carregar_torneio_api_faz_fallback_para_davis_genero_alternativo(self):
        jogador = SimpleNamespace(
            nome="Alexandre",
            idade=25,
            nacionalidade="BRA",
            genero="masculino",
        )
        davis_fake = object()

        with (
            patch.object(
                player_context_service, "load_regular_tournament", return_value=None
            ),
            patch.object(
                player_context_service, "carregar_jogador", return_value=jogador
            ),
            patch.object(
                player_context_service,
                "_carregar_davis_do_jogador",
                side_effect=[None, davis_fake],
            ) as mock_carregar_davis,
            patch.object(
                player_context_service,
                "_criar_jogador_genero_alternativo",
                return_value=SimpleNamespace(genero="feminino"),
            ) as mock_criar_outro,
        ):
            instancia = player_context_service.carregar_torneio_api("save_teste")

        self.assertIs(instancia, davis_fake)
        mock_criar_outro.assert_called_once_with(jogador, "save_teste")
        self.assertEqual(mock_carregar_davis.call_count, 2)


if __name__ == "__main__":
    unittest.main()
