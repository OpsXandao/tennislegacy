import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.services import sponsorship_service


SPONSORS_FIXTURE = {
    "minor_local": {
        "nome": "Ace Local",
        "categoria": "vestuario",
        "tier": "menor",
        "pagamento_semanal": 100,
        "bonus_assinatura": 700,
        "requisito_ranking": 200,
        "req_seguidores": 0,
        "descricao": "Contrato regional.",
    },
    "master_elite": {
        "nome": "Elite Frame",
        "categoria": "raquete",
        "tier": "master",
        "pagamento_semanal": 900,
        "bonus_assinatura": 9000,
        "requisito_ranking": 15,
        "req_seguidores": 10000,
        "descricao": "Contrato global.",
    },
}


class SponsorshipServiceTests(unittest.TestCase):
    def test_listar_patrocinios_ativos_serializa_ids_e_contratos_legados(self):
        jogador = SimpleNamespace(
            patrocinios=[
                {"id": "minor_local", "semanas_restantes": 12},
                "master_elite",
            ],
            seguidores=22000,
            historico_partidas=[
                {"resultado": "V"},
                {"resultado": "D"},
                {"resultado": "V"},
            ],
            historico_torneios=[],
            trofeus=[],
            historico_ranking=[{"posicao": 18}],
        )

        ativos = sponsorship_service.listar_patrocinios_ativos(
            jogador, 18, SPONSORS_FIXTURE
        )

        self.assertEqual(len(ativos), 2)
        self.assertEqual(ativos[0]["id"], "minor_local")
        self.assertEqual(ativos[0]["semanas_restantes"], 12)
        self.assertIn("status", ativos[0])
        self.assertIn("confianca", ativos[0])
        self.assertGreaterEqual(len(ativos[0]["metas"]), 2)
        self.assertEqual(ativos[1]["nivel"], "master")

    def test_listar_patrocinios_disponiveis_informa_requisitos_e_bloqueios(self):
        jogador = SimpleNamespace(patrocinios=["minor_local"], seguidores=3000)

        with patch.object(
            sponsorship_service,
            "carregar_patrocinadores",
            return_value=SPONSORS_FIXTURE,
        ):
            disponiveis = sponsorship_service.listar_patrocinios_disponiveis(
                jogador,
                posicao=120,
                seguidores=jogador.seguidores,
                sponsors=SPONSORS_FIXTURE,
            )

        por_id = {pat["id"]: pat for pat in disponiveis}
        self.assertFalse(por_id["minor_local"]["elegivel"])
        self.assertEqual(
            por_id["minor_local"]["motivo_bloqueio"],
            "Você já tem este patrocínio.",
        )
        self.assertFalse(por_id["master_elite"]["elegivel"])
        self.assertIn("Ranking insuficiente", por_id["master_elite"]["motivo_bloqueio"])
        self.assertEqual(por_id["master_elite"]["bonus_assinatura"], 9000)

    def test_resumir_contexto_patrocinio_calcula_slots_restantes(self):
        jogador = SimpleNamespace(
            patrocinios=[
                {"id": "minor_local", "semanas_restantes": 8},
                {"id": "master_elite", "semanas_restantes": 20},
            ],
            seguidores=15000,
            historico_partidas=[],
            historico_torneios=[],
            trofeus=[],
            historico_ranking=[{"posicao": 18}],
        )

        contexto = sponsorship_service.resumir_contexto_patrocinio(
            jogador,
            posicao=18,
            sponsors=SPONSORS_FIXTURE,
        )

        self.assertEqual(contexto["ranking_atual"], 18)
        self.assertEqual(contexto["seguidores_atuais"], 15000)
        self.assertEqual(contexto["patrocinios_ativos"], 2)
        self.assertEqual(contexto["slots_menores_restantes"], 2)
        self.assertFalse(contexto["slot_master_disponivel"])

    def test_assinar_patrocinio_salva_vigencia_e_baseline(self):
        jogador = SimpleNamespace(
            patrocinios=[],
            seguidores=12000,
            historico_partidas=[{"resultado": "V"}, {"resultado": "V"}],
            historico_torneios=[],
            trofeus=[],
            historico_ranking=[],
            registrar_transacao=lambda *args, **kwargs: None,
        )

        with patch.object(
            sponsorship_service,
            "carregar_patrocinadores",
            return_value=SPONSORS_FIXTURE,
        ), patch("src.save.salvar_jogo", return_value=None):
            resultado = sponsorship_service.assinar_patrocinio(
                "save_teste",
                jogador,
                "minor_local",
                150,
            )

        self.assertTrue(resultado["ok"])
        self.assertEqual(len(jogador.patrocinios), 1)
        contrato = jogador.patrocinios[0]
        self.assertEqual(contrato["id"], "minor_local")
        self.assertEqual(contrato["duracao_semanas"], 12)
        self.assertEqual(contrato["ranking_assinatura"], 150)
        self.assertEqual(contrato["seguidores_assinatura"], 12000)
        self.assertEqual(contrato["vitorias_assinatura"], 2)


if __name__ == "__main__":
    unittest.main()
