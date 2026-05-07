"""
Testes unitários para o pipeline de avanço semanal (SemanaContext + etapas).

Usa mocks leves para isolar cada etapa sem dependências de disco.
"""

import unittest
from dataclasses import dataclass, field
from typing import Optional
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Helpers: fake objects para isolar testes do disco
# ---------------------------------------------------------------------------


def _make_jogador(
    genero="masculino", fadiga=20, energia=80, semana=1, status_lesao=None
):
    j = MagicMock()
    j.genero = genero
    j.fadiga = fadiga
    j.energia = energia
    j.semana = semana
    j.nome = "Jogador Teste"
    j.modalidade_atual = "simples"
    j.parceiro_duplas = None
    j.status_lesao = status_lesao or {
        "lesionado": False,
        "semanas_restantes": 0,
        "nivel": "saudavel",
        "penalidade_atributos": 0.0,
    }
    return j


def _make_ranking():
    r = MagicMock()
    r.ordenar = MagicMock()
    return r


def _make_context(
    semana_atual=10,
    ano_atual=2026,
    jogador_em_torneio=False,
    jogador_participou=False,
):
    from src.services.season_service import SemanaContext

    jogador = _make_jogador()
    ranking = _make_ranking()
    rankings = {
        "simples_atp": _make_ranking(),
        "simples_wta": _make_ranking(),
        "duplas_atp": _make_ranking(),
        "duplas_wta": _make_ranking(),
    }
    temporada = {"semana": semana_atual, "ano": ano_atual}

    return SemanaContext(
        nome_save="test_save",
        temporada=temporada,
        jogador=jogador,
        rankings=rankings,
        ranking=ranking,
        semana_atual=semana_atual,
        ano_atual=ano_atual,
        player_active_tournament_state=None,
        jogador_em_torneio_ativo=jogador_em_torneio,
        jogador_participou=jogador_participou,
    )


# ---------------------------------------------------------------------------
# Testes de SemanaContext
# ---------------------------------------------------------------------------


class SemanaContextTests(unittest.TestCase):
    def test_campos_preenchidos_por_padrao(self):
        from src.services.season_service import SemanaContext

        ctx = _make_context()

        self.assertEqual(ctx.semana_nova, 0)
        self.assertEqual(ctx.ano_novo, 0)
        self.assertIsNone(ctx.torneio_info_semana)
        self.assertEqual(ctx.resumo_campeoes, [])
        self.assertEqual(ctx.eventos_api, [])

    def test_campos_customizaveis_apos_construcao(self):
        ctx = _make_context(semana_atual=5, ano_atual=2027)

        self.assertEqual(ctx.temporada["semana"], 5)
        self.assertEqual(ctx.ano_atual, 2027)

    def test_eventos_api_lista_mutavel_independente(self):
        """Cada instância tem sua própria lista (não compartilhada via default mutable)."""
        ctx_a = _make_context()
        ctx_b = _make_context()

        ctx_a.eventos_api.append("evento_a")
        self.assertEqual(len(ctx_b.eventos_api), 0)

    def test_resumo_campeoes_lista_mutavel_independente(self):
        ctx_a = _make_context()
        ctx_b = _make_context()

        ctx_a.resumo_campeoes.append({"tour": "atp", "torneio": "Roland Garros"})
        self.assertEqual(len(ctx_b.resumo_campeoes), 0)


# ---------------------------------------------------------------------------
# Testes do pipeline — etapas individuais
# ---------------------------------------------------------------------------


class AvancarCalendarioTests(unittest.TestCase):
    def test_incrementa_semana(self):
        from src.services.season_service import _avancar_calendario

        ctx = _make_context(semana_atual=10)

        with patch("src.calendario._processar_virada_ano"):
            _avancar_calendario(ctx)

        self.assertEqual(ctx.temporada["semana"], 11)
        self.assertEqual(ctx.semana_nova, 11)

    def test_adiciona_evento_de_semana(self):
        from src.services.season_service import _avancar_calendario

        ctx = _make_context(semana_atual=3)

        with patch("src.calendario._processar_virada_ano"):
            _avancar_calendario(ctx)

        texto_evento = " ".join(ctx.eventos_api)
        self.assertIn("4", texto_evento)

    def test_virada_ano_chamada(self):
        from src.services.season_service import _avancar_calendario

        ctx = _make_context()

        with patch("src.calendario._processar_virada_ano") as mock_virada:
            _avancar_calendario(ctx)

        mock_virada.assert_called_once()


