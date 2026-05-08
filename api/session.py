from __future__ import annotations

import threading
import time
from typing import Any, Dict, Optional, Tuple

from fastapi import Header, HTTPException

from src.dados import carregar_jogador
from src.jogador import Jogador
from src.constants.torneio_constants import START_YEAR
from src.ranking import SistemaRanking

_SESSION_TTL_SECONDS = 3600  # 1 hora sem uso → evict
_pool_lock = threading.Lock()


class Session:
    """
    Sessão encapsulada por save.
    O jogador é sempre lido do disco; rankings e runtime ficam em cache.
    """

    def __init__(self, nome_save: str):
        self.nome_save_ativo: str = nome_save
        self._ranking_atp: Optional[SistemaRanking] = None
        self._ranking_wta: Optional[SistemaRanking] = None
        self._ranking_duplas_atp: Optional[SistemaRanking] = None
        self._ranking_duplas_wta: Optional[SistemaRanking] = None
        self._rankings_built = False
        self.partida_id: Optional[str] = None
        self.partida_context: Dict[str, Any] = {}
        self.semana_atual: int = 1
        self.ano_atual: int = START_YEAR
        self.jogador: Optional[Jogador] = None

        # Caches de serialização para performance (Sprint 3)
        self._cache_ranking_atp: Optional[dict] = None
        self._cache_ranking_wta: Optional[dict] = None
        self._cache_ranking_superficies: Dict[str, dict] = {}

        self.refresh()

    def refresh(self) -> None:
        """Recarrega jogador e temporada do disco."""
        from src.dados import carregar_temporada, carregar_jogador

        self.jogador = carregar_jogador(self.nome_save_ativo)
        temp = carregar_temporada(self.nome_save_ativo)
        self.semana_atual = temp.get("semana", 1)
        self.ano_atual = temp.get("ano", START_YEAR)
        # Limpa caches de serialização
        self._cache_ranking_atp = None
        self._cache_ranking_wta = None
        self._cache_ranking_superficies = {}

    @property
    def ranking_atp(self) -> Optional[SistemaRanking]:
        if not self._rankings_built:
            self.rebuild_rankings()
        return self._ranking_atp

    @property
    def ranking_wta(self) -> Optional[SistemaRanking]:
        if not self._rankings_built:
            self.rebuild_rankings()
        return self._ranking_wta

    @property
    def ranking_duplas_atp(self) -> Optional[SistemaRanking]:
        if not self._rankings_built:
            self.rebuild_rankings()
        return self._ranking_duplas_atp

    @property
    def ranking_duplas_wta(self) -> Optional[SistemaRanking]:
        if not self._rankings_built:
            self.rebuild_rankings()
        return self._ranking_duplas_wta

    @property
    def nome_save(self) -> str:
        return self.nome_save_ativo

    def clear_ranking_cache(self) -> None:
        """Reseta os objetos de ranking para forçar recarregamento do disco."""
        self._ranking_atp = None
        self._ranking_wta = None
        self._ranking_duplas_atp = None
        self._ranking_duplas_wta = None
        self._rankings_built = False

    def rebuild_rankings(self) -> None:
        """Instancia e ordena os 4 rankings principais a partir do disco."""
        from src.dados import get_caminho_ranking_duplas, get_caminho_ranking_save

        nome = self.nome_save_ativo
        self._ranking_atp = SistemaRanking(
            get_caminho_ranking_save(nome, genero="masculino"),
            modalidade="simples",
        )
        self._ranking_wta = SistemaRanking(
            get_caminho_ranking_save(nome, genero="feminino"),
            modalidade="simples",
        )
        self._ranking_duplas_atp = SistemaRanking(
            get_caminho_ranking_duplas(nome, genero="masculino"),
            modalidade="duplas",
        )
        self._ranking_duplas_wta = SistemaRanking(
            get_caminho_ranking_duplas(nome, genero="feminino"),
            modalidade="duplas",
        )
        self._ranking_atp.ordenar()
        self._ranking_wta.ordenar()
        self._ranking_duplas_atp.ordenar()
        self._ranking_duplas_wta.ordenar()
        self._rankings_built = True


# (nome_save → (Session, last_access_ts))
_sessions_pool: Dict[str, Tuple[Session, float]] = {}
_MAX_POOL_SIZE = 10  # jogo single-player: >10 saves simultâneos indica vazamento


def _evict_expired() -> None:
    """Remove sessões não acessadas há mais de _SESSION_TTL_SECONDS."""
    agora = time.monotonic()
    expirados = [
        k for k, (_, ts) in _sessions_pool.items() if agora - ts > _SESSION_TTL_SECONDS
    ]
    for k in expirados:
        _sessions_pool.pop(k, None)


def obter_sessao_ativa(
    x_save_name: str = Header(..., alias="X-Save-Name"),
) -> Session:
    """
    Retorna a sessão associada ao header X-Save-Name.
    Usa um lock para garantir que requisições paralelas não criem sessões duplicadas.
    """
    from src.dados import validar_nome_save

    try:
        x_save_name = validar_nome_save(x_save_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    with _pool_lock:
        _evict_expired()

        entrada = _sessions_pool.get(x_save_name)
        if entrada is None:
            if len(_sessions_pool) >= _MAX_POOL_SIZE:
                # Evict a sessão mais antiga para evitar crescimento ilimitado
                mais_antiga = min(_sessions_pool, key=lambda k: _sessions_pool[k][1])
                _sessions_pool.pop(mais_antiga, None)
            sessao = Session(x_save_name)
        else:
            sessao = entrada[0]

        _sessions_pool[x_save_name] = (sessao, time.monotonic())
        return sessao


def obter_nome_save_opcional(
    x_save_name: Optional[str] = Header(None, alias="X-Save-Name"),
) -> Optional[str]:
    return x_save_name


def get_session() -> Session:
    """
    Retorna a sessão que foi acessada mais recentemente.
    Útil para fluxos onde o header X-Save-Name não está disponível ou injetado.
    """
    with _pool_lock:
        if _sessions_pool:
            nome = max(_sessions_pool, key=lambda k: _sessions_pool[k][1])
            return _sessions_pool[nome][0]
    raise HTTPException(status_code=400, detail="Nenhuma sessão ativa no pool.")


def get_save_ativo() -> Optional[str]:
    with _pool_lock:
        if not _sessions_pool:
            return None
        return max(_sessions_pool, key=lambda k: _sessions_pool[k][1])


def refresh_session(nome_save: str) -> None:
    """Recarrega jogador e temporada do disco após qualquer ação que avance semana."""
    with _pool_lock:
        entrada = _sessions_pool.get(nome_save)
        if not entrada:
            return
        sess = entrada[0]
        sess.refresh()
        # Usa método de encapsulamento para limpar rankings
        sess.clear_ranking_cache()
        # Atualiza timestamp de acesso
        _sessions_pool[nome_save] = (sess, time.monotonic())


def clear_sessao(nome_save: Optional[str] = None) -> None:
    with _pool_lock:
        if nome_save:
            _sessions_pool.pop(nome_save, None)
            return

        _sessions_pool.clear()
