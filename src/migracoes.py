# Módulo de Migração de Dados Legados - TennisLegacy

from src.patrocinios import PATROCINADORES_DISPONIVEIS
from src.staff_constants import EMPRESARIOS_DISPONIVEIS, PROFISSIONAIS_DISPONIVEIS

_MAPA_PATROCINIO_LEGADO = {
    "patrocinio_teste": "pat_01_teste",
    # Outros IDs legados se houverem...
}


def _resolver_id_patrocinio(item):
    """Auxiliar para converter IDs de patrocínio legados."""
    if item is None:
        return None
    if isinstance(item, dict):
        if item.get("id"):
            item = item.get("id")
        elif item.get("nome"):
            nome = str(item.get("nome", "")).strip().lower()
            for pid, pat in PATROCINADORES_DISPONIVEIS.items():
                if str(pat.get("nome", "")).strip().lower() == nome:
                    return pid
            return None
        else:
            return None

    if not isinstance(item, str):
        item = str(item)
    novo = _MAPA_PATROCINIO_LEGADO.get(item, item)
    return novo if novo in PATROCINADORES_DISPONIVEIS else None


def migrar_patrocinios(patrocinios_raw):
    """Converte IDs legados para os novos e descarta IDs desconhecidos."""
    if not isinstance(patrocinios_raw, (list, tuple, set)):
        return []

    resultado = []
    for p in patrocinios_raw:
        novo = _resolver_id_patrocinio(p)
        if novo and novo not in resultado:
            resultado.append(novo)
    return resultado


def migrar_equipe(equipe_raw, treinador_legado=None):
    """
    Converte a equipe para list[dict] com campos de contrato.
    Trata formato antigo list[str] e migra treinador legado.
    """
    if equipe_raw is None:
        equipe_raw = []
    elif not isinstance(equipe_raw, (list, tuple, set)):
        equipe_raw = [equipe_raw]

    equipe = []
    ids_presentes = set()
    for item in equipe_raw:
        if isinstance(item, dict):
            prof_id = item.get("id", "")
            if prof_id in PROFISSIONAIS_DISPONIVEIS and prof_id not in ids_presentes:
                prof_data = PROFISSIONAIS_DISPONIVEIS[prof_id]
                equipe.append(
                    {
                        "id": prof_id,
                        "semanas_restantes": int(
                            item.get("semanas_restantes", 52) or 52
                        ),
                        "salario": int(
                            item.get("salario", prof_data["salario_semanal"])
                            or prof_data["salario_semanal"]
                        ),
                    }
                )
                ids_presentes.add(prof_id)
        elif isinstance(item, str) and item in PROFISSIONAIS_DISPONIVEIS:
            if item not in ids_presentes:
                equipe.append(
                    {
                        "id": item,
                        "semanas_restantes": 52,
                        "salario": PROFISSIONAIS_DISPONIVEIS[item]["salario_semanal"],
                    }
                )
                ids_presentes.add(item)

    if treinador_legado and "treinador" not in ids_presentes:
        # Tenta mapear o treinador legado para o novo formato
        for tid, prof in PROFISSIONAIS_DISPONIVEIS.items():
            if prof["tipo"] == "treinador":
                equipe.append(
                    {
                        "id": tid,
                        "semanas_restantes": 52,
                        "salario": prof["salario_semanal"],
                    }
                )
                break
    return equipe


def migrar_empresario(empresario_raw):
    """Converte o campo empresario para o formato correto de contrato."""
    if empresario_raw is None:
        return None
    if isinstance(empresario_raw, dict) and "id" in empresario_raw:
        emp_id = empresario_raw.get("id")
        if emp_id not in EMPRESARIOS_DISPONIVEIS:
            return None
        emp = EMPRESARIOS_DISPONIVEIS[emp_id]
        return {
            "id": emp_id,
            "semanas_restantes": int(empresario_raw.get("semanas_restantes", 26) or 26),
            "salario": int(
                empresario_raw.get("salario", emp["salario_semanal"])
                or emp["salario_semanal"]
            ),
        }
    # String legada
    if isinstance(empresario_raw, str) and empresario_raw in EMPRESARIOS_DISPONIVEIS:
        emp = EMPRESARIOS_DISPONIVEIS[empresario_raw]
        return {
            "id": empresario_raw,
            "semanas_restantes": 26,
            "salario": emp["salario_semanal"],
        }
    return None


def aplicar_migracoes(data: dict) -> dict:
    """
    Aplica todas as migrações necessárias em um dicionário de dados de save.
    Deve ser chamado antes da criação do objeto Jogador.
    """
    if not isinstance(data, dict):
        return data

    data["empresario"] = migrar_empresario(data.get("empresario"))
    data["equipe"] = migrar_equipe(
        data.get("equipe", []),
        treinador_legado=data.get("treinador"),
    )
    data["patrocinios"] = migrar_patrocinios(data.get("patrocinios", []))

    # Outras higienizações
    if "atributos" in data and "fisico" not in data["atributos"]:
        data["atributos"]["fisico"] = 50

    return data
