import os
import random

from src.dados import (
    carregar_ranking,
    get_caminho_ranking_global,
    get_caminho_ranking_global_duplas,
    get_caminho_ranking_save,
    get_caminho_ranking_duplas,
    SAVES_DIR,
)
from src.io_utils import safe_input
from src.json_utils import salvar_json_seguro
from src.constantes import (
    DEFAULT_ATRIBUTOS,
    DEFAULT_ATRIBUTOS_PSICOLOGICOS,
    ARCHETYPES,
    MENTAL_ARCHETYPES,
)
from src.player_ratings import calcular_overall_contextual


class Jogador:
    def __init__(
        self,
        nome: str,
        idade: int,
        nacionalidade: str,
        save_name: str = "default",
        genero: str = "masculino",
    ) -> None:
        self.nome: str = nome
        self.idade: int = idade
        self.nacionalidade: str = nacionalidade
        self.save_name: str = save_name
        self.genero: str = genero  # "masculino" or "feminino"

        # Atributos Biográficos (Estilo FIFA)
        self.altura: int = (
            random.randint(175, 195)
            if genero == "masculino"
            else random.randint(165, 185)
        )
        self.peso: int = (
            random.randint(70, 90) if genero == "masculino" else random.randint(55, 75)
        )
        self.mao_dominante: str = random.choice(["Destro", "Canhoto"])
        self.reves: str = random.choice(["Duas mãos", "Uma mão"])
        self.estilo_jogo: str = "All-court"  # Default

        # Atributos de Jogo
        self.semana: int = 1
        self.energia: int = 100
        self.ritmo_jogo: int = 50
        self.moral: int = 70
        self.dinheiro: int = 500
        self.fadiga: int = 0
        self.status_lesao: dict = {
            "lesionado": False,
            "semanas_restantes": 0,
            "nivel": "saudavel",
            "penalidade_atributos": 0.0,
        }
        self.status_doenca: dict = {
            "doente": False,
            "tipo": None,
            "nivel": "saudavel",
            "semanas_restantes": 0,
            "penalidade_atributos": 0.0,
            "penalidade_recuperacao_energia": 0.0,
        }

        # Modalidade e Parceiro
        self.modalidade_atual: str = "simples"  # "simples", "duplas", "ambos"
        self.parceiro_duplas: dict | None = None  # Objeto do parceiro (dict)
        self.vinculos_dupla: dict[str, dict] = (
            {}
        )  # {nome_parceiro: {"partidas": int, "vitorias": int}}

        # Gestão e Equipe
        self.empresario: dict | None = (
            None  # dict {id, semanas_restantes, salario} ou None
        )
        self.equipe: list[dict] = []  # list[dict]: [{id, semanas_restantes, salario}]
        self.patrocinios: list[dict] = []
        self.seguidores: int = 0
        self.avisos_patrocinio: dict[str, bool] = (
            {}
        )  # {pat_id: True} quando patrocinador insatisfeito
        self.reputacao_imprensa: int = 50
        self.caixa_email: list[dict] = []  # propostas e convites pendentes

        # Atributos de Progressão
        self.nivel: int = 1
        self.xp: int = 0
        self.xp_para_proximo_nivel: int = 100
        self.pontos_de_skill: int = 0
        self.pico_carreira: int = random.randint(26, 29)  # Idade do ápice técnico
        self.historico_partidas: list[dict] = []
        self.historico_torneios: list[dict] = []
        self.historico_ranking: list[dict] = (
            []
        )  # list[dict]: [{"semana": int, "ano": int, "posicao": int, "pontos": int}]
        self.rivalidades: dict[str, dict] = {}
        self.pontos_ytd: int = 0
        self.transacoes: list[dict] = []  # Ledger financeiro
        self.snapshots_carreira: list[dict] = []  # Atributos ao longo do tempo

        self.protected_ranking: int | None = None
        self.protected_ranking_semanas: int = 0

        self.atributos = DEFAULT_ATRIBUTOS.copy()
        self.atributos_psicologicos = DEFAULT_ATRIBUTOS_PSICOLOGICOS.copy()
        self._overall_cache = None
        self._sanitizar_atributos()

    def _sanitizar_atributos(self):
        """Garante que todos os atributos estejam dentro dei limites (1-100)."""
        if "duplas" not in self.atributos:
            self.atributos["duplas"] = DEFAULT_ATRIBUTOS.get("duplas", 60)
        for attr in self.atributos:
            self.atributos[attr] = max(1, min(100, self.atributos[attr]))
        for attr in self.atributos_psicologicos:
            self.atributos_psicologicos[attr] = max(
                1, min(100, self.atributos_psicologicos[attr])
            )
        self._overall_cache = None

    def calcular_overall(self) -> int:
        """OVR contextual: atributos técnicos ancorados por ranking/pontos quando disponíveis."""
        if self._overall_cache is None:
            self._overall_cache = calcular_overall_contextual(self.to_dict())
        return self._overall_cache

    def obter_fase_carreira(self) -> str:
        """Determina a fase atual da carreira com base na idade e pico."""
        idade = getattr(self, "idade", 20)
        pico = getattr(self, "pico_carreira", 28)
        dist = pico - idade

        if dist > 3:
            return "Ascensão"
        elif dist > 0:
            return "Pico chegando"
        elif dist == 0:
            return "Auge técnico"
        elif dist >= -4:
            return "Declínio leve"
        else:
            return "Declínio avançado"

    def mostrar_status(self):
        print(f"\n🎾 Jogador: {self.nome} | {self.nacionalidade}")
        print(f"Overall: {self.calcular_overall()}")
        print(f"Idade: {self.idade} | Nível: {self.nivel}")
        print(f"XP: {self.xp} / {self.xp_para_proximo_nivel}")
        print(f"Pontos de Skill: {self.pontos_de_skill}")
        print(f"Energia: {self.energia} | Ritmo de jogo: {self.ritmo_jogo}")
        print(f"Moral: {self.moral} | Dinheiro: ${self.dinheiro}")
        print("Atributos Técnicos:")
        for chave, valor in self.atributos.items():
            print(f"  {chave.capitalize()}: {valor}")
        print("Atributos Psicológicos:")
        for chave, valor in self.atributos_psicologicos.items():
            nome_formatado = chave.replace("_", " ").capitalize()
            print(f"  {nome_formatado}: {valor}")

    def ajustar_energia(self, valor):
        self.energia = max(0, min(100, self.energia + valor))

    def ajustar_ritmo(self, valor):
        self.ritmo_jogo = max(0, min(100, self.ritmo_jogo + valor))

    def registrar_transacao(self, valor, descricao, categoria="torneio"):
        """Registra uma transação financeira no ledger e ajusta o saldo."""
        self.dinheiro += valor
        transacao = {
            "semana": self.semana,
            "valor": valor,
            "descricao": descricao,
            "categoria": categoria,
            "saldo_pos": self.dinheiro,
        }
        self.transacoes.append(transacao)

    def registrar_resultado_dupla(self, nome_parceiro: str, venceu: bool) -> None:
        """Atualiza o vínculo de dupla e evolui o atributo duplas do jogador."""
        v = self.vinculos_dupla.setdefault(
            nome_parceiro, {"partidas": 0, "vitorias": 0}
        )
        v["partidas"] += 1
        if venceu:
            v["vitorias"] += 1

        # Progressão natural: +1 ao atributo duplas a cada 5 partidas jogadas (cap 90)
        total_partidas = sum(x["partidas"] for x in self.vinculos_dupla.values())
        if total_partidas % 5 == 0:
            atual = self.atributos.get("duplas", 60)
            if atual < 90:
                self.atributos["duplas"] = atual + 1
                self._overall_cache = None

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "idade": self.idade,
            "nacionalidade": self.nacionalidade,
            "genero": self.genero,
            "altura": self.altura,
            "peso": self.peso,
            "mao_dominante": self.mao_dominante,
            "reves": self.reves,
            "estilo_jogo": self.estilo_jogo,
            "semana": self.semana,
            "energia": self.energia,
            "ritmo_jogo": self.ritmo_jogo,
            "moral": self.moral,
            "dinheiro": self.dinheiro,
            "modalidade_atual": self.modalidade_atual,
            "parceiro_duplas": self.parceiro_duplas,
            "nivel": self.nivel,
            "xp": self.xp,
            "xp_para_proximo_nivel": self.xp_para_proximo_nivel,
            "pontos_de_skill": self.pontos_de_skill,
            "pico_carreira": self.pico_carreira,
            "historico_partidas": self.historico_partidas,
            "historico_torneios": self.historico_torneios,
            "historico_ranking": self.historico_ranking,
            "rivalidades": self.rivalidades,
            "pontos_ytd": self.pontos_ytd,
            "transacoes": self.transacoes,
            "snapshots_carreira": self.snapshots_carreira,
            "fadiga": self.fadiga,
            "status_lesao": self.status_lesao,
            "status_doenca": self.status_doenca,
            "empresario": self.empresario,
            "equipe": self.equipe,
            "patrocinios": self.patrocinios,
            "seguidores": self.seguidores,
            "avisos_patrocinio": self.avisos_patrocinio,
            "reputacao_imprensa": self.reputacao_imprensa,
            "caixa_email": self.caixa_email,
            "atributos": self.atributos,
            "atributos_psicologicos": self.atributos_psicologicos,
            "protected_ranking": self.protected_ranking,
            "protected_ranking_semanas": self.protected_ranking_semanas,
            "vinculos_dupla": self.vinculos_dupla,
        }

    @classmethod
    def from_dict(cls, data: dict, save_name: str) -> "Jogador":
        """Reconstrói uma instância de Jogador a partir de um dicionário salvo com migrações."""
        from src.migracoes import aplicar_migracoes

        data = aplicar_migracoes(data)

        jogador = cls(
            nome=data["nome"],
            idade=data["idade"],
            nacionalidade=data["nacionalidade"],
            save_name=save_name,
            genero=data.get("genero", "masculino"),
        )

        jogador.altura = data.get("altura", jogador.altura)
        jogador.peso = data.get("peso", jogador.peso)
        jogador.mao_dominante = data.get("mao_dominante", jogador.mao_dominante)
        jogador.reves = data.get("reves", jogador.reves)
        jogador.estilo_jogo = data.get("estilo_jogo", "All-court")

        jogador.semana = data.get("semana", 1)
        jogador.energia = data.get("energia", 100)
        jogador.ritmo_jogo = data.get("ritmo_jogo", 50)
        jogador.moral = data.get("moral", 70)
        jogador.dinheiro = data.get("dinheiro", 500)
        jogador.modalidade_atual = data.get("modalidade_atual", "simples")
        jogador.parceiro_duplas = data.get("parceiro_duplas", None)

        atributos_salvos = data.get("atributos")
        jogador.atributos = (
            atributos_salvos.copy()
            if isinstance(atributos_salvos, dict)
            else DEFAULT_ATRIBUTOS.copy()
        )

        # Progressão
        jogador.nivel = data.get("nivel", 1)
        jogador.xp = data.get("xp", 0)
        jogador.xp_para_proximo_nivel = data.get("xp_para_proximo_nivel", 100)
        jogador.pontos_de_skill = data.get("pontos_de_skill", 0)
        jogador.pico_carreira = data.get("pico_carreira", random.randint(26, 29))
        jogador.historico_partidas = data.get("historico_partidas", [])
        jogador.historico_torneios = data.get("historico_torneios", [])
        jogador.historico_ranking = data.get("historico_ranking", [])
        jogador.rivalidades = data.get("rivalidades", {}) or {}
        jogador.pontos_ytd = data.get("pontos_ytd", 0)
        jogador.transacoes = data.get("transacoes", [])
        jogador.snapshots_carreira = data.get("snapshots_carreira", [])

        # Fadiga e Lesão
        jogador.fadiga = data.get("fadiga", 0)
        jogador.status_lesao = data.get("status_lesao", jogador.status_lesao)
        jogador.status_doenca = data.get("status_doenca", jogador.status_doenca)

        # Gestão
        jogador.empresario = data.get("empresario")
        jogador.equipe = data.get("equipe", [])
        jogador.patrocinios = data.get("patrocinios", [])
        jogador.seguidores = data.get("seguidores", 0)
        jogador.avisos_patrocinio = data.get("avisos_patrocinio") or {}
        jogador.reputacao_imprensa = data.get("reputacao_imprensa", 50)
        jogador.caixa_email = data.get("caixa_email", [])

        # Atributos Psicológicos
        jogador.atributos_psicologicos = data.get(
            "atributos_psicologicos", DEFAULT_ATRIBUTOS_PSICOLOGICOS.copy()
        )

        # Ranking Protegido
        jogador.protected_ranking = data.get("protected_ranking")
        jogador.protected_ranking_semanas = int(
            data.get("protected_ranking_semanas", 0) or 0
        )

        # Vínculos de Dupla
        jogador.vinculos_dupla = data.get("vinculos_dupla", {})

        jogador._sanitizar_atributos()
        return jogador


