from src.calendario import avancar_semana, obter_torneios_da_semana
from src.pontuacao import distribuir_pontos_torneio
from src.presenters.tournament_presenter import formatar_torneio_resumido
from src.services.player_context_service import carregar_temporada_atual, tour_para_genero
from api.session import Session, refresh_session


def obter_semana_por_numero(numero: int, tour: str | None, jogador) -> dict:
    genero = tour_para_genero(tour, jogador.genero)
    torneios = obter_torneios_da_semana(numero, genero=genero)
    return {
        "semana": numero,
        "tour": "atp" if genero == "masculino" else "wta",
        "torneios": [formatar_torneio_resumido(t) for t in torneios],
    }


def obter_semana_atual(nome_save: str, tour: str | None, jogador) -> dict:
    temporada = carregar_temporada_atual(nome_save)
    genero = tour_para_genero(tour, jogador.genero)
    torneios = obter_torneios_da_semana(temporada["semana"], genero=genero)
    return {
        "semana": temporada["semana"],
        "ano": temporada["ano"],
        "tour": "atp" if genero == "masculino" else "wta",
        "torneios": [formatar_torneio_resumido(t) for t in torneios],
    }


def avancar(session: Session) -> dict:
    nome_save = session.nome_save_ativo
    jogador = session.jogador
    try:
        distribuir_pontos_torneio(nome_save, genero=jogador.genero)
    except Exception:
        pass
    resultado = avancar_semana(nome_save, expected_week=session.semana_atual)
    refresh_session(nome_save)
    return resultado
