import json
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.pontuacao import distribuir_pontos_davis, distribuir_pontos_torneio


class _RankingFake:
    instancias = []

    def __init__(self, caminho, modalidade="simples"):
        self.caminho = caminho
        self.modalidade = modalidade
        self.registros = {}
        self.chamadas = []
        self.ranking = [
            {"nome": "Alexandre", "nacionalidade": "[BR]", "pontos_ytd": 0},
            {"nome": "NPC Brasil", "nacionalidade": "[BR]", "pontos_ytd": 0},
            {"nome": "NPC Argentina", "nacionalidade": "[AR]", "pontos_ytd": 0},
        ]
        _RankingFake.instancias.append(self)

    def adicionar_pontos(
        self,
        nome,
        pontos,
        sem_exp,
        modalidade="simples",
        ano_exp=None,
        metadados=None,
        ano_expiracao=None,
    ):
        nome = str(nome)
        registro = self.registros.setdefault(nome, {"nome": nome, "pontos_ytd": 0})
        self.chamadas.append(
            {
                "nome": nome,
                "pontos": pontos,
                "sem_exp": sem_exp,
                "ano_exp": ano_exp if ano_exp is not None else ano_expiracao,
                "modalidade": modalidade,
                "metadados": metadados or {},
            }
        )
        return registro

    def adicionar_dinheiro(self, nome, valor):
        registro = self.registros.setdefault(str(nome), {"nome": str(nome), "pontos_ytd": 0})
        registro["dinheiro"] = registro.get("dinheiro", 0) + valor
        return registro

    def buscar_jogador_por_nome(self, nome):
        nome = str(nome)
        for jogador in self.ranking:
            if str(jogador.get("nome")) == nome:
                return jogador
        return self.registros.setdefault(nome, {"nome": nome, "pontos_ytd": 0})

    def ordenar(self, *args, **kwargs):
        return None

    def salvar_ranking(self):
        return None


class PontuacaoRankingTests(unittest.TestCase):
    def setUp(self):
        _RankingFake.instancias = []

    def test_distribuir_pontos_torneio_atualiza_pontos_ytd_em_simples(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_torneio = os.path.join(tmpdir, "torneio.json")
            estado = {
                "jogador": "Alexandre",
                "genero": "masculino",
                "torneio": "Roma",
                "tournament_data": {"tipo": "ATP 250", "premiacao": 0},
                "resultados": {
                    "final": [
                        {
                            "jogador_a": {"nome": "Alexandre"},
                            "jogador_b": {"nome": "Rival"},
                            "vencedor": {"nome": "Alexandre"},
                            "resultado": "6-4 6-4",
                        }
                    ]
                },
                "resultados_duplas": {},
            }
            with open(caminho_torneio, "w", encoding="utf-8") as arquivo:
                json.dump(estado, arquivo)

            jogador = SimpleNamespace(
                nome="Alexandre",
                dinheiro=0,
                pontos_ytd=0,
                historico_torneios=[],
            )

            with (
                patch("src.pontuacao.get_caminho_torneio_save", return_value=caminho_torneio),
                patch("src.pontuacao.get_caminho_ranking_save", return_value=os.path.join(tmpdir, "ranking.json")),
                patch("src.dados.get_caminho_ranking_duplas", return_value=os.path.join(tmpdir, "ranking_duplas.json")),
                patch("src.pontuacao.carregar_temporada", return_value={"semana": 12, "ano": 2026}),
                patch("src.pontuacao.carregar_jogador", return_value=jogador),
                patch("src.pontuacao.salvar_jogo"),
                patch("src.pontuacao.SistemaRanking", side_effect=_RankingFake),
            ):
                distribuir_pontos_torneio("save_teste")

        ranking_simples = next(inst for inst in _RankingFake.instancias if inst.modalidade == "simples")
        self.assertEqual(ranking_simples.buscar_jogador_por_nome("alexandre")["pontos_ytd"], 250)
        self.assertEqual(jogador.pontos_ytd, 250)

    def test_distribuir_pontos_davis_passa_ano_expiracao(self):
        jogador = SimpleNamespace(nome="Alexandre", genero="masculino", pontos_ytd=0)
        estado = {
            "resultados_confrontos": [
                {
                    "fase": "final",
                    "partidas": [
                        {
                            "tipo": "simples",
                            "vencedor": {"nome": "Alexandre"},
                        }
                    ],
                }
            ],
            "fase_atual": "finalizado",
            "vencedor_torneio": "[BR]",
            "finalista_torneio": "[AR]",
        }
        davis = SimpleNamespace(_carregar_estado=lambda: estado)

        with (
            patch("src.pontuacao.carregar_jogador", return_value=jogador),
            patch("src.pontuacao.SistemaRanking", side_effect=_RankingFake),
            patch("src.pontuacao.carregar_temporada", return_value={"semana": 20, "ano": 2026}),
            patch("src.davis_cup.carregar_davis_cup", return_value=davis),
            patch("src.pontuacao.salvar_jogo"),
            patch("src.pontuacao.log_simulacao"),
            patch("src.pontuacao.get_caminho_ranking_save", return_value="/tmp/ranking.json"),
        ):
            distribuir_pontos_davis("save_teste")

        ranking = _RankingFake.instancias[0]
        self.assertTrue(ranking.chamadas)
        self.assertTrue(all(chamada["ano_exp"] == 2027 for chamada in ranking.chamadas))


if __name__ == "__main__":
    unittest.main()