from src.nome_utils import normalizar_nome


def _rivalidades_ref(jogador):
    if isinstance(jogador, dict):
        rivalidades = jogador.get("rivalidades")
        if not isinstance(rivalidades, dict):
            rivalidades = {}
            jogador["rivalidades"] = rivalidades
        return rivalidades

    rivalidades = getattr(jogador, "rivalidades", None)
    if not isinstance(rivalidades, dict):
        rivalidades = {}
        setattr(jogador, "rivalidades", rivalidades)
    return rivalidades


def atualizar_rivalidade(
    jogador, nome_adversario: str, venceu: bool, semana: int | None = None
):
    nome_norm = normalizar_nome(nome_adversario)
    if not nome_norm:
        return {}

    rivalidades = _rivalidades_ref(jogador)
    rival = rivalidades.setdefault(
        nome_norm,
        {
            "nome": nome_adversario,
            "confrontos": 0,
            "vitorias": 0,
            "ultima_semana": int(semana or 0),
        },
    )
    rival["nome"] = nome_adversario
    rival["confrontos"] = int(rival.get("confrontos", 0) or 0) + 1
    rival["vitorias"] = int(rival.get("vitorias", 0) or 0) + (1 if venceu else 0)
    if semana is not None:
        rival["ultima_semana"] = int(semana)
    return rival


