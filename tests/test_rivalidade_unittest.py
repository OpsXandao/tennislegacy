import unittest
from types import SimpleNamespace

from src.jogador import (
    atualizar_rivalidade,
    obter_bonus_rivalidade,
    obter_rival_info,
    rival_ativo,
)


class RankingFake:
    def obter_posicao(self, nome, modalidade="simples"):
        return {"Rival A": 18, "Rival B": 42}.get(nome, 0)


class RivalidadeTests(unittest.TestCase):
    def test_rivalidade_ativa_apos_tres_confrontos_com_winrate_extrema(self):
        jogador = SimpleNamespace(rivalidades={})

        atualizar_rivalidade(jogador, "Rival A", True, semana=10)
        atualizar_rivalidade(jogador, "Rival A", True, semana=11)
        atualizar_rivalidade(jogador, "Rival A", False, semana=12)

        self.assertTrue(rival_ativo(jogador, "Rival A"))
        bonus = obter_bonus_rivalidade(jogador, "Rival A")
        self.assertEqual(bonus["confrontos"], 3)
        self.assertEqual(bonus["vitorias"], 2)
        self.assertEqual(bonus["derrotas"], 1)

    def test_obter_rival_info_retorna_rival_ativo_mais_relevante(self):
        jogador = SimpleNamespace(
            rivalidades={
                "rival a": {
                    "nome": "Rival A",
                    "confrontos": 4,
                    "vitorias": 1,
                    "ultima_semana": 15,
                },
                "rival b": {
                    "nome": "Rival B",
                    "confrontos": 3,
                    "vitorias": 3,
                    "ultima_semana": 18,
                },
            }
        )

        rival = obter_rival_info(jogador, ranking=RankingFake())

        self.assertEqual(rival["nome"], "Rival A")
        self.assertEqual(rival["ranking"], 18)
        self.assertEqual(rival["h2h"], {"v": 1, "d": 3})


if __name__ == "__main__":
    unittest.main()