class ProcessarJogadorTests(unittest.TestCase):
    def test_descanso_reduz_fadiga(self):
        from src.services.season_service import _processar_jogador

        ctx = _make_context(jogador_participou=False)
        ctx.jogador.fadiga = 40
        ctx.jogador.energia = 70

        with patch("src.calendario._atualizar_recuperacao_jogador", return_value=[]):
            _processar_jogador(ctx)

        self.assertEqual(ctx.jogador.fadiga, 20)
        self.assertEqual(ctx.jogador.energia, 85)

    def test_descanso_energia_nao_passa_100(self):
        from src.services.season_service import _processar_jogador

        ctx = _make_context(jogador_participou=False)
        ctx.jogador.fadiga = 5
        ctx.jogador.energia = 90

        with patch("src.calendario._atualizar_recuperacao_jogador", return_value=[]):
            _processar_jogador(ctx)

        self.assertEqual(ctx.jogador.energia, 100)

    def test_participou_nao_aplica_bonus_descanso(self):
        from src.services.season_service import _processar_jogador

        ctx = _make_context(jogador_participou=True)
        ctx.jogador.fadiga = 40
        ctx.jogador.energia = 70

        with patch("src.calendario._atualizar_recuperacao_jogador", return_value=[]):
            _processar_jogador(ctx)

        # fadiga e energia inalterados pelo bônus de descanso
        self.assertEqual(ctx.jogador.fadiga, 40)
        self.assertEqual(ctx.jogador.energia, 70)

    def test_eventos_recuperacao_adicionados(self):
        from src.services.season_service import _processar_jogador

        ctx = _make_context(jogador_participou=True)
        eventos_mock = ["Recuperação aplicada."]

        with patch(
            "src.calendario._atualizar_recuperacao_jogador",
            return_value=eventos_mock,
        ):
            _processar_jogador(ctx)

        self.assertIn("Recuperação aplicada.", ctx.eventos_api)


class ExpirarPontosTests(unittest.TestCase):
    def test_atualiza_semana_do_jogador(self):
        from src.services.season_service import _expirar_pontos

        ctx = _make_context()
        ctx.semana_nova = 15

        with patch("src.calendario._processar_expiracao_ranking"):
            _expirar_pontos(ctx)

        self.assertEqual(ctx.jogador.semana, 15)

    def test_expiracao_chamada_com_parametros_corretos(self):
        from src.services.season_service import _expirar_pontos

        ctx = _make_context()
        ctx.semana_nova = 7
        ctx.ano_novo = 2026

        with patch("src.calendario._processar_expiracao_ranking") as mock_exp:
            _expirar_pontos(ctx)

        mock_exp.assert_called_once_with("test_save", 7, 2026)

    def test_recarrega_ranking_principal_apos_expirar_pontos(self):
        from src.services.season_service import _expirar_pontos

        ctx = _make_context()
        ctx.semana_nova = 11
        ctx.ano_novo = 2026
        ranking_novo = _make_ranking()
        ranking_novo.buscar_jogador_por_nome.return_value = {"pontos_detalhados": []}

        ctx.ranking.buscar_jogador_por_nome.return_value = {
            "pontos_detalhados": [{"pontos": 120}]
        }

        with (
            patch("src.calendario._processar_expiracao_ranking"),
            patch(
                "src.repositories.ranking_repository.load_singles_ranking",
                return_value=ranking_novo,
            ) as mock_reload,
        ):
            _expirar_pontos(ctx)

        mock_reload.assert_called_once_with("test_save", ctx.jogador.genero)
        self.assertIs(ctx.ranking, ranking_novo)
        self.assertIs(ctx.rankings["simples_atp"], ranking_novo)
        self.assertEqual(ctx.pontos_expirados, 120)


