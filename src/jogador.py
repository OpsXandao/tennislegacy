import json
import os

from src.dados import (
    carregar_ranking,
    get_caminho_jogador_save,
    get_caminho_ranking_global,
    get_caminho_ranking_save,
)
from src.io_utils import safe_input


DEFAULT_ATRIBUTOS_PSICOLOGICOS = {
    "concentracao": 50,
    "agressividade": 50,
    "leitura_de_jogo": 50,
    "determinacao": 50,
}


class Jogador:
    def __init__(self, nome, idade, nacionalidade, save_name="default", genero="masculino"):
        self.nome = nome
        self.idade = idade
        self.nacionalidade = nacionalidade
        self.save_name = save_name
        self.genero = genero  # "masculino" ou "feminino"

        # Atributos de Jogo
        self.semana = 1
        self.energia = 100
        self.ritmo_jogo = 50
        self.moral = 70
        self.dinheiro = 500
        self.fadiga = 0
        self.status_lesao = {"lesionado": False, "semanas_restantes": 0}

        # Atributos de Progressão
        self.nivel = 1
        self.xp = 0
        self.xp_para_proximo_nivel = 100
        self.pontos_de_skill = 0
        
        self.atributos = {
            "saque": 50,
            "forehand": 50,
            "backhand": 50,
            "topspin": 50,
            "voleio": 50,
            "slice": 50,
            "movimento": 50,
            "lob": 50,
            "fisico": 50,
            "winner": 50,
        }
        self.atributos_psicologicos = DEFAULT_ATRIBUTOS_PSICOLOGICOS.copy()

    def calcular_overall(self):
        return round(sum(self.atributos.values()) / len(self.atributos))

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

    def to_dict(self):
        return {
            "nome": self.nome,
            "idade": self.idade,
            "nacionalidade": self.nacionalidade,
            "genero": self.genero,
            "semana": self.semana,
            "energia": self.energia,
            "ritmo_jogo": self.ritmo_jogo,
            "moral": self.moral,
            "dinheiro": self.dinheiro,
            "nivel": self.nivel,
            "xp": self.xp,
            "xp_para_proximo_nivel": self.xp_para_proximo_nivel,
            "pontos_de_skill": self.pontos_de_skill,
            "fadiga": self.fadiga,
            "status_lesao": self.status_lesao,
            "atributos": self.atributos,
            "atributos_psicologicos": self.atributos_psicologicos,
        }



def obter_nome(obj):
    """Retorna o nome normalizado de um jogador, seja ele um str, dict ou objeto."""
    if isinstance(obj, dict):
        return obj.get("nome", "").strip()
    elif hasattr(obj, "nome"):
        return getattr(obj, "nome", "").strip()
    return str(obj).strip()


def normalizar_nome(obj):
    """Retorna o nome do jogador em lowercase e sem espaços extras, seja dict, objeto ou string."""
    nome = obter_nome(obj)
    return nome.lower()



def adicionar_jogador_ao_ranking(jogador_instancia):
    ranking_path = get_caminho_ranking_save(jogador_instancia.save_name)
    ranking = carregar_ranking(ranking_path)

    nomes_existentes = [normalizar_nome(j) for j in ranking]

    if normalizar_nome(jogador_instancia) not in nomes_existentes:
        novo = {
            "nome": jogador_instancia.nome,
            "nacionalidade": jogador_instancia.nacionalidade,
            "genero": jogador_instancia.genero,
            "overall": jogador_instancia.calcular_overall(),
            "atributos": jogador_instancia.atributos,
            "pontos": 0,
        }
        ranking.append(novo)
        with open(ranking_path, "w", encoding="utf-8") as f:
            json.dump(ranking, f, indent=2, ensure_ascii=False)
        print(f"✅ Jogador '{novo['nome']}' adicionado ao ranking local com 0 pontos.")
    else:
        print(f"ℹ️ Jogador '{jogador_instancia.nome}' já está presente no ranking.")


