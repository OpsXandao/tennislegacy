import unittest
import types
import sys

from src.pontuacao import obter_pontos_map

sys.modules.setdefault(
    "fastapi",
    types.SimpleNamespace(
        HTTPException=Exception,
        Header=lambda default=None, **kwargs: default,
    ),
)

from src.services.tournament_service import (
    _filtrar_torneios_elegiveis,
    _torneio_disponivel_por_ranking,
)


class CircuitoItfChallengerTests(unittest.TestCase):
    def test_torneio_disponivel_por_ranking_aplica_cortes_do_circuito(self):
        self.assertFalse(
            _torneio_disponivel_por_ranking({"tipo": "Challenger 125"}, 100)
        )
        self.assertTrue(
            _torneio_disponivel_por_ranking({"tipo": "Challenger 125"}, 101)
        )
        self.assertFalse(_torneio_disponivel_por_ranking({"tipo": "ITF 25"}, 200))
        self.assertTrue(_torneio_disponivel_por_ranking({"tipo": "ITF 25"}, 201))

    def test_filtrar_torneios_elegiveis_remove_eventos_bloqueados(self):
        torneios = [
            {"nome": "Evento ATP", "tipo": "ATP 250"},
            {"nome": "Evento CH", "tipo": "Challenger 125"},
            {"nome": "Evento ITF", "tipo": "ITF 100"},
        ]

        elegiveis = _filtrar_torneios_elegiveis(torneios, 150)

        self.assertEqual(
            [torneio["nome"] for torneio in elegiveis],
            ["Evento ATP", "Evento CH"],
        )

    def test_obter_pontos_map_retorna_tabelas_novas(self):
        self.assertEqual(obter_pontos_map("ITF 25")["campeao"], 25)
        self.assertEqual(obter_pontos_map("ITF 100")["final"], 70)
        self.assertEqual(obter_pontos_map("Challenger 125")["semifinal"], 55)


if __name__ == "__main__":
    unittest.main()
