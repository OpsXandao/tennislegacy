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
            ]
        )

        ativos = sponsorship_service.listar_patrocinios_ativos(
            jogador, SPONSORS_FIXTURE
        )

        self.assertEqual(len(ativos), 2)
        self.assertEqual(ativos[0]["id"], "minor_local")
        self.assertEqual(ativos[0]["semanas_restantes"], 12)
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


if __name__ == "__main__":
    unittest.main()
