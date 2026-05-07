import unittest

from src.player_identity import derive_player_identity


class PlayerIdentityTests(unittest.TestCase):
    def test_derive_identity_for_doubles_specialist(self):
        jogador = {
            "nome": "Especialista",
            "altura": 185,
            "peso": 79,
            "atributos": {
                "saque": 78,
                "forehand": 74,
                "backhand": 76,
                "topspin": 72,
                "voleio": 91,
                "slice": 79,
                "movimento": 84,
                "lob": 80,
                "fisico": 82,
                "winner": 83,
                "duplas": 95,
            },
            "atributos_psicologicos": {
                "concentracao": 74,
                "agressividade": 58,
                "leitura_de_jogo": 81,
                "determinacao": 77,
            },
            "vinculos_dupla": {
                "Parceiro A": {"partidas": 12, "vitorias": 9},
            },
        }

        identity = derive_player_identity(jogador, ranking_pos=34, modalidade="duplas")

        self.assertEqual(identity["role"]["id"], "doubles_specialist")
        self.assertTrue(identity["doubles_profile"]["specialist"])
        self.assertEqual(identity["doubles_profile"]["best_partner"], "Parceiro A")
        self.assertTrue(any(p["id"] == "doubles_iq_plus" for p in identity["playstyles"]))
        self.assertGreaterEqual(identity["hidden_stats"]["doubles_iq"], 85)


if __name__ == "__main__":
    unittest.main()
