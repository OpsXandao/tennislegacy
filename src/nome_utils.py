from functools import lru_cache


def obter_nome(obj):
    """Retorna o nome bruto de um jogador, seja ele um str, dict ou objeto."""
    if isinstance(obj, dict):
        return obj.get("nome", "").strip()
    elif hasattr(obj, "nome"):
        return getattr(obj, "nome", "").strip()
    return str(obj).strip()


@lru_cache(maxsize=2048)
def _normalizar_string(nome_bruto):
    """Normaliza uma string (remove espaços extras e converte para lower)."""
    return " ".join(nome_bruto.split()).lower()


def normalizar_nome(obj):
    """
    Retorna o nome do jogador em lowercase e sem espaços extras, usando cache.
    Funciona com strings, dicionários e objetos que possuam o atributo 'nome'.
    """
    return _normalizar_string(obter_nome(obj))
