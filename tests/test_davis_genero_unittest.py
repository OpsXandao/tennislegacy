import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.davis_cup import DavisCup, carregar_davis_cup, criar_torneio_davis


class DavisGeneroTests(unittest.TestCase):
    def test_davis_cup_init_define_caminho_com_genero(self):
        jogador = SimpleNamespace(genero="feminino", nacionalidade="BRA")
        ranking = object()

        with patch(
            "src.davis_cup.get_caminho_torneio_save",
            return_value="/tmp/torneio_wta.json",
        ) as mock_caminho:
            davis = DavisCup(
                tournament_data={"nome": "Billie Jean King Cup"},
                jogador=jogador,
                ranking=ranking,
                nome_save="save_wta",
            )

        self.assertEqual(davis.genero, "feminino")
        mock_caminho.assert_called_once_with("save_wta", genero="feminino")

    def test_carregar_davis_cup_consulta_estado_e_ranking_com_genero(self):
        jogador = SimpleNamespace(genero="feminino", nacionalidade="BRA")

        with patch(
            "src.davis_cup.carregar_estado_torneio",
            return_value={
                "tipo": "Davis Cup",
                "tournament_data": {"nome": "Copa Davis"},
            },
        ) as mock_estado, patch(
            "src.davis_cup.get_caminho_ranking_save",
            return_value="/tmp/ranking_wta.json",
        ) as mock_ranking_path, patch(
            "src.davis_cup.SistemaRanking", return_value=object()
        ), patch(
            "src.davis_cup.DavisCup", return_value="DAVIS"
        ) as mock_davis:
            resultado = carregar_davis_cup("save_wta", jogador)

        self.assertEqual(resultado, "DAVIS")
        mock_estado.assert_called_once_with("save_wta", genero="feminino")
        mock_ranking_path.assert_called_once_with("save_wta", genero="feminino")
        self.assertTrue(mock_davis.called)

    def test_criar_torneio_davis_carrega_ranking_do_genero(self):
        jogador = SimpleNamespace(genero="feminino", nacionalidade="BRA")
        davis_fake = SimpleNamespace(processar_convocacao=lambda: False)

        with patch(
            "src.davis_cup.get_caminho_ranking_save",
            return_value="/tmp/ranking_wta.json",
        ) as mock_ranking_path, patch(
            "src.davis_cup.SistemaRanking", return_value=object()
        ), patch(
            "src.calendario.carregar_temporada", return_value={"ano": 2026}
        ), patch(
            "src.davis_cup.DavisCup", return_value=davis_fake
        ), patch(
            "src.davis_cup.salvar_jogo"
        ):
            resultado = criar_torneio_davis(
                {"nome": "Billie Jean King Cup"},
                jogador,
                "save_wta",
                10,
            )

        self.assertIsNone(resultado)
        mock_ranking_path.assert_called_once_with("save_wta", genero="feminino")

    def test_criar_torneio_davis_persiste_convocacao_no_estado(self):
        jogador = SimpleNamespace(genero="feminino", nacionalidade="[BR] Brasil")
        estado = {"selecoes": {}, "tipo": "Billie Jean King Cup"}
        selecao = SimpleNamespace(
            pais="[BR] Brasil",
            capitao="Capitã",
            convocados=[{"nome": "Jogadora Principal", "e_jogador_principal": True}],
        )

        def _persistir_convocacao(estado_in):
            estado_in["selecoes"]["[BR] Brasil"] = {
                "capitao": "Capitã",
                "convocados": selecao.convocados,
            }
            return estado_in

        davis_fake = SimpleNamespace(
            processar_convocacao=lambda interactive=True: True,
            _carregar_estado=lambda: estado,
            _persistir_convocacao_no_estado=_persistir_convocacao,
            _salvar_estado=lambda estado_in: None,
            selecao=selecao,
        )

        with patch(
            "src.davis_cup.get_caminho_ranking_save",
            return_value="/tmp/ranking_wta.json",
        ), patch(
            "src.davis_cup.SistemaRanking", return_value=object()
        ), patch(
            "src.calendario.carregar_temporada", return_value={"ano": 2026}
        ), patch(
            "src.davis_cup.DavisCup", return_value=davis_fake
        ), patch(
            "src.davis_cup.salvar_jogo"
        ):
            criar_torneio_davis(
                {"nome": "Billie Jean King Cup"},
                jogador,
                "save_wta",
                10,
                interactive=False,
            )

        self.assertIn("[BR] Brasil", estado["selecoes"])
        self.assertEqual(estado["posicao_convocacao"], 1)
        self.assertTrue(estado["jogador_convocado"])

    def test_criar_estado_inicial_repassa_genero_para_selecoes(self):
        jogador = SimpleNamespace(
            genero="feminino",
            nacionalidade="[BR] Brasil",
            nome="Jogadora Principal",
        )
        ranking = SimpleNamespace(ranking=[])

        with patch(
            "src.davis_cup.get_caminho_torneio_save",
            return_value="/tmp/torneio_wta.json",
        ), patch(
            "src.davis_cup.SelecaoNacional"
        ) as mock_selecao:
            mock_selecao.return_value = SimpleNamespace(
                completar_convocacao=lambda *_args, **_kwargs: None,
                capitao="Capitã",
                convocados=[],
                pais="[BR] Brasil",
            )
            davis = DavisCup(
                tournament_data={
                    "nome": "Billie Jean King Cup - Final 8",
                    "tipo": "Billie Jean King Cup",
                },
                jogador=jogador,
                ranking=ranking,
                nome_save="save_wta",
            )
            davis._criar_estado_inicial()

        self.assertTrue(mock_selecao.called)
        for call in mock_selecao.call_args_list:
            self.assertEqual(call.kwargs["genero"], "feminino")

    def test_obter_confronto_jogador_usa_superficie_oficial_do_tie(self):
        jogador = SimpleNamespace(
            genero="feminino",
            nacionalidade="[BR] Brasil",
            nome="Jogadora Principal",
        )
        ranking = SimpleNamespace(ranking=[])

        class SelecaoFake:
            def __init__(self, pais, ranking, genero="masculino"):
                self.pais = pais
                self.genero = genero
                self.convocados = [
                    {"nome": "Jogadora Principal"},
                    {"nome": "Outra Jogadora"},
                    {"nome": "Reserva"},
                ]

            def completar_convocacao(self, *_args, **_kwargs):
                return None

        estado = {
            "jogador_convocado": True,
            "confronto_atual": {"equipe_a": "[BR] Brasil", "equipe_b": "[FR] França"},
            "pais_jogador": "[BR] Brasil",
            "posicao_convocacao": 2,
            "partida_atual": 1,
            "fase_atual": "quartas",
            "modo_competicao": "final8",
        }

        with patch(
            "src.davis_cup.get_caminho_torneio_save",
            return_value="/tmp/torneio_wta.json",
        ), patch(
            "src.davis_cup.SelecaoNacional", SelecaoFake
        ):
            davis = DavisCup(
                tournament_data={
                    "nome": "Billie Jean King Cup - Final 8",
                    "tipo": "Billie Jean King Cup",
                    "superficie": "Clay",
                },
                jogador=jogador,
                ranking=ranking,
                nome_save="save_wta",
            )
            davis._carregar_estado = lambda: estado
            confronto = davis.obter_confronto_jogador()

        self.assertEqual(confronto["superficie"], "Hard (i)")


if __name__ == "__main__":
    unittest.main()
