from __future__ import annotations


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

    return {
        "nome": t.get("nome"),
        "tipo": t.get("tipo"),
        "superficie": t.get("quadra", t.get("superficie", "dura")),
        "local": t.get("local"),
        "semana": t.get("semana"),
        "premiacao": premio_str,
        "pais": pais_nome,
        "codigo_pais": codigo_pais,
    }
