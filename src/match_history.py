import os
import json
import uuid
from src.utils.json_utils import salvar_json_seguro
from src.dados import SAVES_DIR


class MatchHistoryManager:
    def __init__(self, nome_save):
        self.nome_save = nome_save
        self.caminho_arquivo = os.path.join(
            SAVES_DIR, nome_save, "historico_partidas.json"
        )
        self.historico = self._carregar_historico()

    def _carregar_historico(self):
        if not os.path.exists(self.caminho_arquivo):
            return []
        try:
            with open(self.caminho_arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def adicionar_partida(
        self, torneio, semana, ano, modalidade, jogadores, resultado, vencedor, fase
    ):
        """
        Adiciona uma partida ao histórico otimizado.
        jogadores: list de nomes
        vencedor: nome ou list de nomes
        """
        entry = {
            "id": str(uuid.uuid4())[:8],
            "torneio": torneio,
            "semana": semana,
            "ano": ano,
            "modalidade": modalidade,
            "jogadores": jogadores,
            "resultado": resultado,
            "vencedor": vencedor,
            "fase": fase,
        }
        self.historico.append(entry)
        # Mantém apenas as últimas 500 partidas para otimização extrema,
        # ou remova este limite se preferir histórico completo.
        if len(self.historico) > 1000:
            self.historico = self.historico[-1000:]

        self.salvar()

    def salvar(self):
        salvar_json_seguro(self.caminho_arquivo, self.historico)

    def buscar_por_jogador(self, nome_jogador):
        from src.utils.nome_utils import normalizar_nome

        nome_norm = normalizar_nome(nome_jogador)
        return [
            p
            for p in self.historico
            if any(normalizar_nome(j) == nome_norm for j in p["jogadores"])
        ]

    def resumir_confronto(self, nome_jogador: str, nome_adversario: str) -> dict:
        from src.utils.nome_utils import normalizar_nome

        jogador_norm = normalizar_nome(nome_jogador)
        adversario_norm = normalizar_nome(nome_adversario)
        confrontos = [
            partida
            for partida in self.historico
            if any(
                normalizar_nome(nome) == jogador_norm
                for nome in partida.get("jogadores", [])
            )
            and any(
                normalizar_nome(nome) == adversario_norm
                for nome in partida.get("jogadores", [])
            )
        ]
        vitorias = 0
        derrotas = 0
        for partida in confrontos:
            vencedor = partida.get("vencedor")
            if isinstance(vencedor, list):
                venceu = any(normalizar_nome(nome) == jogador_norm for nome in vencedor)
            else:
                venceu = normalizar_nome(str(vencedor or "")) == jogador_norm
            if venceu:
                vitorias += 1
            else:
                derrotas += 1

        ultima_semana = 0
        if confrontos:
            ultimo = max(
                confrontos,
                key=lambda partida: (
                    int(partida.get("ano", 0) or 0),
                    int(partida.get("semana", 0) or 0),
                ),
            )
            ultima_semana = int(ultimo.get("semana", 0) or 0)

        return {
            "confrontos": len(confrontos),
            "vitorias": vitorias,
            "derrotas": derrotas,
            "ultima_semana": ultima_semana,
        }
