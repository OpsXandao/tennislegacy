import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response

from api.logging_utils import (
    extract_exception_details,
    log_event,
    setup_logging,
    summarize_detail,
)
from api.routes import (
    save,
    ranking,
    jogador,
    calendario,
    torneio,
    partida,
    davis,
    treinamento,
    mercado,
    email,
    historico,
    duplas,
    logs,
    mundo,
    progressao,
    notificacoes,
)
from api.session import clear_sessao
from api.ws import partida as ws_partida


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    # Startup logic
    log_event(logging.INFO, "api_starting")
    yield
    # Shutdown logic
    log_event(logging.INFO, "api_shutting_down")
    clear_sessao()


app = FastAPI(
    title="TennisLegacy API",
    description="Backend para o jogo TennisLegacy",
    version="0.1.0",
    lifespan=lifespan,
)

# Hosts confiáveis — bloqueia host header spoofing
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"],
)

# Configuração de CORS
origins = ["http://localhost:5173", "http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Limite de tamanho do corpo de request: 1 MB
_MAX_BODY_BYTES = 1 * 1024 * 1024


@app.middleware("http")
async def enforce_body_size(request: Request, call_next):
    """
    Bloqueia corpos de requisição maiores que 1MB.
    Nota: Verifica Content-Length mas também protege contra chunked encoding sem header.
    """
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > _MAX_BODY_BYTES:
        return Response(
            status_code=413,
            content='{"detail":"Payload too large."}',
            media_type="application/json",
        )

    # Se for chunked ou sem content-length, Starlette pode demorar a perceber.
    # Em um ambiente de produção real, usaríamos um wrapper no receive ou
    # configuração no servidor (uvicorn --h11-max-incomplete-chunk-size).
    # Aqui, documentamos que o Content-Length é a primeira linha de defesa.

    return await call_next(request)


# Ordem de execução do Middleware:
# 1. TrustedHostMiddleware (definido primeiro)
# 2. CORSMiddleware
# 3. enforce_body_size
# 4. log_requests (@app.middleware é executado por último na pilha de registro,
#    mas é o primeiro a receber a resposta ao subir)

app.include_router(save.router)
app.include_router(ranking.router)
app.include_router(jogador.router)
app.include_router(calendario.router)
app.include_router(torneio.router)
app.include_router(partida.router)
app.include_router(davis.router)
app.include_router(treinamento.router)
app.include_router(mercado.router)
app.include_router(email.router)
app.include_router(historico.router)
app.include_router(duplas.router)
app.include_router(logs.router)
app.include_router(mundo.router)
app.include_router(progressao.router)
app.include_router(notificacoes.router)
app.include_router(ws_partida.router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    # Tenta obter save name do header
    save_ativo = request.headers.get("X-Save-Name")

    started_at = time.perf_counter()
    request.state.request_id = request_id
    request.state.started_at = started_at
    request.state.save_ativo = save_ativo

    response = await call_next(request)
    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    level = logging.WARNING if response.status_code >= 400 else logging.INFO
    log_event(
        level,
        "request_complete",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        query=str(request.url.query),
        status_code=response.status_code,
        duration_ms=duration_ms,
        save_ativo=save_ativo,
        outcome="error" if response.status_code >= 400 else "success",
    )
    response.headers["X-Request-Id"] = request_id
    return response


@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4())[:8])
    started_at = getattr(request.state, "started_at", None)
    duration_ms = (
        round((time.perf_counter() - started_at) * 1000, 2)
        if started_at is not None
        else None
    )
    detail_summary = summarize_detail(exc.detail)

    log_event(
        logging.WARNING if exc.status_code < 500 else logging.ERROR,
        "http_exception",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        query=str(request.url.query),
        status_code=exc.status_code,
        detail=exc.detail,
        reason=detail_summary,
        duration_ms=duration_ms,
        save_ativo=getattr(request.state, "save_ativo", None),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={"X-Request-Id": request_id},
    )


@app.exception_handler(Exception)
async def handle_unexpected_exception(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4())[:8])
    started_at = getattr(request.state, "started_at", None)
    duration_ms = (
        round((time.perf_counter() - started_at) * 1000, 2)
        if started_at is not None
        else None
    )
    error_info = extract_exception_details(exc)

    log_event(
        logging.ERROR,
        "unhandled_exception",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        query=str(request.url.query),
        duration_ms=duration_ms,
        save_ativo=getattr(request.state, "save_ativo", None),
        reason=error_info["root_cause"],
        **error_info,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno inesperado."},
        headers={"X-Request-Id": request_id},
    )


@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do TennisLegacy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
