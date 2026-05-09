import logging
import os
import random

logger = logging.getLogger(__name__)

from src.dados import (
    carregar_ranking,
    get_caminho_ranking_global,
    get_caminho_ranking_global_duplas,
    get_caminho_ranking_save,
    get_caminho_ranking_duplas,
    SAVES_DIR,
)
from src.utils.json_utils import salvar_json_seguro
from src.constants.constantes import (
    DEFAULT_ATRIBUTOS,
    DEFAULT_ATRIBUTOS_PSICOLOGICOS,
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
        self.lifestyle: list[str] = []  # IDs de itens de luxo/investimentos adquiridos

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
        lines = [
            f"Jogador: {self.nome} | {self.nacionalidade}",
            f"Overall: {self.calcular_overall()}",
            f"Idade: {self.idade} | Nível: {self.nivel}",
            f"XP: {self.xp} / {self.xp_para_proximo_nivel}",
            f"Pontos de Skill: {self.pontos_de_skill}",
            f"Energia: {self.energia} | Ritmo de jogo: {self.ritmo_jogo}",
            f"Moral: {self.moral} | Dinheiro: ${self.dinheiro}",
        ]
        for chave, valor in self.atributos.items():
            lines.append(f"  {chave.capitalize()}: {valor}")
        for chave, valor in self.atributos_psicologicos.items():
            lines.append(f"  {chave.replace('_', ' ').capitalize()}: {valor}")
        logger.debug("\n".join(lines))

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
            "lifestyle": self.lifestyle,
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
        jogador.lifestyle = data.get("lifestyle", [])

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


from src.utils.nome_utils import normalizar_nome


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
        logger.info("jogador_adicionado_ao_ranking", extra={"nome": novo["nome"]})
    else:
        logger.debug("jogador_ja_no_ranking", extra={"nome": jogador_instancia.nome})


def carregar_jogador(nome_save: str) -> Jogador:
    """Retorna um objeto Jogador a partir de um save."""
    from src.dados import carregar_jogador as carregar_dados

    return carregar_dados(nome_save)


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
    salvar_jogo(nome_save, jogador_instancia)
    adicionar_jogador_ao_ranking(jogador_instancia)

    return jogador_instancia


def reidratar_jogador(dados: dict, nome_save: str) -> Jogador:
    """Alias de compatibilidade para Jogador.from_dict."""
    return Jogador.from_dict(dados, nome_save)
