from __future__ import annotations

from typing import Any


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, low: int = 1, high: int = 99) -> int:
    return max(low, min(high, round(value)))


def _atributos(jogador: dict) -> tuple[dict, dict]:
    return (
        dict(jogador.get("atributos", {}) or {}),
        dict(jogador.get("atributos_psicologicos", {}) or {}),
    )


def _body_type(jogador: dict, atr: dict) -> dict:
    altura = _int(jogador.get("altura"), 183)
    peso = _int(jogador.get("peso"), 78)
    movimento = _int(atr.get("movimento"), 60)
    fisico = _int(atr.get("fisico"), 60)

    if altura >= 193 and fisico >= 80:
        return {"id": "tower", "label": "Torre", "description": "Alcance enorme, saque pesado e presença física."}
    if movimento >= 85 and fisico <= 76:
        return {"id": "explosive", "label": "Explosivo", "description": "Primeiro passo muito forte e recuperação rápida."}
    if movimento >= 81 and fisico >= 81:
        return {"id": "power_runner", "label": "Motor", "description": "Combina potência física com cobertura de quadra."}
    if altura <= 178 and movimento >= 80:
        return {"id": "compact", "label": "Compacto", "description": "Centro de gravidade baixo e troca de direção rápida."}
    if altura >= 188 and peso <= 82:
        return {"id": "longiline", "label": "Longilíneo", "description": "Boa envergadura com mobilidade acima da média."}
    return {"id": "balanced", "label": "Equilibrado", "description": "Corpo neutro, sem viés extremo de mobilidade ou força."}


def _role_scores(atr: dict, psi: dict, modalidade: str | None) -> dict[str, float]:
    saque = _int(atr.get("saque"), 60)
    forehand = _int(atr.get("forehand"), 60)
    backhand = _int(atr.get("backhand"), 60)
    topspin = _int(atr.get("topspin"), 60)
    voleio = _int(atr.get("voleio"), 60)
    slice_ = _int(atr.get("slice"), 60)
    movimento = _int(atr.get("movimento"), 60)
    fisico = _int(atr.get("fisico"), 60)
    winner = _int(atr.get("winner"), 60)
    duplas = _int(atr.get("duplas"), 60)
    concentracao = _int(psi.get("concentracao"), 50)
    leitura = _int(psi.get("leitura_de_jogo"), 50)

    equilibrio = 100 - max(
        abs(saque - forehand),
        abs(forehand - backhand),
        abs(movimento - fisico),
        abs(voleio - topspin),
    )

    scores = {
        "aggressive_baseliner": forehand * 0.28 + winner * 0.25 + saque * 0.17 + movimento * 0.15 + backhand * 0.15,
        "counterpuncher": backhand * 0.24 + movimento * 0.24 + concentracao * 0.2 + leitura * 0.18 + fisico * 0.14,
        "servebot": saque * 0.44 + winner * 0.18 + forehand * 0.14 + fisico * 0.14 + movimento * 0.10,
        "all_court": (saque + forehand + backhand + voleio + movimento + fisico) / 6 * 0.8 + equilibrio * 0.2,
        "net_rusher": voleio * 0.34 + saque * 0.16 + movimento * 0.16 + duplas * 0.16 + winner * 0.18,
        "clay_grinder": topspin * 0.25 + movimento * 0.2 + fisico * 0.18 + concentracao * 0.14 + backhand * 0.13 + slice_ * 0.10,
        "doubles_specialist": duplas * 0.42 + voleio * 0.22 + movimento * 0.12 + saque * 0.12 + leitura * 0.12,
    }

    if modalidade == "duplas":
        scores["doubles_specialist"] += 6
        scores["net_rusher"] += 2

    return scores


def _primary_role(jogador: dict, modalidade: str | None) -> dict:
    atr, psi = _atributos(jogador)
    scores = _role_scores(atr, psi, modalidade)
    role_id = max(scores, key=scores.get)
    labels = {
        "aggressive_baseliner": "Aggressive Baseliner",
        "counterpuncher": "Counterpuncher",
        "servebot": "Servebot",
        "all_court": "All-Court",
        "net_rusher": "Net Rusher",
        "clay_grinder": "Clay Grinder",
        "doubles_specialist": "Doubles Specialist",
    }
    descriptions = {
        "aggressive_baseliner": "Toma a iniciativa cedo e encurta rallies.",
        "counterpuncher": "Defende, absorve ritmo e castiga a bola extra.",
        "servebot": "Constrói o jogo ao redor do saque e da primeira pancada.",
        "all_court": "Consegue mudar de plano sem perder eficiência.",
        "net_rusher": "Busca transição e fecha ponto na frente.",
        "clay_grinder": "Ritmo pesado, spin alto e resistência em trocas longas.",
        "doubles_specialist": "Leitura de cobertura e reflexo de rede acima da curva.",
    }
    return {
        "id": role_id,
        "label": labels[role_id],
        "fit": _clamp(scores[role_id], 50, 99),
        "description": descriptions[role_id],
    }


