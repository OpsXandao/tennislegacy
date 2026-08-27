import unittest
from types import SimpleNamespace

from src.torneio_core import Torneio


class TorneioCoreResilienceTests(unittest.TestCase):
    def test_carregar_estado_normaliza_campos_minimos_em_save_legado(self):
        torneio = Torneio.__new__(Torneio)
        torneio.nome_torneio_atual = "Evento Teste"
        torneio.nome_save = "save_teste"
        torneio.semana = 5
        torneio.jogador_nome = "Alexandre"
        torneio.tournament_data = {"tipo": "ATP 250", "qualificacao": False}
        torneio.genero = "masculino"
        torneio._estado_cache = None
        torneio._estado_cache_mtime = None
        torneio.caminho_json = "/tmp/inexistente_torneio_core_resilience.json"
        torneio._get_first_main_draw_phase = lambda: "r32"
        torneio._normalizar_agenda_dia = lambda estado: None

        import src.torneio_core as torneio_core

        original_loader = torneio_core.carregar_estado_torneio
        try:
            torneio_core.carregar_estado_torneio = lambda *args, **kwargs: {
                "torneio": "Evento Teste"
            }
            estado = torneio._carregar_estado()
        finally:
            torneio_core.carregar_estado_torneio = original_loader

        self.assertEqual(estado["fase_atual"], "r32")
        self.assertEqual(estado["rodadas"], {})
        self.assertEqual(estado["resultados"], {})
        self.assertEqual(estado["agenda_dia"], {})
        self.assertEqual(estado["entry_status"], {})

    def test_superficie_expoe_quadra_do_tournament_data(self):
        torneio = Torneio.__new__(Torneio)
        torneio.tournament_data = {"quadra": "saibro"}

        self.assertEqual(torneio.superficie, "saibro")

    def test_atualizar_fase_ignora_chave_vazia(self):
        torneio = Torneio.__new__(Torneio)
        estado = {
            "fase_atual": "r32",
            "rodadas": {"r32": []},
            "resultados": {"r32": []},
        }

        torneio._atualizar_fase_se_necessario(estado)

        self.assertEqual(estado["fase_atual"], "r32")

    def test_simular_npcs_na_fase_atual_ignora_torneio_finalizado(self):
        torneio = Torneio.__new__(Torneio)
        torneio._carregar_estado = lambda pular_leitura_arquivo=False: {
            "fase_atual": "finalizado"
        }

        chamado = {"valor": False}

        def _falhar(*args, **kwargs):
            chamado["valor"] = True
            raise AssertionError("nao deveria simular")

        torneio._processar_simulacao_rodada = _falhar

        torneio.simular_npcs_na_fase_atual("Alexandre")

        self.assertFalse(chamado["valor"])

    def test_simular_npcs_remove_confrontos_mesmo_com_listas_no_estado(self):
        torneio = Torneio.__new__(Torneio)
        estado = {
            "fase_atual": "qualy_1",
            "rodadas": {
                "qualy_1": [
                    [{"nome": "Alexandre"}, {"nome": "Jie Cui"}],
                    [{"nome": "Npc A"}, {"nome": "Npc B"}],
                    [{"nome": "Npc C"}, {"nome": "Npc D"}],
                ]
            },
            "resultados": {"qualy_1": []},
        }
        salvo = {}
        torneio._carregar_estado = lambda pular_leitura_arquivo=False: estado
        torneio._salvar_estado = lambda novo_estado: salvo.update(novo_estado)
        torneio._processar_simulacao_rodada = lambda confrontos: [
            {
                "jogador_a": confrontos[0][0],
                "jogador_b": confrontos[0][1],
                "vencedor": confrontos[0][0],
            },
            {
                "jogador_a": confrontos[1][0],
                "jogador_b": confrontos[1][1],
                "vencedor": confrontos[1][1],
            },
        ]

        torneio.simular_npcs_na_fase_atual("Alexandre")

        self.assertEqual(
            salvo["rodadas"]["qualy_1"],
            [[{"nome": "Alexandre"}, {"nome": "Jie Cui"}]],
        )
        self.assertEqual(len(salvo["resultados"]["qualy_1"]), 2)

    def test_desistir_do_torneio_marca_fase_saida_e_registra_walkover(self):
        torneio = Torneio.__new__(Torneio)
        torneio.jogador_nome = "Alexandre"
        torneio.garantir_dados_completos = lambda jogador: jogador
        estado = {
            "fase_atual": "quartas",
            "jogador": "Alexandre",
            "jogador_vivo": True,
            "rodadas": {"quartas": [({"nome": "Alexandre"}, {"nome": "Rival"})]},
            "resultados": {"quartas": []},
            "direct_entries": [{"nome": "Alexandre"}, {"nome": "Rival"}],
        }
        salvo = {}
        torneio._carregar_estado = lambda pular_leitura_arquivo=False: estado
        torneio._salvar_estado = lambda novo_estado: salvo.update(novo_estado)

        resultado = torneio.desistir_do_torneio()

        self.assertTrue(resultado)
        self.assertFalse(salvo["jogador_vivo"])
        self.assertTrue(salvo["desistencia_jogador"])
        self.assertEqual(salvo["jogador_fase_saida"], "quartas")
        self.assertEqual(salvo["rodadas"]["quartas"], [])
        self.assertEqual(salvo["resultados"]["quartas"][0]["vencedor"]["nome"], "Rival")
        self.assertEqual(salvo["resultados"]["quartas"][0]["resultado"], "W.O.")
        self.assertFalse(salvo["direct_entries"][0]["vivo"])
        self.assertEqual(salvo["direct_entries"][0]["fase_saida"], "quartas")

    def test_simular_torneio_restante_recarrega_estado_apos_walkover(self):
        torneio = Torneio.__new__(Torneio)
        torneio.jogador_nome = "Alexandre"
        torneio._perfil = {"vagas_qualy": 4, "merge_transitions": set()}
        torneio.garantir_dados_completos = lambda jogador: jogador
        torneio._fases_ordem = lambda: ["quartas", "final"]
        torneio._is_merge_phase_to_main_draw = lambda fase, proxima: False
        estado = {
            "fase_atual": "quartas",
            "jogador": "Alexandre",
            "jogador_vivo": True,
            "rodadas": {"quartas": [({"nome": "Alexandre"}, {"nome": "Rival"})]},
            "resultados": {"quartas": []},
            "direct_entries": [{"nome": "Alexandre"}, {"nome": "Rival"}],
        }

        def _carregar(_pular_leitura_arquivo=False):
            return estado

        def _salvar(novo_estado):
            copia = dict(novo_estado)
            estado.clear()
            estado.update(copia)

        torneio._carregar_estado = _carregar
        torneio._salvar_estado = _salvar
        torneio.simular_npcs_na_fase_atual = lambda nome_jogador: None

        campeao = torneio.simular_torneio_restante()

        self.assertEqual(estado["fase_atual"], "finalizado")
        self.assertFalse(estado["jogador_vivo"])
        self.assertEqual(len(estado["resultados"]["quartas"]), 1)
        self.assertEqual(estado.get("campeao_simples"), "Rival")
        self.assertEqual(campeao, estado.get("campeao_simples"))

    def test_montar_qualifying_nao_quebra_com_numero_impar(self):
        torneio = Torneio.__new__(Torneio)
        torneio.jogador_nome = "Alexandre"
        torneio.jogador_nacionalidade = "BRA"
        torneio._get_bot_pool = lambda quantidade: []
        torneio.garantir_dados_completos = lambda jogador: jogador

        confrontos = torneio._montar_qualifying(
            [{"nome": "Alexandre"}],
            vagas_qualy=1,
            fases_qualy=[],
            incluir_jogador_principal=False,
        )

        self.assertEqual(confrontos, [])

    def test_jogar_qualy_usa_simulacao_real_em_vez_de_avancar_cabeca_de_chave(self):
        torneio = Torneio.__new__(Torneio)
        torneio.best_of_sets = 3
        torneio.tournament_data = {"quadra": "saibro"}
        torneio._is_finals = lambda: False
        torneio._is_davis_cup = lambda: False
        torneio._fases_qualy = lambda: ["qualy_1"]
        torneio._perfil = {"vagas_qualy": 2}
        torneio._montar_qualifying = lambda *args, **kwargs: [
            ({"nome": "Seed 1"}, {"nome": "Qualifier A"}),
            ({"nome": "Seed 2"}, {"nome": "Qualifier B"}),
        ]

        import src.torneio_core as torneio_core

        original = torneio_core.simular_partida_npc_basica
        try:
            torneio_core.simular_partida_npc_basica = (
                lambda a, b, best_of_sets, superficie=None: (
                    b,
                    a,
                    "placar",
                    2,
                    0,
                )
            )
            vencedores = torneio.jogar_qualy([{"nome": "X"}])
        finally:
            torneio_core.simular_partida_npc_basica = original

        self.assertEqual(
            [j["nome"] for j in vencedores], ["Qualifier A", "Qualifier B"]
        )

    def test_garantir_dados_completos_aceita_objeto_jogador(self):
        class RankingFake:
            def buscar_jogador_por_nome(self, nome):
                return None

        from src.torneio_utils import garantir_dados_completos

        jogador = SimpleNamespace(nome="Alexandre Paiva", nacionalidade="[BR] Brasil")

        dados = garantir_dados_completos(jogador, RankingFake())

        self.assertEqual(dados["nome"], "Alexandre Paiva")
        self.assertEqual(dados["nacionalidade"], "[BR] Brasil")

    def test_iniciar_torneio_com_qualy_ativo_comeca_no_qualy(self):
        torneio = Torneio.__new__(Torneio)
        torneio.tournament_data = {"tipo": "ATP 250", "qualificacao": True}
        torneio._perfil = {
            "draw_size_main": 28,
            "vagas_qualy": 4,
            "qualy_phases": ["qualy_1", "qualy_2"],
            "main_draw_first_phase": "pre_oitavas",
        }
        torneio._ultima_entry_info = {
            "status_entry": {"Alexandre": "Qualifying"},
            "alternates": [],
        }
        torneio.escolher_participantes = lambda jogadores: (
            [{"nome": "Main A"}, {"nome": "Main B"}],
            [{"nome": "Qualy A"}, {"nome": "Qualy B"}],
        )
        torneio._carregar_estado = lambda pular_leitura_arquivo=False: {
            "rodadas": {},
            "resultados": {},
        }
        torneio._fases_qualy = lambda: ["qualy_1", "qualy_2"]
        torneio._get_first_main_draw_phase = lambda: "pre_oitavas"
        torneio.garantir_dados_completos = lambda jogador: jogador
        torneio._aplicar_entry_info_estado = lambda estado, entry_info: estado.update(
            {"entry_status": entry_info.get("status_entry", {})}
        )
        torneio._montar_qualifying = lambda *args, **kwargs: [
            ({"nome": "Qualy A"}, {"nome": "Qualy B"})
        ]
        torneio._montar_rodada_inicial_main_draw = (
            lambda estado, jogadores: estado.setdefault("rodadas", {}).update(
                {"pre_oitavas": [({"nome": "Main A"}, {"nome": "Main B"})]}
            )
        )
        salvo = {}
        torneio._salvar_estado = lambda estado: salvo.update(estado)

        torneio.iniciar_torneio("Hong Kong Open", [])

        self.assertEqual(salvo["fase_atual"], "qualy_1")
        self.assertIn("qualy_1", salvo["rodadas"])
        self.assertNotIn("pre_oitavas", salvo["rodadas"])
        self.assertEqual(salvo["entry_status"], {"Alexandre": "Qualifying"})

    def test_atualizar_fase_mescla_classificados_do_qualy_na_chave_principal(self):
        torneio = Torneio.__new__(Torneio)
        torneio.nome_save = "save_teste"
        torneio.jogador_nome = "Alexandre"
        torneio._perfil = {
            "vagas_qualy": 4,
            "merge_transitions": {("qualy_2", "pre_oitavas")},
        }
        torneio._fases_ordem = lambda: ["qualy_1", "qualy_2", "pre_oitavas", "oitavas"]
        torneio._is_merge_phase_to_main_draw = lambda fase, proxima: (
            fase,
            proxima,
        ) == ("qualy_2", "pre_oitavas")
        chamado = {}
        torneio._montar_main_draw_a_partir_do_qualy = (
            lambda estado, classificados: chamado.update(
                {
                    "classificados": classificados,
                    "direct_entries": list(estado.get("direct_entries", [])),
                }
            )
        )

        estado = {
            "fase_atual": "qualy_2",
            "rodadas": {"qualy_2": []},
            "resultados": {
                "qualy_2": [
                    {
                        "jogador_a": {"nome": "Q1"},
                        "jogador_b": {"nome": "P1"},
                        "vencedor": {"nome": "Q1"},
                    },
                    {
                        "jogador_a": {"nome": "Q2"},
                        "jogador_b": {"nome": "P2"},
                        "vencedor": {"nome": "Q2"},
                    },
                    {
                        "jogador_a": {"nome": "Q3"},
                        "jogador_b": {"nome": "P3"},
                        "vencedor": {"nome": "Q3"},
                    },
                    {
                        "jogador_a": {"nome": "Q4"},
                        "jogador_b": {"nome": "P4"},
                        "vencedor": {"nome": "Q4"},
                    },
                ]
            },
            "direct_entries": [{"nome": "Main A"}, {"nome": "Main B"}],
        }

        torneio._atualizar_fase_se_necessario(estado)

        self.assertEqual(estado["fase_atual"], "pre_oitavas")
        self.assertEqual(
            [j["nome"] for j in chamado["classificados"]],
            ["Q1", "Q2", "Q3", "Q4"],
        )
        self.assertEqual(
            [j["nome"] for j in chamado["direct_entries"]],
            ["Main A", "Main B"],
        )

    def test_escolher_participantes_promove_jogador_de_alternates_para_qualy(self):
        torneio = Torneio.__new__(Torneio)
        torneio.jogador_nome = "Alexandre"
        torneio.jogador_nacionalidade = "BRA"
        torneio.tournament_data = {"tipo": "ATP 250", "pais_sede": "[BR] Brasil"}
        torneio._perfil = {"vagas_qualy": 1, "wildcards": 0}
        torneio._parametros_participacao = lambda: {
            "draw_main": 2,
            "draw_qualy": 2,
            "vagas_qualy": 1,
        }
        torneio._selector_entrada_direta = lambda: None
        ranking_pos = {
            "Main A": 1,
            "Main B": 2,
            "Qualy A": 3,
            "Qualy B": 4,
            "Alexandre": 5,
        }
        torneio._obter_rank_entrada = lambda jogador: ranking_pos.get(
            jogador.get("nome"), 9999
        )

        chave_principal, qualy_players = torneio.escolher_participantes(
            [
                {"nome": "Main A"},
                {"nome": "Main B"},
                {"nome": "Qualy A"},
                {"nome": "Qualy B"},
            ]
        )

        self.assertEqual([j["nome"] for j in chave_principal], ["Main A", "Main B"])
        self.assertEqual([j["nome"] for j in qualy_players], ["Qualy A", "Alexandre"])
        self.assertEqual(
            torneio._ultima_entry_info["status_entry"],
            {"Alexandre": "Qualifying"},
        )
        self.assertEqual(
            [j["nome"] for j in torneio._ultima_entry_info["alternates"]],
            ["Qualy B"],
        )

    def test_escolher_participantes_honra_selector_de_entrada_direta(self):
        torneio = Torneio.__new__(Torneio)
        torneio.jogador_nome = "Alexandre"
        torneio.jogador_nacionalidade = "BRA"
        torneio.tournament_data = {"tipo": "ATP 250", "pais_sede": "[BR] Brasil"}
        torneio._perfil = {"vagas_qualy": 1, "wildcards": 0}
        torneio._parametros_participacao = lambda: {
            "draw_main": 2,
            "draw_qualy": 2,
            "vagas_qualy": 1,
        }
        torneio._selector_entrada_direta = lambda: "_selecionar_entrada_direta_atp250"
        torneio._obter_rank_entrada = lambda jogador: {
            "Main Seed": 1,
            "Selector Pick": 50,
            "Qualy A": 60,
            "Qualy B": 70,
            "Alexandre": 80,
        }.get(jogador.get("nome"), 9999)
        torneio._selecionar_entrada_direta_atp250 = (
            lambda jogadores, num_diretos, nome_jogador_lower, priorizar_jogador: [
                {"nome": "Main Seed"},
                {"nome": "Selector Pick"},
            ]
        )

        chave_principal, qualy_players = torneio.escolher_participantes(
            [
                {"nome": "Main Seed"},
                {"nome": "Qualy A"},
                {"nome": "Qualy B"},
                {"nome": "Selector Pick"},
            ]
        )

        self.assertEqual(
            [j["nome"] for j in chave_principal],
            ["Main Seed", "Selector Pick"],
        )
        self.assertEqual([j["nome"] for j in qualy_players], ["Qualy A", "Alexandre"])

    def test_escolher_participantes_nao_rebaixa_topo_omitido_para_qualy(self):
        torneio = Torneio.__new__(Torneio)
        torneio.jogador_nome = "Alexandre"
        torneio.jogador_nacionalidade = "BRA"
        torneio.tournament_data = {"tipo": "ATP 250", "pais_sede": "[BR] Brasil"}
        torneio._perfil = {"vagas_qualy": 1, "wildcards": 0}
        torneio._parametros_participacao = lambda: {
            "draw_main": 2,
            "draw_qualy": 2,
            "vagas_qualy": 1,
        }
        torneio._selector_entrada_direta = lambda: "_selecionar_entrada_direta_atp250"
        ranking_pos = {
            "Top 5 Omitido": 5,
            "Main Seed": 8,
            "Selector Pick": 52,
            "Qualy A": 70,
            "Qualy B": 85,
            "Alexandre": 120,
        }
        torneio._obter_rank_entrada = lambda jogador: ranking_pos.get(
            jogador.get("nome"), 9999
        )
        torneio._selecionar_entrada_direta_atp250 = (
            lambda jogadores, num_diretos, nome_jogador_lower, priorizar_jogador: [
                {"nome": "Main Seed"},
                {"nome": "Selector Pick"},
            ]
        )

        _chave_principal, qualy_players = torneio.escolher_participantes(
            [
                {"nome": "Top 5 Omitido"},
                {"nome": "Main Seed"},
                {"nome": "Selector Pick"},
                {"nome": "Qualy A"},
                {"nome": "Qualy B"},
            ]
        )

        self.assertEqual([j["nome"] for j in qualy_players], ["Qualy A", "Alexandre"])

    def test_wildcard_realista_prioriza_local_sem_puxar_topo(self):
        torneio = Torneio.__new__(Torneio)
        torneio.tournament_data = {"pais_sede": "[AU] Austrália", "tipo": "ATP 250"}
        torneio.jogador_nome = "Alexandre"
        torneio._obter_rank_entrada = lambda jogador: {
            "Local 1": 140,
            "Top Star": 9,
            "Fringe 1": 78,
            "Alexandre": 160,
        }.get(jogador.get("nome"), 9999)
        torneio._extrair_codigo_pais = lambda valor: (
            "AU" if "AU" in str(valor) else ("BR" if "BR" in str(valor) else "US")
        )

        wildcards, restantes = torneio._selecionar_wildcards_realistas(
            [
                {"nome": "Top Star", "nacionalidade": "[US]"},
                {"nome": "Local 1", "nacionalidade": "[AU]"},
                {"nome": "Fringe 1", "nacionalidade": "[US]"},
                {"nome": "Alexandre", "nacionalidade": "[BR]"},
            ],
            "alexandre",
            2,
        )

        self.assertEqual([j["nome"] for j in wildcards], ["Local 1", "Alexandre"])
        self.assertEqual(
            [j["nome"] for j in restantes],
            ["Top Star", "Fringe 1"],
        )


if __name__ == "__main__":
    unittest.main()
