import json
import os
from jogador import normalizar_nome


class SistemaRanking:
    def __init__(self, caminho_arquivo):
        self.caminho_arquivo = caminho_arquivo
        self.ranking = self.carregar_ranking()

    def carregar_ranking(self):
        if not os.path.exists(self.caminho_arquivo):
            return []
        with open(self.caminho_arquivo, encoding="utf-8") as f:
            return json.load(f)

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
            self.ranking.append({"nome": nome, "pontos": pontos})
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

        self.ranking.append(jogador_dict)
        self.ordenar()
        self.salvar_ranking()
        print(
            f"✅ Jogador '{jogador_dict['nome']}' foi adicionado ao ranking com sucesso."
        )

        self._atualizar_ranking_global(jogador_dict)

    def _atualizar_ranking_global(self, jogador_dict):
        """Garante que o jogador também está no ranking_atp.json global."""
        caminho_global = os.path.join("db", "ranking_atp.json")
        if not os.path.exists(caminho_global):
            print("⚠️ Arquivo ranking_atp.json não encontrado.")
            return

        with open(caminho_global, encoding="utf-8") as f:
            dados = json.load(f)

        nome_normalizado = normalizar_nome(jogador_dict)
        if any(normalizar_nome(j) == nome_normalizado for j in dados):
            return

        jogador_completo = jogador_dict.copy()
        if "atributos" not in jogador_completo:
            jogador_completo["atributos"] = {
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


def carregar_ranking(caminho_arquivo):
    """Função utilitária para carregar ranking a partir de um arquivo JSON."""
    if not os.path.exists(caminho_arquivo):
        return []
    with open(caminho_arquivo, encoding="utf-8") as f:
        return json.load(f)


def get_jogador_by_id(ranking, id_):
    """Retorna o jogador na posição id_ (começando em 1, igual ao ranking tradicional)."""
    try:
        return ranking[id_ - 1]
    except (IndexError, TypeError):
        return None
