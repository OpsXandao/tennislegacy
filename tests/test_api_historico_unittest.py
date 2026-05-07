import importlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import patch


class ApiHistoricoTests(unittest.TestCase):
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
        fastapi.HTTPException = HTTPException
        fastapi.Depends = Depends
        fastapi.Header = Header
        sys.modules["fastapi"] = fastapi

        cls.historico_route = importlib.import_module("api.routes.historico")

    def test_goat_expoe_campos_sem_erro_de_contrato(self):
        sessao = SimpleNamespace(nome_save_ativo="save", jogador=SimpleNamespace(trofeus=["ATP 250"]))
        with patch.object(
            self.historico_route,
            "carregar_historico",
            return_value={"recordes": {"semanas_no1": 1}},
        ):
            resposta = self.historico_route.obter_goat_list(sessao)

        self.assertEqual(resposta["goat_points"], 0)
        self.assertEqual(resposta["GoatPoints"], 0)
        self.assertNotIn(" GoatPoints", resposta)


if __name__ == "__main__":
    unittest.main()
