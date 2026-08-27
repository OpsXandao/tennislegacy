from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, Tuple

from src.dados import SAVES_DIR, carregar_json
from src.utils.json_utils import salvar_json_seguro

# Cache global de runtimes de partida ativos (independente de sessão)
# Estrutura: partida_id → (runtime, last_access_ts)
_global_matches_cache: Dict[str, Tuple[Any, float]] = {}
_MATCH_TTL_SECONDS = 7200  # 2 horas sem acesso → evict
_MAX_CACHED_MATCHES = 20


def _evict_expired_matches() -> None:
    agora = time.monotonic()
    expirados = [
        k
        for k, (_, ts) in _global_matches_cache.items()
        if agora - ts > _MATCH_TTL_SECONDS
    ]
    for k in expirados:
        _global_matches_cache.pop(k, None)


def snapshot_path(save_name: str, partida_id: str) -> Path:
    return (
        Path(SAVES_DIR) / save_name / "api_runtime" / "matches" / f"{partida_id}.json"
    )


def save_snapshot(save_name: str, partida_id: str, payload: dict[str, Any]) -> None:
    salvar_json_seguro(str(snapshot_path(save_name, partida_id)), payload)


def load_snapshot(save_name: str, partida_id: str) -> dict[str, Any] | None:
    return carregar_json(str(snapshot_path(save_name, partida_id)), padrao=None)


def get_runtime_cache(partida_id: str) -> Any | None:
    entrada = _global_matches_cache.get(partida_id)
    if entrada is None:
        return None
    runtime, _ = entrada
    _global_matches_cache[partida_id] = (runtime, time.monotonic())
    return runtime


def set_runtime_cache(partida_id: str, runtime: Any) -> None:
    _evict_expired_matches()
    if len(_global_matches_cache) >= _MAX_CACHED_MATCHES:
        mais_antigo = min(
            _global_matches_cache, key=lambda k: _global_matches_cache[k][1]
        )
        _global_matches_cache.pop(mais_antigo, None)
    _global_matches_cache[partida_id] = (runtime, time.monotonic())


def clear_runtime_cache(partida_id: str) -> None:
    _global_matches_cache.pop(partida_id, None)


def delete_snapshot(save_name: str, partida_id: str) -> bool:
    """Remove o arquivo físico do snapshot da partida."""
    path = snapshot_path(save_name, partida_id)
    try:
        if path.exists():
            path.unlink()
            clear_runtime_cache(partida_id)
            return True
    except Exception:
        pass
    return False


def invalidate_other_snapshots(save_name: str, keep_partida_id: str) -> None:
    matches_dir = snapshot_path(save_name, keep_partida_id).parent
    if not matches_dir.exists():
        return

    for snap in matches_dir.glob("*.json"):
        if snap.stem == keep_partida_id:
            continue
        
        try:
            payload = carregar_json(str(snap), padrao=None)
            if not isinstance(payload, dict) or payload.get("encerrado"):
                # Se já estava encerrado ou corrompido, deleta de vez
                snap.unlink()
                clear_runtime_cache(snap.stem)
                continue
            
            # Se estava aberto, invalida (marca como encerrado) ou deleta
            # Para polimento extremo: deleta logo, já que um novo começou
            snap.unlink()
            clear_runtime_cache(snap.stem)
        except Exception:
            pass