def carregar_jogador(nome_save):
    caminho = get_caminho_jogador_save(nome_save)
    if not os.path.exists(caminho):
        print("❌ Save não encontrado.")
        raise SystemExit(1)

    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)

    return reidratar_jogador(dados, nome_save)


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
    print("2. Feminino (WTA Tour) - Em breve")

    while True:
        escolha = safe_input("Escolha (1 ou 2): ").strip()
        if escolha == "1":
            return "masculino"
        elif escolha == "2":
            print("⚠️ O modo feminino (WTA Tour) ainda está em desenvolvimento.")
            print("   Por enquanto, apenas o modo masculino está disponível.")
            confirmar = safe_input("Deseja continuar com o modo masculino? (s/n): ").strip().lower()
            if confirmar == "s":
                return "masculino"
            # Se não confirmar, volta para o menu de escolha
        else:
            print("❌ Opção inválida. Escolha 1 ou 2.")


def _obter_archetype():
    """Lida com a escolha do archetipo do jogador e retorna os atributos correspondentes."""
    print("\n📌 Escolha o archetipo de jogador:")
    print("1. Técnico — mais controle e precisão")
    print("2. Físico — mais força e movimentação")
    print("3. Equilibrado — tudo balanceado")
    tipo = safe_input("Escolha (1, 2 ou 3): ").strip()

    atributos_por_archetype = {
        "1": {"saque": 60, "forehand": 75, "backhand": 75, "topspin": 72, "voleio": 65, "slice": 72, "movimento": 68, "lob": 74, "fisico": 60, "winner": 65},
        "2": {"saque": 75, "forehand": 72, "backhand": 70, "topspin": 68, "voleio": 60, "slice": 62, "movimento": 78, "lob": 60, "fisico": 80, "winner": 75},
        "3": {"saque": 70, "forehand": 70, "backhand": 70, "topspin": 70, "voleio": 70, "slice": 70, "movimento": 70, "lob": 70, "fisico": 70, "winner": 70},
    }
    return atributos_por_archetype.get(tipo, atributos_por_archetype["3"])


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

        if escolha == 'c':
            if pontos_restantes > 0:
                print(f"⚠️ Você ainda tem {pontos_restantes} pontos não distribuídos. Tem certeza que quer continuar?")
                confirmar = safe_input("Confirmar (s/n)? ").strip().lower()
                if confirmar != 's':
                    continue
            break

        if escolha.isdigit() and 1 <= int(escolha) <= len(atributos):
            idx = int(escolha) - 1
            nome_atributo = list(atributos.keys())[idx]
            valor_atual = atributos[nome_atributo]

            print(f"\nAlterando '{nome_atributo.capitalize()}' (valor atual: {valor_atual})")
            print("Use '+' para aumentar, '-' para diminuir, ou digite um valor.")
            print("Pressione Enter para voltar.")

            op = safe_input("Operação: ").strip()

            if not op:
                continue

            if op == '+':
                if pontos_restantes > 0:
                    atributos[nome_atributo] += 1
                    pontos_restantes -= 1
                else:
                    print("❌ Pontos insuficientes.")
            elif op == '-':
                if atributos[nome_atributo] > 1:
                    atributos[nome_atributo] -= 1
                    pontos_restantes += 1
                else:
                    print("❌ O valor mínimo para um atributo é 1.")
            elif op.isdigit():
                novo_valor = int(op)
                diferenca = novo_valor - valor_atual
                if pontos_restantes >= diferenca and novo_valor >= 1:
                    atributos[nome_atributo] = novo_valor
                    pontos_restantes -= diferenca
                else:
                    print("❌ Pontos insuficientes ou valor inválido.")
            else:
                print("❌ Operação inválida.")
        else:
            print("❌ Opção inválida.")
    return atributos