def rival_ativo(jogador, nome_adversario: str) -> bool:
    rival = _rivalidades_ref(jogador).get(normalizar_nome(nome_adversario), {})
    confrontos = int(rival.get("confrontos", 0) or 0)
    if confrontos < 3:
        return False

    vitorias = int(rival.get("vitorias", 0) or 0)
    taxa = vitorias / confrontos if confrontos else 0.5
    return taxa > 0.60 or taxa < 0.40


def obter_bonus_rivalidade(jogador, nome_adversario: str) -> dict:
    rival = _rivalidades_ref(jogador).get(normalizar_nome(nome_adversario), {})
    confrontos = int(rival.get("confrontos", 0) or 0)
    vitorias = int(rival.get("vitorias", 0) or 0)
    derrotas = max(0, confrontos - vitorias)
    ativa = rival_ativo(jogador, nome_adversario)
    return {
        "ativa": ativa,
        "nome": rival.get("nome", nome_adversario),
        "confrontos": confrontos,
        "vitorias": vitorias,
        "derrotas": derrotas,
        "bonus_mental": 5 if ativa else 0,
        "bonus_momentum": 5 if ativa else 0,
        "ultima_semana": int(rival.get("ultima_semana", 0) or 0),
    }


def obter_rival_info(jogador, ranking=None) -> dict | None:
    candidatos = []
    for nome_norm, rival in _rivalidades_ref(jogador).items():
        nome_rival = rival.get("nome", nome_norm)
        bonus = obter_bonus_rivalidade(jogador, nome_rival)
        if not bonus["ativa"]:
            continue
        candidatos.append(bonus)

    if not candidatos:
        return None

    candidatos.sort(
        key=lambda item: (
            -int(item.get("confrontos", 0) or 0),
            -int(item.get("ultima_semana", 0) or 0),
            item.get("nome", ""),
        )
    )
    escolhido = candidatos[0]
    ranking_pos = None
    if ranking and hasattr(ranking, "obter_posicao"):
        try:
            ranking_pos = ranking.obter_posicao(escolhido["nome"], modalidade="simples")
        except TypeError:
            ranking_pos = ranking.obter_posicao(escolhido["nome"])

    return {
        "nome": escolhido["nome"],
        "ranking": ranking_pos or 0,
        "h2h": {
            "v": escolhido["vitorias"],
            "d": escolhido["derrotas"],
        },
    }


