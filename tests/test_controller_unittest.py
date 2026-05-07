import unittest
from types import SimpleNamespace
from unittest.mock import patch

import src.controller as controller


class ControllerTests(unittest.TestCase):
    def test_tratar_estado_torneio_corrompido_remove_arquivo_quando_possivel(self):
        with patch.object(controller.os, "remove") as mock_remove:
            resultado = controller._tratar_estado_torneio_corrompido(
                "save_teste", "/tmp/torneio.json"
            )

        self.assertTrue(resultado)
        mock_remove.assert_called_once_with("/tmp/torneio.json")

    def test_estado_deve_ser_ignorado_quando_torneio_nao_pertence_ao_jogador(self):
        estado = {"jogador": "NPC Qualquer"}

        self.assertTrue(controller._estado_deve_ser_ignorado(estado, "Alexandre"))
        self.assertFalse(
            controller._estado_deve_ser_ignorado(
                {"jogador": "Alexandre"}, "Alexandre"
            )
        )

    def test_fase_davis_ativa_reconhece_fases_suportadas(self):
        self.assertTrue(controller._fase_davis_ativa("qualifiers"))
        self.assertTrue(controller._fase_davis_ativa("final"))
        self.assertFalse(controller._fase_davis_ativa("finalizado"))

    def test_fase_torneio_regular_ativa_reconhece_r96(self):
        self.assertTrue(controller._fase_torneio_regular_ativa("r96"))
        self.assertFalse(controller._fase_torneio_regular_ativa("finalizado"))

    def test_executar_etapa_finalizacao_marca_chave_quando_executa(self):
        estado = {}
        finalizacao = {}

        with patch.object(
            controller, "_marcar_finalizacao_torneio"
        ) as mock_marcar:
            executou = controller._executar_etapa_finalizacao(
                "save_teste",
                "masculino",
                estado,
                finalizacao,
                "pontos_distribuidos",
                lambda: finalizacao.setdefault("acao_executada", True),
            )

        self.assertTrue(executou)
        self.assertTrue(finalizacao["acao_executada"])
        mock_marcar.assert_called_once_with(
            "save_teste", "masculino", estado, "pontos_distribuidos"
        )

    def test_executar_etapa_finalizacao_pula_quando_chave_ja_existe(self):
        estado = {}
        finalizacao = {"semana_avancada": True}

        with patch.object(
            controller, "_marcar_finalizacao_torneio"
        ) as mock_marcar:
            executou = controller._executar_etapa_finalizacao(
                "save_teste",
                "masculino",
                estado,
                finalizacao,
                "semana_avancada",
                lambda: self.fail("acao nao deveria executar"),
            )

        self.assertFalse(executou)
        mock_marcar.assert_not_called()

    def test_recarregar_jogador_pos_semana_retorna_original_quando_reload_falha(self):
        jogador = SimpleNamespace(nome="Alexandre", genero="masculino")

        with (
            patch("src.jogador.carregar_jogador", return_value=None),
            patch.object(controller, "log_erro") as mock_log,
        ):
            resultado = controller._recarregar_jogador_pos_semana(
                jogador, "save_teste", fase="final"
            )

        self.assertIs(resultado, jogador)
        mock_log.assert_called_once()

    def test_remover_arquivo_torneio_loga_e_retorna_false_em_erro(self):
        with (
            patch.object(controller.os, "remove", side_effect=OSError("falha")),
            patch.object(controller, "log_erro") as mock_log,
        ):
            resultado = controller._remover_arquivo_torneio(
                "/tmp/torneio.json",
                "save_teste",
                "final",
                "remover_torneio_finalizado",
            )

        self.assertFalse(resultado)
        mock_log.assert_called_once()

    def test_finalizar_torneio_regular_reusa_etapas_e_retorna_jogador_recarregado(self):
        jogador = SimpleNamespace(nome="Alexandre", genero="masculino")
        jogador_recarregado = SimpleNamespace(nome="Alexandre", genero="masculino")
        estado = {"jogador_vivo": False}

        with (
            patch.object(controller, "_get_estado_finalizacao", return_value={}),
            patch.object(controller, "_executar_etapa_finalizacao") as mock_etapa,
            patch.object(controller.random, "random", return_value=1.0),
            patch.object(
                controller,
                "_recarregar_jogador_pos_semana",
                return_value=jogador_recarregado,
            ) as mock_reload,
            patch.object(controller, "_remover_arquivo_torneio") as mock_remove,
        ):
            resultado = controller._finalizar_torneio_regular(
                jogador,
                "save_teste",
                "/tmp/torneio.json",
                estado,
                "final",
            )

        self.assertIs(resultado, jogador_recarregado)
        self.assertEqual(mock_etapa.call_count, 3)
        mock_reload.assert_called_once_with(jogador, "save_teste", fase="final")
        mock_remove.assert_called_once()

    def test_aplicar_progressao_natural_limpa_pendencia_no_estado(self):
        jogador = SimpleNamespace(
            genero="masculino",
            atributos={"saque": 60, "forehand": 58},
        )
        estado = {"progressao_natural_pendente": {"saque": 2}}

        with (
            patch.object(controller, "aplicar_melhorias_naturais", return_value={"saque": 62}),
            patch.object(controller, "salvar_jogo") as mock_salvar_jogo,
            patch.object(controller, "salvar_json_seguro") as mock_salvar_json,
            patch.object(controller, "print_blue"),
        ):
            aplicado = controller._aplicar_progressao_natural_pos_torneio(
                jogador, "save_teste", estado
            )

        self.assertTrue(aplicado)
        self.assertEqual(estado["progressao_natural_pendente"], {})
        mock_salvar_jogo.assert_called_once_with("save_teste", jogador)
        mock_salvar_json.assert_called_once()

    def test_fluxo_principal_mantem_jogador_em_memoria_quando_reload_falha(self):
        jogador = SimpleNamespace(nome="Alexandre", genero="masculino")
        estado = {
            "jogador": "Alexandre",
            "fase_atual": "finalizado",
            "jogador_vivo": False,
            "tipo": "ATP 250",
            "progressao_natural_pendente": {},
        }

        with (
            patch.object(controller, "get_caminho_torneio_save", return_value="/tmp/torneio.json"),
            patch.object(controller.os.path, "exists", side_effect=[True, False]),
            patch.object(controller, "carregar_estado_torneio", return_value=estado),
            patch.object(controller, "salvar_json_seguro"),
            patch.object(controller, "distribuir_pontos_torneio"),
            patch.object(controller.random, "random", return_value=1.0),
            patch("src.jogador.carregar_jogador", return_value=None),
            patch("src.calendario.avancar_semana"),
            patch.object(controller.os, "remove"),
            patch.object(controller, "menu_principal", return_value=True) as mock_menu_principal,
            patch.object(controller, "log_erro") as mock_log_erro,
        ):
            controller.fluxo_principal(jogador, "save_teste")

        self.assertEqual(mock_menu_principal.call_args_list[0].args[0], jogador)
        self.assertTrue(mock_log_erro.called)

    def test_fluxo_principal_nao_repete_finalizacao_pos_torneio_ja_marcada(self):
        jogador = SimpleNamespace(nome="Alexandre", genero="masculino")
        estado = {
            "jogador": "Alexandre",
            "fase_atual": "finalizado",
            "jogador_vivo": False,
            "tipo": "ATP 250",
            "progressao_natural_pendente": {},
            "finalizacao_controller": {
                "progressao_aplicada": True,
                "pontos_distribuidos": True,
                "entrevista_processada": True,
                "semana_avancada": True,
            },
        }

        with (
            patch.object(controller, "get_caminho_torneio_save", return_value="/tmp/torneio.json"),
            patch.object(controller.os.path, "exists", side_effect=[True, False]),
            patch.object(controller, "carregar_estado_torneio", return_value=estado),
            patch.object(controller, "_aplicar_progressao_natural_pos_torneio") as mock_progressao,
            patch.object(controller, "salvar_json_seguro"),
            patch.object(controller, "distribuir_pontos_torneio") as mock_pontos,
            patch.object(controller.random, "random", return_value=0.0),
            patch("src.jogador.carregar_jogador", return_value=jogador),
            patch("src.calendario.avancar_semana") as mock_avancar,
            patch.object(controller.os, "remove"),
            patch.object(controller, "menu_principal", return_value=True),
        ):
            controller.fluxo_principal(jogador, "save_teste")

        mock_progressao.assert_not_called()
        mock_pontos.assert_not_called()
        mock_avancar.assert_not_called()

    def test_fluxo_principal_marca_etapa_apos_distribuir_pontos(self):
        jogador = SimpleNamespace(nome="Alexandre", genero="masculino")
        estado = {
            "jogador": "Alexandre",
            "fase_atual": "finalizado",
            "jogador_vivo": False,
            "tipo": "ATP 250",
            "progressao_natural_pendente": {},
        }

        with (
            patch.object(controller, "get_caminho_torneio_save", return_value="/tmp/torneio.json"),
            patch.object(controller.os.path, "exists", side_effect=[True, False]),
            patch.object(controller, "carregar_estado_torneio", return_value=estado),
            patch.object(controller, "_aplicar_progressao_natural_pos_torneio"),
            patch.object(controller, "_marcar_finalizacao_torneio") as mock_marcar,
            patch.object(controller, "distribuir_pontos_torneio"),
            patch.object(controller.random, "random", return_value=1.0),
            patch("src.jogador.carregar_jogador", return_value=jogador),
            patch("src.calendario.avancar_semana"),
            patch.object(controller.os, "remove"),
            patch.object(controller, "menu_principal", return_value=True),
        ):
            controller.fluxo_principal(jogador, "save_teste")

        chaves = [call.args[3] for call in mock_marcar.call_args_list]
        self.assertIn("pontos_distribuidos", chaves)
        self.assertIn("semana_avancada", chaves)


if __name__ == "__main__":
    unittest.main()
