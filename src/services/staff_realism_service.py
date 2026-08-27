from __future__ import annotations

from typing import Any

from src.constants.staff_constants import EMPRESARIOS_DISPONIVEIS, PROFISSIONAIS_DISPONIVEIS


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _attrs(obj: Any) -> dict:
    attrs = _get(obj, "atributos", {})
    return attrs if isinstance(attrs, dict) else {}


def _surface_key(surface: str | None) -> str:
    value = str(surface or "").lower()
    if "saibro" in value or "clay" in value:
        return "saibro"
    if "grama" in value or "grass" in value:
        return "grama"
    return "dura"


def staff_surface_fit(jogador: Any, staff_member: Any, surface: str | None = None) -> int:
    estilo = str(_get(staff_member, "estilo", "") or "").lower()
    foco = [str(item).lower() for item in (_get(staff_member, "foco_atributos", []) or [])]
    surface_key = _surface_key(surface or _get(jogador, "superficie_preferida", None))

    fit = 0
    if "fundo" in estilo and surface_key == "saibro":
        fit += 18
    if "rede" in estilo and surface_key == "grama":
        fit += 18
    if "tatico" in estilo or "tático" in estilo:
        fit += 8
    if "fisico" in estilo or "físico" in estilo:
        fit += 6
    if "psic" in estilo:
        fit += 5
    if foco and surface_key == "saibro" and any(item in foco for item in ("topspin", "movimento")):
        fit += 6
    if foco and surface_key == "grama" and any(item in foco for item in ("saque", "voleio", "slice")):
        fit += 6
    return min(30, fit)


def training_fit_summary(jogador: Any, staff_member: Any, foco: str, atributo_foco: str | None = None) -> dict:
    categoria = str(_get(staff_member, "categoria", "") or "").lower()
    foco_norm = str(foco or "").lower()
    bonus = 0.0
    motivo = "sem_efeito"

    if categoria == "treinador":
        foco_atributos = [str(item).lower() for item in (_get(staff_member, "foco_atributos", []) or [])]
        if foco_norm == "tecnico" and (not foco_atributos or atributo_foco is None or atributo_foco.lower() in foco_atributos):
            bonus = float(_get(staff_member, "bonus_progressao", 0) or 0)
            motivo = "treinador_compatível"
        elif foco_norm == "fisico" and atributo_foco in {"fisico", "movimento"}:
            bonus = float(_get(staff_member, "bonus_progressao", 0) or 0) * 0.65
            motivo = "treinador_aplica_fisico"
        elif foco_norm == "psicologico":
            bonus = float(_get(staff_member, "bonus_xp", 1.0) or 1.0) * 0.05
            motivo = "treinador_aplica_rotina"
        else:
            bonus = float(_get(staff_member, "bonus_progressao", 0) or 0) * 0.35
            motivo = "treinador_parcial"
    elif categoria == "preparador" and foco_norm == "fisico":
        bonus = float(_get(staff_member, "bonus_fisico_pct", 0) or 0)
        motivo = "preparador"
    elif categoria == "psicologo" and foco_norm == "psicologico":
        bonus = float(_get(staff_member, "bonus_mental", 0) or 0) * 0.05
        motivo = "psicologo"

    fit = staff_surface_fit(jogador, staff_member, _get(jogador, "superficie_preferida", None))
    return {
        "categoria": categoria,
        "bonus": round(bonus, 3),
        "motivo": motivo,
        "surface_fit": fit,
    }


def weekly_recovery_bonus(jogador: Any) -> dict:
    equipe = _get(jogador, "equipe", []) or []
    trainer_bonus = 0
    physio_bonus = 0
    psych_bonus = 0
    fit = 0

    for contrato in equipe:
        if not isinstance(contrato, dict):
            continue
        prof_id = contrato.get("id")
        prof = PROFISSIONAIS_DISPONIVEIS.get(prof_id)
        if not prof:
            continue
        cat = str(prof.get("categoria", "") or "").lower()
        fit += staff_surface_fit(jogador, prof)
        if cat == "treinador":
            trainer_bonus = max(trainer_bonus, int(prof.get("bonus_recuperacao", 0) or 0))
        elif cat == "fisioterapeuta":
            physio_bonus = max(physio_bonus, int(prof.get("bonus_recuperacao_lesao", 0) or 0))
        elif cat == "psicologo":
            psych_bonus = max(psych_bonus, int(prof.get("bonus_mental", 0) or 0))

    emp = _get(jogador, "empresario", None)
    if isinstance(emp, dict):
        emp_prof = EMPRESARIOS_DISPONIVEIS.get(emp.get("id"))
        if emp_prof:
            fit += 2 if int(_get(jogador, "seguidores", 0) or 0) >= int(emp_prof.get("seguidores_min", 0) or 0) else 0

    return {
        "trainer_bonus": trainer_bonus,
        "physio_bonus": physio_bonus,
        "psych_bonus": psych_bonus,
        "surface_fit": min(30, fit),
    }


def serialize_staff_member(info: dict | None, contrato: dict | None = None, jogador: Any | None = None) -> dict | None:
    if not info:
        return None
    fit = staff_surface_fit(jogador, info) if jogador is not None else 0
    return {
        "nome": info.get("nome", "Desconhecido"),
        "nivel": int(info.get("estrelas", 1) or 1),
        "custo_semanal": int((contrato or {}).get("salario", info.get("salario_semanal", 0)) or 0),
        "categoria": info.get("categoria"),
        "estilo": info.get("estilo"),
        "descricao": info.get("descricao"),
        "bonus": {k: info[k] for k in info if k.startswith("bonus_") or k in {"seguidores_min", "seguidores_max", "max_equipe"}},
        "surface_fit": fit,
        "contrato_semanas": int((contrato or {}).get("semanas_restantes", 0) or 0),
    }