class InicializarNovaSemanaTests(unittest.TestCase):
    def test_resetar_estado_semanal_jogador_limpa_duplas(self):
        from src.services.season_service import _resetar_estado_semanal_jogador

        ctx = _make_context()
        ctx.jogador.modalidade_atual = "duplas"
        ctx.jogador.parceiro_duplas = "Andre Agassi"

        _resetar_estado_semanal_jogador(ctx)

        self.assertEqual(ctx.jogador.modalidade_atual, "simples")
        self.assertIsNone(ctx.jogador.parceiro_duplas)

    def test_registrar_historico_ranking_inicializa_lista_quando_ausente(self):
        from src.services.season_service import _registrar_historico_ranking

        ctx = _make_context()
        if hasattr(ctx.jogador, "historico_ranking"):
            del ctx.jogador.historico_ranking
        ctx.semana_nova = 14
        ctx.ano_novo = 2026
        ctx.nova_posicao_ranking = 22

        _registrar_historico_ranking(ctx, 410)

        self.assertEqual(
            ctx.jogador.historico_ranking,
            [{"semana": 14, "ano": 2026, "posicao": 22, "pontos": 410}],
        )

    def test_modalidade_resetada_para_simples(self):
        from src.services.season_service import _inicializar_nova_semana

        ctx = _make_context()
        ctx.jogador.modalidade_atual = "duplas"
        ctx.semana_nova = 2

        with (
            patch("src.save.salvar_jogo"),
            patch("src.save.tirar_snapshot_carreira"),
            patch("src.calendario._inicializar_torneios_nova_semana"),
            patch("src.dados.salvar_temporada"),
        ):
            _inicializar_nova_semana(ctx)

        self.assertEqual(ctx.jogador.modalidade_atual, "simples")

    def test_parceiro_duplas_resetado(self):
        from src.services.season_service import _inicializar_nova_semana

        ctx = _make_context()
        ctx.jogador.parceiro_duplas = "Andre Agassi"
        ctx.semana_nova = 3

        with (
            patch("src.save.salvar_jogo"),
            patch("src.save.tirar_snapshot_carreira"),
            patch("src.calendario._inicializar_torneios_nova_semana"),
            patch("src.dados.salvar_temporada"),
        ):
            _inicializar_nova_semana(ctx)

        self.assertIsNone(ctx.jogador.parceiro_duplas)

    def test_snapshot_chamado_em_semanas_1_e_26(self):
        from src.services.season_service import _inicializar_nova_semana

        for semana_especial in [1, 26]:
            ctx = _make_context()
            ctx.jogador.semana = semana_especial
            ctx.semana_nova = semana_especial
            ctx.ano_novo = 2027
            ranking_novo = _make_ranking()
            ranking_novo.buscar_jogador_por_nome.return_value = {"pontos_ranking": 250}
            ranking_novo.obter_posicao.return_value = 17

            with (
                patch("src.save.salvar_jogo"),
                patch("src.save.tirar_snapshot_carreira") as mock_snap,
                patch("src.calendario._inicializar_torneios_nova_semana"),
                patch("src.dados.salvar_temporada"),
                patch(
                    "src.repositories.ranking_repository.load_singles_ranking",
                    return_value=ranking_novo,
                ),
                patch("src.jogador.obter_rival_info", return_value=None),
            ):
                _inicializar_nova_semana(ctx)

            mock_snap.assert_called_once_with(ctx.jogador, ano=2027)

    def test_snapshot_nao_chamado_em_outras_semanas(self):
        from src.services.season_service import _inicializar_nova_semana

        ctx = _make_context()
        ctx.jogador.semana = 10
        ctx.semana_nova = 10
        ctx.ano_novo = 2026
        ranking_novo = _make_ranking()
        ranking_novo.buscar_jogador_por_nome.return_value = {"pontos_ranking": 80}
        ranking_novo.obter_posicao.return_value = 44

        with (
            patch("src.save.salvar_jogo"),
            patch("src.save.tirar_snapshot_carreira") as mock_snap,
            patch("src.calendario._inicializar_torneios_nova_semana"),
            patch("src.dados.salvar_temporada"),
            patch(
                "src.repositories.ranking_repository.load_singles_ranking",
                return_value=ranking_novo,
            ),
            patch("src.jogador.obter_rival_info", return_value=None),
        ):
            _inicializar_nova_semana(ctx)

        mock_snap.assert_not_called()

    def test_historico_ranking_usa_ranking_recarregado(self):
        from src.services.season_service import _inicializar_nova_semana

        ctx = _make_context()
        ctx.jogador.historico_ranking = []
        ctx.jogador.semana = 12
        ctx.semana_nova = 13
        ctx.ano_novo = 2026
        ranking_novo = _make_ranking()
        ranking_novo.buscar_jogador_por_nome.return_value = {"pontos_ranking": 321}
        ranking_novo.obter_posicao.return_value = 29

        with (
            patch("src.save.salvar_jogo"),
            patch("src.save.tirar_snapshot_carreira"),
            patch("src.calendario._inicializar_torneios_nova_semana"),
            patch("src.dados.salvar_temporada"),
            patch(
                "src.repositories.ranking_repository.load_singles_ranking",
                return_value=ranking_novo,
            ),
            patch("src.jogador.obter_rival_info", return_value=None),
        ):
            _inicializar_nova_semana(ctx)

        self.assertEqual(ctx.nova_posicao_ranking, 29)
        self.assertEqual(
            ctx.jogador.historico_ranking[-1],
            {
                "semana": 13,
                "ano": 2026,
                "posicao": 29,
                "pontos": 321,
            },
        )


