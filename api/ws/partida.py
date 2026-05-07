from __future__ import annotations

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.routes._match_runtime import obter_match_runtime

router = APIRouter()


async def _stream_runtime(
    websocket: WebSocket, partida_id: str, play_event: asyncio.Event
) -> None:
    runtime = obter_match_runtime(partida_id)
    while True:
        # Aguarda passivamente até que o jogo não esteja pausado (0% CPU)
        await play_event.wait()

        if runtime.encerrado:
            await websocket.send_json(
                runtime.serializar(event_type="fim", descricao="Partida encerrada.")
            )
            break

        await websocket.send_json(runtime.jogar_ponto())
        await asyncio.sleep(0.3)


@router.websocket("/ws/partida/{partida_id}")
async def partida_ws(websocket: WebSocket, partida_id: str) -> None:
    await websocket.accept()
    runtime = obter_match_runtime(partida_id)
    await websocket.send_json(
        runtime.serializar(event_type="ponto", descricao="Conexao iniciada.")
    )

    # Evento de controle de fluxo (inicia tocando se não estiver pausado no runtime)
    play_event = asyncio.Event()
    if not runtime.pausado:
        play_event.set()

    streamer = asyncio.create_task(_stream_runtime(websocket, partida_id, play_event))

    try:
        while True:
            payload = await websocket.receive_json()
            acao = str(payload.get("acao", "")).strip().lower()
            if acao == "pausar":
                runtime.definir_pausa(True)
                play_event.clear()
            elif acao == "continuar":
                runtime.definir_pausa(False)
                play_event.set()
            elif acao == "estrategia":
                runtime.aplicar_estrategia(payload.get("valor"))
    except WebSocketDisconnect:
        pass
    finally:
        streamer.cancel()
