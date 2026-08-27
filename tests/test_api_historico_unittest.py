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
        with patch(
            "api.routes.historico.obter_goat",
            return_value={"goat_points": 0, "meus_titulos": []},
        ):
            resposta = self.historico_route.get_goat(sessao)

        self.assertEqual(resposta["goat_points"], 0)


class MundoServiceGoatTests(unittest.TestCase):
    def test_obter_goat_deriva_titulo_do_historico_quando_trofeus_vazio(self):
        from api.services import mundo_service

        historico = [
            {
                "torneio": "Hong Kong Open",
                "tipo": "ATP 250",
                "ano": 2026,
                "semana": 1,
                "fase_alcancada": "campeao",
                "modalidade": "simples",
            }
        ]

        with patch("src.dados.carregar_historico", return_value={"recordes": {}}):
            resposta = mundo_service.obter_goat("save", [], historico)

        self.assertEqual(resposta["goat_points"], 250)
        self.assertEqual(len(resposta["meus_titulos"]), 1)
        self.assertEqual(resposta["meus_titulos"][0]["torneio"], "Hong Kong Open")
        self.assertEqual(resposta["meus_titulos"][0]["tipo"], "ATP 250")


if __name__ == "__main__":
    unittest.main()
