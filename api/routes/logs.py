from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from api.logging_utils import log_event
from api.session import obter_nome_save_opcional

router = APIRouter(prefix="/api/logs", tags=["logs"])

# Rate limiter simples em memória: máx 20 logs por IP por 60 segundos
_log_rate: dict[str, list[float]] = defaultdict(list)
_RATE_WINDOW = 60.0
_RATE_MAX = 20


def _check_rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    agora = time.monotonic()
    _log_rate[ip] = [t for t in _log_rate[ip] if agora - t < _RATE_WINDOW]
    if len(_log_rate[ip]) >= _RATE_MAX:
        raise HTTPException(
            status_code=429, detail="Taxa de logs excedida. Tente em breve."
        )
    _log_rate[ip].append(agora)


class FrontendLogPayload(BaseModel):
    kind: str = Field(..., max_length=64)
    message: str = Field(..., max_length=2048)
    stack: str | None = Field(None, max_length=4096)
    url: str | None = Field(None, max_length=512)
    user_agent: str | None = Field(None, max_length=256)
    component_stack: str | None = Field(None, max_length=4096)
    extra: dict[str, Any] | None = None


@router.post("/frontend")
def ingest_frontend_log(
    payload: FrontendLogPayload,
    request: Request,
    save_ativo: str | None = Depends(obter_nome_save_opcional),
) -> dict[str, bool]:
    _check_rate_limit(request)
    log_event(
        logging.ERROR,
        "frontend_error",
        save_ativo=save_ativo,
        kind=payload.kind,
        message=payload.message,
        stack=payload.stack,
        component_stack=payload.component_stack,
        url=payload.url,
        user_agent=payload.user_agent,
        extra=payload.extra or {},
    )
    return {"ok": True}