def adicionar_jogador_ao_ranking(jogador_instancia):
    ranking_path = get_caminho_ranking_save(
        jogador_instancia.save_name, genero=jogador_instancia.genero
    )
    ranking = carregar_ranking(ranking_path)

    nomes_existentes = [normalizar_nome(j) for j in ranking]

    if normalizar_nome(jogador_instancia) not in nomes_existentes:
        novo = {
            "nome": jogador_instancia.nome,
            "nacionalidade": jogador_instancia.nacionalidade,
            "genero": jogador_instancia.genero,
            "overall": jogador_instancia.calcular_overall(),
            "atributos": jogador_instancia.atributos,
            "atributos_psicologicos": jogador_instancia.atributos_psicologicos,
            "pontos": 0,
            "fadiga": jogador_instancia.fadiga,
            "status_lesao": jogador_instancia.status_lesao,
            "status_doenca": jogador_instancia.status_doenca,
            "pontos_de_skill": jogador_instancia.pontos_de_skill,
        }
        ranking.append(novo)
        salvar_json_seguro(ranking_path, ranking)
        print(f"✅ Jogador '{novo['nome']}' adicionado ao ranking local com 0 pontos.")
    else:
        print(f"ℹ️ Jogador '{jogador_instancia.nome}' já está presente no ranking.")


