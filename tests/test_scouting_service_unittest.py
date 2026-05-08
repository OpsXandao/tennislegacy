import unittest

from src.services.scouting_service import (
    calcular_metricas_scouting,
    detectar_superficie_favorita,
    montar_relatorio_scouting,
)


class ScoutingServiceTests(unittest.TestCase):
    def test_calcular_metricas_scouting_combina_resumo_e_psicologico(self):
        metricas = calcular_metricas_scouting(
            atributos={
                "saque": 70,
                "forehand": 82,
                "backhand": 76,
                "movimento": 74,
                "winner": 80,
                "voleio": 66,
            },
            atributos_psicologicos={
                "concentracao": 72,
                "determinacao": 78,
                "leitura_de_jogo": 75,
            },
            resumo_fifa={"SAQ": 84, "FOR": 80, "BAC": 78, "MOV": 76},
        )

        self.assertEqual(metricas["saque"], 84)
        self.assertEqual(metricas["fundo"], 78)
        self.assertEqual(metricas["mental"], 75)

    def test_detectar_superficie_favorita_identifica_grama(self):
        superficie = detectar_superficie_favorita(
            {
                "saque": 80,
                "voleio": 77,
                "topspin": 40,
                "slice": 45,
                "forehand": 65,
                "backhand": 67,
            }
        )

        self.assertEqual(superficie, "Grass")

    def test_montar_relatorio_scouting_destaca_forcas_e_fraquezas(self):
        relatorio = montar_relatorio_scouting(
            {
                "nome": "Rival Teste",
                "energia": 54,
                "atributos": {
                    "saque": 84,
                    "forehand": 82,
                    "backhand": 75,
                    "movimento": 55,
                    "winner": 83,
                    "voleio": 78,
                    "topspin": 52,
                    "slice": 60,
                },
                "atributos_psicologicos": {
                    "agressividade": 76,
                    "concentracao": 79,
                    "determinacao": 48,
                    "leitura_de_jogo": 61,
                },
                "resumo_fifa": {"SAQ": 86, "FOR": 81, "BAC": 74, "MOV": 55},
            },
            superficie="grama",
        )

        self.assertEqual(relatorio["superficie_favorita"], "Grass")
        self.assertIn("CANHÃO DE SAQUE", relatorio["pontos_fortes"])
        self.assertIn("MOBILIDADE REDUZIDA", relatorio["fraquezas"])
        self.assertTrue(relatorio["dicas"])
        self.assertIn("Rival Teste", relatorio["texto"])


if __name__ == "__main__":
    unittest.main()
