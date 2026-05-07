import importlib
import sys
import types
import unittest
from types import SimpleNamespace


class ApiSharedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fastapi = types.ModuleType("fastapi")

        class HTTPException(Exception):
            def __init__(self, status_code, detail):
                super().__init__(detail)
                self.status_code = status_code
                self.detail = detail

        def Header(default=None, alias=None):
            return default

        fastapi.HTTPException = HTTPException
        fastapi.Header = Header
        sys.modules["fastapi"] = fastapi

        cls.shared = importlib.import_module("api.routes._shared")

    def test_resolver_save_ativo_exige_sessao_explicita(self):
        session = SimpleNamespace(nome_save_ativo=None)
        with self.assertRaises(self.shared.HTTPException) as ctx:
            self.shared.resolver_save_ativo(session)

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertEqual(ctx.exception.detail, "Sessao nao iniciada.")

    def test_carregar_contexto_jogador_reutiliza_sessao_carregada(self):
        jogador = SimpleNamespace(nome="Alexandre Silva")
        session = SimpleNamespace(nome_save_ativo="save_teste", jogador=jogador)
        nome_save, jogador_resp = self.shared.carregar_contexto_jogador(session)

        self.assertEqual(nome_save, "save_teste")
        self.assertIs(jogador_resp, jogador)


if __name__ == "__main__":
    unittest.main()
