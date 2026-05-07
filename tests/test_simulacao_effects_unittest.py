import unittest

from src.simulacao_effects import (
    multiplicador_lesao,
    multiplicador_doenca,
    aplicar_saude_nos_atributos,
    calcular_mod_ambiente,
)


class SimulacaoEffectsTests(unittest.TestCase):
    def test_multiplicador_lesao_default_lesionado(self):
        status = {"lesionado": True, "nivel": "grave", "penalidade_atributos": 0.0}
        self.assertAlmostEqual(multiplicador_lesao(status), 0.82)

    def test_multiplicador_doenca_por_nivel(self):
        leve = {"doente": True, "nivel": "leve", "penalidade_atributos": 0.0}
        grave = {"doente": True, "nivel": "grave", "penalidade_atributos": 0.0}
        self.assertGreater(multiplicador_doenca(leve), multiplicador_doenca(grave))

    def test_aplicar_saude_nos_atributos_combina_penalidades(self):
        atributos = {"saque": 80.0, "movimento": 70.0}
        lesionado = {"lesionado": True, "penalidade_atributos": 0.10}
        doente = {"doente": True, "nivel": "moderada", "penalidade_atributos": 0.0}

        ajustados = aplicar_saude_nos_atributos(atributos, lesionado, doente)

        self.assertLess(ajustados["saque"], atributos["saque"])
        self.assertLess(ajustados["movimento"], atributos["movimento"])

    def test_calcular_mod_ambiente_retorna_intervalos_validos(self):
        mod = calcular_mod_ambiente(
            clima="chuvoso",
            vento=30,
            umidade=85,
            altitude_m=1500,
            indoor=False,
        )

        self.assertGreaterEqual(mod["saque"], 0.86)
        self.assertLessEqual(mod["saque"], 1.18)
        self.assertGreaterEqual(mod["ace"], 0.7)
        self.assertLessEqual(mod["ace"], 1.25)
        self.assertGreaterEqual(mod["falta"], 0.82)
        self.assertLessEqual(mod["falta"], 1.35)
        self.assertGreaterEqual(mod["rally"], 0.86)
        self.assertLessEqual(mod["rally"], 1.12)
        self.assertGreaterEqual(mod["erro"], 0.86)
        self.assertLessEqual(mod["erro"], 1.25)


if __name__ == "__main__":
    unittest.main()
