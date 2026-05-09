from src.progressao import treinar_semana
from src.save import salvar_jogo
from src.calendario import avancar_semana
from api.session import Session


def executar_descanso(session: Session) -> tuple:
    j = session.jogador
    j.energia = min(100, j.energia + 30)
    j.fadiga = max(0, j.fadiga - 25)
    salvar_jogo(session.nome_save_ativo, j)
    resultado = avancar_semana(session.nome_save_ativo, expected_week=session.semana_atual)
    return j, resultado


def executar_treino(session: Session, foco: str) -> tuple:
    j = session.jogador
    melhorias = treinar_semana(j, foco)
    salvar_jogo(session.nome_save_ativo, j)
    resultado = avancar_semana(session.nome_save_ativo, expected_week=session.semana_atual)
    return j, melhorias, resultado


def serializar_status_jogador(j) -> dict:
    return {
        "energia": j.energia,
        "fadiga": j.fadiga,
        "atributos": j.atributos,
        "atributos_psicologicos": j.atributos_psicologicos,
    }


def alocar_skill(session: Session, tipo: str, atributo: str) -> dict:
    j = session.jogador
    pontos = getattr(j, "pontos_de_skill", 0)
    if pontos <= 0:
        return {"ok": False, "erro": "Sem pontos de skill disponíveis.", "status": 400}

    if tipo == "tecnico":
        if atributo not in j.atributos:
            return {"ok": False, "erro": f"Atributo '{atributo}' nao encontrado.", "status": 404}
        if j.atributos[atributo] >= 100:
            return {"ok": False, "erro": "Atributo já no máximo.", "status": 400}
        j.atributos[atributo] = min(100, j.atributos[atributo] + 1)
    elif tipo == "psicologico":
        psico = getattr(j, "atributos_psicologicos", {})
        if atributo not in psico:
            return {"ok": False, "erro": f"Atributo '{atributo}' nao encontrado.", "status": 404}
        if psico[atributo] >= 100:
            return {"ok": False, "erro": "Atributo já no máximo.", "status": 400}
        psico[atributo] = min(100, psico[atributo] + 1)
    else:
        return {"ok": False, "erro": "Tipo deve ser 'tecnico' ou 'psicologico'.", "status": 422}

    j.pontos_de_skill = pontos - 1
    if hasattr(j, "_sanitizar_atributos"):
        j._sanitizar_atributos()
    if hasattr(j, "calcular_overall"):
        j.calcular_overall()

    salvar_jogo(session.nome_save_ativo, j)
    return {
        "ok": True,
        "pontos_de_skill": j.pontos_de_skill,
        "atributos": j.atributos,
        "atributos_psicologicos": getattr(j, "atributos_psicologicos", {}),
    }
