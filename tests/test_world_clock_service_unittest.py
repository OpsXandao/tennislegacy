import unittest
from unittest.mock import patch

from src.services import world_clock_service


class WorldClockServiceTests(unittest.TestCase):
    def _estado(self):
        return {
            "nome": "Adelaide International",
            "fase_atual": "r32",
            "semana": 2,
            "ano": 2026,
            "estado": {
                "jogador": "Alexandre",
                "rodadas": {
                    "r32": [
                        ({"nome": "Carlos"}, {"nome": "Bruno"}),
                        ({"nome": "Alexandre"}, {"nome": "Nadal"}),
                    ]
                },
            },
        }

    def test_gerar_ordem_de_jogo_classifica_matchday_do_jogador(self):
        eventos = world_clock_service.gerar_ordem_de_jogo(
            self._estado(), temporada={"semana": 2, "ano": 2026}
        )

        self.assertEqual(len(eventos), 2)
        self.assertEqual(eventos[0]["tipo"], "npc_match")
        self.assertEqual(eventos[1]["tipo"], "player_match")
        self.assertTrue(eventos[1]["stop_for_player"])
        self.assertEqual(eventos[1]["presentation"], "ea_matchday")
        self.assertEqual(eventos[1]["quadra"], "Central")
        self.assertIn("melhor_de", eventos[1])
        self.assertIn("risco_atraso_clima", eventos[1])

    def test_proximo_evento_jogavel_ignora_ticks_de_mundo(self):
        eventos = world_clock_service.gerar_ordem_de_jogo(self._estado())
        agenda = {"clock": {}, "events": eventos}

        proximo = world_clock_service.proximo_evento_jogavel(agenda)

        self.assertEqual(proximo["jogador1"], "Alexandre")
        self.assertEqual(proximo["categoria"], "matchday")

    def test_sincronizar_agenda_remove_eventos_agendados_antigos_do_mesmo_torneio(self):
        estado = self._estado()
        estado["fase_atual"] = "r16"
        estado["estado"]["rodadas"] = {
            "r16": [({"nome": "Alexandre"}, {"nome": "Murray"})]
        }
        agenda = {
            "clock": {"ano": 2026, "semana": 2, "dia": 1, "hora": "09:00"},
            "events": [
                {
                    "id": "Adelaide International:r32:2",
                    "torneio": "Adelaide International",
                    "fase": "r32",
                    "status": "scheduled",
                    "stop_for_player": True,
                    "jogador1": "Alexandre",
                    "jogador2": "Nadal",
                    "ano": 2026,
                    "semana": 2,
                    "dia": 2,
                    "hora": "13:00",
                    "prioridade": 0,
                },
                {
                    "id": "Outro Torneio:r32:1",
                    "torneio": "Outro Torneio",
                    "fase": "r32",
                    "status": "scheduled",
                    "stop_for_player": False,
                },
            ],
        }
        salvo = {}

        with patch.object(world_clock_service, "carregar_agenda", return_value=agenda), patch.object(
            world_clock_service, "salvar_agenda", side_effect=lambda _save, data: salvo.update(data)
        ):
            resultado = world_clock_service.sincronizar_agenda_torneio(
                "save_teste", estado, temporada={"semana": 2, "ano": 2026}
            )

        fases_adelaide = [
            evento["fase"]
            for evento in resultado["events"]
            if evento.get("torneio") == "Adelaide International"
        ]
        self.assertEqual(fases_adelaide, ["r16"])
        self.assertTrue(any(evento.get("torneio") == "Outro Torneio" for evento in resultado["events"]))
        self.assertEqual(world_clock_service.proximo_evento_jogavel(resultado)["fase"], "r16")
        self.assertEqual(salvo["events"], resultado["events"])

    def test_avancar_ate_proximo_momento_atualiza_clock(self):
        agenda = {
            "clock": {"ano": 2026, "semana": 2, "dia": 1, "hora": "09:00"},
            "events": world_clock_service.gerar_ordem_de_jogo(self._estado()),
        }
        salvo = {}

        with patch.object(world_clock_service, "carregar_agenda", return_value=agenda), patch.object(
            world_clock_service, "salvar_agenda", side_effect=lambda _save, data: salvo.update(data)
        ):
            resultado = world_clock_service.avancar_ate_proximo_momento("save_teste")

        self.assertTrue(resultado["ok"])
        self.assertEqual(resultado["evento"]["tipo"], "player_match")
        self.assertEqual(salvo["clock"]["hora"], resultado["evento"]["hora"])


if __name__ == "__main__":
    unittest.main()
