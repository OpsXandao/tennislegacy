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
        dupla = {
            "nome": "Silva / Costa",
            "jogadores": [{"nome": "Alexandre Silva"}, {"nome": "Bruno Costa"}],
        }
        self.assertTrue(self.partida_route._dupla_contem_jogador(dupla, "Alexandre Silva"))
        self.assertFalse(self.partida_route._dupla_contem_jogador(dupla, "Caio Lima"))

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


if __name__ == "__main__":
    unittest.main()
