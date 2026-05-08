import importlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.match_config import ConfigPartida
from src.constants.match_constants import EstrategiaSaque, IntencaoPonto, TipoSaque


class ApiPartidaResumeTests(unittest.TestCase):
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
        fastapi.HTTPException = HTTPException
        fastapi.Depends = Depends
        fastapi.Header = Header
        sys.modules["fastapi"] = fastapi

        pydantic = types.ModuleType("pydantic")

        class BaseModel:
            def __init__(self, **kwargs):
                for chave, valor in kwargs.items():
                    setattr(self, chave, valor)

        pydantic.BaseModel = BaseModel
        sys.modules["pydantic"] = pydantic

        cls.partida_route = importlib.import_module("api.routes.partida")

    def test_obter_ativa_delega_para_servico(self):
        session = SimpleNamespace(nome_save_ativo="save_teste")
        with patch.object(
            self.partida_route, "get_active_match", return_value={"partida_id": "p1", "adversario": {"nome": "NPC"}}
        ):
            resposta = self.partida_route.obter_ativa(session)

        self.assertEqual(resposta["partida_id"], "p1")
        self.assertEqual(resposta["adversario"]["nome"], "NPC")

    def test_from_snapshot_restaura_estrategias_persistidas(self):
        runtime_module = importlib.import_module("api.routes._match_runtime")
        payload = {
            "partida_id": "p1",
            "save_name": "save_teste",
            "modo": "manual",
            "adversario": {
                "nome": "NPC",
                "energia": 91,
                "atributos": {"saque": 70, "forehand": 68},
                "atributos_psicologicos": {"agressividade": 62},
            },
            "torneio_info": {"nome": "Roma"},
            "config": dict(ConfigPartida(superficie="saibro").__dict__),
            "modalidade": "simples",
            "estrategia_j": {
                "estilo": "atacar_na_rede",
                "saque": "forcar",
                "saque_tipo": "agressivo",
                "intencao": "arriscar",
            },
            "estrategia_a": {
                "estilo": "atacar_pelo_meio",
                "saque": "seguro",
                "saque_tipo": "variado",
                "intencao": "defensivo",
            },
            "stats_j": {},
            "stats_a": {},
            "contexto_partida": {"superficie": "saibro"},
            "sets": [0, 0],
            "games": [0, 0],
            "pontos": [0, 0],
            "set_scores": [],
            "sacador": "j",
        }
        jogador = SimpleNamespace(
            nome="Jogador",
            energia=100,
            moral=70,
            ritmo_jogo=50,
            fadiga=0,
            atributos={"saque": 65},
            atributos_psicologicos={"agressividade": 55},
            rivalidades={},
        )

        with patch.object(runtime_module, "carregar_jogador", return_value=jogador):
            runtime = runtime_module.MatchRuntime.from_snapshot(payload)

        self.assertEqual(runtime.estrategia_j["estilo"], "atacar_na_rede")
        self.assertEqual(runtime.estrategia_j["saque"], EstrategiaSaque.FORCAR)
        self.assertEqual(runtime.estrategia_j["saque_tipo"], TipoSaque.AGRESSIVO)
        self.assertEqual(runtime.estrategia_j["intencao"], IntencaoPonto.ARRISCAR)
        self.assertEqual(runtime.estrategia_a["estilo"], "atacar_pelo_meio")
        self.assertEqual(runtime.estrategia_a["intencao"], IntencaoPonto.DEFENSIVO)


if __name__ == "__main__":
    unittest.main()
