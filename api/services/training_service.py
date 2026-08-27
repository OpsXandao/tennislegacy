from src.progressao import treinar_semana
from src.save import salvar_jogo
from src.calendario import avancar_semana
from api.session import Session


def executar_descanso(session: Session) -> tuple:
    j = session.jogador
    energia_antes = j.energia
    j.energia = min(100, j.energia + 30)
    j.fadiga = max(0, j.fadiga - 25)
    
    # Feedback Narrativo
    recup = j.energia - energia_antes
    msg = f"Ótima escolha. Seu preparador físico nota uma recuperação de {recup}% na sua energia."
    if j.fadiga == 0:
        msg += " Você está se sentindo renovado e pronto para o próximo desafio."
        
    salvar_jogo(session.nome_save_ativo, j)
    resultado = avancar_semana(session.nome_save_ativo, expected_week=session.semana_atual)
    resultado["eventos"].append(msg)
    return j, resultado


def executar_treino(session: Session, foco: str, atributo_foco: str | None = None) -> tuple:
    j = session.jogador
    melhorias = treinar_semana(j, foco, atributo_foco=atributo_foco)
    
    # Feedback Narrativo
    if "LESIONADO" in melhorias:
        msg = f"DESASTRE NO TREINO! Você tentou forçar demais e sofreu uma lesão. Seu preparador está furioso com a falta de cuidado."
        salvar_jogo(session.nome_save_ativo, j)
        resultado = avancar_semana(session.nome_save_ativo, expected_week=session.semana_atual)
        resultado["eventos"].append(msg)
        return j, {}, resultado

    if melhorias:
        fatos = ", ".join([f"{k.capitalize()} (+{v})" for k, v in melhorias.items() if k != "moral"])
        if atributo_foco and atributo_foco in melhorias:
            msg = f"Treino de especialização concluído. Seu treinador elogia seu foco em {atributo_foco.capitalize()}. Evolução: {fatos}."
        else:
            msg = f"Seu treinador está satisfeito com a evolução em: {fatos}."
    else:
        msg = "O treino foi intenso, mas seu treinador acredita que você precisa de mais foco para atingir o próximo nível."

    salvar_jogo(session.nome_save_ativo, j)
    resultado = avancar_semana(session.nome_save_ativo, expected_week=session.semana_atual)
    resultado["eventos"].append(msg)
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
