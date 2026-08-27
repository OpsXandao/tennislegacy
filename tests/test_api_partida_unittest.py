import importlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import patch


class ApiPartidaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fastapi = types.ModuleType("fastapi")

        class APIRouter:
            def __init__(self, *args, **kwargs):
                pass

            def get(self, *args, **kwargs):
                def decorator(fn):
                    return fn

                return decorator

            def post(self, *args, **kwargs):
                def decorator(fn):
                    return fn

                return decorator

        class HTTPException(Exception):
            def __init__(self, status_code, detail):
                super().__init__(detail)
                self.status_code = status_code
                self.detail = detail

        def Depends(dependency):
            return dependency

        def Header(default=None, alias=None):
            return default

        fastapi.APIRouter = APIRouter
        fastapi.Depends = Depends
        fastapi.Header = Header
        fastapi.HTTPException = HTTPException
        sys.modules["fastapi"] = fastapi

        pydantic = types.ModuleType("pydantic")

        class BaseModel:
            def __init__(self, **kwargs):
                for chave, valor in kwargs.items():
                    setattr(self, chave, valor)

        pydantic.BaseModel = BaseModel
        sys.modules["pydantic"] = pydantic

        cls.partida_route = importlib.import_module("api.routes.partida")

    def test_dupla_contem_jogador_pelo_elenco(self):
        from src.services.match_service import dupla_contem_jogador
        dupla = {
            "nome": "Silva / Costa",
            "jogadores": [{"nome": "Alexandre Silva"}, {"nome": "Bruno Costa"}],
        }
        self.assertTrue(dupla_contem_jogador(dupla, "Alexandre Silva"))
        self.assertFalse(dupla_contem_jogador(dupla, "Caio Lima"))

    @patch("api.routes.partida.start_match")
    def test_iniciar_partida_delega_para_servico(self, mock_start_match):
        mock_start_match.return_value = {"partida_id": "p1"}
        session = SimpleNamespace(
            nome_save_ativo="save_teste",
            jogador=SimpleNamespace(nome="Alexandre Silva"),
        )

        data = self.partida_route.iniciar(
            self.partida_route.IniciarPartidaBody(modo="manual"), session
        )

        self.assertEqual(data["partida_id"], "p1")
        mock_start_match.assert_called_once_with(
            "manual", "save_teste", session.jogador
        )

    @patch("api.routes.partida.obter_match_runtime")
    def test_ponto_busca_runtime_no_save_da_sessao(self, mock_obter_runtime):
        runtime = SimpleNamespace(jogar_ponto=lambda: {"ok": True})
        mock_obter_runtime.return_value = runtime
        session = SimpleNamespace(nome_save_ativo="save_teste")

        data = self.partida_route.ponto(
            self.partida_route.PontoBody(partida_id="p1"), session
        )

        self.assertEqual(data, {"ok": True})
        mock_obter_runtime.assert_called_once_with("p1", "save_teste")

    def test_scout_usa_tournament_data_quando_instancia_nao_tem_superficie(self):
        adversario = {
            "nome": "Pengyu Lu",
            "ranking_pos": 123,
            "overall": 67,
            "atributos": {
                "vel_saque": 80,
                "voleio": 76,
                "forehand": 84,
                "backhand": 82,
                "velocidade": 83,
                "winner": 81,
            },
            "atributos_psicologicos": {},
        }
        instancia = SimpleNamespace(
            tournament_data={"quadra": "saibro"},
            to_api_state=lambda: {"info_partida": {"adversario": adversario}},
        )
        session = SimpleNamespace(
            nome_save_ativo="save_teste",
            jogador=SimpleNamespace(
                nome="Alexandre Silva", genero="masculino", rivalidades={}
            ),
            ranking_atp=None,
            ranking_wta=None,
        )

        with (
            patch(
                "src.services.player_context_service.carregar_torneio_api",
                return_value=instancia,
            ),
            patch("src.match_history.MatchHistoryManager") as mock_history,
        ):
            mock_history.return_value.buscar_por_jogador.return_value = []
            resposta = self.partida_route.scout("Pengyu Lu", session)

        self.assertEqual(resposta.nome, "Pengyu Lu")
        self.assertIn("saibro", " ".join(resposta.dicas).lower())


if __name__ == "__main__":
    unittest.main()
