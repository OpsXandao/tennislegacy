import json
import os

from src.dados import carregar_ranking, get_caminho_ranking_global
from src.jogador import normalizar_nome

DEFAULT_ATRIBUTOS = {
    "saque": 60,
    "forehand": 60,
    "backhand": 60,
    "topspin": 60,
    "voleio": 60,
    "slice": 60,
    "movimento": 60,
    "lob": 60,
    "winner": 60,
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
        mudou = False
        normalizado = []
        for jogador in ranking:
            jogador_norm, alterado = self._normalizar_jogador(jogador)
            normalizado.append(jogador_norm)
            mudou = mudou or alterado
        return normalizado, mudou

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

        pontos = jogador.get("pontos", 0)
        if not isinstance(pontos, int):
            jogador["pontos"] = int(pontos) if pontos else 0
            mudou = True
        elif "pontos" not in jogador:
            jogador["pontos"] = 0
            mudou = True

        atributos = jogador.get("atributos")
        if not isinstance(atributos, dict) or not atributos:
            jogador["atributos"] = DEFAULT_ATRIBUTOS.copy()
            mudou = True

        if "overall" not in jogador:
            atributos = jogador["atributos"]
            jogador["overall"] = round(sum(atributos.values()) / len(atributos))
            mudou = True

        return jogador, mudou

    def salvar_ranking(self):
        with open(self.caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(self.ranking, f, indent=2, ensure_ascii=False)

    def ordenar(self):
        for jogador in self.ranking:
            if "pontos" not in jogador:
                jogador["pontos"] = 0
        self.ranking.sort(key=lambda jogador: jogador["pontos"], reverse=True)

    def atualizar_pontuacao(self, nome, pontos):
        nome_normalizado = normalizar_nome(nome)
        for jogador in self.ranking:
            if normalizar_nome(jogador) == nome_normalizado:
                jogador["pontos"] += pontos
                break
        else:
            jogador_novo, _ = self._normalizar_jogador({"nome": nome, "pontos": pontos})
            self.ranking.append(jogador_novo)
        self.ordenar()
        self.salvar_ranking()

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
                with open(caminho_global, "w", encoding="utf-8") as f:
                    json.dump(dados, f, indent=2, ensure_ascii=False)
            return

        jogador_completo, _ = self._normalizar_jogador(jogador_dict.copy())

        dados.append(jogador_completo)
        with open(caminho_global, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

        print(
            f"📈 Jogador '{jogador_dict['nome']}' também adicionado ao ranking_atp.json global."
        )

    def buscar_jogador_por_nome(self, nome):
        nome_normalizado = normalizar_nome(nome)
        for jogador in self.ranking:
            if normalizar_nome(jogador) == nome_normalizado:
                return jogador
        return None
def get_jogador_by_id(ranking, id_):
    """Retorna o jogador na posição id_ (começando em 1, igual ao ranking tradicional)."""
    try:
        return ranking[id_ - 1]
    except (IndexError, TypeError):
        return None
