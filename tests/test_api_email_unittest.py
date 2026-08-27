import importlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import patch


class ApiEmailTests(unittest.TestCase):
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

        cls.email_route = importlib.import_module("api.routes.email")

    @classmethod
    def tearDownClass(cls):
        for key in ["fastapi", "pydantic", "api.routes.email"]:
            sys.modules.pop(key, None)

    def test_inbox_nao_marca_como_lido_automaticamente(self):
        jogador = SimpleNamespace(
            caixa_email=[
                {"id": "1", "lido": False, "assunto": "Teste"},
                {"id": "2", "lido": True, "assunto": "Antigo"},
            ]
        )
        sessao = SimpleNamespace(jogador=jogador, nome_save_ativo="save")

        with patch.object(self.email_route, "salvar_jogo") as mock_salvar:
            resposta = self.email_route.listar_emails(session=sessao)

        self.assertEqual(resposta["unread_count"], 1)
        self.assertFalse(jogador.caixa_email[0]["lido"])
        mock_salvar.assert_not_called()

    def test_marcar_lidos_persiste_apenas_quando_necessario(self):
        jogador = SimpleNamespace(caixa_email=[{"id": "1", "lido": False}])
        sessao = SimpleNamespace(jogador=jogador, nome_save_ativo="save")

        with patch("api.routes.email.marcar_emails_lidos") as mock_marcar:
            resposta = self.email_route.marcar_lidos(session=sessao)

        self.assertTrue(resposta["ok"])
        mock_marcar.assert_called_once_with("save", jogador)

    def test_acao_aceitar_resolve_email_por_ref_id_quando_nao_tem_id(self):
        jogador = SimpleNamespace(
            nome="Alexandre",
            genero="masculino",
            seguidores=1000,
            patrocinios=[],
            caixa_email=[
                {
                    "tipo": "patrocinio",
                    "status": "pendente",
                    "ref_id": "clothing_regional",
                    "titulo": "Proposta",
                    "oferta": {"bonus_assinatura": 0},
                }
            ],
        )
        ranking = SimpleNamespace(obter_posicao=lambda _nome: 200)
        sessao = SimpleNamespace(
            jogador=jogador,
            nome_save_ativo="save",
            ranking_atp=ranking,
            ranking_wta=ranking,
        )
        req = self.email_route.EmailActionRequest(
            email_id="clothing_regional", acao="aceitar"
        )

        with patch("src.services.communication_service.pode_assinar_patrocinio", return_value=(True, "ok")), patch("src.save.salvar_jogo") as mock_salvar, patch.object(self.email_route, "refresh_session"):
            resposta = self.email_route.processar_email(req, session=sessao)

        self.assertTrue(resposta["ok"])
        self.assertEqual(jogador.patrocinios, ["clothing_regional"])
        self.assertEqual(jogador.caixa_email, [])
        mock_salvar.assert_called_once()

    def test_unread_count_retorna_somente_contagem(self):
        jogador = SimpleNamespace(
            caixa_email=[{"id": "1", "lido": False}, {"id": "2", "lido": True}]
        )
        sessao = SimpleNamespace(jogador=jogador, nome_save_ativo="save")

        resposta = self.email_route.obter_contagem_nao_lidos(session=sessao)

        self.assertEqual(resposta, {"unread_count": 1})


if __name__ == "__main__":
    unittest.main()
