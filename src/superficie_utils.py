def normalizar_superficie(superficie: str) -> str:
    if not superficie:
        return "dura"
    superficie = superficie.strip().lower()
    mapa = {
        "hard": "dura",
        "dura": "dura",
        "rapida": "dura",
        "clay": "saibro",
        "saibro": "saibro",
        "terra": "saibro",
        "grass": "grama",
        "grama": "grama",
    }
    return mapa.get(superficie, "dura")