def _distribuir_pontos_psicologicos(pontos_totais):
    """Distribui pontos entre os atributos psicológicos."""
    atributos = DEFAULT_ATRIBUTOS_PSICOLOGICOS.copy()
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

        if escolha == 'c':
            if pontos_restantes > 0:
                print(f"⚠️ Você ainda tem {pontos_restantes} pontos não distribuídos. Tem certeza que quer continuar?")
                confirmar = safe_input("Confirmar (s/n)? ").strip().lower()
                if confirmar != 's':
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

            if op == '+':
                if pontos_restantes > 0:
                    atributos[nome_atributo] += 1
                    pontos_restantes -= 1
                else:
                    print("❌ Pontos insuficientes.")
            elif op == '-':
                if atributos[nome_atributo] > 1:
                    atributos[nome_atributo] -= 1
                    pontos_restantes += 1
                else:
                    print("❌ O valor mínimo para um atributo é 1.")
            elif op.isdigit():
                novo_valor = int(op)
                diferenca = novo_valor - valor_atual
                if pontos_restantes >= diferenca and novo_valor >= 1:
                    atributos[nome_atributo] = novo_valor
                    pontos_restantes -= diferenca
                else:
                    print("❌ Pontos insuficientes ou valor inválido.")
            else:
                print("❌ Operação inválida.")
        else:
            print("❌ Opção inválida.")
    return atributos


def _inicializar_arquivos_save(nome_save):
    """Cria a pasta do save e copia o ranking global se necessário."""
    from src.save import criar_pasta_save
    from shutil import copyfile

    criar_pasta_save(nome_save)

    ranking_origem = get_caminho_ranking_global()
    ranking_destino = get_caminho_ranking_save(nome_save)
    if not os.path.exists(ranking_destino):
        copyfile(ranking_origem, ranking_destino)


def criar_jogador(nome_save):
    """Cria uma nova instância de jogador, inicializa os arquivos e salva o jogo."""
    import builtins
    from src.save import salvar_jogo

    nome, idade, nacionalidade, genero = _obter_dados_iniciais_jogador()

    atributos_base = _obter_archetype()

    print("\nAgora, distribua os pontos de atributo do seu jogador.")
    print("Você tem 20 pontos para distribuir entre os atributos técnicos.")
    atributos = _distribuir_pontos_atributos(atributos_base, 20)

    print("\n🧠 Agora, distribua os pontos psicológicos do seu jogador.")
    print("Você tem 15 pontos para distribuir entre os atributos psicológicos.")
    atributos_psicologicos = _distribuir_pontos_psicologicos(15)

    jogador_instancia = Jogador(nome, idade, nacionalidade, save_name=nome_save, genero=genero)
    jogador_instancia.atributos = atributos
    jogador_instancia.atributos_psicologicos = atributos_psicologicos
    builtins.jogador = jogador_instancia

    _inicializar_arquivos_save(nome_save)
    salvar_jogo(nome_save, jogador_instancia)
    adicionar_jogador_ao_ranking(jogador_instancia)

    return jogador_instancia

def reidratar_jogador(dados, nome_save):
    jogador = Jogador(
        nome=dados["nome"],
        idade=dados["idade"],
        nacionalidade=dados["nacionalidade"],
        save_name=nome_save,
        genero=dados.get("genero", "masculino"),  # Compatibilidade com saves antigos
    )
    # Mantem compatibilidade com saves antigos
    jogador.semana = dados.get("semana", 1)
    jogador.energia = dados.get("energia", 100)
    jogador.ritmo_jogo = dados.get("ritmo_jogo", 50)
    jogador.moral = dados.get("moral", 70)
    jogador.dinheiro = dados.get("dinheiro", 500)
    jogador.atributos = dados["atributos"]
    if "fisico" not in jogador.atributos:
        jogador.atributos["fisico"] = 50
    
    # Progressão
    jogador.nivel = dados.get("nivel", 1)
    jogador.xp = dados.get("xp", 0)
    jogador.xp_para_proximo_nivel = dados.get("xp_para_proximo_nivel", 100)
    jogador.pontos_de_skill = dados.get("pontos_de_skill", 0)

    # Fadiga e Lesão
    jogador.fadiga = dados.get("fadiga", 0)
    jogador.status_lesao = dados.get("status_lesao", {"lesionado": False, "semanas_restantes": 0})

    # Migração automática para saves antigos sem atributos psicológicos
    jogador.atributos_psicologicos = dados.get(
        "atributos_psicologicos", DEFAULT_ATRIBUTOS_PSICOLOGICOS.copy()
    )
    return jogador
