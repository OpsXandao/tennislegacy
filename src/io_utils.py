def safe_input(prompt):
    """Wrapper para input que encerra o programa em EOF (execucao nao interativa)."""
    try:
        return input(prompt)
    except EOFError:
        print("EOF recebido. Encerrando o jogo.")
        raise SystemExit(0)