def carregar_jogador(nome_save: str) -> Jogador:
    """Retorna um objeto Jogador a partir de um save."""
    from src.dados import carregar_jogador as carregar_dados

    return carregar_dados(nome_save)


def _obter_dados_iniciais_jogador():
    """Lida com a coleta de nome, idade, nacionalidade e gênero do jogador."""
    from src.interface.menu_jogador import escolher_nacionalidade_menu

    print("🎾 Criação do Jogador")
    nome = safe_input("Nome: ")
    while True:
        idade_str = safe_input("Idade: ").strip()
        if idade_str.isdigit():
            idade = int(idade_str)
            break
        print("❌ Idade inválida. Digite apenas números inteiros.")

    nacionalidade = escolher_nacionalidade_menu()

    # Seleção de gênero
    genero = _escolher_genero()

    return nome, idade, nacionalidade, genero


def _escolher_genero():
    """Permite ao jogador escolher o gênero do personagem."""
    print("\n👤 Escolha o gênero do jogador:")
    print("1. Masculino (ATP Tour)")
    print("2. Feminino (WTA Tour)")

    while True:
        escolha = safe_input("Escolha (1 ou 2): ").strip()
        if escolha == "1":
            return "masculino"
        elif escolha == "2":
            return "feminino"
        else:
            print("❌ Opção inválida. Escolha 1 ou 2.")


def _obter_archetype():
    """Lida com a escolha do archetipo do jogador e retorna os atributos correspondentes."""
    print("\n📌 Escolha o archetipo de jogador:")
    for key, data in ARCHETYPES.items():
        print(f"{key}. {data['nome']} — {data['descricao']}")

    tipo = safe_input(f"Escolha ({', '.join(ARCHETYPES.keys())}): ").strip()

    if tipo in ARCHETYPES:
        return ARCHETYPES[tipo]["atributos"].copy()

    return ARCHETYPES["3"]["atributos"].copy()


def _obter_mental_archetype():
    """Lida com a escolha do arquetipo mental do jogador."""
    print("\n🧠 Escolha o perfil psicológico do seu jogador:")
    for key, data in MENTAL_ARCHETYPES.items():
        print(f"{key}. {data['nome']} — {data['descricao']}")

    tipo = safe_input(f"Escolha ({', '.join(MENTAL_ARCHETYPES.keys())}): ").strip()

    if tipo in MENTAL_ARCHETYPES:
        return MENTAL_ARCHETYPES[tipo]["atributos"].copy()

    return MENTAL_ARCHETYPES["5"]["atributos"].copy()


def _distribuir_pontos_atributos(atributos_base, pontos_totais):
    atributos = atributos_base.copy()
    pontos_restantes = pontos_totais

    while True:
        print(f"\nPontos restantes: {pontos_restantes}")
        print("Atributos atuais:")
        for i, (atributo, valor) in enumerate(atributos.items(), 1):
            print(f"{i}. {atributo.capitalize()}: {valor}")

        print("\nEscolha uma opção:")
        print("1-9: Alterar um atributo")
        print("c: Confirmar e continuar")

        escolha = safe_input("Opção: ").strip().lower()

        if escolha == "c":
            if pontos_restantes > 0:
                print(
                    f"⚠️ Você ainda tem {pontos_restantes} pontos não distribuídos. Tem certeza que quer continuar?"
                )
                confirmar = safe_input("Confirmar (s/n)? ").strip().lower()
                if confirmar != "s":
                    continue
            break

        if escolha.isdigit() and 1 <= int(escolha) <= len(atributos):
            idx = int(escolha) - 1
            nome_atributo = list(atributos.keys())[idx]
            valor_atual = atributos[nome_atributo]

            print(
                f"\nAlterando '{nome_atributo.capitalize()}' (valor atual: {valor_atual})"
            )
            print("Use '+' para aumentar, '-' para diminuir, ou digite um valor.")
            print("Pressione Enter para voltar.")

            op = safe_input("Operação: ").strip()

            if not op:
                continue

            if op == "+":
                if pontos_restantes > 0:
                    atributos[nome_atributo] += 1
                    pontos_restantes -= 1
                else:
                    print("❌ Pontos insuficientes.")
            elif op == "-":
                if atributos[nome_atributo] > 1:
                    atributos[nome_atributo] -= 1
                    pontos_restantes += 1
                else:
                    print("❌ O valor mínimo para um atributo é 1.")
            elif op.isdigit():
                novo_valor = int(op)
                diferenca = novo_valor - valor_atual
                if pontos_restantes >= diferenca and 1 <= novo_valor <= 100:
                    atributos[nome_atributo] = novo_valor
                    pontos_restantes -= diferenca
                else:
                    print("❌ Pontos insuficientes ou valor inválido (1-100).")
            else:
                print("❌ Operação inválida.")
        else:
            print("❌ Opção inválida.")
    return atributos


