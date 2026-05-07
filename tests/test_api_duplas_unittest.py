import importlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import patch


class RankingFake:
    def __init__(self, ranking, posicoes=None, detalhes=None):
        self.ranking = ranking
        self._posicoes = posicoes or {}
        self._detalhes = detalhes or {}

    def buscar_jogador_por_nome(self, nome):
        return self._detalhes.get(nome)

    def obter_posicao(self, nome, modalidade=None):
        return self._posicoes.get(nome)


class ApiDuplasTests(unittest.TestCase):
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
                if not hasattr(self, "torneio_tipo"):
                    self.torneio_tipo = "ATP 250"

        pydantic.BaseModel = BaseModel
        sys.modules["pydantic"] = pydantic
        cls._orig_fastapi = sys.modules.get("fastapi")
        cls._orig_pydantic = sys.modules.get("pydantic")

        cls.duplas_route = importlib.import_module("api.routes.duplas")

    @classmethod
    def tearDownClass(cls):
        for key in ["fastapi", "pydantic", "api.routes.duplas"]:
            sys.modules.pop(key, None)

    def test_busca_prefere_ranking_duplas_quando_disponivel(self):
        jogador = SimpleNamespace(nome="Alexandre Silva", genero="masculino")
        ranking_duplas = RankingFake([
            {"nome": "Bruno Costa", "nacionalidade": "[BR]", "overall": 70},
        ])
        session = SimpleNamespace(nome_save_ativo="save", jogador=jogador)

        with patch.object(
            self.duplas_route,
            "_carregar_ranking_duplas_ou_simples",
            return_value=ranking_duplas,
        ):
            resposta = self.duplas_route.buscar_parceiros(nome="bruno", session=session)

        self.assertEqual(len(resposta["parceiros"]), 1)
        self.assertEqual(resposta["parceiros"][0]["nome"], "Bruno Costa")

    def test_convidar_busca_npc_no_ranking_duplas(self):
        jogador = SimpleNamespace(
            nome="Alexandre Silva",
            genero="masculino",
            nacionalidade="[BR]",
            parceiro_duplas=None,
            vinculos_dupla={"Bruno Costa": {"partidas": 4, "vitorias": 3}},
        )
        ranking_duplas = RankingFake([
            {"nome": "Bruno Costa", "nacionalidade": "[BR]", "overall": 72}
        ])
        ranking_simples = RankingFake([], posicoes={})
        session = SimpleNamespace(nome_save_ativo="save", jogador=jogador)

        with patch.object(
            self.duplas_route, "get_caminho_ranking_duplas", return_value="duplas.json"
        ), patch.object(
            self.duplas_route, "get_caminho_ranking_save", return_value="simples.json"
        ), patch.object(
            self.duplas_route,
            "SistemaRanking",
            side_effect=[ranking_duplas, ranking_simples],
        ), patch.object(
            self.duplas_route,
            "tentar_convidar_parceiro",
            return_value=(True, "aceitou"),
        ) as mock_convite, patch.object(
            self.duplas_route, "salvar_jogo"
        ) as mock_salvar:
            resposta = self.duplas_route.convidar(
                self.duplas_route.InviteRequest(npc_nome="Bruno Costa"),
                session=session,
            )

        self.assertTrue(resposta["ok"])
        self.assertEqual(mock_convite.call_args.kwargs["ranking_pos"], 999)
        self.assertEqual(mock_convite.call_args.kwargs["vinculo"]["partidas"], 4)
        self.assertEqual(jogador.parceiro_duplas["nome"], "Bruno Costa")
        mock_salvar.assert_called_once_with("save", jogador)

    def test_convidar_faz_fallback_para_entrada_lean_sem_shard(self):
        jogador = SimpleNamespace(
            nome="Alexandre Silva",
            genero="masculino",
            nacionalidade="[BR]",
            parceiro_duplas=None,
            vinculos_dupla={"Bruno Costa": {"partidas": 2, "vitorias": 1}},
        )
        ranking_duplas = RankingFake([
            {"nome": "Bruno Costa", "nacionalidade": "[BR]", "overall": 72, "is_lean": True}
        ])
        ranking_simples = RankingFake([], posicoes={"Bruno Costa": 18})
        session = SimpleNamespace(nome_save_ativo="save", jogador=jogador)

        with patch.object(
            self.duplas_route, "get_caminho_ranking_duplas", return_value="duplas.json"
        ), patch.object(
            self.duplas_route, "get_caminho_ranking_save", return_value="simples.json"
        ), patch.object(
            self.duplas_route,
            "SistemaRanking",
            side_effect=[ranking_duplas, ranking_simples],
        ), patch.object(
            self.duplas_route,
            "tentar_convidar_parceiro",
            return_value=(False, "recusou"),
        ) as mock_convite:
            resposta = self.duplas_route.convidar(
                self.duplas_route.InviteRequest(npc_nome="Bruno Costa"),
                session=session,
            )

        self.assertFalse(resposta["ok"])
        npc = mock_convite.call_args.args[1]
        self.assertEqual(npc["nome"], "Bruno Costa")
        self.assertEqual(mock_convite.call_args.kwargs["ranking_pos"], 18)


if __name__ == "__main__":
    unittest.main()
