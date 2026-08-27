from __future__ import annotations
from typing import Any

from src.services.match_runtime_core import MatchRuntime, criar_match_runtime, obter_match_runtime
from src.utils.match_doubles_utils import (
    buscar_jogador_por_nome_ranking as _buscar_jogador_por_nome_ranking,
    compor_dupla_efetiva as _compor_dupla_efetiva,
    resolver_integrante_dupla as _resolver_integrante_dupla,
)
from src.utils.match_runtime_utils import atualizar_historico_torneios as _atualizar_historico_torneios

# Re-exportando para manter compatibilidade com rotas que importam daqui.
__all__ = [
    "MatchRuntime",
    "criar_match_runtime",
    "obter_match_runtime",
    "_buscar_jogador_por_nome_ranking",
    "_resolver_integrante_dupla",
    "_compor_dupla_efetiva",
    "_atualizar_historico_torneios",
]
