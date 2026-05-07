"""Utilitário de log para operações internas do jogo (não visíveis ao jogador)."""

import os
import traceback
from datetime import datetime


def log_simulacao(mensagem: str, nome_save: str) -> None:
    """Grava mensagem no arquivo de log do save (saves/<nome_save>/log.txt)."""
    try:
        from src.dados import SAVES_DIR, validar_nome_save

        nome_save = validar_nome_save(nome_save)
        pasta = os.path.join(SAVES_DIR, nome_save)
        os.makedirs(pasta, exist_ok=True)
        caminho = os.path.join(pasta, "log.txt")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(caminho, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {mensagem}\n")
    except OSError:
        pass  # log nunca deve travar o jogo


def log_erro(
    nome_save: str | None,
    contexto: str,
    exc: Exception,
    dados: dict | None = None,
) -> None:
    """
    Grava erro com contexto estruturado em saves/<nome_save>/log.txt.
    Inclui traceback curto para facilitar diagnóstico de produção.
    """
    try:
        from src.dados import SAVES_DIR, validar_nome_save

        save_ref = "global"
        if nome_save:
            save_ref = validar_nome_save(nome_save)

        pasta = os.path.join(SAVES_DIR, save_ref)
        os.makedirs(pasta, exist_ok=True)
        caminho = os.path.join(pasta, "log.txt")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload = dados or {}
        tb = traceback.format_exc(limit=6).strip()
        with open(caminho, "a", encoding="utf-8") as f:
            f.write(
                f"[{timestamp}] [ERRO] {contexto} | {type(exc).__name__}: {exc} | dados={payload}\n"
            )
            if tb and tb != "NoneType: None":
                f.write(f"[{timestamp}] [TRACE] {tb}\n")
    except OSError:
        pass
