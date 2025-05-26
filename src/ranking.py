import json
import os

class SistemaRanking:
    def __init__(self, caminho_arquivo):
        self.caminho_arquivo = caminho_arquivo
        self.ranking = self.carregar_ranking()

    def carregar_ranking(self):
        if not os.path.exists(self.caminho_arquivo):
            return []
        with open(self.caminho_arquivo, encoding='utf-8') as f:
            return json.load(f)

    def salvar_ranking(self):
        with open(self.caminho_arquivo, "w", encoding='utf-8') as f:
            json.dump(self.ranking, f, indent=2, ensure_ascii=False)

    def ordenar(self):
        self.ranking.sort(key=lambda jogador: jogador["pontos"], reverse=True)

    def atualizar_pontuacao(self, nome, pontos):
        for jogador in self.ranking:
            if jogador["nome"] == nome:
                jogador["pontos"] += pontos
                break
        else:
            self.ranking.append({"nome": nome, "pontos": pontos})
        self.ordenar()
        self.salvar_ranking()

    def obter_posicao(self, nome):
        self.ordenar()
        for idx, jogador in enumerate(self.ranking, 1):
            if jogador["nome"] == nome:
                return idx
        return None

    def top_n(self, n=10):
        self.ordenar()
        return self.ranking[:n]

    def adicionar_jogador_novo(self, jogador_dict):
        """Adiciona um novo jogador ao final do ranking com pontuação zero."""
        self.ordenar()
        jogador_dict["pontos"] = 0
        self.ranking.append(jogador_dict)
        self.salvar_ranking()
