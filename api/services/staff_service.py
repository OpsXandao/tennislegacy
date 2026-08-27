from fastapi import HTTPException
from api.session import Session
from src.management import obter_max_equipe, obter_profissional_da_equipe
from src.save import salvar_jogo
from src.constants.staff_constants import EMPRESARIOS_DISPONIVEIS, PROFISSIONAIS_DISPONIVEIS
from src.services.staff_realism_service import serialize_staff_member, staff_surface_fit

_CATEGORIAS_EQUIPE = ("treinador", "fisioterapeuta", "psicologo", "marketing", "preparador")

_CAMPOS_BONUS = (
    "bonus_progressao", "bonus_recuperacao", "bonus_xp", "chance_mental",
    "bonus_mental", "bonus_fadiga", "bonus_fisico_pct", "seguidores_min",
    "seguidores_max", "bonus_patrocinio", "max_equipe",
)


def _serialize_membro(info: dict | None, contrato: dict | None = None, jogador=None) -> dict | None:
    return serialize_staff_member(info, contrato, jogador=jogador)


def get_equipe_dict(jogador) -> dict:
    equipe_list = getattr(jogador, "equipe", [])
    if not isinstance(equipe_list, list):
        equipe_list = []

    res: dict = {c: None for c in ("treinador", "fisio", "psicologo", "empresario", "marketing", "preparador")}

    for item in equipe_list:
        if not isinstance(item, dict) or "id" not in item:
            continue
        info = PROFISSIONAIS_DISPONIVEIS.get(item["id"])
        if not info:
            continue
        cat = info.get("categoria")
        key_map = {"fisioterapeuta": "fisio"}
        res_key = key_map.get(cat, cat)
        if res_key in res:
            res[res_key] = _serialize_membro(info, item, jogador=jogador)

    emp_item = getattr(jogador, "empresario", None)
    if isinstance(emp_item, dict) and "id" in emp_item:
        info_emp = EMPRESARIOS_DISPONIVEIS.get(emp_item["id"])
        if info_emp:
            res["empresario"] = _serialize_membro(info_emp, emp_item, jogador=jogador)
    elif isinstance(emp_item, str):
        info_emp = EMPRESARIOS_DISPONIVEIS.get(emp_item)
        if info_emp:
            res["empresario"] = _serialize_membro(info_emp, jogador=jogador)

    return res


def listar_todos() -> dict:
    categorias: dict = {c: [] for c in ("treinador", "fisioterapeuta", "psicologo", "marketing", "empresario", "preparador")}
    for pid, info in PROFISSIONAIS_DISPONIVEIS.items():
        cat = info.get("categoria")
        if cat in categorias:
            categorias[cat].append({"id": pid, **info, "surface_fit": staff_surface_fit(None, info)})
    for eid, info in EMPRESARIOS_DISPONIVEIS.items():
        categorias["empresario"].append({"id": eid, **info, "surface_fit": 0})
    return categorias


def contratar(session: Session, prof_id: str) -> dict:
    j = session.jogador

    if prof_id in EMPRESARIOS_DISPONIVEIS:
        info = EMPRESARIOS_DISPONIVEIS[prof_id]
        custo = info["salario_semanal"]
        if j.dinheiro < custo * 4:
            raise HTTPException(
                status_code=400,
                detail=f"Saldo insuficiente. Você precisa de pelo menos ${custo*4} para contratar este empresário.",
            )
        j.empresario = {"id": prof_id, "semanas_restantes": 26, "salario": custo}
        salvar_jogo(session.nome_save_ativo, j)
        return {"ok": True, "mensagem": f"{info['nome']} contratado como seu novo empresário!"}

    if prof_id in PROFISSIONAIS_DISPONIVEIS:
        info = PROFISSIONAIS_DISPONIVEIS[prof_id]
        custo = info["salario_semanal"]
        if j.dinheiro < custo * 4:
            raise HTTPException(
                status_code=400,
                detail=f"Saldo insuficiente. Você precisa de pelo menos ${custo*4} para contratar este profissional.",
            )
        cat = info["categoria"]
        if obter_profissional_da_equipe(j.equipe, cat):
            raise HTTPException(
                status_code=400,
                detail=f"Você já possui um {cat} na equipe. Demita-o primeiro.",
            )
        max_equipe = obter_max_equipe(j)
        if len(j.equipe) >= max_equipe:
            raise HTTPException(
                status_code=400,
                detail=f"Sua equipe está cheia (máximo {max_equipe} profissionais).",
            )
        j.equipe.append({"id": prof_id, "semanas_restantes": 26, "salario": info["salario_semanal"]})
        salvar_jogo(session.nome_save_ativo, j)
        return {"ok": True, "mensagem": f"{info['nome']} contratado com sucesso!"}

    raise HTTPException(status_code=404, detail="Profissional não encontrado.")


def demitir(session: Session, prof_id: str) -> dict:
    j = session.jogador
    msg_multa = ""

    if j.empresario and j.empresario.get("id") == prof_id:
        # Multa rescisória se demitir antes do fim (mais de 1 semana restante)
        semanas = j.empresario.get("semanas_restantes", 0)
        if semanas > 1:
            multa = j.empresario.get("salario", 0) * 2
            if multa > 0 and j.dinheiro < multa:
                raise HTTPException(
                    status_code=400,
                    detail=f"Saldo insuficiente para multa de rescisão (R$ {multa:,.0f}).",
                )
            j.registrar_transacao(-multa, f"Multa rescisória: {prof_id}", categoria="equipe")
            msg_multa = f" Multa de rescisão paga: ${multa}."

        j.empresario = None
        salvar_jogo(session.nome_save_ativo, j)
        return {"ok": True, "mensagem": f"Empresário demitido.{msg_multa}"}

    # Busca o contrato na equipe para calcular multa
    contrato = next((c for c in j.equipe if c.get("id") == prof_id), None)
    if contrato:
        semanas = contrato.get("semanas_restantes", 0)
        if semanas > 1:
            multa = contrato.get("salario", 0) * 2
            if multa > 0 and j.dinheiro < multa:
                raise HTTPException(
                    status_code=400,
                    detail=f"Saldo insuficiente para multa de rescisão (R$ {multa:,.0f}).",
                )
            j.registrar_transacao(-multa, f"Multa rescisória: {prof_id}", categoria="equipe")
            msg_multa = f" Multa de rescisão paga: ${multa}."

        j.equipe = [c for c in j.equipe if c.get("id") != prof_id]
        salvar_jogo(session.nome_save_ativo, j)
        return {"ok": True, "mensagem": f"Profissional demitido.{msg_multa}"}

    raise HTTPException(status_code=404, detail="Profissional não encontrado na sua equipe.")
