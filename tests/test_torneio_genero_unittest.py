import unittest
from unittest.mock import patch

from src.torneio import Torneio, salvar_torneio


class RankingDummy:
    def obter_posicao(self, _nome):
        return 1


class TorneioGeneroTests(unittest.TestCase):
    def _novo_torneio_stub(self):
        torneio = Torneio.__new__(Torneio)
        torneio.nome_save = "save_wta"
        torneio.genero = "feminino"
        torneio.jogador_nome = "Jogadora A"
        torneio.caminho_json = "/tmp/torneio_wta.json"
        torneio.ranking = RankingDummy()
        torneio._perfil = {"merge_transitions": set(), "vagas_qualy": 2}
        torneio._atualizar_fase_se_necessario = lambda _estado: None
        return torneio

    def test_remover_confronto_carrega_estado_com_genero(self):
        torneio = self._novo_torneio_stub()
        estado = {"rodadas": {"r16": [("Jogadora A", "Jogadora B")]}}

        with (
            patch(
                "src.torneio_core.carregar_estado_torneio", return_value=estado
            ) as mock_carregar,
            patch("src.torneio_core.salvar_json_seguro"),
        ):
            torneio.remover_confronto_do_jogador("r16", "Jogadora A")

        mock_carregar.assert_called_once_with(torneio.nome_save, genero=torneio.genero)

    def test_processar_resultado_partida_persiste_com_genero(self):
        torneio = self._novo_torneio_stub()
        estado = {
            "fase_atual": "r16",
            "rodadas": {"r16": [("Jogadora A", "Jogadora B")]},
            "resultados": {},
        }

        with (
            patch(
                "src.torneio_core.get_caminho_torneio_save",
                return_value="/tmp/torneio_wta.json",
            ) as mock_caminho,
            patch(
                "src.torneio_core.carregar_estado_torneio", return_value=estado
            ) as mock_carregar,
            patch("src.torneio_core.salvar_json_seguro"),
        ):
            torneio.processar_resultado_partida(
                {"nome": "Jogadora A"},
                {"nome": "Jogadora B"},
                {"nome": "Jogadora A"},
                "Jogadora A: 6-4 6-4",
            )

        mock_caminho.assert_called_once_with(torneio.nome_save, genero=torneio.genero)
        mock_carregar.assert_called_once_with(torneio.nome_save, genero=torneio.genero)

    def test_processar_resultado_partida_avanca_fase_e_mantem_jogadora_viva(self):
        torneio = self._novo_torneio_stub()
        torneio.garantir_dados_completos = lambda item: (
            item
            if isinstance(item, dict)
            else {"nome": getattr(item, "nome", str(item))}
        )
        estado = {
            "fase_atual": "qualy_1",
            "jogador_vivo": True,
            "rodadas": {
                "qualy_1": [({"nome": "Jogadora A"}, {"nome": "Jogadora B"})],
                "qualy_2": [],
            },
            "resultados": {
                "qualy_1": [
                    {
                        "jogador_a": {"nome": "NPC 1"},
                        "jogador_b": {"nome": "NPC 2"},
                        "vencedor": {"nome": "NPC 1"},
                        "resultado": "NPC 1 2 x 0 NPC 2",
                    }
                ]
            },
        }

        torneio._atualizar_fase_se_necessario = (
            Torneio._atualizar_fase_se_necessario.__get__(torneio, Torneio)
        )
        torneio._fases_ordem = lambda: ["qualy_1", "qualy_2", "final"]

        with (
            patch(
                "src.torneio_core.get_caminho_torneio_save",
                return_value="/tmp/torneio_wta.json",
            ),
            patch("src.torneio_core.carregar_estado_torneio", return_value=estado),
            patch("src.torneio_core.salvar_json_seguro"),
        ):
            torneio.processar_resultado_partida(
                {"nome": "Jogadora A"},
                {"nome": "Jogadora B"},
                {"nome": "Jogadora A"},
                "Jogadora A 2 x 0 Jogadora B",
            )

        self.assertTrue(estado["jogador_vivo"])
        self.assertEqual(estado["fase_atual"], "qualy_2")
        self.assertEqual(
            estado["rodadas"]["qualy_2"],
            [({"nome": "NPC 1"}, {"nome": "Jogadora A"})],
        )

    def test_processar_resultado_partida_marca_eliminacao_quando_jogadora_perde(self):
        torneio = self._novo_torneio_stub()
        torneio.garantir_dados_completos = lambda item: (
            item
            if isinstance(item, dict)
            else {"nome": getattr(item, "nome", str(item))}
        )
        estado = {
            "fase_atual": "r16",
            "jogador_vivo": True,
            "rodadas": {"r16": [({"nome": "Jogadora A"}, {"nome": "Jogadora B"})]},
            "resultados": {},
        }

        torneio._atualizar_fase_se_necessario = lambda _estado: None

        with (
            patch(
                "src.torneio_core.get_caminho_torneio_save",
                return_value="/tmp/torneio_wta.json",
            ),
            patch("src.torneio_core.carregar_estado_torneio", return_value=estado),
            patch("src.torneio_core.salvar_json_seguro"),
        ):
            torneio.processar_resultado_partida(
                {"nome": "Jogadora A"},
                {"nome": "Jogadora B"},
                {"nome": "Jogadora B"},
                "Jogadora B 2 x 0 Jogadora A",
            )

        self.assertFalse(estado["jogador_vivo"])

    def test_salvar_torneio_persiste_no_arquivo_do_genero(self):
        torneio = self._novo_torneio_stub()
        torneio._carregar_estado = lambda: {"fase_atual": "r16"}

        with (
            patch(
                "src.torneio.get_caminho_torneio_save",
                return_value="/tmp/torneio_wta.json",
            ) as mock_caminho,
            patch("src.torneio.salvar_json_seguro"),
        ):
            salvar_torneio(torneio)

        mock_caminho.assert_called_once_with(torneio.nome_save, genero=torneio.genero)


if __name__ == "__main__":
    unittest.main()
