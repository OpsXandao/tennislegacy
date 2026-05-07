import unittest

from src.torneio_core import Torneio


class RankingFake:
    def buscar_jogador_por_nome(self, nome):
        return {
            "nome": nome,
            "nacionalidade": {
                "Alexandre Paiva": "BRA",
                "Bruno Costa": "POR",
                "Caio Lima": "ARG",
                "Diego Alves": "ESP",
            }.get(nome, "??"),
        }


class TorneioApiStateTests(unittest.TestCase):
    def test_to_api_state_inclui_resultados_de_fase_sem_confronto_restante(self):
        torneio = Torneio.__new__(Torneio)
        torneio.nome_torneio_atual = "Hong Kong Open"
        torneio.tournament_data = {"tipo": "ATP 250", "quadra": "dura"}
        torneio.jogador_nome = "Alexandre Paiva"
        torneio.jogador_nacionalidade = "BRA"
        torneio.ranking = RankingFake()
        torneio._carregar_estado = lambda: {
            "fase_atual": "qualy_2",
            "jogador_vivo": True,
            "campeao_simples": None,
            "rodadas": {
                "qualy_1": [],
                "qualy_2": [({"nome": "Alexandre Paiva", "nacionalidade": "BRA"}, {"nome": "Diego Alves", "nacionalidade": "ESP"})],
            },
            "rodadas_duplas": {},
            "resultados": {
                "qualy_1": [
                    {
                        "jogador_a": {"nome": "Bruno Costa", "nacionalidade": "POR"},
                        "jogador_b": {"nome": "Caio Lima", "nacionalidade": "ARG"},
                        "vencedor": {"nome": "Bruno Costa", "nacionalidade": "POR"},
                        "resultado": "6/4 6/3",
                    }
                ],
                "qualy_2": [],
            },
            "resultados_duplas": {},
            "agenda_dia": {},
            "entry_status": {},
        }

        state = torneio.to_api_state()

        qualy_1 = [node for node in state["bracket"] if node["fase"] == "qualy_1"]
        self.assertEqual(len(qualy_1), 1)
        self.assertEqual(qualy_1[0]["jogador1"], "Bruno Costa")
        self.assertEqual(qualy_1[0]["jogador2"], "Caio Lima")
        self.assertEqual(qualy_1[0]["vencedor"], "Bruno Costa")
        self.assertEqual(qualy_1[0]["placar"], "6/4 6/3")

    def test_to_api_state_ordena_resultados_pela_proxima_fase(self):
        torneio = Torneio.__new__(Torneio)
        torneio.nome_torneio_atual = "Hong Kong Open"
        torneio.tournament_data = {"tipo": "ATP 250", "quadra": "dura"}
        torneio.jogador_nome = "Alexandre Paiva"
        torneio.jogador_nacionalidade = "BRA"
        torneio.ranking = RankingFake()
        torneio._fases_ordem = lambda: ["qualy_1", "qualy_2", "pre_oitavas", "oitavas", "quartas", "semifinal", "final"]
        torneio._carregar_estado = lambda: {
            "fase_atual": "qualy_2",
            "jogador_vivo": True,
            "campeao_simples": None,
            "rodadas": {
                "qualy_1": [],
                "qualy_2": [
                    ({"nome": "Suk Hyun Choo", "nacionalidade": "KOR"}, {"nome": "Mees Rottgering", "nacionalidade": "NED"}),
                    ({"nome": "Evgeny Karlovskiy", "nacionalidade": "RUS"}, {"nome": "Alexandre Paiva", "nacionalidade": "BRA"}),
                ],
            },
            "rodadas_duplas": {},
            "resultados": {
                "qualy_1": [
                    {
                        "jogador_a": {"nome": "Alexandre Paiva", "nacionalidade": "BRA"},
                        "jogador_b": {"nome": "Louis Larue", "nacionalidade": "FRA"},
                        "vencedor": {"nome": "Alexandre Paiva", "nacionalidade": "BRA"},
                        "resultado": "2 x 0",
                    },
                    {
                        "jogador_a": {"nome": "Suk Hyun Choo", "nacionalidade": "KOR"},
                        "jogador_b": {"nome": "Outro A", "nacionalidade": "USA"},
                        "vencedor": {"nome": "Suk Hyun Choo", "nacionalidade": "KOR"},
                        "resultado": "2 x 1",
                    },
                    {
                        "jogador_a": {"nome": "Mees Rottgering", "nacionalidade": "NED"},
                        "jogador_b": {"nome": "Outro B", "nacionalidade": "ESP"},
                        "vencedor": {"nome": "Mees Rottgering", "nacionalidade": "NED"},
                        "resultado": "2 x 0",
                    },
                    {
                        "jogador_a": {"nome": "Evgeny Karlovskiy", "nacionalidade": "RUS"},
                        "jogador_b": {"nome": "Outro C", "nacionalidade": "ITA"},
                        "vencedor": {"nome": "Evgeny Karlovskiy", "nacionalidade": "RUS"},
                        "resultado": "2 x 1",
                    },
                ],
            },
            "resultados_duplas": {},
            "agenda_dia": {},
            "entry_status": {},
        }

        state = torneio.to_api_state()

        qualy_1 = [node for node in state["bracket"] if node["fase"] == "qualy_1"]
        self.assertEqual(
            [node["vencedor"] for node in qualy_1[:4]],
            ["Suk Hyun Choo", "Mees Rottgering", "Evgeny Karlovskiy", "Alexandre Paiva"],
        )


if __name__ == "__main__":
    unittest.main()
