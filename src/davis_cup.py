"""
Copa Davis - Torneio de Tênis por Equipes Nacionais

A Copa Davis é a principal competição masculina de tênis por equipes.
Cada confronto (tie) consiste em:
- 2 partidas de simples
- 1 partida de duplas (simulada automaticamente)

O jogador participa representando seu país nas partidas de simples,
mas precisa ser convocado pela seleção nacional.
"""

import random

from src.dados import (
    get_caminho_ranking_save,
    get_caminho_ranking_global,
    get_caminho_torneio_save,
    carregar_estado_torneio,
    carregar_ranking,
    carregar_ranking_nacoes_davis,
)
from src.jogador import normalizar_nome
from src.ranking import SistemaRanking
from src.gerador_nomes import gerar_nome_completo
from src.constantes import DEFAULT_ATRIBUTOS, DEFAULT_ATRIBUTOS_PSICOLOGICOS
from src.jogar_partida import criar_config_partida, jogar_partida
from src.progressao import handle_xp_e_level_up
from src.fadiga import handle_fadiga_e_lesao
from src.save import salvar_jogo
from src.json_utils import salvar_json_seguro
from src.io_utils import (
    safe_input,
    print_blue,
    print_green,
    print_yellow,
    print_red,
    clear_screen,
)
from src.log_jogo import log_erro
from src.duplas import fundir_dupla as _fundir_dupla

# Países participantes da Davis Cup (18 equipes no formato atual)
# Nomes seguem o formato do ranking_atp.json
PAISES_DAVIS_CUP = [
    "[IT] Itália",
    "[ES] Espanha",
    "[AU] Austrália",
    "[CA] Canadá",
    "[HR] Croácia",
    "[NL] Holanda",
    "[US] USA",
    "[GB] Grã-Bretanha",
    "[DE] Alemanha",
    "[FR] França",
    "[AR] Argentina",
    "[CZ] Czechia",
    "[SE] Suécia",
    "[BE] Bélgica",
    "[CH] Suíça",
    "[RS] Sérvia",
    "[CL] Chile",
    "[KR] Coreia do Sul",
    "[BR] Brasil",
    "[PT] Portugal",
    "[JP] Japão",
    "[PL] Polônia",
]

# Formato real de 2026:
# - Qualifiers 1ª Rodada: 13 ties (26 equipes), confronto melhor de 5 partidas.
# - Qualifiers 2ª Rodada: 7 ties (14 equipes), confronto melhor de 5 partidas.
# - Final 8: mata-mata (quartas, semifinal, final), confronto melhor de 3 partidas.
EQUIPES_QUALIFIERS_R1_2026 = [
    "[AU] Austrália",
    "[HU] Hungria",
    "[DE] Alemanha",
    "[US] USA",
    "[DK] Dinamarca",
    "[HR] Croácia",
    "[FR] França",
    "[ES] Espanha",
    "[CZ] Czechia",
    "[JP] Japão",
    "[AT] Áustria",
    "[BE] Bélgica",
    "[AR] Argentina",
    "[SE] Suécia",
    "[CA] Canadá",
    "[IL] Israel",
    "[TW] Chinese Taipei",
    "[RS] Sérvia",
    "[SK] Eslováquia",
    "[BR] Brasil",
    "[CH] Suíça",
    "[KR] Coreia do Sul",
    "[GB] Grã-Bretanha",
    "[FI] Finlândia",
    "[CL] Chile",
    "[NO] Noruega",
]

EQUIPES_QUALIFIERS_R2_2026 = [
    "[AR] Argentina",
    "[BE] Bélgica",
    "[AT] Áustria",
    "[DE] Alemanha",
    "[CZ] Czechia",
    "[ES] Espanha",
    "[FR] França",
    "[NL] Holanda",
    "[AU] Austrália",
    "[HU] Hungria",
    "[JP] Japão",
    "[US] USA",
    "[DK] Dinamarca",
    "[HR] Croácia",
]

EQUIPES_FINAL8_2026 = [
    "[IT] Itália",
    "[AR] Argentina",
    "[BE] Bélgica",
    "[AT] Áustria",
    "[DE] Alemanha",
    "[CZ] Czechia",
    "[ES] Espanha",
    "[FR] França",
]

TIES_QUALIFIERS_R1_2026 = [
    ("[AU] Austrália", "[SE] Suécia"),
    ("[HU] Hungria", "[CA] Canadá"),
    ("[DE] Alemanha", "[IL] Israel"),
    ("[US] USA", "[TW] Chinese Taipei"),
    ("[DK] Dinamarca", "[RS] Sérvia"),
    ("[HR] Croácia", "[SK] Eslováquia"),
    ("[FR] França", "[BR] Brasil"),
    ("[ES] Espanha", "[CH] Suíça"),
    ("[CZ] Czechia", "[KR] Coreia do Sul"),
    ("[JP] Japão", "[GB] Grã-Bretanha"),
    ("[AT] Áustria", "[FI] Finlândia"),
    ("[BE] Bélgica", "[CL] Chile"),
    ("[AR] Argentina", "[NO] Noruega"),
]

TIES_QUALIFIERS_R2_2026 = [
    ("[NL] Holanda", "[AR] Argentina"),
    ("[AU] Austrália", "[BE] Bélgica"),
    ("[HU] Hungria", "[AT] Áustria"),
    ("[JP] Japão", "[DE] Alemanha"),
    ("[US] USA", "[CZ] Czechia"),
    ("[DK] Dinamarca", "[ES] Espanha"),
    ("[HR] Croácia", "[FR] França"),
]

TIES_FINAL8_QUARTAS_2026 = [
    ("[FR] França", "[BE] Bélgica"),
    ("[IT] Itália", "[AT] Áustria"),
    ("[ES] Espanha", "[CZ] Czechia"),
    ("[AR] Argentina", "[DE] Alemanha"),
]

# Sedes oficiais 2026 por tie (team A = mandante), conforme calendário real.
TIES_QUALIFIERS_R1_INFO_2026 = {
    ("AU", "SE"): {"cidade": "Stockholm", "pais": "Suécia", "superficie": "Hard (i)"},
    ("HU", "CA"): {"cidade": "Montreal", "pais": "Canadá", "superficie": "Hard (i)"},
    ("DE", "IL"): {"cidade": "Vilnius", "pais": "Lituânia", "superficie": "Hard (i)"},
    ("US", "TW"): {
        "cidade": "Taipei",
        "pais": "Chinese Taipei",
        "superficie": "Hard (i)",
    },
    ("DK", "RS"): {
        "cidade": "Copenhagen",
        "pais": "Dinamarca",
        "superficie": "Hard (i)",
    },
    ("HR", "SK"): {"cidade": "Osijek", "pais": "Croácia", "superficie": "Hard (i)"},
    ("FR", "BR"): {"cidade": "Orléans", "pais": "França", "superficie": "Hard (i)"},
    ("ES", "CH"): {"cidade": "Biel", "pais": "Suíça", "superficie": "Hard (i)"},
    ("CZ", "KR"): {
        "cidade": "Ostrava",
        "pais": "Czechia",
        "superficie": "Hard (i)",
    },
    ("JP", "GB"): {"cidade": "Miki", "pais": "Japão", "superficie": "Hard (i)"},
    ("AT", "FI"): {"cidade": "Schwechat", "pais": "Áustria", "superficie": "Clay (i)"},
    ("BE", "CL"): {"cidade": "Hasselt", "pais": "Bélgica", "superficie": "Hard (i)"},
    ("AR", "NO"): {"cidade": "Fjellhamar", "pais": "Noruega", "superficie": "Hard (i)"},
}

TIES_QUALIFIERS_R2_INFO_2026 = {
    ("NL", "AR"): {"cidade": "Groningen", "pais": "Holanda", "superficie": "Hard (i)"},
    ("AU", "BE"): {"cidade": "Sydney", "pais": "Austrália", "superficie": "Hard"},
    ("HU", "AT"): {"cidade": "Debrecen", "pais": "Hungria", "superficie": "Hard (i)"},
    ("JP", "DE"): {"cidade": "Tokyo", "pais": "Japão", "superficie": "Hard (i)"},
    ("US", "CZ"): {
        "cidade": "Delray Beach",
        "pais": "Estados Unidos",
        "superficie": "Hard",
    },
    ("DK", "ES"): {"cidade": "Marbella", "pais": "Espanha", "superficie": "Clay"},
    ("HR", "FR"): {"cidade": "Osijek", "pais": "Croácia", "superficie": "Clay (i)"},
}

FINAL8_INFO_2026 = {"cidade": "Bologna", "pais": "Itália", "superficie": "Hard (i)"}

