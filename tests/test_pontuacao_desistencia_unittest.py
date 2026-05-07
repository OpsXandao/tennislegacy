import json
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.pontuacao import distribuir_pontos_torneio


class RankingFake:
    instancias = []

    def __init__(self, caminho, modalidade="simples"):
        self.caminho = caminho
        self.modalidade = modalidade
        self.ranking = []
        self.pontos_adicionados = []
        self.salvou = 0
        RankingFake.instancias.append(self)

    def adicionar_pontos(
        self,
        nome,
        pontos,
        semana_expiracao,
        modalidade="simples",
        ano_exp=None,
        metadados=None,
    ):
        self.pontos_adicionados.append((nome, pontos, modalidade, metadados or {}))

    def adicionar_dinheiro(self, nome, valor):
        return None

    def buscar_jogador_por_nome(self, nome):
        return None

    def ordenar(self, *args, **kwargs):
        return None

    def salvar_ranking(self):
        self.salvou += 1


class PontuacaoDesistenciaTests(unittest.TestCase):
    def setUp(self):
        RankingFake.instancias = []
        self.tmpdir = tempfile.TemporaryDirectory()
        self.caminho_torneio = os.path.join(self.tmpdir.name, "torneio.json")
        estado = {
            "jogador": "Alexandre",
            "desistencia_jogador": True,
            "jogador_fase_saida": "quartas",
            "genero": "masculino",
            "torneio": "Roland Garros",
            "tournament_data": {"tipo": "Grand Slam", "premiacao": 0},
            "resultados": {
                "quartas": [
                    {
                        "jogador_a": {"nome": "Alexandre"},
                        "jogador_b": {"nome": "Rival"},
                        "vencedor": {"nome": "Rival"},
                        "resultado": "W.O.",
                    }
                ],
                "semifinal": [
                    {
                        "jogador_a": {"nome": "Rival"},
                        "jogador_b": {"nome": "Npc Finalista"},
                        "vencedor": {"nome": "Rival"},
                        "resultado": "6-4 6-4",
                    }
                ],
                "final": [
                    {
                        "jogador_a": {"nome": "Rival"},
                        "jogador_b": {"nome": "Campeao"},
                        "vencedor": {"nome": "Campeao"},
                        "resultado": "6-4 6-4",
                    }
                ],
            },
            "resultados_duplas": {},
        }
        with open(self.caminho_torneio, "w", encoding="utf-8") as arquivo:
            json.dump(estado, arquivo)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_desistencia_em_quartas_pontua_como_r16_e_marca_idempotencia(self):
        jogador = SimpleNamespace(nome="Alexandre", dinheiro=0, historico_torneios=[])

        def _salvar_json(caminho, estado):
            with open(caminho, "w", encoding="utf-8") as arquivo:
                json.dump(estado, arquivo)

        with (
            patch(
                "src.pontuacao.get_caminho_torneio_save",
                return_value=self.caminho_torneio,
            ),
            patch(
                "src.pontuacao.get_caminho_ranking_save",
                return_value=os.path.join(self.tmpdir.name, "ranking.json"),
            ),
            patch(
                "src.dados.get_caminho_ranking_duplas",
                return_value=os.path.join(self.tmpdir.name, "ranking_duplas.json"),
            ),
            patch(
                "src.pontuacao.carregar_temporada",
                return_value={"semana": 12, "ano": 2026},
            ),
            patch("src.pontuacao.carregar_jogador", return_value=jogador),
            patch("src.pontuacao.salvar_jogo"),
            patch("src.pontuacao.salvar_json_seguro", side_effect=_salvar_json),
            patch("src.pontuacao.SistemaRanking", side_effect=RankingFake),
        ):
            distribuir_pontos_torneio("save_teste")
            distribuir_pontos_torneio("save_teste")

        ranking_simples = next(
            instancia
            for instancia in RankingFake.instancias
            if instancia.modalidade == "simples"
        )
        alexandre = [
            item
            for item in ranking_simples.pontos_adicionados
            if item[0] == "alexandre"
        ]
        self.assertEqual(len(alexandre), 1)
        self.assertEqual(alexandre[0][1], 180)
        self.assertEqual(ranking_simples.salvou, 1)

        with open(self.caminho_torneio, "r", encoding="utf-8") as arquivo:
            estado_final = json.load(arquivo)
        self.assertTrue(estado_final["pontos_distribuidos"])


if __name__ == "__main__":
    unittest.main()
