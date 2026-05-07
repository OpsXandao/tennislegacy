import random
import unittest
from unittest.mock import patch

from src.duplas import buscar_parceiros_disponiveis, fundir_dupla
from src.torneio_core import Torneio


class JogadorDummy:
    def __init__(self, nome, overall, duplas):
        self.nome = nome
        self._overall = overall
        self.atributos = {"duplas": duplas}

    def calcular_overall(self):
        return self._overall


class DuplasTests(unittest.TestCase):
    def test_busca_parceiros_fallback_usa_pool_sem_name_error(self):
        jogador = JogadorDummy("Alexandre Silva", overall=95, duplas=95)
        pool = [
            {"nome": "Bruno Costa", "overall": 70, "atributos": {"duplas": 60}},
            {"nome": "Caio Lima", "overall": 68, "atributos": {"duplas": 58}},
        ]

        parceiros = buscar_parceiros_disponiveis(jogador, pool, n=2)

        self.assertEqual(len(parceiros), 2)
        self.assertEqual({p["nome"] for p in parceiros}, {"Bruno Costa", "Caio Lima"})

    def test_busca_parceiros_prioriza_vinculos_e_limita_quantidade(self):
        jogador = JogadorDummy("Alexandre Silva", overall=75, duplas=75)
        pool = [
            {"nome": "Bruno Costa", "overall": 74, "atributos": {"duplas": 74}},
            {"nome": "Caio Lima", "overall": 75, "atributos": {"duplas": 75}},
            {"nome": "Diego Alves", "overall": 76, "atributos": {"duplas": 76}},
        ]
        vinculos = {
            "Caio Lima": {"partidas": 8, "vitorias": 5},
            "Bruno Costa": {"partidas": 3, "vitorias": 2},
        }

        with patch.object(random, "shuffle", lambda itens: None):
            parceiros = buscar_parceiros_disponiveis(
                jogador, pool, n=2, vinculos=vinculos
            )

        self.assertEqual(len(parceiros), 2)
        self.assertEqual(parceiros[0]["nome"], "Caio Lima")
        self.assertEqual(parceiros[1]["nome"], "Bruno Costa")
        self.assertEqual(parceiros[0]["_vinculo"]["partidas"], 8)

    def test_distribuicao_pontos_duplas_nao_duplica_vinculos_humanos(self):
        class RankingFake:
            def __init__(self):
                self.pontos = []
                self.salvou = 0

            def adicionar_pontos(
                self,
                nome,
                pontos,
                semana_exp,
                modalidade=None,
                ano_exp=None,
                metadados=None,
            ):
                self.pontos.append((nome, pontos, modalidade, metadados))

            def salvar_ranking(self):
                self.salvou += 1

        torneio = Torneio.__new__(Torneio)
        torneio.genero = "masculino"
        torneio.nome_torneio_atual = "ATP Teste"
        torneio.ranking = RankingFake()
        torneio._tipo_torneio = lambda: "ATP 250"

        estado = {
            "tipo_duplas": "mesmo_genero",
            "fases_duplas": ["r16", "qf"],
            "resultados_duplas": {
                "r16": [
                    {
                        "jogador_a": {
                            "nome": "Silva / Costa",
                            "jogadores": [
                                {"nome": "Alexandre Silva"},
                                {"nome": "Bruno Costa"},
                            ],
                        },
                        "jogador_b": {
                            "nome": "Lima / Alves",
                            "jogadores": [
                                {"nome": "Caio Lima"},
                                {"nome": "Diego Alves"},
                            ],
                        },
                        "vencedor": {"nome": "Silva / Costa"},
                    }
                ],
                "qf": [
                    {
                        "jogador_a": {
                            "nome": "Silva / Costa",
                            "jogadores": [
                                {"nome": "Alexandre Silva"},
                                {"nome": "Bruno Costa"},
                            ],
                        },
                        "jogador_b": {
                            "nome": "Souza / Rocha",
                            "jogadores": [
                                {"nome": "Enzo Souza"},
                                {"nome": "Felipe Rocha"},
                            ],
                        },
                        "vencedor": {"nome": "Souza / Rocha"},
                    }
                ],
            },
            "nome_par_duplas": "Silva / Costa",
        }

        with (
            patch(
                "src.ranking.SistemaRanking", return_value=torneio.ranking
            ) as mock_ranking,
            patch(
                "src.dados.carregar_temporada", return_value={"semana": 10, "ano": 2026}
            ),
        ):
            torneio._distribuir_pontos_duplas(estado, "save_teste")
            torneio._distribuir_pontos_duplas(estado, "save_teste")

        self.assertEqual(torneio.ranking.salvou, 1)
        self.assertEqual(len(torneio.ranking.pontos), 2)
        self.assertTrue(estado["pontos_duplas_distribuidos"])
        self.assertEqual(mock_ranking.call_args.kwargs["modalidade"], "duplas")

    def test_fundir_dupla_preserva_nacionalidade_quando_compatriotas(self):
        dupla = fundir_dupla(
            {
                "nome": "Alexandre Silva",
                "nacionalidade": "[BR] Brasil",
                "atributos": {},
            },
            {"nome": "Bruno Costa", "nacionalidade": "[BR] Brasil", "atributos": {}},
        )

        self.assertEqual(dupla["nacionalidade"], "[BR] Brasil")


if __name__ == "__main__":
    unittest.main()
