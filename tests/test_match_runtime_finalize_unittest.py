import unittest
import sys
import types
from types import SimpleNamespace
from unittest.mock import patch

sys.modules.setdefault("fastapi", types.SimpleNamespace(HTTPException=Exception))
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
                "api.routes._match_runtime.carregar_torneio_api", return_value=instancia
            ),
            patch("api.routes._match_runtime.avancar_fase"),
            patch(
                "api.routes._match_runtime.handle_xp_e_level_up",
                side_effect=lambda jogador, vitoria: jogador,
            ),
            patch("src.progressao.handle_progressao_natural"),
            patch(
                "api.routes._match_runtime.handle_fadiga_e_lesao",
                side_effect=lambda jogador, **kwargs: jogador,
            ),
            patch(
                "api.routes._match_runtime.handle_fadiga_e_lesao_npc",
                side_effect=lambda adversario, **kwargs: adversario,
            ),
            patch("api.routes._match_runtime.salvar_jogo"),
            patch("src.pontuacao.distribuir_pontos_torneio") as mock_distribuir,
        ):
            runtime._finalizar_torneio()

        mock_distribuir.assert_called_once_with("save_teste", genero="masculino")


if __name__ == "__main__":
    unittest.main()