# ---------------------------------------------------------------------------
# Teste de integração leve — advance_week retorna estrutura esperada
# ---------------------------------------------------------------------------


class AdvanceWeekContractTests(unittest.TestCase):
    def test_retorna_chaves_obrigatorias(self):
        from src.services.season_service import advance_week

        with (
            patch("src.services.season_service._build_context") as mock_build,
            patch("src.services.season_service.PIPELINE", []),
        ):
            ctx = _make_context(semana_atual=10)
            ctx.temporada = {"semana": 11, "ano": 2026}
            ctx.eventos_api = ["Semana avancada."]
            ctx.resumo_campeoes = []
            mock_build.return_value = ctx

            result = advance_week("test_save")

        self.assertIn("semana", result)
        self.assertIn("ano", result)
        self.assertIn("recuperacao", result)
        self.assertIn("torneios_disponiveis", result)
        self.assertIn("eventos", result)
        self.assertIn("pontos_expirados", result)
        self.assertIn("nova_posicao_ranking", result)
        self.assertIn("resumo_mundial", result)
        self.assertIn("campeoes", result["resumo_mundial"])

    def test_semana_incrementada_no_resultado(self):
        from src.services.season_service import advance_week

        with (
            patch("src.services.season_service._build_context") as mock_build,
            patch("src.services.season_service.PIPELINE", []),
        ):
            ctx = _make_context(semana_atual=5)
            ctx.temporada = {"semana": 6, "ano": 2026}
            ctx.eventos_api = []
            ctx.resumo_campeoes = []
            mock_build.return_value = ctx

            result = advance_week("test_save")

        self.assertEqual(result["semana"], 6)

    def test_retorna_payload_estruturado_do_hub(self):
        from src.services.season_service import advance_week

        with (
            patch("src.services.season_service._build_context") as mock_build,
            patch("src.services.season_service.PIPELINE", []),
        ):
            ctx = _make_context(semana_atual=12)
            ctx.temporada = {"semana": 13, "ano": 2026}
            ctx.recuperacao = {
                "fadiga_antes": 42.0,
                "fadiga_depois": 18.0,
                "lesao_status": "saudavel",
            }
            ctx.torneios_disponiveis = [{"nome": "Monte Carlo", "tipo": "ATP 1000"}]
            ctx.eventos_api = ["Semana avancada."]
            ctx.pontos_expirados = 90
            ctx.nova_posicao_ranking = 37
            ctx.resumo_campeoes = []
            mock_build.return_value = ctx

            result = advance_week("test_save")

        self.assertEqual(result["recuperacao"]["fadiga_antes"], 42.0)
        self.assertEqual(result["torneios_disponiveis"][0]["nome"], "Monte Carlo")
        self.assertEqual(result["pontos_expirados"], 90)
        self.assertEqual(result["nova_posicao_ranking"], 37)

    def test_retorna_rival_info_quando_presente_no_contexto(self):
        from src.services.season_service import advance_week

        with (
            patch("src.services.season_service._build_context") as mock_build,
            patch("src.services.season_service.PIPELINE", []),
        ):
            ctx = _make_context(semana_atual=20)
            ctx.temporada = {"semana": 21, "ano": 2026}
            ctx.recuperacao = {}
            ctx.torneios_disponiveis = []
            ctx.eventos_api = []
            ctx.pontos_expirados = 0
            ctx.nova_posicao_ranking = 44
            ctx.rival_info = {
                "nome": "Rival ATP",
                "ranking": 28,
                "h2h": {"v": 1, "d": 3},
            }
            ctx.resumo_campeoes = []
            mock_build.return_value = ctx

            result = advance_week("test_save")

        self.assertEqual(result["rival_info"]["nome"], "Rival ATP")
        self.assertEqual(result["rival_info"]["h2h"]["d"], 3)

    def test_pipeline_todas_etapas_chamadas(self):
        """Verifica que o pipeline chama todas as etapas em ordem."""
        from src.services.season_service import advance_week

        chamadas = []
        etapa_a = lambda ctx: chamadas.append("a")
        etapa_b = lambda ctx: chamadas.append("b")
        etapa_c = lambda ctx: chamadas.append("c")

        with (
            patch("src.services.season_service._build_context") as mock_build,
            patch(
                "src.services.season_service.PIPELINE",
                [etapa_a, etapa_b, etapa_c],
            ),
        ):
            ctx = _make_context()
            ctx.temporada = {"semana": 1, "ano": 2026}
            ctx.eventos_api = []
            ctx.resumo_campeoes = []
            mock_build.return_value = ctx

            advance_week("test_save")

        self.assertEqual(chamadas, ["a", "b", "c"])


if __name__ == "__main__":
    unittest.main()
