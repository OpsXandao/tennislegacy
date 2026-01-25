"""
Copa Davis - Torneio de Tênis por Equipes Nacionais

A Copa Davis é a principal competição masculina de tênis por equipes.
Cada confronto (tie) consiste em:
- 2 partidas de simples
- 1 partida de duplas (simulada automaticamente)

O jogador participa representando seu país nas partidas de simples,
mas precisa ser convocado pela seleção nacional.
"""

import json
import random

from src.dados import (
    get_caminho_ranking_save,
    get_caminho_torneio_save,
    carregar_estado_torneio,
)
from src.jogador import normalizar_nome
from src.ranking import SistemaRanking
from src.jogar_partida import criar_config_partida, jogar_partida
from src.progressao import handle_xp_e_level_up, handle_fadiga_e_lesao
from src.save import salvar_jogo
from src.io_utils import safe_input, print_blue, print_green, print_yellow, print_red, clear_screen


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


class SelecaoNacional:
    """Representa uma seleção nacional na Copa Davis."""

    def __init__(self, pais, ranking):
        self.pais = pais
        self.ranking = ranking
        self.jogadores = self._buscar_jogadores_do_pais()
        self.convocados = []
        self.capitao = self._gerar_capitao()

    def _buscar_jogadores_do_pais(self):
        """Busca todos os jogadores do país no ranking."""
        jogadores = []
        for j in self.ranking.ranking:
            nac = j.get("nacionalidade", "")
            # Normaliza para comparação
            if self._normalizar_pais(nac) == self._normalizar_pais(self.pais):
                jogadores.append(j)

        # Ordena por pontos no ranking
        jogadores.sort(key=lambda x: x.get("pontos", 0), reverse=True)
        return jogadores

    def _normalizar_pais(self, pais):
        """Normaliza o nome do país para comparação."""
        if not pais:
            return ""
        # Extrai o código do país [XX]
        if pais.startswith("["):
            codigo = pais.split("]")[0] + "]"
            return codigo.upper()
        return pais.upper()

    def _gerar_capitao(self):
        """Gera um capitão fictício para a seleção."""
        # Mapeamento por código de país para funcionar com qualquer formato de nome
        capitaes_por_codigo = {
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
            "[SE]": "Robin Söderling",
            "[BE]": "Johan Van Herck",
            "[CH]": "Severin Lüthi",
            "[RS]": "Viktor Troicki",
            "[BR]": "Jaime Oncins",
            "[PT]": "Rui Machado",
            "[JP]": "Satoshi Iwabuchi",
            "[PL]": "Radosław Szymanik",
            "[CL]": "Nicolás Massú",
            "[KR]": "Hyung-Taik Lee",
        }

        # Extrai o código do país
        if self.pais and self.pais.startswith("["):
            codigo = self.pais.split("]")[0] + "]"
            return capitaes_por_codigo.get(codigo, f"Capitão de {self.pais}")

        return f"Capitão de {self.pais}"

    def verificar_elegibilidade(self, jogador):
        """
        Verifica se o jogador é elegível para convocação.
        Retorna (elegivel, posicao_no_pais, mensagem).
        """
        nome_normalizado = normalizar_nome(jogador.nome)

        # Verifica se o jogador é do mesmo país
        if self._normalizar_pais(jogador.nacionalidade) != self._normalizar_pais(self.pais):
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
            "overall": jogador.calcular_overall() if hasattr(jogador, 'calcular_overall') else jogador.get("overall", 70),
            "atributos": jogador.atributos if hasattr(jogador, 'atributos') else jogador.get("atributos", {}),
            "posicao_convocacao": posicao_convocacao,
            "e_jogador_principal": True
        }

        # Remove se já estava convocado
        self.convocados = [c for c in self.convocados if normalizar_nome(c.get("nome", "")) != normalizar_nome(jogador.nome)]

        # Adiciona na posição correta
        self.convocados.insert(posicao_convocacao - 1, jogador_dict)

    def completar_convocacao(self, num_jogadores=4):
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

        # Se ainda faltam jogadores, gera fictícios
        while len(self.convocados) < num_jogadores:
            ficticio = {
                "nome": f"Jogador {len(self.convocados) + 1} ({self.pais})",
                "nacionalidade": self.pais,
                "overall": random.randint(55, 70),
                "atributos": self._gerar_atributos_ficticios(),
                "posicao_convocacao": len(self.convocados) + 1,
                "e_jogador_principal": False,
                "e_ficticio": True
            }
            self.convocados.append(ficticio)

    def _gerar_atributos_ficticios(self):
        """Gera atributos para jogadores fictícios."""
        return {
            "saque": random.randint(50, 75),
            "forehand": random.randint(50, 75),
            "backhand": random.randint(50, 75),
            "topspin": random.randint(50, 75),
            "voleio": random.randint(50, 75),
            "slice": random.randint(50, 75),
            "movimento": random.randint(50, 75),
            "lob": random.randint(50, 75),
            "winner": random.randint(50, 75),
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
            posicao = "Simples 1" if i == 1 else ("Simples 2" if i == 2 else ("Duplas" if i <= 4 else "Reserva"))

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
        self.caminho_json = get_caminho_torneio_save(nome_save)
        self.pais_jogador = jogador.nacionalidade
        self.selecao = None

    def _carregar_estado(self):
        """Carrega o estado atual do torneio."""
        estado = carregar_estado_torneio(self.nome_save)
        # Verifica se o estado é do tipo correto (Davis Cup)
        if estado is None or estado.get("tipo") != "Davis Cup":
            estado = self._criar_estado_inicial()
            self._salvar_estado(estado)
        return estado

    def _salvar_estado(self, estado):
        """Salva o estado do torneio."""
        with open(self.caminho_json, "w", encoding="utf-8") as f:
            json.dump(estado, f, indent=2, ensure_ascii=False)

    def verificar_convocacao(self):
        """
        Verifica se o jogador será convocado para a seleção.
        Retorna (convocado, posicao, mensagem).
        """
        self.selecao = SelecaoNacional(self.pais_jogador, self.ranking)
        elegivel, posicao, msg = self.selecao.verificar_elegibilidade(self.jogador)

        if not elegivel:
            return False, None, msg

        # Critérios de convocação:
        # - Top 4 do país: convocação garantida
        # - Posição 5-10: chance de 70%
        # - Posição 11+: chance de 30%

        if posicao <= 4:
            return True, posicao, f"Parabéns! Você foi convocado como #{posicao} do país!"
        elif posicao <= 10:
            if random.random() < 0.7:
                return True, posicao, f"Você foi convocado! (#{posicao} do país)"
            else:
                return False, posicao, f"Infelizmente você não foi convocado desta vez. (#{posicao} do país)"
        else:
            if random.random() < 0.3:
                return True, posicao, f"Surpresa! Você foi convocado como revelação! (#{posicao} do país)"
            else:
                return False, posicao, f"Você não foi convocado. Continue subindo no ranking! (#{posicao} do país)"

    def processar_convocacao(self):
        """
        Processa toda a lógica de convocação do jogador.
        Retorna True se foi convocado E aceitou, False caso contrário.
        """
        clear_screen()
        print_blue("\n" + "=" * 60)
        print_blue("           🏆 COPA DAVIS - CONVOCAÇÃO")
        print_blue("=" * 60)

        print(f"\n📍 Sua nacionalidade: {self.pais_jogador}")
        print(f"📍 Capitão da seleção: ", end="")

        self.selecao = SelecaoNacional(self.pais_jogador, self.ranking)
        print(f"{self.selecao.capitao}")

        print("\n" + "-" * 60)
        print("📊 JOGADORES DO SEU PAÍS NO RANKING:")
        print("-" * 60)

        for i, j in enumerate(self.selecao.jogadores[:10], 1):
            nome = j.get("nome", "??")
            pontos = j.get("pontos", 0)
            overall = j.get("overall", "??")
            destaque = " ⭐ (VOCÊ)" if normalizar_nome(nome) == normalizar_nome(self.jogador.nome) else ""
            print(f"  {i:2}. {nome:<25} | OVR: {overall:>3} | Pts: {pontos:>5}{destaque}")

        print("-" * 60)

        safe_input("\nPressione Enter para ver a convocação...")

        # Verifica convocação
        convocado, posicao, mensagem = self.verificar_convocacao()

        clear_screen()
        print_blue("\n" + "=" * 60)
        print_blue("           📋 LISTA DE CONVOCADOS")
        print_blue("=" * 60)

        if convocado:
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
            self.selecao.completar_convocacao(4)
            self.selecao.exibir_convocacao()

            print(f"\n🎾 Você jogará as partidas de {('Simples 1' if pos_convocacao == 1 else 'Simples 2')}!")

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
                    print_green(f"\n🎉 Você aceitou representar {self.pais_jogador} na Copa Davis!")
                    safe_input("Pressione Enter para continuar...")
                    return True
                elif escolha == "2":
                    return self._processar_recusa_convocacao(posicao)
                else:
                    print_red("Opção inválida. Digite 1 ou 2.")

        else:
            print_red(f"\n❌ {mensagem}")

            # Mostra a convocação sem o jogador
            self.selecao.completar_convocacao(4)
            print("\n📋 Convocados para representar o país:")
            self.selecao.exibir_convocacao()

            print_yellow("\n💪 Continue trabalhando duro para ser convocado na próxima!")

            safe_input("\nPressione Enter para continuar...")
            return False

    def _processar_recusa_convocacao(self, posicao):
        """Processa a recusa de convocação pelo jogador."""
        clear_screen()
        print_blue("\n" + "=" * 60)
        print_blue("           ❌ CONVOCAÇÃO RECUSADA")
        print_blue("=" * 60)

        print_yellow(f"\n📰 NOTÍCIA: {self.jogador.nome} recusa convocação para a Copa Davis!")
        print()

        # Mensagens diferentes baseadas na posição do jogador
        if posicao == 1:
            print(f"   \"{self.jogador.nome}, número 1 do país, decidiu não")
            print(f"   defender as cores de {self.pais_jogador} na Copa Davis.")
            print(f"   A decisão causou surpresa no mundo do tênis.\"")
            impacto_moral = -10
        elif posicao <= 3:
            print(f"   \"{self.jogador.nome}, um dos principais jogadores do país,")
            print(f"   optou por não participar da Copa Davis, priorizando")
            print(f"   sua agenda no circuito individual.\"")
            impacto_moral = -5
        else:
            print(f"   \"{self.jogador.nome} comunicou ao capitão {self.selecao.capitao}")
            print(f"   que não poderá atender à convocação para a Copa Davis.\"")
            impacto_moral = -3

        print()
        print_yellow(f"📊 Impacto: Moral {impacto_moral}")

        # Aplica penalidade de moral
        if hasattr(self.jogador, 'moral'):
            self.jogador.moral = max(0, self.jogador.moral + impacto_moral)

        # Mostra a convocação substituta
        print()
        print("-" * 60)
        print_yellow("O capitão convocou um substituto:")
        print("-" * 60)

        # Reconstrói a convocação sem o jogador
        self.selecao = SelecaoNacional(self.pais_jogador, self.ranking)
        self.selecao.completar_convocacao(4)
        self.selecao.exibir_convocacao()

        print()
        print_yellow("A Copa Davis seguirá sem sua participação.")
        print_yellow("Você poderá focar em outros torneios do calendário.")

        safe_input("\nPressione Enter para continuar...")
        return False

    def _criar_estado_inicial(self):
        """Cria o estado inicial da Copa Davis com grupos e confrontos."""
        # Garante que o país do jogador esteja entre os participantes
        paises = list(PAISES_DAVIS_CUP)

        # Normaliza o país do jogador
        pais_jogador_normalizado = self._normalizar_pais_para_lista(self.pais_jogador)

        if pais_jogador_normalizado and pais_jogador_normalizado not in paises:
            paises[-1] = pais_jogador_normalizado

        random.shuffle(paises)

        # Divide em 6 grupos de 3 equipes
        grupos = {}
        nomes_grupos = ["A", "B", "C", "D", "E", "F"]
        for i, nome_grupo in enumerate(nomes_grupos):
            inicio = i * 3
            equipes_grupo = paises[inicio:inicio + 3]
            grupos[nome_grupo] = {
                "equipes": equipes_grupo,
                "resultados": [],
                "tabela": {pais: {"v": 0, "d": 0, "pts": 0} for pais in equipes_grupo}
            }

        # Encontra o grupo do jogador
        grupo_jogador = None
        pais_no_torneio = pais_jogador_normalizado or self.pais_jogador

        for nome_grupo, dados in grupos.items():
            for equipe in dados["equipes"]:
                if self._paises_iguais(equipe, self.pais_jogador):
                    grupo_jogador = nome_grupo
                    pais_no_torneio = equipe
                    break
            if grupo_jogador:
                break

        # Gera as seleções de cada país
        selecoes = {}
        for pais in paises:
            sel = SelecaoNacional(pais, self.ranking)
            sel.completar_convocacao(4)
            selecoes[pais] = {
                "capitao": sel.capitao,
                "convocados": sel.convocados
            }

        return {
            "torneio": self.tournament_data["nome"],
            "tipo": "Davis Cup",
            "semana": self.tournament_data.get("semana", 1),
            "fase_atual": "grupos",
            "jogador": self.jogador.nome,
            "pais_jogador": pais_no_torneio,
            "grupo_jogador": grupo_jogador,
            "jogador_vivo": True,
            "jogador_convocado": False,
            "posicao_convocacao": None,
            "grupos": grupos,
            "selecoes": selecoes,
            "eliminatorias": {},
            "resultados_confrontos": [],
            "confronto_atual": None,
            "partida_atual": 0,
            "tournament_data": self.tournament_data,
        }

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

        # Compara códigos [XX]
        def extrair_codigo(pais):
            if pais.startswith("["):
                return pais.split("]")[0].upper() + "]"
            return pais.upper()

        return extrair_codigo(pais1) == extrair_codigo(pais2)

    def _gerar_equipe_adversaria(self, pais):
        """Retorna a equipe adversária (jogadores convocados)."""
        estado = self._carregar_estado()
        selecao_dados = estado.get("selecoes", {}).get(pais)

        if selecao_dados and selecao_dados.get("convocados"):
            return selecao_dados["convocados"][:2]

        # Fallback: gera jogadores
        sel = SelecaoNacional(pais, self.ranking)
        sel.completar_convocacao(4)
        return sel.convocados[:2]

    def obter_proximo_confronto(self):
        """Retorna informações sobre o próximo confronto do jogador."""
        estado = self._carregar_estado()

        if not estado.get("jogador_convocado"):
            return None

        if estado["fase_atual"] == "grupos":
            grupo = estado["grupos"].get(estado["grupo_jogador"])
            if not grupo:
                return None

            pais_jogador = estado["pais_jogador"]

            # Encontra adversários que ainda não enfrentou
            adversarios_enfrentados = set()
            for resultado in grupo["resultados"]:
                if self._paises_iguais(pais_jogador, resultado["equipe_a"]) or \
                   self._paises_iguais(pais_jogador, resultado["equipe_b"]):
                    adversarios_enfrentados.add(resultado["equipe_a"])
                    adversarios_enfrentados.add(resultado["equipe_b"])

            for equipe in grupo["equipes"]:
                if not self._paises_iguais(equipe, pais_jogador) and equipe not in adversarios_enfrentados:
                    return {
                        "fase": "grupos",
                        "adversario": equipe,
                        "grupo": estado["grupo_jogador"],
                    }

            return None

        elif estado["fase_atual"] in ["quartas", "semifinal", "final"]:
            confronto = estado.get("confronto_atual")
            if confronto:
                pais_jogador = estado["pais_jogador"]
                if self._paises_iguais(pais_jogador, confronto["equipe_a"]) or \
                   self._paises_iguais(pais_jogador, confronto["equipe_b"]):
                    adversario = confronto["equipe_b"] if self._paises_iguais(pais_jogador, confronto["equipe_a"]) else confronto["equipe_a"]
                    return {
                        "fase": estado["fase_atual"],
                        "adversario": adversario,
                    }

        return None

    def jogar_confronto(self, adversario_pais):
        """
        Joga um confronto (tie) contra um país adversário.
        Retorna o resultado do confronto.
        """
        estado = self._carregar_estado()
        pais_jogador = estado["pais_jogador"]

        clear_screen()
        print_blue(f"\n{'=' * 60}")
        print_blue(f"     🏆 COPA DAVIS - {pais_jogador} vs {adversario_pais}")
        print_blue(f"{'=' * 60}")

        equipe_adversaria = self._gerar_equipe_adversaria(adversario_pais)

        print(f"\n📋 Adversários:")
        for i, adv in enumerate(equipe_adversaria, 1):
            print(f"   {i}. {adv.get('nome', '??')} (OVR: {adv.get('overall', '??')})")

        safe_input("\nPressione Enter para começar o confronto...")

        vitorias_jogador = 0
        vitorias_adversario = 0
        resultados_partidas = []

        # Configuração para partidas da Davis Cup (melhor de 3)
        config = criar_config_partida(self.tournament_data)

        # Partida 1: Simples - Jogador vs Adversário 1
        clear_screen()
        print_blue(f"\n{'=' * 60}")
        print_blue(f"     SIMPLES 1: {self.jogador.nome} vs {equipe_adversaria[0]['nome']}")
        print_blue(f"{'=' * 60}\n")

        vencedor_nome, placar, pontos_disputados = jogar_partida(
            self.jogador, equipe_adversaria[0], self.nome_save, config=config
        )

        if normalizar_nome(vencedor_nome) == normalizar_nome(self.jogador.nome):
            vitorias_jogador += 1
            print_green(f"\n✅ {pais_jogador} vence! Placar: {placar}")
        else:
            vitorias_adversario += 1
            print_red(f"\n❌ {adversario_pais} vence! Placar: {placar}")

        print(f"\n📊 Placar do confronto: {pais_jogador} {vitorias_jogador} x {vitorias_adversario} {adversario_pais}")

        resultados_partidas.append({
            "tipo": "simples",
            "jogador_a": self.jogador.nome,
            "jogador_b": equipe_adversaria[0]["nome"],
            "vencedor": vencedor_nome,
            "placar": placar
        })

        # Atualiza XP e fadiga
        vitoria1 = normalizar_nome(vencedor_nome) == normalizar_nome(self.jogador.nome)
        self.jogador = handle_xp_e_level_up(self.jogador, vitoria1)
        self.jogador = handle_fadiga_e_lesao(self.jogador, pontos_disputados=pontos_disputados)
        salvar_jogo(self.nome_save, self.jogador)

        safe_input("\nPressione Enter para a próxima partida...")

        # Partida 2: Simples - Jogador vs Adversário 2
        clear_screen()
        print_blue(f"\n{'=' * 60}")
        print_blue(f"     SIMPLES 2: {self.jogador.nome} vs {equipe_adversaria[1]['nome']}")
        print_blue(f"{'=' * 60}\n")

        vencedor_nome2, placar2, pontos_disputados2 = jogar_partida(
            self.jogador, equipe_adversaria[1], self.nome_save, config=config
        )

        if normalizar_nome(vencedor_nome2) == normalizar_nome(self.jogador.nome):
            vitorias_jogador += 1
            print_green(f"\n✅ {pais_jogador} vence! Placar: {placar2}")
        else:
            vitorias_adversario += 1
            print_red(f"\n❌ {adversario_pais} vence! Placar: {placar2}")

        print(f"\n📊 Placar do confronto: {pais_jogador} {vitorias_jogador} x {vitorias_adversario} {adversario_pais}")

        resultados_partidas.append({
            "tipo": "simples",
            "jogador_a": self.jogador.nome,
            "jogador_b": equipe_adversaria[1]["nome"],
            "vencedor": vencedor_nome2,
            "placar": placar2
        })

        vitoria2 = normalizar_nome(vencedor_nome2) == normalizar_nome(self.jogador.nome)
        self.jogador = handle_xp_e_level_up(self.jogador, vitoria2)
        self.jogador = handle_fadiga_e_lesao(self.jogador, pontos_disputados=pontos_disputados2)
        salvar_jogo(self.nome_save, self.jogador)

        safe_input("\nPressione Enter para a partida de duplas...")

        # Partida 3: Duplas (simulada)
        clear_screen()
        print_blue(f"\n{'=' * 60}")
        print_blue(f"     DUPLAS: {pais_jogador} vs {adversario_pais}")
        print_blue(f"{'=' * 60}\n")

        print_yellow("🎾 A partida de duplas será simulada...")
        print()

        # Simula com base no desempenho anterior
        chance_vitoria = 0.5 + (0.15 * (vitorias_jogador - vitorias_adversario))
        sets_a = 0
        sets_b = 0

        for set_num in range(3):
            if random.random() < chance_vitoria:
                sets_a += 1
                print(f"   Set {set_num + 1}: {pais_jogador} vence")
            else:
                sets_b += 1
                print(f"   Set {set_num + 1}: {adversario_pais} vence")

            if sets_a == 2 or sets_b == 2:
                break

        if sets_a > sets_b:
            vitorias_jogador += 1
            resultado_duplas = f"{sets_a}-{sets_b}"
            print_green(f"\n✅ {pais_jogador} vence as duplas! ({resultado_duplas})")
        else:
            vitorias_adversario += 1
            resultado_duplas = f"{sets_b}-{sets_a}"
            print_red(f"\n❌ {adversario_pais} vence as duplas! ({resultado_duplas})")

        resultados_partidas.append({
            "tipo": "duplas",
            "equipe_a": pais_jogador,
            "equipe_b": adversario_pais,
            "vencedor": pais_jogador if vitorias_jogador > vitorias_adversario else adversario_pais,
            "placar": resultado_duplas
        })

        # Resultado final
        vencedor_confronto = pais_jogador if vitorias_jogador >= 2 else adversario_pais

        clear_screen()
        print_blue(f"\n{'=' * 60}")
        print_blue(f"           RESULTADO FINAL")
        print_blue(f"{'=' * 60}\n")

        print(f"   {pais_jogador}  {vitorias_jogador}  x  {vitorias_adversario}  {adversario_pais}\n")

        if vencedor_confronto == pais_jogador:
            print_green(f"🎉 {pais_jogador} VENCE O CONFRONTO!")
        else:
            print_red(f"😔 {adversario_pais} vence o confronto.")

        resultado_confronto = {
            "equipe_a": pais_jogador,
            "equipe_b": adversario_pais,
            "vencedor": vencedor_confronto,
            "placar": f"{vitorias_jogador}-{vitorias_adversario}",
            "partidas": resultados_partidas
        }

        self._atualizar_estado_apos_confronto(resultado_confronto)

        safe_input("\nPressione Enter para continuar...")

        return {
            "vencedor": vencedor_confronto,
            "placar": f"{vitorias_jogador}-{vitorias_adversario}",
            "eliminado": vencedor_confronto != pais_jogador and estado["fase_atual"] != "grupos"
        }

    def _atualizar_estado_apos_confronto(self, resultado):
        """Atualiza o estado do torneio após um confronto."""
        estado = self._carregar_estado()
        pais_jogador = estado["pais_jogador"]

        estado["resultados_confrontos"].append(resultado)

        if estado["fase_atual"] == "grupos":
            grupo = estado["grupos"][estado["grupo_jogador"]]
            grupo["resultados"].append(resultado)

            # Atualiza tabela
            vencedor = resultado["vencedor"]
            perdedor = resultado["equipe_b"] if resultado["equipe_a"] == vencedor else resultado["equipe_a"]

            if vencedor in grupo["tabela"]:
                grupo["tabela"][vencedor]["v"] += 1
                grupo["tabela"][vencedor]["pts"] += 2
            if perdedor in grupo["tabela"]:
                grupo["tabela"][perdedor]["d"] += 1

            # Verifica se fase de grupos terminou para o jogador
            confrontos_feitos = sum(
                1 for r in grupo["resultados"]
                if self._paises_iguais(pais_jogador, r["equipe_a"]) or self._paises_iguais(pais_jogador, r["equipe_b"])
            )

            if confrontos_feitos >= 2:
                self._simular_restante_grupos(estado)
                self._preparar_eliminatorias(estado)

        self._salvar_estado(estado)

    def _simular_restante_grupos(self, estado):
        """Simula os confrontos restantes dos grupos."""
        for nome_grupo, grupo in estado["grupos"].items():
            equipes = grupo["equipes"]

            confrontos_possiveis = [
                (equipes[0], equipes[1]),
                (equipes[0], equipes[2]),
                (equipes[1], equipes[2]),
            ]

            confrontos_feitos = set()
            for r in grupo["resultados"]:
                confrontos_feitos.add(frozenset([r["equipe_a"], r["equipe_b"]]))

            for eq_a, eq_b in confrontos_possiveis:
                if frozenset([eq_a, eq_b]) not in confrontos_feitos:
                    vencedor = random.choice([eq_a, eq_b])
                    perdedor = eq_b if vencedor == eq_a else eq_a

                    resultado = {
                        "equipe_a": eq_a,
                        "equipe_b": eq_b,
                        "vencedor": vencedor,
                        "placar": f"{random.choice([2, 3])}-{random.choice([0, 1])}",
                        "partidas": []
                    }
                    grupo["resultados"].append(resultado)

                    if vencedor in grupo["tabela"]:
                        grupo["tabela"][vencedor]["v"] += 1
                        grupo["tabela"][vencedor]["pts"] += 2
                    if perdedor in grupo["tabela"]:
                        grupo["tabela"][perdedor]["d"] += 1

    def _preparar_eliminatorias(self, estado):
        """Prepara a fase eliminatória."""
        classificados = []
        pais_jogador = estado["pais_jogador"]

        for nome_grupo, grupo in estado["grupos"].items():
            tabela_ordenada = sorted(
                grupo["tabela"].items(),
                key=lambda x: (x[1]["pts"], x[1]["v"]),
                reverse=True
            )

            for i in range(min(2, len(tabela_ordenada))):
                classificados.append({
                    "pais": tabela_ordenada[i][0],
                    "grupo": nome_grupo,
                    "posicao": i + 1
                })

        pais_classificou = any(self._paises_iguais(c["pais"], pais_jogador) for c in classificados)

        if not pais_classificou:
            estado["jogador_vivo"] = False
            estado["fase_atual"] = "eliminado_grupos"
            return

        estado["fase_atual"] = "quartas"

        random.shuffle(classificados)
        estado["eliminatorias"] = {
            "quartas": [],
            "semifinal": [],
            "final": []
        }

        for i in range(0, min(len(classificados), 8), 2):
            if i + 1 < len(classificados):
                estado["eliminatorias"]["quartas"].append({
                    "equipe_a": classificados[i]["pais"],
                    "equipe_b": classificados[i + 1]["pais"],
                    "vencedor": None
                })

        for confronto in estado["eliminatorias"]["quartas"]:
            if self._paises_iguais(pais_jogador, confronto["equipe_a"]) or \
               self._paises_iguais(pais_jogador, confronto["equipe_b"]):
                estado["confronto_atual"] = confronto
                break

    def jogador_ainda_ativo(self):
        """Verifica se o jogador ainda está no torneio."""
        estado = self._carregar_estado()
        return estado.get("jogador_vivo", True) and estado.get("jogador_convocado", False)

    def obter_fase_atual(self):
        """Retorna a fase atual do torneio."""
        estado = self._carregar_estado()
        return estado.get("fase_atual", "grupos")

    def exibir_tabela_grupo(self):
        """Exibe a tabela do grupo do jogador."""
        estado = self._carregar_estado()
        grupo_nome = estado.get("grupo_jogador")
        pais_jogador = estado.get("pais_jogador")

        if not grupo_nome:
            print("Grupo não encontrado.")
            return

        grupo = estado["grupos"].get(grupo_nome)
        if not grupo:
            print("Dados do grupo não encontrados.")
            return

        print_blue(f"\n{'=' * 50}")
        print_blue(f"     📊 TABELA - GRUPO {grupo_nome}")
        print_blue(f"{'=' * 50}")
        print(f"{'País':<25} {'V':>3} {'D':>3} {'Pts':>4}")
        print("-" * 50)

        tabela_ordenada = sorted(
            grupo["tabela"].items(),
            key=lambda x: (x[1]["pts"], x[1]["v"]),
            reverse=True
        )

        for i, (pais, dados) in enumerate(tabela_ordenada):
            marcador = " ⭐" if self._paises_iguais(pais, pais_jogador) else "  "
            classificado = " ✓" if i < 2 else "  "
            print(f"{marcador}{pais:<23} {dados['v']:>3} {dados['d']:>3} {dados['pts']:>4}{classificado}")

        print("=" * 50)
        print("✓ = Classificado para eliminatórias")


def criar_torneio_davis(torneio_data, jogador, nome_save, semana):
    """Cria e inicializa um torneio de Copa Davis."""
    ranking_path = get_caminho_ranking_save(nome_save)
    ranking = SistemaRanking(ranking_path)

    torneio_data["semana"] = semana

    davis = DavisCup(
        tournament_data=torneio_data,
        jogador=jogador,
        ranking=ranking,
        nome_save=nome_save
    )

    # Processa a convocação
    convocado = davis.processar_convocacao()

    if not convocado:
        # Jogador não foi convocado ou recusou - salva moral atualizada
        salvar_jogo(nome_save, jogador)
        return None

    # Atualiza estado com a convocação
    estado = davis._carregar_estado()
    estado["jogador_convocado"] = True

    # Encontra a posição do jogador na convocação
    if davis.selecao:
        for i, c in enumerate(davis.selecao.convocados):
            if c.get("e_jogador_principal"):
                estado["posicao_convocacao"] = i + 1
                break

    davis._salvar_estado(estado)

    print_green(f"\n🏆 Copa Davis iniciada!")
    print(f"📍 {jogador.nacionalidade} está no Grupo {estado['grupo_jogador']}")

    davis.exibir_tabela_grupo()

    safe_input("\nPressione Enter para continuar...")

    return davis


def carregar_davis_cup(nome_save, jogador):
    """Carrega um torneio de Copa Davis existente."""
    estado = carregar_estado_torneio(nome_save)
    if not estado or estado.get("tipo") != "Davis Cup":
        return None

    ranking_path = get_caminho_ranking_save(nome_save)
    ranking = SistemaRanking(ranking_path)

    return DavisCup(
        tournament_data=estado.get("tournament_data", {}),
        jogador=jogador,
        ranking=ranking,
        nome_save=nome_save
    )
