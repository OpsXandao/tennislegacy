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
