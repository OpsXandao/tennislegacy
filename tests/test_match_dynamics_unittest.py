import unittest

from src.match_dynamics import (
    atualizar_momentum_contextual,
    aplicar_custo_stamina_contextual,
    calcular_stamina_pos_recuperacao,
)
from src.superficie_utils import normalizar_superficie


class MatchDynamicsTests(unittest.TestCase):
    def test_normalizar_superficie(self):
        self.assertEqual(normalizar_superficie("hard"), "dura")
        self.assertEqual(normalizar_superficie("terra"), "saibro")
        self.assertEqual(normalizar_superficie("grass"), "grama")
        self.assertEqual(normalizar_superficie("desconhecida"), "dura")

    def test_atualizar_momentum_contextual_aplica_pressao_e_sequencia(self):
        resultado = atualizar_momentum_contextual(
            momentum_j=2,
            momentum_a=3,
            sequencia_j=2,
            sequencia_a=0,
            ultimo_vencedor="j",
            vencedor="j",
            is_match_point=False,
            is_set_point=False,
            is_break_point=True,
            is_tiebreak=False,
            jogador_perdendo=True,
            adversario_perdendo=False,
            pj=3,
            pa=2,
        )

        momentum_j, momentum_a, sequencia_j, sequencia_a, ultimo = resultado
        self.assertEqual(sequencia_j, 3)
        self.assertEqual(sequencia_a, 0)
        self.assertEqual(ultimo, "j")
        self.assertGreater(momentum_j, 2)
        self.assertLess(momentum_a, 3)

    def test_aplicar_custo_stamina_contextual_reduz_stamina(self):
        nova_j, nova_a = aplicar_custo_stamina_contextual(
            stamina_j=100.0,
            stamina_a=100.0,
            stats_info={"intensidade": "longo", "winner": True},
            superficie="saibro",
            clima="quente",
            umidade=80,
            contexto_flags={
                "is_break_point": True,
                "is_set_point": False,
                "is_match_point": False,
            },
            atributos_j={"fisico": 60, "movimento": 70, "topspin": 65},
            atributos_a={"fisico": 55, "movimento": 60, "topspin": 58},
            psico_j={"agressividade": 55},
            psico_a={"agressividade": 50},
            estrategia_j={"estilo": "atacar_do_fundo"},
            estrategia_a={"estilo": "atacar_na_rede"},
        )

        self.assertGreaterEqual(nova_j, 0.0)
        self.assertGreaterEqual(nova_a, 0.0)
        self.assertLess(nova_j, 100.0)
        self.assertLess(nova_a, 100.0)

    def test_calcular_stamina_pos_recuperacao_limita_ate_100(self):
        recuperada = calcular_stamina_pos_recuperacao(
            stamina=99.8,
            fisico=95,
            indoor=False,
            clima="ameno",
            umidade=50,
        )
        self.assertLessEqual(recuperada, 100.0)
        self.assertGreater(recuperada, 99.8)


if __name__ == "__main__":
    unittest.main()
