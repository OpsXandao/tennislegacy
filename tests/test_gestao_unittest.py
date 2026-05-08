import unittest
from types import SimpleNamespace

from src.jogador import reidratar_jogador
from src.management import (
    processar_expiracoes_contratos,
    processar_gastos_equipe,
)
from src.migracoes import migrar_empresario, migrar_equipe
from src.patrocinios import migrar_patrocinios
from src.constants.staff_constants import EMPRESARIOS_DISPONIVEIS


class JogadorDummy(SimpleNamespace):
    def registrar_transacao(self, valor, _descricao, categoria=""):
        self.movimentos.append((valor, categoria))
        self.dinheiro += int(valor)


class GestaoTests(unittest.TestCase):
    def test_ultima_semana_contrato_equipe_cobra_salario(self):
        jogador = JogadorDummy(
            dinheiro=1000,
            equipe=[
                {"id": "treinador_fundo_jr", "semanas_restantes": 1, "salario": 200}
            ],
            movimentos=[],
        )

        # Ordem semanal usada no calendário: pagar salário antes de expirar contrato.
        processar_gastos_equipe(jogador)
        processar_expiracoes_contratos(jogador)

        self.assertEqual(jogador.dinheiro, 800)
        self.assertEqual(len(jogador.equipe), 0)
        self.assertEqual(jogador.movimentos[0][0], -200)

    def test_migrar_empresario_dict_incompleto_define_defaults(self):
        migrado = migrar_empresario({"id": "empresario_jr"})
        emp_ref = EMPRESARIOS_DISPONIVEIS["empresario_jr"]

        self.assertIsInstance(migrado, dict)
        self.assertEqual(migrado["id"], "empresario_jr")
        self.assertEqual(migrado["semanas_restantes"], 26)
        self.assertEqual(migrado["salario"], emp_ref["salario_semanal"])

    def test_migracoes_aceitam_campos_nulos(self):
        self.assertEqual(migrar_patrocinios(None), [])
        self.assertEqual(migrar_equipe(None), [])

    def test_reidratar_jogador_com_equipe_e_patrocinios_nulos(self):
        dados = {
            "nome": "Jogador Legacy",
            "idade": 21,
            "nacionalidade": "BRA",
            "genero": "masculino",
            "equipe": None,
            "patrocinios": None,
            "avisos_patrocinio": None,
        }

        jogador = reidratar_jogador(dados, "save_legacy")

        self.assertEqual(jogador.equipe, [])
        self.assertEqual(jogador.patrocinios, [])
        self.assertEqual(jogador.avisos_patrocinio, {})


if __name__ == "__main__":
    unittest.main()