_MAPA_PAIS_3_PARA_2 = {
    "ITA": "IT",
    "ESP": "ES",
    "AUS": "AU",
    "CAN": "CA",
    "CRO": "HR",
    "NED": "NL",
    "USA": "US",
    "GBR": "GB",
    "GER": "DE",
    "FRA": "FR",
    "ARG": "AR",
    "CZE": "CZ",
    "SWE": "SE",
    "BEL": "BE",
    "SUI": "CH",
    "SRB": "RS",
    "CHI": "CL",
    "KOR": "KR",
    "BRA": "BR",
    "POR": "PT",
    "JPN": "JP",
    "POL": "PL",
    "AUT": "AT",
    "HUN": "HU",
    "DEN": "DK",
    "ITA": "IT",
    "ESP": "ES",
    "AUS": "AU",
    "CAN": "CA",
    "CRO": "HR",
    "RUS": "RU",
    "CHN": "CN",
    "KAZ": "KZ",
    "SVK": "SK",
    "FIN": "FI",
    "NOR": "NO",
    "ISR": "IL",
    "IND": "IN",
    "GRE": "GR",
    "UKR": "UA",
    "ROU": "RO",
    "RSA": "ZA",
    "MEX": "MX",
}


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

                # Filtra jogadores lesionados da convocação
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

        # Fonte principal: ranking da carreira/save.
        _adicionar_fonte(self.ranking.ranking)

        # Fonte complementar: ranking global do gênero, para evitar elenco genérico.
        genero_ref = "feminino" if self.genero == "feminino" else "masculino"
        ranking_global = carregar_ranking(get_caminho_ranking_global(genero=genero_ref))
        _adicionar_fonte(ranking_global)

        # Ordena por força competitiva.
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
        """Normaliza o nome do país para comparação."""
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

        # Verifica se o jogador é do mesmo país
        if self._normalizar_pais(jogador.nacionalidade) != self._normalizar_pais(
            self.pais
        ):
            return False, None, "Você não é elegível para esta seleção."

        # Encontra a posição do jogador entre os compatriotas
        for i, j in enumerate(self.jogadores):
            if normalizar_nome(j.get("nome", "")) == nome_normalizado:
                return True, i + 1, f"Você é o #{i + 1} do seu país."

        # Jogador não está no ranking, adiciona temporariamente
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

        # Remove se já estava convocado
        self.convocados = [
            c
            for c in self.convocados
            if normalizar_nome(c.get("nome", "")) != normalizar_nome(jogador.nome)
        ]

        # Adiciona na posição correta
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

        # Se ainda faltam jogadores, gera fictícios baseados na força da nação
        if len(self.convocados) < num_jogadores:
            # Obtém posição da nação para calibrar força dos fictícios
            nacoes_dados = carregar_ranking_nacoes_davis()
            nacoes_lista = nacoes_dados.get("nations", [])
            pos_nacao = 50  # Default se não encontrada
            for i, n in enumerate(
                sorted(nacoes_lista, key=lambda x: x.get("points", 0), reverse=True), 1
            ):
                if self._normalizar_pais(n.get("name", "")) == self._normalizar_pais(
                    self.pais
                ):
                    pos_nacao = i
                    break

            # Base de overall: Top 10 ganha bônus, fora do Top 50 penalidade
            base_ovr = 75 - min(25, pos_nacao // 2)

            while len(self.convocados) < num_jogadores:
                pos = len(self.convocados) + 1
                nome_ficticio = gerar_nome_completo(self.pais, self.genero)

                # Garante que o nome não é duplicado na equipe
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
        """Exibe a lista de convocados."""
        print(f"\n📋 CONVOCAÇÃO - {self.pais}")
        print(f"   Capitão: {self.capitao}")
        print("=" * 50)

        for i, jogador in enumerate(self.convocados, 1):
            nome = jogador.get("nome", "??")
            overall = jogador.get("overall", "??")
            posicao = (
                "Simples 1"
                if i == 1
                else ("Simples 2" if i == 2 else ("Duplas" if i <= 4 else "Reserva"))
            )

            if jogador.get("e_jogador_principal"):
                print_green(f"  {i}. ⭐ {nome} (OVR: {overall}) - {posicao}")
            elif jogador.get("e_ficticio"):
                print_yellow(f"  {i}. 🆕 {nome} (OVR: {overall}) - {posicao}")
            else:
                print(f"  {i}. {nome} (OVR: {overall}) - {posicao}")

        print("=" * 50)


class DavisCup:
    """Classe que gerencia a Copa Davis."""

    def __init__(self, tournament_data, jogador, ranking, nome_save):
        self.tournament_data = tournament_data
        self.jogador = jogador
        self.ranking = ranking
        self.nome_save = nome_save
        self.genero = getattr(jogador, "genero", "masculino")
        self.caminho_json = get_caminho_torneio_save(nome_save, genero=self.genero)
        self.pais_jogador = jogador.nacionalidade
        self.selecao = None

    def _nome_competicao(self):
        tipo = self.tournament_data.get("tipo")
        if tipo in {"Davis Cup", "Billie Jean King Cup"}:
            return tipo
        return "Davis Cup" if self.genero == "masculino" else "Billie Jean King Cup"

    def _carregar_estado(self):
        """Carrega o estado atual do torneio."""
        estado = carregar_estado_torneio(self.nome_save, genero=self.genero)
        # Verifica se o estado é do tipo correto (Davis Cup)
        tipos_validos = {"Davis Cup", "Billie Jean King Cup"}
        if estado is None or estado.get("tipo") not in tipos_validos:
            estado = self._criar_estado_inicial()
            self._salvar_estado(estado)
        elif "modo_competicao" not in estado:
            # Migração de formato legado (fase de grupos antiga) para o regulamento atual.
            estado = self._criar_estado_inicial()
            self._salvar_estado(estado)
        return estado

    def _salvar_estado(self, estado):
        """Salva o estado do torneio."""
        salvar_json_seguro(self.caminho_json, estado)

    def _persistir_convocacao_no_estado(self, estado=None):
        estado = estado or self._carregar_estado()
        if not self.selecao:
            return estado

        selecoes = estado.setdefault("selecoes", {})
        selecoes[self.selecao.pais] = {
            "capitao": self.selecao.capitao,
            "convocados": list(self.selecao.convocados),
        }
        return estado

    def verificar_convocacao(self):
        """
        Verifica se o jogador será convocado para a seleção.
        Retorna (convocado, posicao, mensagem).
        """
        self.selecao = SelecaoNacional(
            self.pais_jogador, self.ranking, genero=self.jogador.genero
        )
        estado = self._carregar_estado()
        if not estado.get("jogador_vivo", True):
            return (
                False,
                None,
                f"Sua seleção não está participante desta etapa da {self._nome_competicao()}.",
            )
        elegivel, posicao, msg = self.selecao.verificar_elegibilidade(self.jogador)

        if not elegivel:
            return False, None, msg

        # Critérios mais fiéis:
        # - Top 5 nacional: convocação praticamente garantida
        # - Top 6-8: alta chance (reserva/titular alternativo)
        # - Top 9-15: chance baixa (lesão/rotação)
        # - >15: exceção rara
        if posicao <= 5:
            return (
                True,
                posicao,
                f"Parabéns! Você foi convocado como #{posicao} do país!",
            )
        if posicao <= 8:
            if random.random() < 0.85:
                return True, posicao, f"Você foi convocado! (#{posicao} do país)"
            return (
                False,
                posicao,
                f"Você ficou fora por pouco nesta convocação. (#{posicao} do país)",
            )
        if posicao <= 15:
            if random.random() < 0.30:
                return (
                    True,
                    posicao,
                    f"Você foi convocado como opção tática! (#{posicao} do país)",
                )
            return (
                False,
                posicao,
                f"Não convocado desta vez. (#{posicao} do país)",
            )

        if random.random() < 0.08:
            return (
                True,
                posicao,
                f"Convocação surpresa! (#{posicao} do país)",
            )
        return (
            False,
            posicao,
            f"Você não foi convocado. Continue subindo no ranking! (#{posicao} do país)",
        )

    def processar_convocacao(self, interactive=True):
        """
        Processa toda a lógica de convocação do jogador.
        Retorna True se foi convocado E aceitou, False caso contrário.
        """
        if interactive:
            clear_screen()
            print_blue("\n" + "=" * 60)
            print_blue(f"           🏆 {self._nome_competicao().upper()} - CONVOCAÇÃO")
            print_blue("=" * 60)

            print(f"\n📍 Sua nacionalidade: {self.pais_jogador}")
            print("📍 Capitão da seleção: ", end="")

        self.selecao = SelecaoNacional(
            self.pais_jogador,
            self.ranking,
            genero=getattr(self.jogador, "genero", "masculino"),
        )
        if interactive:
            print(f"{self.selecao.capitao}")

            print("\n" + "-" * 60)
            print("📊 JOGADORES DO SEU PAÍS NO RANKING:")
            print("-" * 60)

            for i, j in enumerate(self.selecao.jogadores[:10], 1):
                nome = j.get("nome", "??")
                pontos = j.get("pontos", 0)
                overall = j.get("overall", "??")
                destaque = (
                    " ⭐ (VOCÊ)"
                    if normalizar_nome(nome) == normalizar_nome(self.jogador.nome)
                    else ""
                )
                print(
                    f"  {i:2}. {nome:<25} | OVR: {overall:>3} | Pts: {pontos:>5}{destaque}"
                )

            print("-" * 60)

            safe_input("\nPressione Enter para ver a convocação...")

        # Verifica convocação
        convocado, posicao, mensagem = self.verificar_convocacao()

        if interactive:
            clear_screen()
            print_blue("\n" + "=" * 60)
            print_blue("           📋 LISTA DE CONVOCADOS")
            print_blue("=" * 60)

        if convocado:
            if interactive:
                print_green(f"\n✅ {mensagem}")

            # Define posição do jogador na convocação
            if posicao == 1:
                pos_convocacao = 1  # Simples 1
            elif posicao == 2:
                pos_convocacao = 2  # Simples 2
            else:
                # Se não é top 2, pode jogar simples 1 ou 2
                pos_convocacao = random.choice([1, 2])

            self.selecao.convocar_jogador(self.jogador, pos_convocacao)
            self.selecao.completar_convocacao(5)

            if interactive:
                self.selecao.exibir_convocacao()

                print(
                    f"\n🎾 Você jogará as partidas de {('Simples 1' if pos_convocacao == 1 else 'Simples 2')}!"
                )

                # Pergunta se aceita a convocação
                print()
                print_yellow("=" * 60)
                print_yellow("   O capitão aguarda sua resposta sobre a convocação...")
                print_yellow("=" * 60)
                print()
                print("[1] ✅ Aceitar convocação - Defender as cores do país")
                print("[2] ❌ Recusar convocação - Priorizar carreira individual")
                print()

                while True:
                    escolha = safe_input("Sua decisão: ").strip()
                    if escolha == "1":
                        print_green(
                            f"\n🎉 Você aceitou representar {self.pais_jogador} na {self._nome_competicao()}!"
                        )
                        safe_input("Pressione Enter para continuar...")
                        return True
                    elif escolha == "2":
                        return self._processar_recusa_convocacao(posicao)
                    else:
                        print_red("Opção inválida. Digite 1 ou 2.")
            else:
                # No backend da API, assumimos aceite instantâneo.
                return True

        else:
            if interactive:
                print_red(f"\n❌ {mensagem}")

                # Mostra a convocação sem o jogador
                self.selecao.completar_convocacao(5)
                print("\n📋 Convocados para representar o país:")
                self.selecao.exibir_convocacao()

                print_yellow(
                    "\n💪 Continue trabalhando duro para ser convocado na próxima!"
                )

                safe_input("\nPressione Enter para continuar...")
            else:
                self.selecao.completar_convocacao(5)
            return False

    def _processar_recusa_convocacao(self, posicao):
        """Processa a recusa de convocação pelo jogador."""
        clear_screen()
        print_blue("\n" + "=" * 60)
        print_blue("           ❌ CONVOCAÇÃO RECUSADA")
        print_blue("=" * 60)

        print_yellow(
            f"\n📰 NOTÍCIA: {self.jogador.nome} recusa convocação para a {self._nome_competicao()}!"
        )
        print()

        # Mensagens diferentes baseadas na posição do jogador
        if posicao == 1:
            print(f'   "{self.jogador.nome}, número 1 do país, decidiu não')
            print(
                f"   defender as cores de {self.pais_jogador} na {self._nome_competicao()}."
            )
            print('   A decisão causou surpresa no mundo do tênis."')
            impacto_moral = -10
        elif posicao <= 3:
            print(f'   "{self.jogador.nome}, um dos principais jogadores do país,')
            print(
                f"   optou por não participar da {self._nome_competicao()}, priorizando"
            )
            print('   sua agenda no circuito individual."')
            impacto_moral = -5
        else:
            print(
                f'   "{self.jogador.nome} comunicou ao capitão {self.selecao.capitao}'
            )
            print(
                f'   que não poderá atender à convocação para a {self._nome_competicao()}."'
            )
            impacto_moral = -3

        print()
        print_yellow(f"📊 Impacto: Moral {impacto_moral}")

        # Aplica penalidade de moral
        if hasattr(self.jogador, "moral"):
            self.jogador.moral = max(0, self.jogador.moral + impacto_moral)

        # Mostra a convocação substituta
        print()
        print("-" * 60)
        print_yellow("O capitão convocou um substituto:")
        print("-" * 60)

        # Reconstrói a convocação sem o jogador
        self.selecao = SelecaoNacional(
            self.pais_jogador, self.ranking, genero=self.genero
        )
        self.selecao.completar_convocacao(4)
        self.selecao.exibir_convocacao()

        print()
        print_yellow(f"A {self._nome_competicao()} seguirá sem sua participação.")
        print_yellow("Você poderá focar em outros torneios do calendário.")

        safe_input("\nPressione Enter para continuar...")
        return False

    def _modo_competicao(self):
        nome = (self.tournament_data.get("nome") or "").lower()
        if (
            "qualifiers - 1" in nome
            or "qualificatórias da copa davis, primeira rodada" in nome
        ):
            return "qualifiers_r1"
        if (
            "qualifiers - 2" in nome
            or "qualificatórias da copa davis, segunda rodada" in nome
        ):
            return "qualifiers_r2"
        if "qualifiers" in nome or "qualificat" in nome:
            if "2" in nome or "segunda" in nome or "2ª" in nome:
                return "qualifiers_r2"
            return "qualifiers_r1"
        if "finais - grupos" in nome or "finals - grupos" in nome:
            # Calendário legado usava fase de grupos; no formato 2026 isso representa
            # a 2ª rodada de qualifiers para definir o Final 8.
            return "qualifiers_r2"
        if "final 8" in nome or ("finals" in nome and "grupos" not in nome):
            return "final8"
        # Fallback para eventos Davis genéricos
        return "final8"

    def _ano_competicao(self):
        ano_torneio = self.tournament_data.get("ano_referencia")
        if ano_torneio is not None:
            try:
                return int(ano_torneio)
            except (TypeError, ValueError):
                pass
        try:
            from src.dados import carregar_temporada

            return int(carregar_temporada(self.nome_save).get("ano", 2026))
        except Exception as e:
            log_erro(
                self.nome_save,
                "davis_cup_ano_competicao",
                e,
                {"ano_torneio_raw": ano_torneio},
            )
            return 2026

    def _usar_modo_carreira(self):
        # 2026 usa a chave histórica oficial; anos seguintes usam modo carreira dinâmico.
        return self._ano_competicao() > 2026

    def _codigo_pais(self, valor):
        if not valor:
            return ""
        texto = str(valor).strip()
        if texto.startswith("[") and "]" in texto:
            fechamento = texto.find("]")
            return texto[1:fechamento].upper()
        return texto.upper()

    def _ranking_nacoes_carreira(self):
        """
        Ranking de nações no modo carreira:
        usa base oficial da Davis + adiciona países faltantes com 0 pontos.
        """
        base = carregar_ranking_nacoes_davis().get("nations", [])
        ranking = []
        codigos_vistos = set()
        nome_por_codigo = {}

        for item in base:
            if not isinstance(item, dict):
                continue
            codigo = self._codigo_pais(item.get("code") or item.get("codigo"))
            if not codigo:
                continue
            nome = item.get("name") or item.get("nome") or codigo
            played = int(item.get("played", 0) or 0)
            pontos = float(item.get("points", 0) or 0)
            ranking.append((codigo, pontos, played, f"[{codigo}] {nome}"))
            codigos_vistos.add(codigo)
            nome_por_codigo[codigo] = nome

        # Países conhecidos no ecossistema do jogo que não estejam no ranking oficial
        paises_referencia = (
            list(PAISES_DAVIS_CUP)
            + list(EQUIPES_QUALIFIERS_R1_2026)
            + list(EQUIPES_QUALIFIERS_R2_2026)
            + list(EQUIPES_FINAL8_2026)
        )
        for p in paises_referencia:
            if isinstance(p, tuple):
                for x in p:
                    codigo = self._codigo_pais(x)
                    if codigo and codigo not in codigos_vistos:
                        nome = x.split("]", 1)[1].strip() if "]" in x else codigo
                        ranking.append((codigo, 0.0, 0, f"[{codigo}] {nome}"))
                        codigos_vistos.add(codigo)
                        nome_por_codigo[codigo] = nome

        # Países presentes no ranking de jogadores também entram com 0 se faltarem
        for j in self.ranking.ranking:
            if not isinstance(j, dict):
                continue
            codigo = self._codigo_pais(j.get("nacionalidade", ""))
            if codigo and codigo not in codigos_vistos:
                nome = nome_por_codigo.get(codigo, codigo)
                ranking.append((codigo, 0.0, 0, f"[{codigo}] {nome}"))
                codigos_vistos.add(codigo)

        ranking.sort(key=lambda x: (x[1], x[2], x[0]), reverse=True)
        return [(codigo, pontos, rotulo) for codigo, pontos, _played, rotulo in ranking]

    def _equipes_carreira(self, quantidade):
        ranking_nacoes = self._ranking_nacoes_carreira()
        equipes = [nac for _, _, nac in ranking_nacoes[:quantidade]]
        if len(equipes) < quantidade:
            base = list(PAISES_DAVIS_CUP)
            for pais in base:
                if len(equipes) >= quantidade:
                    break
                if not any(self._paises_iguais(pais, e) for e in equipes):
                    equipes.append(pais)
        return equipes

    def _ties_por_seeding(self, equipes_ordenadas):
        ties = []
        i = 0
        j = len(equipes_ordenadas) - 1
        while i < j:
            ties.append((equipes_ordenadas[i], equipes_ordenadas[j]))
            i += 1
            j -= 1
        return ties

    def _equipes_modo_competicao(self, modo):
        if self._usar_modo_carreira():
            if modo == "qualifiers_r1":
                return self._equipes_carreira(26)
            if modo == "qualifiers_r2":
                return self._equipes_carreira(14)
            if modo == "final8":
                return self._equipes_carreira(8)
        if modo == "qualifiers_r1":
            return list(EQUIPES_QUALIFIERS_R1_2026)
        if modo == "qualifiers_r2":
            return list(EQUIPES_QUALIFIERS_R2_2026)
        if modo == "final8":
            return list(EQUIPES_FINAL8_2026)
        return list(PAISES_DAVIS_CUP)

    def _vitorias_para_vencer_tie(self, estado):
        fase = estado.get("fase_atual")
        if fase in ("quartas", "semifinal", "final"):
            return 2
        return 3

    def _criar_estado_inicial(self):
        """Cria o estado inicial da Copa Davis conforme o formato real de 2026."""
        modo = self._modo_competicao()
        paises = self._equipes_modo_competicao(modo)
        pais_jogador_normalizado = self._normalizar_pais_para_lista(self.pais_jogador)

        if pais_jogador_normalizado and pais_jogador_normalizado not in paises:
            # Garante presença do país do jogador para não bloquear gameplay.
            paises[-1] = pais_jogador_normalizado

        pais_no_torneio = pais_jogador_normalizado or self.pais_jogador
        jogador_participa = any(self._paises_iguais(p, pais_no_torneio) for p in paises)

        selecoes = {}
        for pais in paises:
            sel = SelecaoNacional(pais, self.ranking, genero=self.genero)
            sel.completar_convocacao(5)
            selecoes[pais] = {"capitao": sel.capitao, "convocados": sel.convocados}

        estado_base = {
            "torneio": self.tournament_data["nome"],
            "tipo": self.tournament_data.get("tipo", "Davis Cup"),
            "semana": self.tournament_data.get("semana", 1),
            "modo_competicao": modo,
            "modo_davis": (
                "carreira" if self._usar_modo_carreira() else "historico_2026"
            ),
            "ano_competicao": self._ano_competicao(),
            "jogador": self.jogador.nome,
            "pais_jogador": pais_no_torneio,
            "jogador_vivo": bool(jogador_participa),
            "jogador_convocado": False,
            "posicao_convocacao": None,
            "selecoes": selecoes,
            "eliminatorias": {"quartas": [], "semifinal": [], "final": []},
            "resultados_confrontos": [],
            "confronto_atual": None,
            "partida_atual": 0,
            "tournament_data": self.tournament_data,
        }

        if modo in ("qualifiers_r1", "qualifiers_r2"):
            estado_base["fase_atual"] = "qualifiers"
            if self._usar_modo_carreira():
                ties = self._ties_por_seeding(paises)
            else:
                ties = (
                    TIES_QUALIFIERS_R1_2026
                    if modo == "qualifiers_r1"
                    else TIES_QUALIFIERS_R2_2026
                )
            confronto_jogador = None
            for equipe_a, equipe_b in ties:
                if self._paises_iguais(
                    equipe_a, pais_no_torneio
                ) or self._paises_iguais(equipe_b, pais_no_torneio):
                    confronto_jogador = {
                        "equipe_a": equipe_a,
                        "equipe_b": equipe_b,
                        "vencedor": None,
                    }
                    break
            estado_base["confronto_atual"] = confronto_jogador
            if not confronto_jogador:
                estado_base["jogador_vivo"] = False
        else:
            estado_base["fase_atual"] = "quartas"
            ties_qf = (
                self._ties_por_seeding(paises)
                if self._usar_modo_carreira()
                else TIES_FINAL8_QUARTAS_2026
            )
            for equipe_a, equipe_b in ties_qf:
                estado_base["eliminatorias"]["quartas"].append(
                    {"equipe_a": equipe_a, "equipe_b": equipe_b, "vencedor": None}
                )
            if jogador_participa:
                for confronto in estado_base["eliminatorias"]["quartas"]:
                    if self._paises_iguais(
                        pais_no_torneio, confronto["equipe_a"]
                    ) or self._paises_iguais(pais_no_torneio, confronto["equipe_b"]):
                        estado_base["confronto_atual"] = confronto
                        break
            else:
                estado_base["jogador_vivo"] = False

        return estado_base

    def _normalizar_pais_para_lista(self, pais):
        """Encontra o país correspondente na lista oficial."""
        if not pais:
            return None

        pais_upper = pais.upper()

        for p in PAISES_DAVIS_CUP:
            if p.upper() == pais_upper:
                return p
            # Compara código
            if pais.startswith("["):
                codigo = pais.split("]")[0] + "]"
                if p.startswith(codigo.upper()):
                    return p

        return None

    def _paises_iguais(self, pais1, pais2):
        """Verifica se dois países são o mesmo (comparação flexível)."""
        if not pais1 or not pais2:
            return False

        # Compara diretamente
        if pais1.upper() == pais2.upper():
            return True
        return _codigo_pais_canonico(pais1) == _codigo_pais_canonico(pais2)

    def _garantir_atributos_jogador(self, jogador_dict):
        if "atributos" not in jogador_dict or not isinstance(
            jogador_dict["atributos"], dict
        ):
            jogador_dict["atributos"] = DEFAULT_ATRIBUTOS.copy()
        if "atributos_psicologicos" not in jogador_dict or not isinstance(
            jogador_dict["atributos_psicologicos"], dict
        ):
            jogador_dict["atributos_psicologicos"] = (
                DEFAULT_ATRIBUTOS_PSICOLOGICOS.copy()
            )
        if "overall" not in jogador_dict:
            jogador_dict["overall"] = round(
                sum(jogador_dict["atributos"].values()) / len(jogador_dict["atributos"])
            )

        # HEAL: Se o nome for genérico (Jogador X), gera um real
        nome_atual = jogador_dict.get("nome", "")
        if "Jogador " in nome_atual and jogador_dict.get("e_ficticio"):
            novo_nome = gerar_nome_completo(
                jogador_dict.get("nacionalidade", "US"), self.genero
            )
            jogador_dict["nome"] = novo_nome

        return jogador_dict

    def _gerar_equipe_adversaria(self, pais):
        """Retorna a equipe adversária (jogadores convocados)."""
        estado = self._carregar_estado()
        selecao_dados = estado.get("selecoes", {}).get(pais)

        if selecao_dados and selecao_dados.get("convocados"):
            return selecao_dados["convocados"]

        # Fallback: gera jogadores
        sel = SelecaoNacional(pais, self.ranking, genero=self.genero)
        sel.completar_convocacao(5)
        return sel.convocados

    def _forca_simples(self, atleta):
        """Score para escalar simples (ranking atual + overall)."""
        if not isinstance(atleta, dict):
            return 0
        pontos = int(atleta.get("pontos_ranking", atleta.get("pontos", 0)) or 0)
        overall = int(atleta.get("overall", 50) or 50)
        return pontos * 2 + overall * 25

    def _forca_duplas(self, atleta):
        """Score para escalar duplas (ranking de duplas + voleio + atributo duplas)."""
        if not isinstance(atleta, dict):
            return 0
        pontos_duplas = int(
            atleta.get("pontos_ranking_duplas", atleta.get("pontos_duplas", 0)) or 0
        )
        atributos = (
            atleta.get("atributos", {})
            if isinstance(atleta.get("atributos"), dict)
            else {}
        )
        voleio = int(atributos.get("voleio", 50) or 50)
        saque = int(atributos.get("saque", 50) or 50)
        duplas_attr = int(atributos.get("duplas", 60) or 60)
        return pontos_duplas * 3 + voleio * 20 + saque * 12 + duplas_attr * 15

    def _info_local_confronto(self, modo_competicao, equipe_a, equipe_b):
        """Retorna dados de sede do tie conforme formato/ano."""
        cod_a = _codigo_pais_canonico(equipe_a)
        cod_b = _codigo_pais_canonico(equipe_b)
        chave = (cod_a, cod_b)

        if modo_competicao == "qualifiers_r1":
            return TIES_QUALIFIERS_R1_INFO_2026.get(chave)
        if modo_competicao == "qualifiers_r2":
            return TIES_QUALIFIERS_R2_INFO_2026.get(chave)
        if modo_competicao == "final8":
            return dict(FINAL8_INFO_2026)
        return None

    def obter_info_confronto_atual(self):
        """Informações do confronto atual (adversário, sede e superfície)."""
        estado = self._carregar_estado()
        confronto = estado.get("confronto_atual") or {}
        if not confronto:
            return None

        pais_jogador = estado.get("pais_jogador", self.pais_jogador)
        equipe_a = confronto.get("equipe_a")
        equipe_b = confronto.get("equipe_b")
        if not equipe_a or not equipe_b:
            return None
        adversario = (
            equipe_b if self._paises_iguais(pais_jogador, equipe_a) else equipe_a
        )
        local = (
            self._info_local_confronto(
                estado.get("modo_competicao"), equipe_a, equipe_b
            )
            or {}
        )
        return {
            "equipe_a": equipe_a,
            "equipe_b": equipe_b,
            "adversario": adversario,
            "cidade": local.get("cidade"),
            "pais_sede": local.get("pais"),
            "superficie": local.get("superficie"),
        }

    def obter_proximo_confronto(self):
        """Retorna informações sobre o próximo confronto do jogador."""
        estado = self._carregar_estado()

        if not estado.get("jogador_convocado"):
            return None

        fase = estado.get("fase_atual")
        confronto = estado.get("confronto_atual")
        if fase in ["qualifiers", "quartas", "semifinal", "final"] and confronto:
            pais_jogador = estado.get("pais_jogador")
            if self._paises_iguais(
                pais_jogador, confronto.get("equipe_a")
            ) or self._paises_iguais(pais_jogador, confronto.get("equipe_b")):
                adversario = (
                    confronto.get("equipe_b")
                    if self._paises_iguais(pais_jogador, confronto.get("equipe_a"))
                    else confronto.get("equipe_a")
                )
                return {"fase": fase, "adversario": adversario}

        return None

    def jogar_confronto(self, adversario_pais):
        """
        Joga um confronto (tie) contra um país adversário.
        Retorna o resultado do confronto.
        """
        estado = self._carregar_estado()
        pais_jogador = estado["pais_jogador"]
        fase = estado.get("fase_atual")
        alvo_vitorias = self._vitorias_para_vencer_tie(estado)
        total_partidas = 5 if alvo_vitorias == 3 else 3
        confronto_atual = estado.get("confronto_atual") or {}

        # Mantém ordem real do tie (mandante/visitante) nos qualifiers.
        equipe_a_tie = confronto_atual.get("equipe_a", pais_jogador)
        equipe_b_tie = confronto_atual.get("equipe_b", adversario_pais)
        if not (
            self._paises_iguais(equipe_a_tie, pais_jogador)
            or self._paises_iguais(equipe_b_tie, pais_jogador)
        ):
            equipe_a_tie = pais_jogador
            equipe_b_tie = adversario_pais
        mandante_jogador = fase == "qualifiers" and self._paises_iguais(
            equipe_a_tie, pais_jogador
        )
        bonus_mando = 0.03 if fase == "qualifiers" and mandante_jogador else 0.0
        if fase == "qualifiers" and not mandante_jogador:
            bonus_mando = -0.03

        clear_screen()
        print_blue(f"\n{'=' * 60}")
        titulo_comp = (
            "COPA DAVIS"
            if self._nome_competicao() == "Davis Cup"
            else "BILLIE JEAN KING CUP"
        )
        print_blue(
            f"     🏆 {titulo_comp} ({fase.upper()}) - {pais_jogador} vs {adversario_pais}"
        )
        print_blue(f"{'=' * 60}")
        if fase == "qualifiers":
            label_mando = "MANDANTE" if mandante_jogador else "VISITANTE"
            print_yellow(f"📍 Condição do tie: {label_mando}")

        equipe_adversaria = [
            self._garantir_atributos_jogador(j)
            for j in self._gerar_equipe_adversaria(adversario_pais)
        ]
        equipe_adversaria = sorted(
            equipe_adversaria, key=self._forca_simples, reverse=True
        )

        selecao_jogador = estado.get("selecoes", {}).get(pais_jogador, {})
        equipe_jogador = selecao_jogador.get("convocados")
        if not equipe_jogador:
            sel = SelecaoNacional(pais_jogador, self.ranking)
            sel.completar_convocacao(4)
            equipe_jogador = sel.convocados

        equipe_jogador = [
            self._garantir_atributos_jogador(dict(a))
            for a in equipe_jogador
            if isinstance(a, dict)
        ]
        equipe_jogador = sorted(equipe_jogador, key=self._forca_simples, reverse=True)

        companheiro = None
        for atleta in equipe_jogador:
            if normalizar_nome(atleta.get("nome", "")) != normalizar_nome(
                self.jogador.nome
            ):
                companheiro = self._garantir_atributos_jogador(atleta)
                break
        if companheiro is None:
            # Gera um companheiro realista se não houver convocado
            comp_nome = gerar_nome_completo(pais_jogador, self.genero)
            companheiro = {
                "nome": comp_nome,
                "nacionalidade": pais_jogador,
                "overall": 65,
                "atributos": DEFAULT_ATRIBUTOS.copy(),
                "atributos_psicologicos": DEFAULT_ATRIBUTOS_PSICOLOGICOS.copy(),
            }

        print("\n📋 Adversários:")
        for i, adv in enumerate(equipe_adversaria[:4], 1):
            print(f"   {i}. {adv.get('nome', '??')} (OVR: {adv.get('overall', '??')})")

        safe_input("\nPressione Enter para começar o confronto...")

        vitorias_jogador = 0
        vitorias_adversario = 0
        resultados_partidas = []

        # Configuração para partidas da Davis Cup (melhor de 3)
        config = criar_config_partida(self.tournament_data)

        def _registrar_placar_parcial():
            if self._paises_iguais(equipe_a_tie, pais_jogador):
                placar_a, placar_b = vitorias_jogador, vitorias_adversario
            else:
                placar_a, placar_b = vitorias_adversario, vitorias_jogador
            print(
                f"\n📊 Placar do confronto: {equipe_a_tie} {placar_a} x {placar_b} {equipe_b_tie}"
            )

        def _finalizar_confronto():
            vencedor_confronto = (
                pais_jogador if vitorias_jogador >= alvo_vitorias else adversario_pais
            )
            local_info = (
                self._info_local_confronto(
                    estado.get("modo_competicao"), equipe_a_tie, equipe_b_tie
                )
                or {}
            )
            resultado_confronto = {
                "equipe_a": equipe_a_tie,
                "equipe_b": equipe_b_tie,
                "vencedor": vencedor_confronto,
                "placar": f"{vitorias_jogador}-{vitorias_adversario}",
                "partidas": resultados_partidas,
                "cidade": local_info.get("cidade"),
                "pais_sede": local_info.get("pais"),
                "superficie": local_info.get("superficie"),
            }
            self._atualizar_estado_apos_confronto(resultado_confronto)

            clear_screen()
            print_blue(f"\n{'=' * 60}")
            print_blue("           RESULTADO FINAL")
            print_blue(f"{'=' * 60}\n")
            print(
                f"   {pais_jogador}  {vitorias_jogador}  x  {vitorias_adversario}  {adversario_pais}\n"
            )
            if vencedor_confronto == pais_jogador:
                print_green(f"🎉 {pais_jogador} VENCE O CONFRONTO!")
            else:
                print_red(f"😔 {adversario_pais} vence o confronto.")
            safe_input("\nPressione Enter para continuar...")
            return {
                "vencedor": vencedor_confronto,
                "placar": f"{vitorias_jogador}-{vitorias_adversario}",
                "eliminado": vencedor_confronto != pais_jogador,
            }

        # Ordem oficial:
        # Final 8 (best-of-3): S2 vs S2, S1 vs S1, D (se necessário)
        # Qualifiers (best-of-5): S2 vs S2, S1 vs S1, D, S1 vs S2, S2 vs S1
        # No jogo, o jogador humano joga a partida correspondente à sua posição de convocação.

        pos_conv = int(estado.get("posicao_convocacao") or 1)

        # Titulares de simples do usuário: respeita posição convocada do humano.
        equipe_jogador_ordenada = sorted(
            equipe_jogador,
            key=lambda a: (
                normalizar_nome(a.get("nome", ""))
                != normalizar_nome(self.jogador.nome),
                -self._forca_simples(a),
            ),
        )
        melhor_outro = next(
            (
                a
                for a in equipe_jogador_ordenada
                if normalizar_nome(a.get("nome", ""))
                != normalizar_nome(self.jogador.nome)
            ),
            companheiro,
        )
        j_titular_1 = self.jogador if pos_conv == 1 else melhor_outro
        j_titular_2 = melhor_outro if pos_conv == 1 else self.jogador

        # Titulares adversários de simples (top 2 por força de simples).
        adv_1 = (
            equipe_adversaria[0]
            if len(equipe_adversaria) > 0
            else {"nome": "Adversário A", "overall": 60}
        )
        adv_2 = (
            equipe_adversaria[1]
            if len(equipe_adversaria) > 1
            else {"nome": "Adversário B", "overall": 58}
        )

        # Duplas titulares: escolhe os 2 melhores por força específica de duplas.
        # Pode ser diferente da dupla de simples, como no circuito real.
        equipe_jogador_para_duplas = []
        for a in equipe_jogador:
            if normalizar_nome(a.get("nome", "")) == normalizar_nome(self.jogador.nome):
                equipe_jogador_para_duplas.append(
                    {
                        "nome": self.jogador.nome,
                        "nacionalidade": self.jogador.nacionalidade,
                        "overall": getattr(
                            self.jogador, "overall", a.get("overall", 70)
                        ),
                        "pontos_ranking_duplas": a.get(
                            "pontos_ranking_duplas", a.get("pontos_duplas", 0)
                        ),
                        "pontos_duplas": a.get("pontos_duplas", 0),
                        "atributos": getattr(
                            self.jogador,
                            "atributos",
                            a.get("atributos", DEFAULT_ATRIBUTOS.copy()),
                        ),
                    }
                )
            else:
                equipe_jogador_para_duplas.append(a)
        equipe_jogador_para_duplas = sorted(
            equipe_jogador_para_duplas, key=self._forca_duplas, reverse=True
        )
        dupla_j_a = (
            equipe_jogador_para_duplas[0]
            if len(equipe_jogador_para_duplas) > 0
            else {
                "nome": self.jogador.nome,
                "overall": 65,
                "atributos": DEFAULT_ATRIBUTOS.copy(),
            }
        )
        dupla_j_b = (
            equipe_jogador_para_duplas[1]
            if len(equipe_jogador_para_duplas) > 1
            else {
                "nome": companheiro.get("nome", "Parceiro"),
                "overall": companheiro.get("overall", 62),
                "atributos": companheiro.get("atributos", DEFAULT_ATRIBUTOS.copy()),
            }
        )
        equipe_adversaria_duplas = sorted(
            equipe_adversaria, key=self._forca_duplas, reverse=True
        )
        dupla_a_a = (
            equipe_adversaria_duplas[0] if len(equipe_adversaria_duplas) > 0 else adv_1
        )
        dupla_a_b = (
            equipe_adversaria_duplas[1] if len(equipe_adversaria_duplas) > 1 else adv_2
        )

        if total_partidas == 3:
            # Formato Final 8 (S2 vs S2, S1 vs S1, D)
            agenda = [
                ("simples", j_titular_2, adv_2),  # Partida 1: Segundos titulares
                ("simples", j_titular_1, adv_1),  # Partida 2: Primeiros titulares
                ("duplas", None, None),  # Partida 3: Duplas (decisiva)
            ]
        else:
            # Formato Qualifiers (S2 vs S2, S1 vs S1, D, S1 vs S2, S2 vs S1)
            agenda = [
                ("simples", j_titular_2, adv_2),
                ("simples", j_titular_1, adv_1),
                ("duplas", None, None),
                ("simples", j_titular_1, adv_2),
                ("simples", j_titular_2, adv_1),
            ]

        for idx, (tipo_partida, p_a, p_b) in enumerate(agenda, 1):
            # Verifica se o confronto já foi decidido antes de cada partida
            if (
                vitorias_jogador >= alvo_vitorias
                or vitorias_adversario >= alvo_vitorias
            ):
                print_yellow(
                    f"\n🏁 O confronto já foi decidido ({vitorias_jogador}x{vitorias_adversario})!"
                )
                print_yellow("As partidas restantes não serão disputadas.")
                break

            clear_screen()
            _registrar_placar_parcial()
            print(f"\n🎾 Partida {idx}: {tipo_partida.upper()}")

            # Recuperação parcial entre partidas do mesmo confronto (descanso noturno)
            if idx > 1:
                rec = int((100 - self.jogador.energia) * 0.2)
                self.jogador.energia = min(100, self.jogador.energia + rec)
                if isinstance(companheiro, dict):
                    rec_c = int((100 - companheiro.get("energia", 100)) * 0.2)
                    companheiro["energia"] = min(
                        100, companheiro.get("energia", 100) + rec_c
                    )

            if tipo_partida == "duplas":
                if (
                    vitorias_jogador >= alvo_vitorias
                    or vitorias_adversario >= alvo_vitorias
                ):
                    # Segurança extra: não simula duplas se o tie já estiver decidido.
                    break
                clear_screen()
                print_blue(f"\n{'=' * 60}")
                print_blue(f"     DUPLAS: {pais_jogador} vs {adversario_pais}")
                print_blue(f"{'=' * 60}\n")
                print_yellow("🎾 A partida de duplas será simulada...")
                print(
                    f"   {dupla_j_a.get('nome', 'Dupla A')} / {dupla_j_b.get('nome', 'Dupla B')}"
                )
                print(
                    f"   vs {dupla_a_a.get('nome', 'Dupla C')} / {dupla_a_b.get('nome', 'Dupla D')}"
                )

                equipe_j = _fundir_dupla(dupla_j_a, dupla_j_b)
                equipe_a = _fundir_dupla(dupla_a_a, dupla_a_b)
                diff = (equipe_j["overall"] - equipe_a["overall"]) * 75
                bonus_momento = 0.10 * (vitorias_jogador - vitorias_adversario)
                chance_vitoria = 0.5 + diff / 6000.0 + bonus_momento + bonus_mando
                chance_vitoria = max(0.15, min(0.85, chance_vitoria))
                sets_a = 0
                sets_b = 0
                for _ in range(3):
                    if random.random() < chance_vitoria:
                        sets_a += 1
                    else:
                        sets_b += 1
                    if sets_a == 2 or sets_b == 2:
                        break
                if sets_a > sets_b:
                    vitorias_jogador += 1
                    placar = f"{sets_a}-{sets_b}"
                    vencedor = pais_jogador
                    print_green(f"\n✅ {pais_jogador} vence as duplas! ({placar})")
                else:
                    vitorias_adversario += 1
                    placar = f"{sets_b}-{sets_a}"
                    vencedor = adversario_pais
                    print_red(f"\n❌ {adversario_pais} vence as duplas! ({placar})")

                # Registrar vínculo com o parceiro (se o jogador estava na dupla)
                nome_j_norm = normalizar_nome(self.jogador.nome)
                j_em_a = normalizar_nome(dupla_j_a.get("nome", "")) == nome_j_norm
                j_em_b = normalizar_nome(dupla_j_b.get("nome", "")) == nome_j_norm
                if j_em_a or j_em_b:
                    parceiro_dc = dupla_j_b if j_em_a else dupla_j_a
                    nome_parceiro_dc = parceiro_dc.get("nome", "")
                    if nome_parceiro_dc and hasattr(
                        self.jogador, "registrar_resultado_dupla"
                    ):
                        self.jogador.registrar_resultado_dupla(
                            nome_parceiro_dc, sets_a > sets_b
                        )

                resultados_partidas.append(
                    {
                        "tipo": "duplas",
                        "equipe_a": equipe_a_tie,
                        "equipe_b": equipe_b_tie,
                        "dupla_a": f"{dupla_j_a.get('nome', '??')} / {dupla_j_b.get('nome', '??')}",
                        "dupla_b": f"{dupla_a_a.get('nome', '??')} / {dupla_a_b.get('nome', '??')}",
                        "vencedor": vencedor,
                        "placar": placar,
                    }
                )
                _registrar_placar_parcial()
                continue

            nome_a = (
                p_a.get("nome", "??")
                if isinstance(p_a, dict)
                else getattr(p_a, "nome", "??")
            )
            nome_b = (
                p_b.get("nome", "??")
                if isinstance(p_b, dict)
                else getattr(p_b, "nome", "??")
            )
            clear_screen()
            print_blue(f"\n{'=' * 60}")
            print_blue(f"     SIMPLES {idx}: {nome_a} vs {nome_b}")
            print_blue(f"{'=' * 60}\n")

            jogador_humano_no_jogo = normalizar_nome(nome_a) == normalizar_nome(
                self.jogador.nome
            )
            if jogador_humano_no_jogo:
                energia_antes_davis = getattr(self.jogador, "energia", 100)
                vencedor_nome, placar, pontos_disputados = jogar_partida(
                    self.jogador, p_b, self.nome_save, config=config
                )
                energia_perdida_davis = max(
                    0, energia_antes_davis - getattr(self.jogador, "energia", 100)
                )
                venceu = normalizar_nome(vencedor_nome) == normalizar_nome(
                    self.jogador.nome
                )
                self.jogador = handle_xp_e_level_up(self.jogador, venceu)
                self.jogador = handle_fadiga_e_lesao(
                    self.jogador,
                    pontos_disputados=pontos_disputados,
                    energia_perdida=energia_perdida_davis,
                )
                salvar_jogo(self.nome_save, self.jogador)
                vencedor_nome_reg = vencedor_nome
            else:
                npc_a = (
                    p_a
                    if isinstance(p_a, dict)
                    else {"nome": nome_a, "atributos": DEFAULT_ATRIBUTOS.copy()}
                )
                npc_b = (
                    p_b
                    if isinstance(p_b, dict)
                    else {"nome": nome_b, "atributos": DEFAULT_ATRIBUTOS.copy()}
                )
                # Simples NPC com viés de mando (apenas nos qualifiers).
                forca_a = self._forca_simples(npc_a)
                forca_b = self._forca_simples(npc_b)
                chance_a = 0.5 + ((forca_a - forca_b) / 6000.0) + bonus_mando
                chance_a = max(0.15, min(0.85, chance_a))
                sets_a = 0
                sets_b = 0
                while sets_a < 2 and sets_b < 2:
                    if random.random() < chance_a:
                        sets_a += 1
                    else:
                        sets_b += 1
                venceu = sets_a > sets_b
                vencedor_nome_reg = nome_a if venceu else nome_b
                placar = f"{sets_a}-{sets_b}" if venceu else f"{sets_b}-{sets_a}"

            if venceu:
                vitorias_jogador += 1
                print_green(f"\n✅ {pais_jogador} vence! Placar: {placar}")
            else:
                vitorias_adversario += 1
                print_red(f"\n❌ {adversario_pais} vence! Placar: {placar}")

            resultados_partidas.append(
                {
                    "tipo": "simples",
                    "jogador_a": nome_a,
                    "jogador_b": nome_b,
                    "equipe_a": equipe_a_tie,
                    "equipe_b": equipe_b_tie,
                    "vencedor": vencedor_nome_reg,
                    "placar": placar,
                }
            )
            _registrar_placar_parcial()
            if vitorias_jogador < alvo_vitorias and vitorias_adversario < alvo_vitorias:
                safe_input("\nPressione Enter para a próxima partida...")

        return _finalizar_confronto()

    def _atualizar_estado_apos_confronto(self, resultado):
        """Atualiza o estado do torneio após um confronto."""
        estado = self._carregar_estado()
        pais_jogador = estado["pais_jogador"]
        estado.setdefault("resultados_confrontos", []).append(resultado)
        fase = estado.get("fase_atual")
        modo = estado.get("modo_competicao")
        vencedor = resultado.get("vencedor")

        if fase == "qualifiers":
            estado["fase_atual"] = "finalizado"
            estado["confronto_atual"] = None
            estado["jogador_vivo"] = self._paises_iguais(vencedor, pais_jogador)
            if not estado["jogador_vivo"]:
                estado["fase_eliminacao"] = "eliminado_qualifiers"
            if modo == "qualifiers_r2" and estado["jogador_vivo"]:
                estado["classificado_final8"] = True
            self._salvar_estado(estado)
            return

        if fase in ("quartas", "semifinal", "final"):
            chave = estado.get("eliminatorias", {}).get(fase, [])
            for confronto in chave:
                if self._paises_iguais(
                    confronto.get("equipe_a"), resultado.get("equipe_a")
                ) and self._paises_iguais(
                    confronto.get("equipe_b"), resultado.get("equipe_b")
                ):
                    confronto["vencedor"] = vencedor
                    break
                if self._paises_iguais(
                    confronto.get("equipe_a"), resultado.get("equipe_b")
                ) and self._paises_iguais(
                    confronto.get("equipe_b"), resultado.get("equipe_a")
                ):
                    confronto["vencedor"] = vencedor
                    break

            self._simular_restante_fase_eliminatoria(estado, fase)
            self._avancar_fase_eliminatoria(estado, fase)

            if not estado.get("confronto_atual"):
                estado["jogador_vivo"] = False
            elif not (
                self._paises_iguais(
                    pais_jogador, estado["confronto_atual"].get("equipe_a")
                )
                or self._paises_iguais(
                    pais_jogador, estado["confronto_atual"].get("equipe_b")
                )
            ):
                estado["jogador_vivo"] = False

        self._salvar_estado(estado)

    def _simular_confronto_npc(self, equipe_a, equipe_b, alvo_vitorias=2):
        """Simula confronto NPC baseado no overall das equipes e vantagem de casa."""
        total_partidas = 5 if alvo_vitorias == 3 else 3
        v_a = 0
        v_b = 0

        estado = self._carregar_estado()
        local_info = (
            self._info_local_confronto(
                estado.get("modo_competicao"), equipe_a, equipe_b
            )
            or {}
        )

        # Simula força base (média dos convocados ou 65 default)
        ovr_a = 65
        ovr_b = 65

        # Tenta pegar dados reais do ranking para calibrar a força
        try:
            sel_a = SelecaoNacional(equipe_a, self.ranking, genero=self.genero)
            sel_a.completar_convocacao(2)
            ovr_a = sum(j.get("overall", 65) for j in sel_a.convocados[:2]) / 2

            sel_b = SelecaoNacional(equipe_b, self.ranking, genero=self.genero)
            sel_b.completar_convocacao(2)
            ovr_b = sum(j.get("overall", 65) for j in sel_b.convocados[:2]) / 2
        except Exception:
            pass

        # Bônus de casa apenas nos qualifiers (equipe_a é mandante no tie oficial).
        if estado.get("fase_atual") == "qualifiers":
            ovr_a += 3

        prob_a = 0.5 + (ovr_a - ovr_b) * 0.04
        prob_a = max(0.1, min(0.9, prob_a))

        for _ in range(total_partidas):
            if v_a >= alvo_vitorias or v_b >= alvo_vitorias:
                break
            if random.random() < prob_a:
                v_a += 1
            else:
                v_b += 1
        vencedor = equipe_a if v_a >= alvo_vitorias else equipe_b
        return {
            "equipe_a": equipe_a,
            "equipe_b": equipe_b,
            "vencedor": vencedor,
            "placar": f"{v_a}-{v_b}",
            "partidas": [],
            "cidade": local_info.get("cidade"),
            "pais_sede": local_info.get("pais"),
            "superficie": local_info.get("superficie"),
        }

    def _simular_restante_fase_eliminatoria(self, estado, fase):
        chave = estado.get("eliminatorias", {}).get(fase, [])
        alvo_vitorias = 2 if fase in ("quartas", "semifinal", "final") else 3
        for confronto in chave:
            if confronto.get("vencedor"):
                continue
            resultado = self._simular_confronto_npc(
                confronto["equipe_a"],
                confronto["equipe_b"],
                alvo_vitorias=alvo_vitorias,
            )
            confronto["vencedor"] = resultado["vencedor"]
            estado.setdefault("resultados_confrontos", []).append(resultado)

    def _avancar_fase_eliminatoria(self, estado, fase):
        pais_jogador = estado.get("pais_jogador")
        chave_atual = estado.get("eliminatorias", {}).get(fase, [])
        vencedores = [c.get("vencedor") for c in chave_atual if c.get("vencedor")]

        if fase == "quartas":
            if len(vencedores) < 4:
                return
            estado["eliminatorias"]["semifinal"] = [
                {
                    "equipe_a": vencedores[0],
                    "equipe_b": vencedores[1],
                    "vencedor": None,
                },
                {
                    "equipe_a": vencedores[2],
                    "equipe_b": vencedores[3],
                    "vencedor": None,
                },
            ]
            estado["fase_atual"] = "semifinal"
            estado["confronto_atual"] = next(
                (
                    c
                    for c in estado["eliminatorias"]["semifinal"]
                    if self._paises_iguais(pais_jogador, c["equipe_a"])
                    or self._paises_iguais(pais_jogador, c["equipe_b"])
                ),
                None,
            )
            return

        if fase == "semifinal":
            if len(vencedores) < 2:
                return
            estado["eliminatorias"]["final"] = [
                {"equipe_a": vencedores[0], "equipe_b": vencedores[1], "vencedor": None}
            ]
            estado["fase_atual"] = "final"
            confronto_final = estado["eliminatorias"]["final"][0]
            if self._paises_iguais(
                pais_jogador, confronto_final["equipe_a"]
            ) or self._paises_iguais(pais_jogador, confronto_final["equipe_b"]):
                estado["confronto_atual"] = confronto_final
            else:
                estado["confronto_atual"] = None
            return

        if fase == "final":
            if not vencedores:
                return
            estado["fase_atual"] = "finalizado"
            estado["campeao"] = vencedores[0]
            estado["confronto_atual"] = None
            estado["jogador_vivo"] = self._paises_iguais(vencedores[0], pais_jogador)

    def jogador_ainda_ativo(self):
        """Verifica se o jogador ainda está no torneio."""
        estado = self._carregar_estado()
        return estado.get("jogador_vivo", True) and estado.get(
            "jogador_convocado", False
        )

    def obter_fase_atual(self):
        """Retorna a fase atual do torneio."""
        estado = self._carregar_estado()
        return estado.get("fase_atual", "qualifiers")

    def exibir_tabela_grupo(self):
        """Exibe status do torneio (qualifiers ou chave final)."""
        estado = self._carregar_estado()
        fase = estado.get("fase_atual")
        pais_jogador = estado.get("pais_jogador", self.pais_jogador)

        if fase == "qualifiers":
            confronto = estado.get("confronto_atual") or {}
            local = (
                self._info_local_confronto(
                    estado.get("modo_competicao"),
                    confronto.get("equipe_a"),
                    confronto.get("equipe_b"),
                )
                or {}
            )
            print_blue(f"\n{'=' * 60}")
            print_blue("           📊 DAVIS CUP QUALIFIERS")
            print_blue(f"{'=' * 60}")
            modo_davis = estado.get("modo_davis")
            modo_label = (
                "Carreira (ranking de nações)"
                if modo_davis == "carreira"
                else "Histórico 2026"
            )
            print(f"Modo: {modo_label}")
            print(f"Seleção: {pais_jogador}")
            print(
                f"Tie: {confronto.get('equipe_a', '??')} vs {confronto.get('equipe_b', '??')}"
            )
            if local:
                print(
                    f"Sede: {local.get('cidade', '??')}, {local.get('pais', '??')} | {local.get('superficie', 'Hard')}"
                )
            print("Formato: melhor de 5 partidas (2 simples + 1 duplas + 2 simples)")
            return

        print_blue(f"\n{'=' * 60}")
        print_blue("             📊 DAVIS CUP - FINAL 8")
        print_blue(f"{'=' * 60}")
        for fase_chave in ("quartas", "semifinal", "final"):
            confrontos = estado.get("eliminatorias", {}).get(fase_chave, [])
            if not confrontos:
                continue
            print(f"\n{fase_chave.capitalize()}:")
            for c in confrontos:
                a = c.get("equipe_a", "??")
                b = c.get("equipe_b", "??")
                v = c.get("vencedor")
                marca = f" -> {v}" if v else ""
                estrela = (
                    " ⭐"
                    if self._paises_iguais(a, pais_jogador)
                    or self._paises_iguais(b, pais_jogador)
                    else ""
                )
                local = (
                    self._info_local_confronto(estado.get("modo_competicao"), a, b)
                    or {}
                )
                local_txt = ""
                if local:
                    local_txt = (
                        f" [{local.get('cidade', '??')}, {local.get('pais', '??')}]"
                    )
                print(f"  {a} vs {b}{marca}{estrela}{local_txt}")

    def obter_confronto_jogador(self, nome_jogador=None):
        """Retorna os dados do confronto atual do jogador humano."""
        estado = self._carregar_estado()
        if not estado.get("jogador_convocado"):
            return None

        confronto = estado.get("confronto_atual")
        if not confronto:
            return None

        # O "adversário" depende de qual partida do tie estamos
        idx_partida = estado.get("partida_atual", 0)
        # Se o tie já acabou ou passou do limite
        if idx_partida >= 5:
            return None

        # Determina a partida atual do tie
        # Formato simplificado para MatchRuntime: retorna o oponente direto
        # Precisamos saber se o jogador joga a partida atual
        pais_jogador = estado.get("pais_jogador")
        equipe_a = confronto.get("equipe_a")
        equipe_b = confronto.get("equipe_b")

        # Gera a agenda (mesma lógica de jogar_confronto)
        selecao_a = SelecaoNacional(equipe_a, self.ranking, genero=self.genero)
        selecao_a.completar_convocacao(5)
        selecao_b = SelecaoNacional(equipe_b, self.ranking, genero=self.genero)
        selecao_b.completar_convocacao(5)

        # Identifica quem é a seleção do jogador
        minha_sel = (
            selecao_a if self._paises_iguais(equipe_a, pais_jogador) else selecao_b
        )
        adv_sel = selecao_b if minha_sel == selecao_a else selecao_a

        # Agenda 5 partidas (Qualifiers) ou 3 (Final 8)
        fase = estado.get("fase_atual")
        total = 3 if fase in ("quartas", "semifinal", "final") else 5

        if idx_partida >= total:
            return None

        # Titulares
        s1_j = minha_sel.convocados[0]
        s2_j = minha_sel.convocados[1]
        s1_a = adv_sel.convocados[0]
        s2_a = adv_sel.convocados[1]

        agenda = []
        if total == 3:
            agenda = [
                ("simples", s2_j, s2_a),
                ("simples", s1_j, s1_a),
                ("duplas", None, None),
            ]
        else:
            agenda = [
                ("simples", s2_j, s2_a),
                ("simples", s1_j, s1_a),
                ("duplas", None, None),
                ("simples", s1_j, s2_a),
                ("simples", s2_j, s1_a),
            ]

        tipo, p_j, p_a = agenda[idx_partida]

        # Verifica se é a vez do humano
        if tipo == "simples":
            if normalizar_nome(p_j.get("nome", "")) == normalizar_nome(
                self.jogador.nome
            ):
                return {
                    "jogador1": p_j.get("nome"),
                    "jogador2": p_a.get("nome"),
                    "jogador1_nacionalidade": minha_sel.pais,
                    "jogador2_nacionalidade": adv_sel.pais,
                    "superficie": (
                        (self.obter_info_confronto_atual() or {}).get("superficie")
                        or self.tournament_data.get("superficie", "Hard")
                    ),
                    "tipo": "simples",
                    "fase": fase,
                }

        return None

    def processar_resultado_partida(self, jogador, adversario, resultado, placar_texto):
        """Registra o resultado de uma partida individual no tie da Davis."""
        estado = self._carregar_estado()
        confronto = estado.get("confronto_atual")
        if not confronto:
            return

        idx = estado.get("partida_atual", 0)
        venc_nome = resultado.get("nome")

        # Registra a partida no log do confronto
        partida_log = {
            "tipo": "simples",
            "jogador_a": (
                jogador.nome if hasattr(jogador, "nome") else jogador.get("nome")
            ),
            "jogador_b": adversario.get("nome"),
            "vencedor": venc_nome,
            "placar": placar_texto,
        }

        if "partidas" not in confronto:
            confronto["partidas"] = []
        confronto["partidas"].append(partida_log)

        # Atualiza placar do tie
        if "placar_tie" not in confronto:
            confronto["placar_tie"] = [0, 0]

        # Quem é equipe A e B no tie?
        pais_j = estado.get("pais_jogador")
        if self._paises_iguais(confronto["equipe_a"], pais_j):
            idx_venc = (
                0
                if normalizar_nome(venc_nome)
                == normalizar_nome(
                    jogador.nome if hasattr(jogador, "nome") else jogador.get("nome")
                )
                else 1
            )
        else:
            idx_venc = (
                1
                if normalizar_nome(venc_nome)
                == normalizar_nome(
                    jogador.nome if hasattr(jogador, "nome") else jogador.get("nome")
                )
                else 0
            )

        confronto["placar_tie"][idx_venc] += 1
        estado["partida_atual"] = idx + 1

        # Verifica se o tie acabou
        alvo = self._vitorias_para_vencer_tie(estado)
        if max(confronto["placar_tie"]) >= alvo:
            venc_tie = (
                confronto["equipe_a"]
                if confronto["placar_tie"][0] >= alvo
                else confronto["equipe_b"]
            )
            confronto["vencedor"] = venc_tie
            # Atualiza o estado geral com o vencedor do tie
            self._atualizar_estado_apos_confronto(confronto)
        else:
            self._salvar_estado(estado)

    def simular_npcs_na_fase_atual(self, nome_jogador=None):
        """Simula as outras partidas do tie (NPCs) até que seja a vez do jogador ou o tie acabe."""
        estado = self._carregar_estado()
        confronto = estado.get("confronto_atual")
        if not confronto or confronto.get("vencedor"):
            return

        pais_j = estado.get("pais_jogador")
        equipe_a = confronto.get("equipe_a")
        equipe_b = confronto.get("equipe_b")

        selecao_a = SelecaoNacional(equipe_a, self.ranking, genero=self.genero)
        selecao_a.completar_convocacao(5)
        selecao_b = SelecaoNacional(equipe_b, self.ranking, genero=self.genero)
        selecao_b.completar_convocacao(5)

        minha_sel = selecao_a if self._paises_iguais(equipe_a, pais_j) else selecao_b
        adv_sel = selecao_b if minha_sel == selecao_a else selecao_a

        fase = estado.get("fase_atual")
        total = 3 if fase in ("quartas", "semifinal", "final") else 5
        alvo = self._vitorias_para_vencer_tie(estado)

        # Titulares
        s1_j = minha_sel.convocados[0]
        s2_j = minha_sel.convocados[1]
        s1_a = adv_sel.convocados[0]
        s2_a = adv_sel.convocados[1]

        agenda = []
        if total == 3:
            agenda = [
                ("simples", s2_j, s2_a),
                ("simples", s1_j, s1_a),
                ("duplas", None, None),
            ]
        else:
            agenda = [
                ("simples", s2_j, s2_a),
                ("simples", s1_j, s1_a),
                ("duplas", None, None),
                ("simples", s1_j, s2_a),
                ("simples", s2_j, s1_a),
            ]

        while estado["partida_atual"] < total and not confronto.get("vencedor"):
            idx = estado["partida_atual"]
            tipo, p_j, p_a = agenda[idx]

            # Se for a vez do humano, para a simulação
            if tipo == "simples" and normalizar_nome(
                p_j.get("nome", "")
            ) == normalizar_nome(self.jogador.nome):
                break

            # Simula partida NPC
            if tipo == "simples":
                # Lógica simplificada de vitória baseada em overall
                ovr_j = p_j.get("overall", 70)
                ovr_a = p_a.get("overall", 70)
                prob = 0.5 + (ovr_j - ovr_a) * 0.05
                venceu = random.random() < prob
                venc_nome = p_j["nome"] if venceu else p_a["nome"]
                placar = "2-0" if venceu else "0-2"

                partida_log = {
                    "tipo": "simples",
                    "jogador_a": p_j["nome"],
                    "jogador_b": p_a["nome"],
                    "vencedor": venc_nome,
                    "placar": placar,
                }
            else:
                # Duplas
                ovr_j = (
                    minha_sel.convocados[0]["overall"]
                    + minha_sel.convocados[2]["overall"]
                ) / 2
                ovr_a = (
                    adv_sel.convocados[0]["overall"] + adv_sel.convocados[2]["overall"]
                ) / 2
                prob = 0.5 + (ovr_j - ovr_a) * 0.05
                venceu = random.random() < prob
                venc_nome = minha_sel.pais if venceu else adv_sel.pais
                placar = "2-1" if venceu else "1-2"

                partida_log = {
                    "tipo": "duplas",
                    "equipe_a": minha_sel.pais,
                    "equipe_b": adv_sel.pais,
                    "vencedor": venc_nome,
                    "placar": placar,
                }

            if "partidas" not in confronto:
                confronto["partidas"] = []
            confronto["partidas"].append(partida_log)

            if "placar_tie" not in confronto:
                confronto["placar_tie"] = [0, 0]

            idx_venc = 0 if venceu == (minha_sel == selecao_a) else 1
            confronto["placar_tie"][idx_venc] += 1
            estado["partida_atual"] += 1

            if max(confronto["placar_tie"]) >= alvo:
                venc_tie = (
                    confronto["equipe_a"]
                    if confronto["placar_tie"][0] >= alvo
                    else confronto["equipe_b"]
                )
                confronto["vencedor"] = venc_tie
                self._atualizar_estado_apos_confronto(confronto)
                return

        self._salvar_estado(estado)

    def _montar_fatores_fadiga(self, config, adversario):
        """Retorna dicionário de fatores para cálculo de fadiga."""
        return {
            "superficie": config.superficie,
            "melhor_de": config.melhor_de,
            "ovr_adversario": adversario.get("overall", 70),
        }

    def to_api_state(self):
        """Retorna o estado serializável para a API."""
        estado = self._carregar_estado()
        confronto_tie = estado.get("confronto_atual") or {}

        # Cria um 'bracket' virtual com a partida atual para o MatchScreen encontrar o adversário
        bracket = []
        conf_humano = self.obter_confronto_jogador()
        if conf_humano:
            bracket.append(
                {
                    "jogador1": conf_humano["jogador1"],
                    "jogador2": conf_humano["jogador2"],
                    "jogador1_nacionalidade": conf_humano["jogador1_nacionalidade"],
                    "jogador2_nacionalidade": conf_humano["jogador2_nacionalidade"],
                    "fase": conf_humano["fase"],
                    "vencedor": None,
                    "placar": "",
                }
            )

        return {
            "nome": estado.get("torneio", "Davis Cup"),
            "tipo": estado.get("tipo", "Davis Cup"),
            "fase_atual": estado.get("fase_atual", "qualifiers"),
            "jogador_ativo": self.jogador_ainda_ativo(),
            "davis": True,
            "estado": estado,
            "confronto_atual": confronto_tie,
            "bracket": bracket,
            "superficie": (
                (self.obter_info_confronto_atual() or {}).get("superficie")
                or self.tournament_data.get("superficie", "Hard")
            ),
        }


def criar_torneio_davis(torneio_data, jogador, nome_save, semana, interactive=True):
    """Cria e inicializa um torneio de Copa Davis."""
    ranking_path = get_caminho_ranking_save(
        nome_save, genero=getattr(jogador, "genero", "masculino")
    )
    ranking = SistemaRanking(ranking_path)

    torneio_data = dict(torneio_data or {})
    torneio_data["semana"] = semana
    try:
        from src.dados import carregar_temporada

        torneio_data["ano_referencia"] = int(
            carregar_temporada(nome_save).get("ano", 2026)
        )
    except Exception as e:
        log_erro(
            nome_save,
            "criar_torneio_davis_ano_referencia",
            e,
            {"semana": semana, "torneio": torneio_data.get("nome")},
        )
        torneio_data["ano_referencia"] = 2026

    davis = DavisCup(
        tournament_data=torneio_data,
        jogador=jogador,
        ranking=ranking,
        nome_save=nome_save,
    )

    # Processa a convocação
    try:
        convocado = davis.processar_convocacao(interactive=interactive)
    except TypeError:
        # Compatibilidade com stubs/test doubles antigos que não aceitam o novo parâmetro.
        convocado = davis.processar_convocacao()

    if not convocado:
        # Jogador não foi convocado ou recusou - salva moral atualizada
        salvar_jogo(nome_save, jogador)
        return None

    # Atualiza estado com a convocação
    estado = davis._carregar_estado()
    estado["jogador_convocado"] = True
    estado = davis._persistir_convocacao_no_estado(estado)

    # Encontra a posição do jogador na convocação
    if davis.selecao:
        for i, c in enumerate(davis.selecao.convocados):
            if c.get("e_jogador_principal"):
                estado["posicao_convocacao"] = i + 1
                break

    davis._salvar_estado(estado)

    if interactive:
        nome_competicao = estado.get("tipo", "Davis Cup")
        print_green(f"\n🏆 {nome_competicao} iniciada!")
        if estado.get("fase_atual") == "qualifiers":
            confronto = estado.get("confronto_atual") or {}
            print(
                f"📍 Tie classificatório: {confronto.get('equipe_a', '??')} vs {confronto.get('equipe_b', '??')}"
            )
            local = (
                davis._info_local_confronto(
                    estado.get("modo_competicao"),
                    confronto.get("equipe_a"),
                    confronto.get("equipe_b"),
                )
                or {}
            )
            if local:
                print(
                    f"📌 Sede: {local.get('cidade', '??')}, {local.get('pais', '??')} | {local.get('superficie', 'Hard')}"
                )
        else:
            print("📍 Formato Final 8 em mata-mata.")

        davis.exibir_tabela_grupo()

        safe_input("\nPressione Enter para continuar...")

    return davis


def carregar_davis_cup(nome_save, jogador):
    """Carrega um torneio de Copa Davis existente."""
    genero = getattr(jogador, "genero", "masculino")
    estado = carregar_estado_torneio(nome_save, genero=genero)
    tipos_validos = {"Davis Cup", "Billie Jean King Cup"}
    if not estado or estado.get("tipo") not in tipos_validos:
        return None

    ranking_path = get_caminho_ranking_save(nome_save, genero=genero)
    ranking = SistemaRanking(ranking_path)

    return DavisCup(
        tournament_data=estado.get("tournament_data", {}),
        jogador=jogador,
        ranking=ranking,
        nome_save=nome_save,
    )
