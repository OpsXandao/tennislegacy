import unittest
from types import SimpleNamespace

from fastapi import HTTPException

from src.services import tournament_service


class TournamentServiceTests(unittest.TestCase):
    def test_destino_click_hub_por_tipo_retorna_davis_para_competicao_equipes(self):
        self.assertEqual(
            tournament_service._destino_click_hub_por_tipo("Davis Cup"), "/davis"
        )
        self.assertEqual(
            tournament_service._destino_click_hub_por_tipo("ATP 250"), "/tournament"
        )

    def test_estado_torneio_ativo_na_semana_ignora_finalizado(self):
        self.assertTrue(
            tournament_service._estado_torneio_ativo_na_semana(
                {"semana": 10, "fase_atual": "r32"}, 10
            )
        )
        self.assertFalse(
            tournament_service._estado_torneio_ativo_na_semana(
                {"semana": 10, "fase_atual": "finalizado"}, 10
            )
        )

    def test_configurar_modalidade_jogador_define_mistas_com_tipo_mista(self):
        jogador = SimpleNamespace(modalidade_atual="simples", tipo_duplas_atual=None)

        modalidade = tournament_service._configurar_modalidade_jogador(
            jogador, "mistas"
        )

        self.assertEqual(modalidade, "mistas")
        self.assertEqual(jogador.modalidade_atual, "duplas")
        self.assertEqual(jogador.tipo_duplas_atual, "mista")

    def test_configurar_modalidade_jogador_rejeita_modalidade_invalida(self):
        jogador = SimpleNamespace(modalidade_atual="simples", tipo_duplas_atual=None)

        with self.assertRaises(HTTPException):
            tournament_service._configurar_modalidade_jogador(jogador, "tripla")

    def test_enriquecer_adversario_info_calcula_overall_e_ranking(self):
        ranking = SimpleNamespace(obter_posicao=lambda nome: 18)
        instancia = SimpleNamespace(
            ranking=ranking,
            garantir_dados_completos=lambda adv: {
                "nome": adv["nome"],
                "atributos": {"saque": 70, "forehand": 80},
                "atributos_psicologicos": {"foco": 60, "confianca": 50},
            },
        )

        info = tournament_service._enriquecer_adversario_info(
            instancia, {"nome": "Bruno Costa"}
        )

        self.assertEqual(info["ranking_pos"], 18)
        self.assertIn("overall", info)

    def test_montar_partida_pendente_regular_retorna_confronto_do_jogador(self):
        instancia = SimpleNamespace(
            ranking=SimpleNamespace(obter_posicao=lambda nome: 25),
            garantir_dados_completos=lambda adv: adv,
        )
        state = {
            "fase_atual": "r32",
            "estado": {
                "jogador": "Alexandre",
                "rodadas": {
                    "r32": [
                        (
                            {"nome": "Alexandre"},
                            {"nome": "Bruno Costa", "atributos": {}, "atributos_psicologicos": {}},
                        )
                    ]
                },
            },
        }

        partida = tournament_service._montar_partida_pendente_regular(instancia, state)

        self.assertEqual(partida["fase"], "r32")
        self.assertEqual(partida["adversario"]["nome"], "Bruno Costa")


if __name__ == "__main__":
    unittest.main()
