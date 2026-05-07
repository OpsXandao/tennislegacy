import json
import os
import tempfile
import unittest
from unittest.mock import patch

from src import calendario
from src.calendario import (
    _marcar_historico_expirado,
    _estado_torneio_ativo,
    _processar_recuperacao_npc,
    processar_avisos_patrocinio,
    processar_seguidores,
)
from src.jogador import normalizar_nome
from src.ranking import SistemaRanking


class RegrasNegocioTests(unittest.TestCase):
    def test_estado_torneio_ativo_retorna_false_para_finalizado(self):
        estado = {"torneio": "Brisbane", "fase_atual": "finalizado", "semana": 3}
        self.assertFalse(_estado_torneio_ativo(estado, semana_referencia=3))

    def test_estado_torneio_ativo_retorna_false_para_semana_diferente(self):
        estado = {"torneio": "Brisbane", "fase_atual": "r32", "semana": 2}
        self.assertFalse(_estado_torneio_ativo(estado, semana_referencia=3))

    def test_estado_torneio_ativo_retorna_true_quando_em_andamento_na_semana(self):
        estado = {"torneio": "Brisbane", "fase_atual": "r32", "semana": 3}
        self.assertTrue(_estado_torneio_ativo(estado, semana_referencia=3))

    def test_estado_torneio_ativo_retorna_false_para_semana_invalida(self):
        estado = {"torneio": "Brisbane", "fase_atual": "r32", "semana": "semana-x"}
        self.assertFalse(_estado_torneio_ativo(estado, semana_referencia=3))

    def test_normalizar_nome_remove_espacos_extras(self):
        self.assertEqual(normalizar_nome("  Rafael   Nadal  "), "rafael nadal")

    def test_adicionar_pontos_persiste_ano_e_metadados(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump([], tmp)
            caminho = tmp.name

        try:
            ranking = SistemaRanking(caminho)
            ranking.adicionar_pontos(
                "Jogador Teste",
                125,
                10,
                modalidade="duplas",
                ano_expiracao=2027,
                metadados={
                    "torneio": "Torneio X",
                    "tipo": "ATP 250",
                    "semana_origem": 10,
                    "ano_origem": 2026,
                    "fase": "campeao",
                    "modalidade": "duplas",
                },
            )
            jogador = ranking.buscar_jogador_por_nome("Jogador Teste")
            bloco = jogador["pontos_detalhados_duplas"][-1]
            self.assertEqual(bloco.get("ano_expiracao"), 2027)
            self.assertEqual(bloco.get("torneio"), "Torneio X")
            self.assertEqual(bloco.get("semana_origem"), 10)
        finally:
            if os.path.exists(caminho):
                os.remove(caminho)

    def test_adicionar_jogador_novo_em_save_nao_contamina_ranking_global(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            saves_dir = os.path.join(tmpdir, "saves", "carreira_teste")
            os.makedirs(saves_dir, exist_ok=True)
            caminho_save = os.path.join(saves_dir, "ranking_atp.json")
            caminho_global = os.path.join(tmpdir, "ranking_atp.json")

            with open(caminho_save, "w", encoding="utf-8") as f:
                json.dump([], f)
            with open(caminho_global, "w", encoding="utf-8") as f:
                json.dump([{"nome": "Jogador Base", "nacionalidade": "[BR]"}], f)

            with patch(
                "src.ranking.get_caminho_ranking_global", return_value=caminho_global
            ):
                ranking = SistemaRanking(caminho_save)
                ranking.adicionar_jogador_novo(
                    {"nome": "Novo Save", "nacionalidade": "[AR]"}
                )

            with open(caminho_global, "r", encoding="utf-8") as f:
                ranking_global = json.load(f)

            self.assertEqual(len(ranking_global), 1)
            self.assertEqual(ranking_global[0]["nome"], "Jogador Base")

    def test_salvar_ranking_lean_persiste_apenas_identidade_e_pontos(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            base = [
                {
                    "nome": f"Jogador Base {idx}",
                    "nacionalidade": "[BR]",
                    "pontos": 0,
                    "pontos_duplas": 0,
                    "pontos_ranking": 0,
                    "pontos_ranking_duplas": 0,
                    "pontos_ytd": 0,
                }
                for idx in range(299)
            ]
            json.dump(
                base
                + [
                    {
                        "nome": "Jogador Teste",
                        "nacionalidade": "[BR]",
                        "pontos": 120,
                        "pontos_duplas": 40,
                        "pontos_ranking": 100,
                        "pontos_ranking_duplas": 35,
                        "pontos_ytd": 90,
                        "atributos": {"fisico": 77, "saque": 66},
                        "energia": 81,
                        "fadiga": 12,
                        "moral": 73,
                        "status_lesao": {"lesionado": True},
                    }
                ],
                tmp,
            )
            caminho = tmp.name

        try:
            ranking = SistemaRanking(caminho)
            ranking.salvar_ranking(save_details=False)

            with open(caminho, "r", encoding="utf-8") as f:
                salvo = json.load(f)

            self.assertEqual(len(salvo), 300)
            entry = next(j for j in salvo if j["nome"] == "Jogador Teste")
            self.assertEqual(
                set(entry.keys()),
                {
                    "nome",
                    "nacionalidade",
                    "pontos",
                    "pontos_duplas",
                    "pontos_ranking",
                    "pontos_ranking_duplas",
                    "pontos_ytd",
                    "energia",
                    "fadiga",
                    "moral",
                    "is_lean",
                },
            )
        finally:
            if os.path.exists(caminho):
                os.remove(caminho)

    def test_marcar_historico_expirado_prioriza_identidade_do_torneio(self):
        jogador = {
            "historico_torneios": [
                {
                    "nome": "Evento A",
                    "tipo": "ATP 250",
                    "semana": 3,
                    "ano": 2026,
                    "pontos": 45,
                    "expirado": False,
                },
                {
                    "nome": "Evento B",
                    "tipo": "ATP 250",
                    "semana": 7,
                    "ano": 2026,
                    "pontos": 45,
                    "expirado": False,
                },
            ]
        }
        _marcar_historico_expirado(
            jogador,
            [
                {
                    "pontos": 45,
                    "torneio": "Evento B",
                    "tipo": "ATP 250",
                    "semana_origem": 7,
                    "ano_origem": 2026,
                }
            ],
            ano_novo=2027,
            semana_nova=7,
        )
        self.assertFalse(jogador["historico_torneios"][0]["expirado"])
        self.assertTrue(jogador["historico_torneios"][1]["expirado"])

    def test_processar_avisos_patrocinio_aceita_posicao_none(self):
        class RankingSemJogador:
            def obter_posicao(self, _nome):
                return None

        class JogadorDummy:
            def __init__(self):
                self.nome = "Sem Ranking"
                self.seguidores = 0
                self.avisos_patrocinio = {}
                self.patrocinios = ["pat_temp_teste"]

        pat_backup = dict(calendario.PATROCINADORES_DISPONIVEIS)
        try:
            calendario.PATROCINADORES_DISPONIVEIS["pat_temp_teste"] = {
                "nome": "Patrocinio Teste",
                "requisito_ranking": 50,
                "req_seguidores": 1000,
            }
            jogador = JogadorDummy()
            processar_avisos_patrocinio(jogador, RankingSemJogador())
            self.assertIn("pat_temp_teste", jogador.avisos_patrocinio)
        finally:
            calendario.PATROCINADORES_DISPONIVEIS.clear()
            calendario.PATROCINADORES_DISPONIVEIS.update(pat_backup)

    def test_semana_estado_torneio_retorna_none_para_valor_invalido(self):
        self.assertIsNone(calendario._semana_estado_torneio({"semana": "?"}))

    def test_processar_seguidores_consulta_torneio_com_genero_do_jogador(self):
        class RankingDummy:
            def obter_posicao(self, _nome):
                return 10

        class JogadorDummy:
            def __init__(self):
                self.nome = "Jogadora WTA"
                self.save_name = "save_teste"
                self.genero = "feminino"
                self.equipe = []
                self.seguidores = 0
                self.moral = 80
                self.atributos_psicologicos = {"concentracao": 60}

        jogador = JogadorDummy()
        ranking = RankingDummy()

        with patch(
            "src.dados.carregar_estado_torneio",
            return_value={"fase_atual": "r16"},
        ) as mock_carregar_estado:
            processar_seguidores(jogador, ranking)

        mock_carregar_estado.assert_called_once_with(
            jogador.save_name, genero=jogador.genero
        )
        self.assertEqual(jogador.seguidores, 1000)

    def test_processar_recuperacao_npc_reduz_doenca_ate_curar(self):
        npc = {
            "fadiga": 15,
            "energia": 70,
            "moral": 68,
            "fisico": 55,
            "status_doenca": {
                "doente": True,
                "tipo": "gripe",
                "nivel": "moderada",
                "semanas_restantes": 1,
                "penalidade_atributos": 0.08,
                "penalidade_recuperacao_energia": 0.18,
            },
            "status_lesao": {
                "lesionado": False,
                "semanas_restantes": 0,
                "nivel": "saudavel",
                "penalidade_atributos": 0.0,
            },
        }

        _processar_recuperacao_npc(npc)

        self.assertEqual(
            npc["status_doenca"],
            {
                "doente": False,
                "tipo": None,
                "nivel": "saudavel",
                "semanas_restantes": 0,
                "penalidade_atributos": 0.0,
                "penalidade_recuperacao_energia": 0.0,
            },
        )


if __name__ == "__main__":
    unittest.main()
