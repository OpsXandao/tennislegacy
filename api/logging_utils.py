from __future__ import annotations

import json
import logging
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

_LOGGER_NAME = "tennislegacy"


def setup_logging() -> logging.Logger:
    logger = logging.getLogger(_LOGGER_NAME)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "app.log"

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger


def get_logger() -> logging.Logger:
    return setup_logging()


def log_event(level: int, event: str, **context: Any) -> None:
    logger = get_logger()
    payload = {"event": event, **context}
    logger.log(level, json.dumps(payload, ensure_ascii=True, default=str))


def summarize_detail(detail: Any) -> str:
    if detail is None:
        return "Sem detalhe informado."
    if isinstance(detail, str):
        texto = detail.strip()
        return texto or "Sem detalhe informado."
    if isinstance(detail, dict):
        for chave in ("detail", "message", "erro", "error", "reason", "motivo"):
            valor = detail.get(chave)
            if isinstance(valor, str) and valor.strip():
                return valor.strip()
        try:
            return json.dumps(detail, ensure_ascii=True, default=str)
        except Exception:
            return str(detail)
    if isinstance(detail, (list, tuple, set)):
        itens = [summarize_detail(item) for item in detail]
        return "; ".join(item for item in itens if item) or "Sem detalhe informado."
    return str(detail)


def extract_exception_details(exc: BaseException) -> dict[str, Any]:
    cadeia: list[dict[str, str]] = []
    atual: BaseException | None = exc
    while atual is not None:
        cadeia.append(
            {
                "type": type(atual).__name__,
                "message": summarize_detail(str(atual)),
            }
        )
        proxima = atual.__cause__ or atual.__context__
        if proxima is atual:
            break
        atual = proxima

    raiz = (
        cadeia[-1]
        if cadeia
        else {"type": type(exc).__name__, "message": summarize_detail(str(exc))}
    )
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    return {
        "error_type": type(exc).__name__,
        "error": summarize_detail(str(exc)),
        "root_cause_type": raiz["type"],
        "root_cause": raiz["message"],
        "cause_chain": cadeia,
        "traceback": tb.strip(),
    }


def log_exception(
    event: str, exc: BaseException, level: int = logging.ERROR, **context: Any
) -> None:
    detalhes = extract_exception_details(exc)
    log_event(
        level,
        event,
        reason=detalhes["root_cause"],
        **detalhes,
        **context,
    )
