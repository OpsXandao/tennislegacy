from __future__ import annotations


SPECIAL_COURTS = {
    "Australian Open": "Rod Laver Arena",
    "Roland Garros": "Court Philippe-Chatrier",
    "Wimbledon": "Centre Court",
    "US Open": "Arthur Ashe Stadium",
    "ATP Finals": "Pala Alpitour Centre Court",
    "WTA Finals": "Championship Court",
    "Indian Wells": "Stadium 1",
    "Miami Open": "Stadium Court",
    "Monte-Carlo Masters": "Court Rainier III",
    "Madrid Open": "Manolo Santana Stadium",
    "Internazionali BNL d'Italia": "Campo Centrale",
}


def _nome_quadra_principal(t: dict) -> str:
    nome = str(t.get("nome", "") or "").strip()
    if nome in SPECIAL_COURTS:
        return SPECIAL_COURTS[nome]

    local = str(t.get("local", "") or "").strip()
    if not local:
        return "Quadra Central"
    return f"Quadra Central de {local}"


def _janela_torneio(tipo: str) -> str:
    tipo_norm = str(tipo or "").lower()
    if "grand slam" in tipo_norm:
        return "SEG-DOM"
    if "finals" in tipo_norm:
        return "TER-DOM"
    if "cup" in tipo_norm:
        return "QUA-DOM"
    return "SEG-DOM"


def _horario_principal(tipo: str, superficie: str) -> tuple[str, str]:
    tipo_norm = str(tipo or "").lower()
    superficie_norm = str(superficie or "").lower()

    if "cup" in tipo_norm:
        return ("14:00", "Sessão de nações")
    if "grand slam" in tipo_norm:
        return ("11:00", "Sessão principal")
    if "grass" in superficie_norm or "grama" in superficie_norm:
        return ("12:00", "Sessão central")
    if "clay" in superficie_norm or "saibro" in superficie_norm:
        return ("10:30", "Sessão diurna")
    return ("13:00", "Sessão principal")


def formatar_torneio_resumido(t: dict) -> dict:
    premio = t.get("premiacao")
    if isinstance(premio, (int, float)) and premio > 0:
        if premio >= 1_000_000:
            premio_str = f"${premio/1_000_000:.1f}M"
        elif premio >= 1_000:
            premio_str = f"${premio/1_000:.0f}K"
        else:
            premio_str = f"${premio}"
    else:
        premio_str = None

    pais_raw = t.get("pais_sede", "")
    codigo_pais = None
    pais_nome = pais_raw
    if "]" in pais_raw:
        parts = pais_raw.split("]", 1)
        codigo_pais = parts[0].replace("[", "").strip()
        pais_nome = parts[1].strip()

    superficie = t.get("quadra", t.get("superficie", "dura"))
    horario_local, sessao_label = _horario_principal(t.get("tipo", ""), superficie)

    return {
        "nome": t.get("nome"),
        "tipo": t.get("tipo"),
        "superficie": superficie,
        "local": t.get("local"),
        "semana": t.get("semana"),
        "premiacao": premio_str,
        "pais": pais_nome,
        "codigo_pais": codigo_pais,
        "quadra_nome": _nome_quadra_principal(t),
        "horario_local": horario_local,
        "sessao_label": sessao_label,
        "janela_semana": _janela_torneio(t.get("tipo", "")),
    }
