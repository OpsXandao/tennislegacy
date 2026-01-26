import json
import os

from src.dados import carregar_ranking, get_caminho_ranking_global
from src.jogador import normalizar_nome
from src.json_utils import salvar_json_seguro

DEFAULT_ATRIBUTOS = {
    "saque": 60,
    "forehand": 60,
    "backhand": 60,
    "topspin": 60,
    "voleio": 60,
    "slice": 60,
    "movimento": 60,
    "lob": 60,
    "fisico": 60,
    "winner": 60,
}

DEFAULT_ATRIBUTOS_PSICOLOGICOS = {
    "concentracao": 50,
    "agressividade": 50,
    "leitura_de_jogo": 50,
    "determinacao": 50,
}


class SistemaRanking:
    def __init__(self, caminho_arquivo):
        self.caminho_arquivo = caminho_arquivo
        ranking = self.carregar_ranking()
        self.ranking, mudou = self._normalizar_ranking(ranking)
        if mudou:
            self.salvar_ranking()

    def carregar_ranking(self):
        return carregar_ranking(self.caminho_arquivo)

    def _normalizar_ranking(self, ranking):
        if not isinstance(ranking, list):
            return [], True
        
        ranking_sem_duplicados, mudou_remocao = self._remover_duplicados(ranking)

        mudou_norm = False
        normalizado = []
        for jogador in ranking_sem_duplicados:
            jogador_norm, alterado = self._normalizar_jogador(jogador)
            normalizado.append(jogador_norm)
            mudou_norm = mudou_norm or alterado

        return normalizado, mudou_remocao or mudou_norm

    def _normalizar_jogador(self, jogador):
        mudou = False
        if not isinstance(jogador, dict):
            jogador = {"nome": str(jogador)}
            mudou = True

        nome = jogador.get("nome")
        if not isinstance(nome, str) or not nome.strip():
            jogador["nome"] = str(nome) if nome is not None else "Desconhecido"
            mudou = True

        if "nacionalidade" not in jogador:
            jogador["nacionalidade"] = "??"
            mudou = True

        # Normalização da nova estrutura de pontos
        if "pontos_detalhados" not in jogador:
            jogador["pontos_detalhados"] = []
            mudou = True

        if "trofeus" not in jogador:
            jogador["trofeus"] = []
            mudou = True

        pontos = jogador.get("pontos", 0)
        if not isinstance(pontos, int):
            try:
                jogador["pontos"] = int(pontos)
            except (ValueError, TypeError):
                jogador["pontos"] = 0
            mudou = True
        
        # Garante que 'pontos' seja a soma de 'pontos_detalhados' se existir
        soma_detalhada = sum(p.get("pontos", 0) for p in jogador["pontos_detalhados"])
        if jogador["pontos"] != soma_detalhada and soma_detalhada > 0:
             jogador["pontos"] = soma_detalhada
             mudou = True
        elif "pontos" not in jogador:
             jogador["pontos"] = 0
             mudou = True


        atributos = jogador.get("atributos")
        if not isinstance(atributos, dict) or not atributos:
            jogador["atributos"] = DEFAULT_ATRIBUTOS.copy()
            mudou = True
        elif "fisico" not in atributos:
            jogador["atributos"]["fisico"] = DEFAULT_ATRIBUTOS["fisico"]
            mudou = True

        if "overall" not in jogador or mudou:
            atributos = jogador["atributos"]
            jogador["overall"] = round(sum(atributos.values()) / len(atributos))
            mudou = True

        # Normalização de atributos psicológicos
        atributos_psico = jogador.get("atributos_psicologicos")
        if not isinstance(atributos_psico, dict) or not atributos_psico:
            jogador["atributos_psicologicos"] = DEFAULT_ATRIBUTOS_PSICOLOGICOS.copy()
            mudou = True

        return jogador, mudou

    def _remover_duplicados(self, ranking):
        jogadores_unicos = {}
        mudou = False
        for jogador in ranking:
            nome_normalizado = normalizar_nome(jogador)
            if nome_normalizado not in jogadores_unicos:
                jogadores_unicos[nome_normalizado] = jogador
            else:
                mudou = True
                # Logica de merge: manter o jogador com mais pontos, ou o primeiro encontrado
                jogador_existente = jogadores_unicos[nome_normalizado]
                if jogador.get("pontos", 0) > jogador_existente.get("pontos", 0):
                    jogadores_unicos[nome_normalizado] = jogador
        
        return list(jogadores_unicos.values()), mudou

    def salvar_ranking(self):
        salvar_json_seguro(self.caminho_arquivo, self.ranking)

    def ordenar(self):
        for jogador in self.ranking:
            if "pontos" not in jogador:
                jogador["pontos"] = 0
        self.ranking.sort(key=lambda jogador: jogador["pontos"], reverse=True)

    def adicionar_pontos(self, nome, pontos, semana_expiracao):
        """Adiciona um bloco de pontos detalhados a um jogador."""
        nome_normalizado = normalizar_nome(nome)
        jogador_encontrado = None
        for j in self.ranking:
            if normalizar_nome(j) == nome_normalizado:
                jogador_encontrado = j
                break
        
        if not jogador_encontrado:
            # Cria um novo jogador se não for encontrado
            jogador_encontrado, _ = self._normalizar_jogador({"nome": nome})
            self.ranking.append(jogador_encontrado)

        # Adiciona o novo bloco de pontos
        bloco_pontos = {"pontos": pontos, "semana_expiracao": semana_expiracao}
        jogador_encontrado["pontos_detalhados"].append(bloco_pontos)
        
        # Recalcula o total de pontos
        jogador_encontrado["pontos"] = sum(p["pontos"] for p in jogador_encontrado["pontos_detalhados"])

        self.ordenar()
        # O salvamento é feito externamente (ex: no final da distribuição)


    def obter_posicao(self, nome):
        self.ordenar()
        nome_normalizado = normalizar_nome(nome)
        for idx, jogador in enumerate(self.ranking, 1):
            if normalizar_nome(jogador) == nome_normalizado:
                return idx
        return None

    def top_n(self, n=10):
        self.ordenar()
        return self.ranking[:n]

    def adicionar_jogador_novo(self, jogador_dict):
        """Adiciona um novo jogador ao ranking, caso ainda não exista."""
        nome_normalizado = normalizar_nome(jogador_dict)
        if any(normalizar_nome(j) == nome_normalizado for j in self.ranking):
            print(f"ℹ️ Jogador '{jogador_dict['nome']}' já está no ranking.")
            return

        if "pontos" not in jogador_dict:
            jogador_dict["pontos"] = 0

        jogador_normalizado, _ = self._normalizar_jogador(jogador_dict)
        self.ranking.append(jogador_normalizado)
        self.ordenar()
        self.salvar_ranking()
        print(
            f"✅ Jogador '{jogador_dict['nome']}' foi adicionado ao ranking com sucesso."
        )

        self._atualizar_ranking_global(jogador_dict)

    def _atualizar_ranking_global(self, jogador_dict):
        """Garante que o jogador também está no ranking_atp.json global."""
        caminho_global = get_caminho_ranking_global()
        if not os.path.exists(caminho_global):
            print(f"⚠️ Arquivo de ranking global em {caminho_global} não encontrado.")
            return

        dados = carregar_ranking(caminho_global)
        dados, mudou = self._normalizar_ranking(dados)
        if not dados:
            print(
                f"⚠️ O arquivo de ranking global em {caminho_global} está vazio ou corrompido."
            )

        nome_normalizado = normalizar_nome(jogador_dict)
        if any(normalizar_nome(j) == nome_normalizado for j in dados):
            if mudou:
                salvar_json_seguro(caminho_global, dados)
            return

        jogador_completo, _ = self._normalizar_jogador(jogador_dict.copy())

        dados.append(jogador_completo)
        salvar_json_seguro(caminho_global, dados)

        print(
            f"📈 Jogador '{jogador_dict['nome']}' também adicionado ao ranking_atp.json global."
        )

    def buscar_jogador_por_nome(self, nome):
        nome_normalizado = normalizar_nome(nome)
        for jogador in self.ranking:
            if normalizar_nome(jogador) == nome_normalizado:
                return jogador
        return None
    def exibir_ranking(self, start_pos=1, end_pos=None, player_name=None):
        self.ordenar()
        
        if not self.ranking:
            print("\n🚫 Ranking vazio. Nao ha jogadores para exibir.")
            return

        print("\n--- 🌐 RANKING ---")
        
        # Display player's rank if requested
        if player_name:
            player_rank = self.obter_posicao(player_name)
            if player_rank:
                player_info = self.buscar_jogador_por_nome(player_name)
                print(f"⭐ Sua Posicao: #{player_rank} - {player_info['nome']} ({player_info['nacionalidade']}) - {player_info['pontos']} pts")
            else:
                print(f"⭐ {player_name} nao encontrado no ranking atual.")
            print("--------------------")

        # Determine the range to display
        if end_pos is None:
            end_pos = len(self.ranking) # Show all if no end specified
        
        # Ensure valid range
        start_idx = max(0, start_pos - 1)
        end_idx = min(len(self.ranking), end_pos)

        if start_idx >= len(self.ranking):
            print(f"\n🚫 A posicao inicial {start_pos} esta fora do alcance do ranking.")
            return
        if end_idx <= start_idx:
            print(f"\n🚫 Nenhuma posicao para exibir no intervalo {start_pos}-{end_pos}.")
            return

        print(f"\nExibindo posicoes de #{start_pos} a #{end_idx}:")
        for i in range(start_idx, end_idx):
            jogador = self.ranking[i]
            pos = i + 1
            destaque = " (Voce)" if player_name and normalizar_nome(jogador) == normalizar_nome(player_name) else ""
            print(f"#{pos} - {jogador['nome']} ({jogador['nacionalidade']}) - {jogador['pontos']} pts{destaque}")
        print("--------------------")

def get_jogador_by_id(ranking, id_):
    """Retorna o jogador na posição id_ (começando em 1, igual ao ranking tradicional)."""
    try:
        return ranking[id_ - 1]
    except (IndexError, TypeError):
        return None
