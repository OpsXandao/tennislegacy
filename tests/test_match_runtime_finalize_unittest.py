import unittest
import sys
import types
from types import SimpleNamespace
from unittest.mock import patch

sys.modules.setdefault(
    "fastapi",
    types.SimpleNamespace(
        HTTPException=Exception,
        Header=lambda default=None, **_kwargs: default,
    ),
)
sys.modules.setdefault(
    "api.routes._shared",
    types.SimpleNamespace(carregar_torneio_api=lambda *args, **kwargs: None),
)

from api.routes._match_runtime import MatchRuntime


class MatchRuntimeFinalizeTests(unittest.TestCase):
    def test_finalizar_distribui_pontos_quando_jogador_e_eliminado(self):
        runtime = MatchRuntime.__new__(MatchRuntime)
        runtime.finalizado_torneio = False
        runtime.vencedor = "adversario"
        runtime.jogador = SimpleNamespace(nome="Alexandre", genero="masculino")
        runtime.adversario = {"nome": "Rival", "ranking_pos": 12}
        runtime.torneio_info = {"nome": "Roma"}
        runtime.stats_j = object()
        runtime.stats_a = object()
        runtime.set_scores = []
        runtime.estrategia_j = {}
        runtime.total_pontos = 24
        runtime.energia_inicial = 80
        runtime.energia_inicial_a = 78
        runtime.contexto_partida = SimpleNamespace(stamina_j=52, stamina_a=61)
        runtime.config = object()
        runtime.modalidade = "simples"
        runtime.save_name = "save_teste"
        runtime._placar_final_texto = lambda: "6-4 6-3"
        runtime._registrar_historicos = lambda instancia: None
        runtime._persistir = lambda: None

        instancia = SimpleNamespace(
            jogador_nome="Alexandre",
            ranking=SimpleNamespace(),
            processar_resultado_partida=lambda *args, **kwargs: None,
            simular_npcs_na_fase_atual=lambda *args, **kwargs: None,
            _montar_fatores_fadiga=lambda *args, **kwargs: {},
            _carregar_estado=lambda: {"fase_atual": "r16", "jogador_vivo": False},
        )

        with (
            patch(
                "api.routes._shared.carregar_torneio_api", return_value=instancia
            ),
            patch("src.torneio.avancar_fase"),
            patch(
                "src.progressao.handle_xp_e_level_up",
                side_effect=lambda jogador, vitoria: jogador,
            ),
            patch("src.progressao.handle_progressao_natural"),
            patch(
                "src.fadiga.handle_fadiga_e_lesao",
                side_effect=lambda jogador, **kwargs: jogador,
            ),
            patch(
                "src.fadiga.handle_fadiga_e_lesao_npc",
                side_effect=lambda adversario, **kwargs: adversario,
            ),
            patch("src.save.salvar_jogo"),
            patch("src.pontuacao.distribuir_pontos_torneio") as mock_distribuir,
        ):
            runtime._finalizar_torneio()

        mock_distribuir.assert_called_once_with("save_teste", genero="masculino")

    def test_finalizar_recupera_energia_quando_jogador_avanca_no_torneio(self):
        runtime = MatchRuntime.__new__(MatchRuntime)
        runtime.finalizado_torneio = False
        runtime.vencedor = "jogador"
        runtime.jogador = SimpleNamespace(
            nome="Alexandre",
            genero="masculino",
            energia=72,
            fadiga=28,
            moral=70,
            atributos={"fisico": 70, "resistencia": 65},
        )
        runtime.adversario = {"nome": "Rival", "ranking_pos": 120}
        runtime.torneio_info = {"nome": "Roma"}
        runtime.stats_j = object()
        runtime.stats_a = object()
        runtime.set_scores = []
        runtime.estrategia_j = {}
        runtime.total_pontos = 32
        runtime.energia_inicial = 88
        runtime.energia_inicial_a = 84
        runtime.contexto_partida = SimpleNamespace(stamina_j=61, stamina_a=58)
        runtime.config = SimpleNamespace(superficie="dura")
        runtime.modalidade = "simples"
        runtime.save_name = "save_teste"
        runtime.log = []
        runtime._placar_final_texto = lambda: "6-4 6-3"
        runtime._registrar_historicos = lambda instancia: None
        runtime._persistir = lambda: None

        estado_ativo = {
            "fase_atual": "quartas",
            "jogador_vivo": True,
            "agenda_dia": {"jogos_realizados": ["simples"]},
        }
        instancia = SimpleNamespace(
            jogador_nome="Alexandre",
            ranking=SimpleNamespace(),
            processar_resultado_partida=lambda *args, **kwargs: None,
            simular_npcs_na_fase_atual=lambda *args, **kwargs: None,
            _montar_fatores_fadiga=lambda *args, **kwargs: {},
            _carregar_estado=lambda: estado_ativo,
            _multiplicador_recuperacao_mesmo_dia=lambda: 0.85,
        )

        def _recuperar(jogador, **kwargs):
            jogador.energia = 79
            return jogador, [SimpleNamespace(mensagem="Energia recuperada.")]

        with (
            patch(
                "api.routes._shared.carregar_torneio_api", return_value=instancia
            ),
            patch("src.torneio.avancar_fase"),
            patch(
                "src.services.milestone_service.MilestoneService.detect_match_milestones",
                return_value=[],
            ),
            patch(
                "src.progressao.handle_xp_e_level_up",
                side_effect=lambda jogador, vitoria: jogador,
            ),
            patch("src.progressao.handle_progressao_natural"),
            patch(
                "src.fadiga.handle_fadiga_e_lesao",
                side_effect=lambda jogador, **kwargs: jogador,
            ),
            patch(
                "src.fadiga.handle_fadiga_e_lesao_npc",
                side_effect=lambda adversario, **kwargs: adversario,
            ),
            patch(
                "src.fadiga.recuperar_energia_entre_rodadas",
                side_effect=_recuperar,
            ) as mock_recuperar,
            patch("src.save.salvar_jogo") as mock_salvar,
        ):
            runtime._finalizar_torneio()

        mock_recuperar.assert_called_once()
        self.assertEqual(mock_recuperar.call_args.kwargs["multiplicador"], 0.85)
        self.assertTrue(mock_recuperar.call_args.kwargs["return_eventos"])
        self.assertEqual(runtime.jogador.energia, 79)
        self.assertIn("Energia recuperada.", runtime.log)
        mock_salvar.assert_called_once_with("save_teste", runtime.jogador)


if __name__ == "__main__":
    unittest.main()
