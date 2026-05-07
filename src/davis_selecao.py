"""
Seleção Nacional para Copa Davis / Billie Jean King Cup.
"""

import random
import logging

from src.dados import (
    get_caminho_ranking_global,
    carregar_ranking,
    carregar_ranking_nacoes_davis,
)
from src.jogador import normalizar_nome
from src.gerador_nomes import gerar_nome_completo
from src.davis_cup_constants import _MAPA_PAIS_3_PARA_2

logger = logging.getLogger(__name__)


def _codigo_pais_canonico(pais):
    """Normaliza país para código ISO-2 (sem colchetes), para comparação robusta."""
    if not pais:
        return ""
    texto = str(pais).strip()
    if texto.startswith("[") and "]" in texto:
        fechamento = texto.find("]")
        codigo = texto[1:fechamento].strip().upper()
    else:
        codigo = texto.strip().upper()
    if len(codigo) == 3:
        return _MAPA_PAIS_3_PARA_2.get(codigo, codigo)
    return codigo


class SelecaoNacional:
    """Representa uma seleção nacional na Copa Davis / BJK Cup."""

    def __init__(self, pais, ranking, genero="masculino"):
        self.pais = pais
        self.ranking = ranking
        self.genero = genero
        self.jogadores = self._buscar_jogadores_do_pais()
        self.convocados = []
        self.capitao = self._gerar_capitao(genero)
        self.nome_copa = (
            "Copa Davis" if genero == "masculino" else "Billie Jean King Cup"
        )

    def _buscar_jogadores_do_pais(self):
        """Busca jogadores reais do país (save + global) para convocação, filtrando lesionados."""
        pais_norm = self._normalizar_pais(self.pais)
        jogadores = []
        vistos = set()

        def _adicionar_fonte(lista):
            for j in lista:
                if not isinstance(j, dict):
                    continue
                if self._normalizar_pais(j.get("nacionalidade", "")) != pais_norm:
                    continue

                status_lesao = j.get("status_lesao", {})
                if isinstance(status_lesao, dict) and status_lesao.get("lesionado"):
                    continue

                nome = j.get("nome", "")
                nome_norm = normalizar_nome(nome)
                if not nome_norm or nome_norm in vistos:
                    continue
                if str(nome).startswith("Jogador "):
                    continue
                jogadores.append(j)
                vistos.add(nome_norm)

        _adicionar_fonte(self.ranking.ranking)

        genero_ref = "feminino" if self.genero == "feminino" else "masculino"
        ranking_global = carregar_ranking(get_caminho_ranking_global(genero=genero_ref))
        _adicionar_fonte(ranking_global)

        jogadores.sort(
            key=lambda x: (
                int(x.get("pontos_ranking", 0) or 0),
                int(x.get("pontos", 0) or 0),
                int(x.get("overall", 0) or 0),
            ),
            reverse=True,
        )
        return jogadores

    def _normalizar_pais(self, pais):
        return _codigo_pais_canonico(pais)

    def _gerar_capitao(self, genero="masculino"):
        """Gera um capitão real para a seleção baseada no gênero."""
        capitaes_atp = {
            "[IT]": "Filippo Volandri",
            "[ES]": "David Ferrer",
            "[AU]": "Lleyton Hewitt",
            "[CA]": "Frank Dancevic",
            "[HR]": "Vedran Martić",
            "[NL]": "Paul Haarhuis",
            "[US]": "Bob Bryan",
            "[GB]": "Leon Smith",
            "[DE]": "Michael Kohlmann",
            "[FR]": "Arnaud Clément",
            "[AR]": "Guillermo Coria",
            "[CZ]": "Jaroslav Navrátil",
            "[BR]": "Jaime Oncins",
            "[RS]": "Viktor Troicki",
            "[CL]": "Nicolás Massú",
        }
        capitaes_wta = {
            "[IT]": "Tathiana Garbin",
            "[ES]": "Anabel Medina Garrigues",
            "[AU]": "Alicia Molik",
            "[CA]": "Heidi El Tabakh",
            "[US]": "Lindsay Davenport",
            "[GB]": "Anne Keothavong",
            "[DE]": "Rainer Schüttler",
            "[FR]": "Julien Benneteau",
            "[CZ]": "Petr Pála",
            "[BR]": "Luiz Peniza",
            "[PL]": "Dawid Celt",
            "[CH]": "Heinz Günthardt",
        }
        codigo = self.pais.split("]")[0] + "]" if self.pais.startswith("[") else ""
        if genero == "feminino":
            return capitaes_wta.get(codigo, f"Capitã de {self.pais}")
        return capitaes_atp.get(codigo, f"Capitão de {self.pais}")

    def verificar_elegibilidade(self, jogador):
        """
        Verifica se o jogador é elegível para convocação.
        Retorna (elegivel, posicao_no_pais, mensagem).
        """
        nome_normalizado = normalizar_nome(jogador.nome)

        if self._normalizar_pais(jogador.nacionalidade) != self._normalizar_pais(
            self.pais
        ):
            return False, None, "Você não é elegível para esta seleção."

        for i, j in enumerate(self.jogadores):
            if normalizar_nome(j.get("nome", "")) == nome_normalizado:
                return True, i + 1, f"Você é o #{i + 1} do seu país."

        return True, len(self.jogadores) + 1, "Você ainda não está no ranking nacional."

    def convocar_jogador(self, jogador, posicao_convocacao=1):
        """
        Convoca um jogador para a seleção.
        posicao_convocacao: 1 = titular principal, 2 = segundo titular
        """
        jogador_dict = {
            "nome": jogador.nome,
            "nacionalidade": jogador.nacionalidade,
            "overall": (
                jogador.calcular_overall()
                if hasattr(jogador, "calcular_overall")
                else jogador.get("overall", 70)
            ),
            "atributos": (
                jogador.atributos
                if hasattr(jogador, "atributos")
                else jogador.get("atributos", {})
            ),
            "posicao_convocacao": posicao_convocacao,
            "e_jogador_principal": True,
        }

        self.convocados = [
            c
            for c in self.convocados
            if normalizar_nome(c.get("nome", "")) != normalizar_nome(jogador.nome)
        ]
        self.convocados.insert(posicao_convocacao - 1, jogador_dict)

    def completar_convocacao(self, num_jogadores=5):
        """Completa a convocação com outros jogadores do país."""
        nomes_convocados = {normalizar_nome(c.get("nome", "")) for c in self.convocados}

        for j in self.jogadores:
            if len(self.convocados) >= num_jogadores:
                break
            if normalizar_nome(j.get("nome", "")) not in nomes_convocados:
                j_copia = dict(j)
                j_copia["posicao_convocacao"] = len(self.convocados) + 1
                j_copia["e_jogador_principal"] = False
                self.convocados.append(j_copia)
                nomes_convocados.add(normalizar_nome(j.get("nome", "")))

        if len(self.convocados) < num_jogadores:
            nacoes_dados = carregar_ranking_nacoes_davis()
            nacoes_lista = nacoes_dados.get("nations", [])
            pos_nacao = 50
            for i, n in enumerate(
                sorted(nacoes_lista, key=lambda x: x.get("points", 0), reverse=True), 1
            ):
                if self._normalizar_pais(n.get("name", "")) == self._normalizar_pais(
                    self.pais
                ):
                    pos_nacao = i
                    break

            base_ovr = 75 - min(25, pos_nacao // 2)

            while len(self.convocados) < num_jogadores:
                pos = len(self.convocados) + 1
                nome_ficticio = gerar_nome_completo(self.pais, self.genero)

                while normalizar_nome(nome_ficticio) in nomes_convocados:
                    nome_ficticio = gerar_nome_completo(self.pais, self.genero)

                ovr_ficticio = max(45, min(85, base_ovr + random.randint(-5, 5)))
                ficticio = {
                    "nome": nome_ficticio,
                    "nacionalidade": self.pais,
                    "overall": ovr_ficticio,
                    "atributos": self._gerar_atributos_ficticios(ovr_ficticio),
                    "posicao_convocacao": pos,
                    "e_jogador_principal": False,
                    "e_ficticio": True,
                }
                self.convocados.append(ficticio)
                nomes_convocados.add(normalizar_nome(nome_ficticio))

    def _gerar_atributos_ficticios(self, overall=60):
        """Gera atributos para jogadores fictícios baseados em um overall alvo."""
        variacao = 10
        return {
            "saque": random.randint(overall - variacao, overall + variacao),
            "forehand": random.randint(overall - variacao, overall + variacao),
            "backhand": random.randint(overall - variacao, overall + variacao),
            "topspin": random.randint(overall - variacao, overall + variacao),
            "voleio": random.randint(overall - variacao, overall + variacao),
            "slice": random.randint(overall - variacao, overall + variacao),
            "movimento": random.randint(overall - variacao, overall + variacao),
            "lob": random.randint(overall - variacao, overall + variacao),
            "winner": random.randint(overall - variacao, overall + variacao),
            "fisico": random.randint(overall - variacao, overall + variacao),
        }

    def obter_titulares_simples(self):
        """Retorna os 2 jogadores que jogarão os simples."""
        return self.convocados[:2] if len(self.convocados) >= 2 else self.convocados

    def exibir_convocacao(self):
        """Exibe a lista de convocados (formato texto simples para log/API)."""
        linhas = [
            f"\n CONVOCAÇÃO - {self.pais}",
            f"   Capitão: {self.capitao}",
            "=" * 50,
        ]

        for i, jogador in enumerate(self.convocados, 1):
            nome = jogador.get("nome", "??")
            overall = jogador.get("overall", "??")
            posicao = (
                "Simples 1"
                if i == 1
                else ("Simples 2" if i == 2 else ("Duplas" if i <= 4 else "Reserva"))
            )
            prefixo = (
                "⭐"
                if jogador.get("e_jogador_principal")
                else ("🆕" if jogador.get("e_ficticio") else " ")
            )
            linhas.append(f"  {i}. {prefixo} {nome} (OVR: {overall}) - {posicao}")

        linhas.append("=" * 50)
        logger.debug("\n".join(linhas))
