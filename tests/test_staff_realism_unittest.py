import unittest
from types import SimpleNamespace

from src.progressao import treinar_semana
from src.services.staff_realism_service import training_fit_summary, weekly_recovery_bonus


class StaffRealismTests(unittest.TestCase):
    def test_treino_invalido_nao_consume_recursos(self):
        jogador = SimpleNamespace(
            energia=100,
            fadiga=10,
            atributos={"forehand": 70, "backhand": 68},
            atributos_psicologicos={"concentracao": 60},
            equipe=[],
        )

        resultado = treinar_semana(jogador, "foco_inexistente")

        self.assertEqual(resultado, {})
        self.assertEqual(jogador.energia, 100)
        self.assertEqual(jogador.fadiga, 10)

    def test_staff_fit_e_recovery_bonus_reagem_ao_contexto(self):
        jogador = SimpleNamespace(
            superficie_preferida="saibro",
            equipe=[{"id": "treinador_fundo_pro", "semanas_restantes": 10, "salario": 600}, {"id": "fisio_pro", "semanas_restantes": 10, "salario": 600}],
            atributos={"saque": 70, "voleio": 58, "fisico": 72},
            atributos_psicologicos={"concentracao": 60},
            seguidores=1200,
            empresario={"id": "mkt_freelancer", "semanas_restantes": 20, "salario": 100},
        )
        treinador = {"categoria": "treinador", "estilo": "Fundo de Quadra", "foco_atributos": ["forehand", "backhand", "topspin", "movimento"], "bonus_progressao": 0.2}

        summary = training_fit_summary(jogador, treinador, "tecnico", "forehand")
        recovery = weekly_recovery_bonus(jogador)

        self.assertGreaterEqual(summary["surface_fit"], 18)
        self.assertGreater(summary["bonus"], 0)
        self.assertGreaterEqual(recovery["trainer_bonus"], 0)
        self.assertGreaterEqual(recovery["physio_bonus"], 0)


if __name__ == "__main__":
    unittest.main()
