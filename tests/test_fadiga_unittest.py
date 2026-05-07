import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.fadiga import (
    _atualizar_status_lesao_por_risco,
    handle_fadiga_e_lesao,
    handle_fadiga_e_lesao_npc,
    recuperar_energia_entre_rodadas,
)


class FadigaTests(unittest.TestCase):
    def test_status_lesao_prioriza_gravidade_em_fadiga_extrema(self):
        with (
            patch("src.fadiga.random.random", return_value=0.0),
            patch("src.fadiga.random.randint", return_value=4),
        ):
            status, evento = _atualizar_status_lesao_por_risco(
                {"lesionado": False, "nivel": "saudavel", "semanas_restantes": 0},
                fadiga=95,
                energia_atual=20,
            )

        self.assertEqual(evento, "lesionado")
        self.assertTrue(status["lesionado"])
        self.assertEqual(status["nivel"], "lesionado")
        self.assertEqual(status["semanas_restantes"], 4)

    def test_handle_fadiga_e_lesao_ativa_ranking_protegido_quando_lesao_longa(self):
        jogador = SimpleNamespace(
            nome="Alexandre",
            fadiga=92,
            energia=18,
            status_lesao={},
            protected_ranking=None,
            protected_ranking_semanas=0,
        )
        ranking = SimpleNamespace(obter_posicao=lambda _nome: 37)

        with (
            patch("src.fadiga.random.random", return_value=0.0),
            patch("src.fadiga.random.randint", return_value=4),
        ):
            jogador, eventos = handle_fadiga_e_lesao(
                jogador,
                pontos_disputados=220,
                energia_perdida=40,
                ranking=ranking,
                return_eventos=True,
            )

        self.assertEqual(jogador.protected_ranking, 37)
        self.assertEqual(jogador.protected_ranking_semanas, 52)
        self.assertIn("ranking_protegido", [evento.tipo for evento in eventos])

    def test_handle_fadiga_e_lesao_npc_ativa_ranking_protegido(self):
        npc = {"fadiga": 92, "energia": 18, "status_lesao": {}}

        with (
            patch("src.fadiga.random.random", return_value=0.0),
            patch("src.fadiga.random.randint", return_value=5),
        ):
            resultado = handle_fadiga_e_lesao_npc(
                npc,
                pontos_disputados=220,
                energia_perdida=40,
                rank_atual=58,
            )

        self.assertEqual(resultado["protected_ranking"], 58)
        self.assertEqual(resultado["protected_ranking_semanas"], 52)

    def test_recuperar_energia_entre_rodadas_aceita_dict(self):
        jogador = {
            "atributos": {"fisico": 80},
            "fadiga": 25,
            "energia": 60,
            "status_lesao": {"lesionado": False, "nivel": "saudavel"},
            "equipe": [],
        }

        resultado, eventos = recuperar_energia_entre_rodadas(
            jogador, multiplicador=1.0, return_eventos=True
        )

        self.assertIs(resultado, jogador)
        self.assertGreater(jogador["energia"], 60)
        self.assertEqual(eventos[-1].tipo, "energia_recuperada")


if __name__ == "__main__":
    unittest.main()