def _add_playstyle(playstyles: list[dict], seen: set[str], playstyle_id: str, label: str, description: str, tier: str, focus: list[str]) -> None:
    if playstyle_id in seen:
        return
    playstyles.append(
        {
            "id": playstyle_id,
            "label": label,
            "description": description,
            "tier": tier,
            "focus": focus,
        }
    )
    seen.add(playstyle_id)


def _playstyles(jogador: dict, modalidade: str | None) -> list[dict]:
    atr, psi = _atributos(jogador)
    playstyles: list[dict] = []
    seen: set[str] = set()

    saque = _int(atr.get("saque"), 60)
    forehand = _int(atr.get("forehand"), 60)
    backhand = _int(atr.get("backhand"), 60)
    topspin = _int(atr.get("topspin"), 60)
    voleio = _int(atr.get("voleio"), 60)
    slice_ = _int(atr.get("slice"), 60)
    movimento = _int(atr.get("movimento"), 60)
    fisico = _int(atr.get("fisico"), 60)
    winner = _int(atr.get("winner"), 60)
    duplas = _int(atr.get("duplas"), 60)
    concentracao = _int(psi.get("concentracao"), 50)
    leitura = _int(psi.get("leitura_de_jogo"), 50)
    determinacao = _int(psi.get("determinacao"), 50)

    if saque >= 86:
        _add_playstyle(playstyles, seen, "ace_machine", "Ace Machine", "Cria vantagem imediata com o saque.", "base", ["saque"])
    if saque >= 93:
        _add_playstyle(playstyles, seen, "ace_machine_plus", "Ace Machine+", "Saque de elite em pontos grátis e padrões curtos.", "plus", ["saque"])

    if saque >= 80 and max(forehand, winner) >= 84:
        _add_playstyle(playstyles, seen, "first_strike", "First Strike", "A primeira bola após o saque entra para machucar.", "base", ["saque", "winner"])
    if saque >= 88 and winner >= 89:
        _add_playstyle(playstyles, seen, "first_strike_plus", "First Strike+", "Abre quadra e define o ponto quase de imediato.", "plus", ["saque", "winner"])

    if voleio >= 84 or (duplas >= 86 and voleio >= 80):
        _add_playstyle(playstyles, seen, "net_hunter", "Net Hunter", "Timing forte de abordagem e reflexo de rede.", "base", ["voleio", "movimento"])
    if voleio >= 91 and duplas >= 90:
        _add_playstyle(playstyles, seen, "net_hunter_plus", "Net Hunter+", "Fecha a rede como especialista puro.", "plus", ["voleio", "duplas"])

    if backhand >= 84 and movimento >= 80:
        _add_playstyle(playstyles, seen, "return_wall", "Return Wall", "Absorve bem saque forte e devolve neutro ou profundo.", "base", ["backhand", "movimento"])
    if backhand >= 89 and leitura >= 78:
        _add_playstyle(playstyles, seen, "return_wall_plus", "Return Wall+", "Antecipação de devolução de nível elite.", "plus", ["backhand", "leitura_de_jogo"])

    if concentracao >= 72 or determinacao >= 74:
        _add_playstyle(playstyles, seen, "big_match", "Big Match", "Responde melhor em break points e tie-breaks.", "base", ["concentracao", "determinacao"])
    if concentracao >= 82 and determinacao >= 82:
        _add_playstyle(playstyles, seen, "big_match_plus", "Big Match+", "Sobe de produção nos pontos de maior pressão.", "plus", ["concentracao", "determinacao"])

    if duplas >= 86:
        _add_playstyle(playstyles, seen, "doubles_iq", "Doubles IQ", "Cobre espaços e lê cruzamentos muito bem.", "base", ["duplas", "voleio"])
    if duplas >= 93:
        _add_playstyle(playstyles, seen, "doubles_iq_plus", "Doubles IQ+", "Especialista raro de rede e cobertura em dupla.", "plus", ["duplas", "voleio"])

    if topspin >= 84 and fisico >= 78:
        _add_playstyle(playstyles, seen, "clay_grinder", "Clay Grinder", "Spin alto, profundidade e perna para rallies longos.", "base", ["topspin", "fisico"])
    if topspin >= 90 and movimento >= 84:
        _add_playstyle(playstyles, seen, "clay_grinder_plus", "Clay Grinder+", "Controle de altura e desgaste de elite.", "plus", ["topspin", "movimento"])

    if slice_ >= 80 and _int(atr.get("lob"), 60) >= 78:
        _add_playstyle(playstyles, seen, "change_pace", "Change Pace", "Varia altura, spin e tempo da troca.", "base", ["slice", "lob"])

    if movimento >= 84 and fisico >= 82:
        _add_playstyle(playstyles, seen, "iron_legs", "Iron Legs", "Sustenta intensidade alta por mais tempo.", "base", ["movimento", "fisico"])

    role_id = _primary_role(jogador, modalidade)["id"]
    role_style_map = {
        "aggressive_baseliner": ("inside_out", "Inside-Out Pressure", "Cria espaço para atacar de forehand.", ["forehand", "winner"]),
        "counterpuncher": ("elastic_defense", "Elastic Defense", "Recupera bola extra e reinicia o ponto.", ["movimento", "backhand"]),
        "servebot": ("service_command", "Service Command", "Domina padrões de saque e primeira pancada.", ["saque", "forehand"]),
        "all_court": ("shape_shifter", "Shape Shifter", "Muda altura, direção e plano de jogo com fluidez.", ["saque", "voleio", "backhand"]),
        "net_rusher": ("front_foot", "Front Foot", "Pressiona transição e fecha a frente da quadra.", ["voleio", "movimento"]),
        "clay_grinder": ("heavy_spin", "Heavy Spin", "Empurra o rival para trás com bola pesada.", ["topspin", "forehand"]),
        "doubles_specialist": ("poach_master", "Poach Master", "Intercepta e fecha a rede com leitura instantânea.", ["duplas", "voleio"]),
    }
    role_style = role_style_map.get(role_id)
    if role_style:
        _add_playstyle(playstyles, seen, role_style[0], role_style[1], role_style[2], "base", role_style[3])

    playstyles.sort(key=lambda item: (0 if item["tier"] == "plus" else 1, item["label"]))
    return playstyles[:6]


