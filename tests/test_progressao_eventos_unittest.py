import unittest
from unittest.mock import patch

from src.progressao import (
    evoluir_npc_pos_torneio,
    handle_xp_e_level_up,
    treinar_semana,
)
from src.fadiga import handle_fadiga_e_lesao


class _JogadorFake:
    def __init__(self):
        self.nome = "Tester"
        self.equipe = []
        self.xp = 0
        self.nivel = 1
        self.xp_para_proximo_nivel = 100
        self.pontos_de_skill = 0
        self.fadiga = 0
        self.energia = 100
        self.status_lesao = {
            "lesionado": False,
            "semanas_restantes": 0,
            "nivel": "saudavel",
            "penalidade_atributos": 0.0,
        }
        self.atributos = {"saque": 60, "duplas": 60}
        self.atributos_psicologicos = {
            "concentracao": 60,
            "leitura_de_jogo": 60,
            "determinacao": 60,
        }
        self.moral = 70


class ProgressaoEventosTests(unittest.TestCase):
    def test_handle_xp_e_level_up_retorna_eventos_tipados(self):
        jogador = _JogadorFake()

        _jogador, eventos = handle_xp_e_level_up(
            jogador, vitoria=True, return_eventos=True
        )

        self.assertGreaterEqual(len(eventos), 1)
        self.assertEqual(eventos[0].tipo, "xp_ganho")
        self.assertIn("xp_ganho", eventos[0].payload)

    def test_handle_fadiga_e_lesao_retorna_evento_de_fadiga(self):
        jogador = _JogadorFake()

        _jogador, eventos = handle_fadiga_e_lesao(
            jogador,
            pontos_disputados=120,
            fatores_partida={"superficie": "dura"},
            return_eventos=True,
        )

        tipos = [e.tipo for e in eventos]
        self.assertIn("fadiga_atualizada", tipos)

    def test_progressao_natural_duplas_so_em_duplas(self):
        from src.progressao import calcular_progressao_natural
        class _StatsFake:
            def __init__(self):
                self.primeiro_saque_total = 100
                self.primeiro_saque_in = 60
                self.winners = 30
                self.aces = 5
                self.pontos_ganhos_saque = 50
                self.pontos_total_saque = 100

        jogador = _JogadorFake()
        stats = _StatsFake()
        estrategia = {"estilo": "atacar_do_fundo"}

        # Em simples, não deve ter chance de evoluir duplas
        melhorias_simples = calcular_progressao_natural(jogador, stats, estrategia, 200, modalidade="simples")
        self.assertNotIn("duplas", melhorias_simples)

        # Em duplas, deve haver chance
        found_duplas = False
        for _ in range(100):
            melhorias = calcular_progressao_natural(jogador, stats, estrategia, 2000, modalidade="duplas")
            if "duplas" in melhorias:
                found_duplas = True
                break
        self.assertTrue(found_duplas, "Deveria ter evoluído duplas em modalidade duplas com 2000 pontos")

    def test_evoluir_npc_pos_torneio_permte_npc_real_e_bloqueia_jogador_principal(self):
        npc_real = {
            "nome": "NPC Real",
            "idade": 20,
            "pico_carreira": 27,
            "is_bot": False,
            "e_jogador_principal": False,
            "atributos": {"saque": 70, "forehand": 68},
        }
        jogador_principal = {
            "nome": "Humano",
            "idade": 20,
            "pico_carreira": 27,
            "is_bot": False,
            "e_jogador_principal": True,
            "atributos": {"saque": 70, "forehand": 68},
        }

        with (
            patch("src.progressao.random.random", return_value=0.10),
            patch("src.progressao.random.choice", return_value="saque"),
            patch("src.player_ratings.ajustar_atributo_duplas"),
            patch("src.player_ratings.calcular_overall_contextual", return_value=75),
        ):
            evoluir_npc_pos_torneio(npc_real, "campeao")
            evoluir_npc_pos_torneio(jogador_principal, "campeao")

        self.assertEqual(npc_real["atributos"]["saque"], 71)
        self.assertEqual(jogador_principal["atributos"]["saque"], 70)

    def test_evoluir_npc_pos_torneio_limita_chance_de_jovem_campeao(self):
        npc_jovem = {
            "nome": "Jovem",
            "idade": 19,
            "pico_carreira": 27,
            "is_bot": False,
            "atributos": {"saque": 70, "forehand": 68},
        }

        with (
            patch("src.progressao.random.random", return_value=0.97),
            patch("src.progressao.random.choice", return_value="saque"),
            patch("src.player_ratings.ajustar_atributo_duplas"),
            patch("src.player_ratings.calcular_overall_contextual", return_value=75),
        ):
            evoluir_npc_pos_torneio(npc_jovem, "campeao")

        self.assertEqual(npc_jovem["atributos"]["saque"], 70)

    def test_treinar_semana_com_foco_invalido_nao_consume_recursos(self):
        jogador = _JogadorFake()
        energia_inicial = jogador.energia
        fadiga_inicial = jogador.fadiga

        melhorias = treinar_semana(jogador, "foco_inexistente")

        self.assertEqual(melhorias, {})
        self.assertEqual(jogador.energia, energia_inicial)
        self.assertEqual(jogador.fadiga, fadiga_inicial)


if __name__ == "__main__":
    unittest.main()