def _distribuir_pontos_psicologicos(atributos_base, pontos_totais):
    """Distribui pontos entre os atributos psicologicos a partir de um arquetipo."""
    atributos = atributos_base.copy()
    pontos_restantes = pontos_totais

    descricoes = {
        "concentracao": "Consistência durante a partida - menos erros não forçados",
        "agressividade": "Tendência a arriscar - mais winners, mais erros",
        "leitura_de_jogo": "Antecipação e posicionamento - bônus em rallies longos",
        "determinacao": "Capacidade de virar jogos - bônus quando está perdendo",
    }

    while True:
        print(f"\n📊 Pontos psicológicos restantes: {pontos_restantes}")
        print("Atributos psicológicos atuais:")
        for i, (atributo, valor) in enumerate(atributos.items(), 1):
            nome_formatado = atributo.replace("_", " ").capitalize()
            print(f"{i}. {nome_formatado}: {valor}")
            print(f"   ({descricoes[atributo]})")

        print("\nEscolha uma opção:")
        print("1-4: Alterar um atributo")
        print("c: Confirmar e continuar")

        escolha = safe_input("Opção: ").strip().lower()

        if escolha == "c":
            if pontos_restantes > 0:
                print(
                    f"⚠️ Você ainda tem {pontos_restantes} pontos não distribuídos. Tem certeza que quer continuar?"
                )
                confirmar = safe_input("Confirmar (s/n)? ").strip().lower()
                if confirmar != "s":
                    continue
            break

        if escolha.isdigit() and 1 <= int(escolha) <= len(atributos):
            idx = int(escolha) - 1
            nome_atributo = list(atributos.keys())[idx]
            valor_atual = atributos[nome_atributo]
            nome_formatado = nome_atributo.replace("_", " ").capitalize()

            print(f"\nAlterando '{nome_formatado}' (valor atual: {valor_atual})")
            print("Use '+' para aumentar, '-' para diminuir, ou digite um valor.")
            print("Pressione Enter para voltar.")

            op = safe_input("Operação: ").strip()

            if not op:
                continue

            if op == "+":
                if pontos_restantes > 0:
                    atributos[nome_atributo] += 1
                    pontos_restantes -= 1
                else:
                    print("❌ Pontos insuficientes.")
            elif op == "-":
                if atributos[nome_atributo] > 1:
                    atributos[nome_atributo] -= 1
                    pontos_restantes += 1
                else:
                    print("❌ O valor mínimo para um atributo é 1.")
            elif op.isdigit():
                novo_valor = int(op)
                diferenca = novo_valor - valor_atual
                if pontos_restantes >= diferenca and 1 <= novo_valor <= 100:
                    atributos[nome_atributo] = novo_valor
                    pontos_restantes -= diferenca
                else:
                    print("❌ Pontos insuficientes ou valor inválido (1-100).")
            else:
                print("❌ Operação inválida.")
        else:
            print("❌ Opção inválida.")
    return atributos


