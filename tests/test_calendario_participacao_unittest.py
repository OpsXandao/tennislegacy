import sys
import types
import unittest
from unittest.mock import patch

if "colorama" not in sys.modules:
    colorama_stub = types.SimpleNamespace(
        init=lambda *args, **kwargs: None,
        Fore=types.SimpleNamespace(
            RED="", GREEN="", BLUE="", YELLOW="", MAGENTA="", CYAN="", WHITE=""
        ),
        Style=types.SimpleNamespace(RESET_ALL="", BRIGHT=""),
    )
    sys.modules["colorama"] = colorama_stub


class CalendarioParticipacaoTests(unittest.TestCase):
    def test_contexto_pune_npc_exausto_em_sequencia(self):
        from src.calendario_participacao import ajustar_prob_participacao_por_contexto

        jogador = {
            "energia": 32,
            "fadiga": 78,
            "moral": 61,
            "historico_torneios": [
                {"torneio": "Adelaide", "semana": 3, "ano": 2026},
                {"torneio": "Auckland", "semana": 2, "ano": 2026},
                {"torneio": "Brisbane", "semana": 1, "ano": 2026},
            ],
            "status_lesao": {"lesionado": False, "nivel": "desconforto"},
        }

        prob = ajustar_prob_participacao_por_contexto(
            0.60,
            jogador,
            tipo="ATP 250",
            rank=34,
            semana_atual=3,
            ano_atual=2026,
        )

        self.assertLess(prob, 0.12)

    def test_contexto_reduz_top_player_em_atp_250(self):
        from src.calendario_participacao import ajustar_prob_participacao_por_contexto

        jogador = {
            "energia": 88,
            "fadiga": 18,
            "moral": 78,
            "historico_torneios": [],
            "status_lesao": {"lesionado": False, "nivel": "saudavel"},
        }

        prob = ajustar_prob_participacao_por_contexto(
            0.35,
            jogador,
            tipo="ATP 250",
            rank=8,
            semana_atual=6,
            ano_atual=2026,
        )

        self.assertLess(prob, 0.20)

    def test_contexto_premia_retorno_a_torneio_com_titulo_previo(self):
        from src.calendario_participacao import ajustar_prob_participacao_por_contexto

        jogador = {
            "energia": 82,
            "fadiga": 24,
            "moral": 76,
            "historico_torneios": [
                {
                    "torneio": "Brisbane International",
                    "fase_alcancada": "campeao",
                    "semana": 1,
                    "ano": 2025,
                }
            ],
            "status_lesao": {"lesionado": False, "nivel": "saudavel"},
        }

        base = ajustar_prob_participacao_por_contexto(
            0.45,
            jogador,
            tipo="ATP 250",
            rank=22,
            nome_torneio="Evento Aleatorio",
            semana_atual=1,
            ano_atual=2026,
        )
        com_memoria = ajustar_prob_participacao_por_contexto(
            0.45,
            jogador,
            tipo="ATP 250",
            rank=22,
            nome_torneio="Brisbane International",
            semana_atual=1,
            ano_atual=2026,
        )

        self.assertGreater(com_memoria, base)

    def test_contexto_grinder_mantem_agenda_mais_cheia(self):
        from src.calendario_participacao import ajustar_prob_participacao_por_contexto

        grinder = {
            "energia": 80,
            "fadiga": 20,
            "moral": 72,
            "fisico": 72,
            "historico_torneios": [],
            "status_lesao": {"lesionado": False, "nivel": "saudavel"},
        }
        elite = {
            "energia": 80,
            "fadiga": 20,
            "moral": 72,
            "fisico": 72,
            "historico_torneios": [],
            "status_lesao": {"lesionado": False, "nivel": "saudavel"},
        }

        prob_grinder = ajustar_prob_participacao_por_contexto(
            0.60,
            grinder,
            tipo="ATP 250",
            rank=120,
            nome_torneio="Santiago",
            semana_atual=8,
            ano_atual=2026,
        )
        prob_elite = ajustar_prob_participacao_por_contexto(
            0.60,
            elite,
            tipo="ATP 250",
            rank=8,
            nome_torneio="Santiago",
            semana_atual=8,
            ano_atual=2026,
        )

        self.assertGreater(prob_grinder, prob_elite)

    def test_selecao_prefere_npc_descansado_ao_cansado(self):
        from src.calendario import _selecionar_participantes_para_torneio

        info_torneio = {
            "nome": "ATP 250 Teste",
            "tipo": "ATP 250",
            "pais_sede": "[BRA]",
            "quadra": "dura",
            "semana": 4,
            "ano": 2026,
        }
        ranking = [
            {
                "nome": "NPC Exausto",
                "nacionalidade": "[BRA]",
                "energia": 30,
                "fadiga": 82,
                "moral": 60,
                "historico_torneios": [
                    {"torneio": "Semana 4", "semana": 4, "ano": 2026},
                    {"torneio": "Semana 3", "semana": 3, "ano": 2026},
                    {"torneio": "Semana 2", "semana": 2, "ano": 2026},
                ],
                "status_lesao": {"lesionado": False, "nivel": "desconforto"},
            },
            {
                "nome": "NPC Descansado",
                "nacionalidade": "[BRA]",
                "energia": 89,
                "fadiga": 14,
                "moral": 73,
                "historico_torneios": [],
                "status_lesao": {"lesionado": False, "nivel": "saudavel"},
            },
        ]

        with patch("src.calendario.random.random", return_value=0.20):
            selecionados = _selecionar_participantes_para_torneio(
                info_torneio,
                ranking,
                {"npc exausto", "npc descansado"},
                max_jogadores=1,
            )

        self.assertEqual([j["nome"] for j in selecionados], ["NPC Descansado"])

    def test_selecao_considera_memoria_de_titulo_no_mesmo_torneio(self):
        from src.calendario import _selecionar_participantes_para_torneio

        info_torneio = {
            "nome": "Brisbane International",
            "tipo": "ATP 250",
            "pais_sede": "[AUS]",
            "quadra": "dura",
            "semana": 1,
            "ano": 2026,
        }
        ranking = [
            {
                "nome": "NPC Campeao Brisbane",
                "nacionalidade": "[ESP]",
                "energia": 84,
                "fadiga": 18,
                "moral": 75,
                "historico_torneios": [
                    {
                        "torneio": "Brisbane International",
                        "fase_alcancada": "campeao",
                        "semana": 1,
                        "ano": 2025,
                    }
                ],
                "status_lesao": {"lesionado": False, "nivel": "saudavel"},
            },
            {
                "nome": "NPC Sem Historia",
                "nacionalidade": "[ESP]",
                "energia": 84,
                "fadiga": 18,
                "moral": 75,
                "historico_torneios": [],
                "status_lesao": {"lesionado": False, "nivel": "saudavel"},
            },
        ]

        with patch("src.calendario.random.random", return_value=0.45):
            selecionados = _selecionar_participantes_para_torneio(
                info_torneio,
                ranking,
                {"npc campeao brisbane", "npc sem historia"},
                max_jogadores=1,
            )

        self.assertEqual([j["nome"] for j in selecionados], ["NPC Campeao Brisbane"])


if __name__ == "__main__":
    unittest.main()