def _hidden_stats(jogador: dict) -> dict:
    atr, psi = _atributos(jogador)
    saque = _int(atr.get("saque"), 60)
    backhand = _int(atr.get("backhand"), 60)
    voleio = _int(atr.get("voleio"), 60)
    slice_ = _int(atr.get("slice"), 60)
    movimento = _int(atr.get("movimento"), 60)
    fisico = _int(atr.get("fisico"), 60)
    duplas = _int(atr.get("duplas"), 60)
    concentracao = _int(psi.get("concentracao"), 50)
    leitura = _int(psi.get("leitura_de_jogo"), 50)
    determinacao = _int(psi.get("determinacao"), 50)

    return {
        "clutch": _clamp(concentracao * 0.45 + determinacao * 0.45 + saque * 0.10),
        "positioning": _clamp(movimento * 0.42 + leitura * 0.33 + backhand * 0.25),
        "anticipation": _clamp(leitura * 0.45 + movimento * 0.25 + backhand * 0.15 + duplas * 0.15),
        "rally_tolerance": _clamp(fisico * 0.38 + concentracao * 0.34 + backhand * 0.28),
        "transition": _clamp(voleio * 0.40 + movimento * 0.25 + slice_ * 0.20 + _int(atr.get("lob"), 60) * 0.15),
        "doubles_iq": _clamp(duplas * 0.48 + voleio * 0.20 + leitura * 0.20 + movimento * 0.12),
    }


def _doubles_archetype(atr: dict, psi: dict) -> str:
    saque = _int(atr.get("saque"), 60)
    voleio = _int(atr.get("voleio"), 60)
    backhand = _int(atr.get("backhand"), 60)
    winner = _int(atr.get("winner"), 60)
    leitura = _int(psi.get("leitura_de_jogo"), 50)
    if voleio >= 86 and winner >= 80:
        return "Poacher"
    if saque >= 86:
        return "Launcher"
    if backhand >= 82 and leitura >= 75:
        return "Anchor"
    return "Hybrid"


def _doubles_profile(jogador: dict) -> dict:
    atr, psi = _atributos(jogador)
    duplas = _int(atr.get("duplas"), 60)
    vinculos = dict(jogador.get("vinculos_dupla", {}) or {})

    best_partner = None
    best_score = -1.0
    chemistry = _clamp(duplas * 0.82, 40, 99)
    record = None

    for nome, stats in vinculos.items():
        partidas = _int(stats.get("partidas"), 0)
        vitorias = _int(stats.get("vitorias"), 0)
        if partidas <= 0:
            continue
        win_rate = vitorias / partidas
        score = duplas * 0.35 + min(partidas, 20) * 1.6 + win_rate * 34
        if score > best_score:
            best_score = score
            best_partner = nome
            chemistry = _clamp(score, 45, 99)
            record = f"{vitorias}W-{max(0, partidas - vitorias)}L"

    return {
        "specialist": duplas >= 88,
        "rating": chemistry,
        "archetype": _doubles_archetype(atr, psi),
        "best_partner": best_partner,
        "record": record,
        "partnerships": len([1 for s in vinculos.values() if _int(s.get("partidas"), 0) > 0]),
    }


def derive_player_identity(jogador: dict, ranking_pos: int | None = None, modalidade: str | None = None) -> dict:
    atr, _psi = _atributos(jogador)
    return {
        "role": _primary_role(jogador, modalidade),
        "body_type": _body_type(jogador, atr),
        "playstyles": _playstyles(jogador, modalidade),
        "hidden_stats": _hidden_stats(jogador),
        "doubles_profile": _doubles_profile(jogador),
        "meta": {
            "ranking_anchor": _int(ranking_pos, 0) or None,
            "surface_bias": "clay" if _int(atr.get("topspin"), 60) >= 84 and _int(atr.get("slice"), 60) >= 74 else "neutral",
        },
    }