def _inicializar_arquivos_save(nome_save, genero="masculino"):
    """Cria a pasta do save e copia ambos os rankings globais se necessário."""
    from src.save import criar_pasta_save
    import json

    criar_pasta_save(nome_save)

    def _ranking_limpo(jogadores):
        limpos = []
        for j in jogadores:
            if not isinstance(j, dict):
                continue
            nome_norm = normalizar_nome(j)
            if (
                j.get("is_bot")
                or j.get("e_ficticio")
                or nome_norm.startswith("bot ")
                or nome_norm.startswith("bot externo")
                or nome_norm == "lowest_rank_bot"
            ):
                continue
            limpos.append(j)
        return limpos

    # Garante que a pasta rankings/ existe antes de escrever os índices
    rankings_dir = os.path.join(SAVES_DIR, nome_save, "rankings")
    os.makedirs(rankings_dir, exist_ok=True)

    # Copia rankings de Simples e Duplas (ATP e WTA) independente do gênero do jogador
    for gen in ("masculino", "feminino"):
        # --- Simples ---
        ranking_origem_s = get_caminho_ranking_global(gen)
        ranking_destino_s = get_caminho_ranking_save(nome_save, gen)
        if not os.path.exists(ranking_destino_s):
            with open(ranking_origem_s, "r", encoding="utf-8") as f:
                ranking = json.load(f)
            ranking = _ranking_limpo(ranking)
            with open(ranking_destino_s, "w", encoding="utf-8") as f:
                json.dump(ranking, f, ensure_ascii=False, indent=2)

        # --- Duplas ---
        ranking_origem_d = get_caminho_ranking_global_duplas(gen)
        ranking_destino_d = get_caminho_ranking_duplas(nome_save, gen)
        if not os.path.exists(ranking_destino_d) and os.path.exists(ranking_origem_d):
            with open(ranking_origem_d, "r", encoding="utf-8") as f:
                ranking_d = json.load(f)
            ranking_d = _ranking_limpo(ranking_d)
            with open(ranking_destino_d, "w", encoding="utf-8") as f:
                json.dump(ranking_d, f, ensure_ascii=False, indent=2)


def criar_jogador(nome_save: str) -> Jogador:
    """Cria uma nova instância de jogador, inicializa os arquivos e salva o jogo."""
    from src.save import salvar_jogo

    nome, idade, nacionalidade, genero = _obter_dados_iniciais_jogador()

    atributos_base = _obter_archetype()

    print("\nAgora, distribua os pontos de atributo do seu jogador.")
    print("Você tem 20 pontos para distribuir entre os atributos técnicos.")
    atributos = _distribuir_pontos_atributos(atributos_base, 20)

    # Escolha do archetipo mental
    mental_base = _obter_mental_archetype()

    print("\n🧠 Agora, refine os pontos psicológicos do seu jogador.")
    print("Você tem 10 pontos extras para distribuir sobre o perfil escolhido.")
    atributos_psicologicos = _distribuir_pontos_psicologicos(mental_base, 10)

    jogador_instancia = Jogador(
        nome, idade, nacionalidade, save_name=nome_save, genero=genero
    )
    jogador_instancia.atributos = atributos
    jogador_instancia.atributos_psicologicos = atributos_psicologicos

    _inicializar_arquivos_save(nome_save, genero=genero)
    salvar_jogo(nome_save, jogador_instancia)
    adicionar_jogador_ao_ranking(jogador_instancia)

    return jogador_instancia


def criar_jogador_alexandre_paiva(nome_save: str) -> Jogador:
    """Cria um novo jogo do zero com o perfil fixo de Alexandre Paiva."""
    from src.save import salvar_jogo

    jogador_instancia = Jogador(
        nome="Alexandre Paiva",
        idade=18,
        nacionalidade="[BR] Brasil",
        save_name=nome_save,
        genero="masculino",
    )
    jogador_instancia.atributos = {
        "saque": 80,
        "forehand": 72,
        "backhand": 80,
        "topspin": 68,
        "voleio": 60,
        "slice": 62,
        "movimento": 78,
        "lob": 65,
        "fisico": 80,
        "winner": 75,
    }
    jogador_instancia.atributos_psicologicos = {
        "concentracao": 75,
        "agressividade": 50,
        "leitura_de_jogo": 60,
        "determinacao": 65,
    }
    _inicializar_arquivos_save(nome_save, genero="masculino")
    salvar_jogo(nome_save, jogador_instancia)
    adicionar_jogador_ao_ranking(jogador_instancia)

    return jogador_instancia


def reidratar_jogador(dados: dict, nome_save: str) -> Jogador:
    """Alias de compatibilidade para Jogador.from_dict."""
    return Jogador.from_dict(dados, nome_save)
