from __future__ import annotations

from typing import Any


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _attrs(obj: Any) -> dict:
    attrs = _get(obj, "atributos", {})
    return attrs if isinstance(attrs, dict) else {}


def doubles_skill_score(jogador: Any) -> int:
    overall = int(_get(jogador, "overall", 50) or 50)
    duplas = int(_attrs(jogador).get("duplas", _get(jogador, "duplas", 60)) or 60)
    voleio = int(_attrs(jogador).get("voleio", 55) or 55)
    saque = int(_attrs(jogador).get("saque", 55) or 55)
    return max(1, min(99, round(overall * 0.35 + duplas * 0.35 + voleio * 0.18 + saque * 0.12)))


def combined_rank(rank_a: int | None, rank_b: int | None) -> int:
    a = int(rank_a or 999)
    b = int(rank_b or 999)
    return a + b


def partnership_profile(jogador: Any, parceiro: Any, vinculo: dict | None = None) -> dict:
    vinculo = vinculo if isinstance(vinculo, dict) else {}
    partidas = int(vinculo.get("partidas", 0) or 0)
    vitorias = int(vinculo.get("vitorias", 0) or 0)
    win_rate = vitorias / partidas if partidas > 0 else 0.0
    skill_media = round((doubles_skill_score(jogador) + doubles_skill_score(parceiro)) / 2)

    if partidas >= 20:
        status = "fixa"
    elif partidas >= 5:
        status = "recorrente"
    elif partidas >= 1:
        status = "testada"
    else:
        status = "ocasional"

    return {
        "status": status,
        "partidas": partidas,
        "vitorias": vitorias,
        "win_rate": round(win_rate, 3),
        "skill_duplas": skill_media,
    }


def availability_status(
    jogador: Any,
    parceiro: Any,
    torneio_tipo: str = "ATP 250",
    parceiro_rank_simples: int | None = None,
    vinculo: dict | None = None,
) -> dict:
    tipo = str(torneio_tipo or "ATP 250")
    rank = int(parceiro_rank_simples or 999)
    vinculo = vinculo if isinstance(vinculo, dict) else {}
    partidas = int(vinculo.get("partidas", 0) or 0)

    status_lesao = _get(parceiro, "status_lesao", {})
    if isinstance(status_lesao, dict) and status_lesao.get("lesionado"):
        return {"status": "indisponivel", "motivo": "lesionado", "score": 0}

    energia = int(_get(parceiro, "energia", 100) or 100)
    fadiga = int(_get(parceiro, "fadiga", 0) or 0)
    if energia < 25 or fadiga >= 88:
        return {"status": "duvida", "motivo": "fisico", "score": 25}

    if rank <= 30 and tipo not in {"Grand Slam", "Davis Cup", "Billie Jean King Cup", "United Cup"}:
        if partidas < 5:
            return {"status": "baixa", "motivo": "prioriza_simples", "score": 35}
        return {"status": "media", "motivo": "parceria_existente", "score": 58}

    if partidas >= 10:
        return {"status": "alta", "motivo": "parceiro_habitual", "score": 86}
    if partidas >= 1:
        return {"status": "media", "motivo": "ja_jogaram_juntos", "score": 68}
    return {"status": "aberta", "motivo": "sem_compromisso", "score": 55}


def doubles_match_format(torneio_tipo: str, mistas: bool = False) -> dict:
    tipo = str(torneio_tipo or "ATP 250")
    is_grand_slam = tipo == "Grand Slam"
    return {
        "sets": "melhor_de_3",
        "no_ad": not is_grand_slam or mistas,
        "match_tiebreak": not is_grand_slam or mistas,
        "terceiro_set": "match_tiebreak_10" if (not is_grand_slam or mistas) else "set_completo",
    }
