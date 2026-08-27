import unittest

from src import torneio_sim


class DummyTournament:
    best_of_sets = 3
    tournament_data = {"quadra": "dura"}

    def garantir_dados_completos(self, entidade):
        return dict(entidade)

    def _aplicar_fadiga_npc_por_nome(self, *_args, **_kwargs):
        return True

    def _aplicar_moral_npc_partida(self, *_args, **_kwargs):
        return None


class TorneioSimWalkoverTests(unittest.TestCase):
    def test_npc_lesionado_retirado_gera_walkover(self):
        lesionado = {
            "nome": "Jogador Lesionado",
            "status_lesao": {"lesionado": True, "nivel": "lesionado"},
        }
        adversario = {"nome": "Adversario Saudavel"}

        resultado = torneio_sim.simular_partida_npc(DummyTournament(), lesionado, adversario)

        self.assertTrue(resultado["walkover"])
        self.assertEqual(resultado["resultado"], "W.O.")
        self.assertEqual(resultado["vencedor"]["nome"], "Adversario Saudavel")
        self.assertEqual(resultado["retirado"], "Jogador Lesionado")


if __name__ == "__main__":
    unittest.main()
