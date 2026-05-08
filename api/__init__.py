from importlib import import_module


try:
    import_module("api.routes._shared")
except Exception:
    # Mantém a importação do pacote resiliente em ambientes parciais de teste.
    pass
