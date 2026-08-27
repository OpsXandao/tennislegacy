"""Ajuste tático de estratégia entre sets de uma partida."""

from src.constants.match_constants import EstrategiaSaque
from src.match_state import EstatisticasPartida


def _pct(numerador: int, denominador: int) -> float:
    if denominador <= 0:
        return 0.0
    return (numerador / denominador) * 100.0


def ajustar_estrategia_entre_sets(
    estrategia: dict,
    stats_set: EstatisticasPartida,
    stats_set_adv: EstatisticasPartida,
    superficie: str,
    is_jogador: bool = False,
):
    """Ajusta a estratégia com base nas estatísticas do set anterior.

    Returns:
        (estrategia_atualizada, lista_de_dicas)  — dicas só são preenchidas
        quando ``is_jogador=True``.
    """
    estrategia = (estrategia or {}).copy()
    ajustes = []

    pct_primeiro = _pct(stats_set.primeiro_saque_in, stats_set.primeiro_saque_total)
    pct_devolucao = _pct(
        stats_set.pontos_ganhos_devolucao, stats_set.pontos_total_devolucao
    )
    winners = stats_set.winners
    erros = stats_set.erros_nao_forcados

    if pct_primeiro < 54:
        estrategia["saque"] = EstrategiaSaque.SEGURO
        if is_jogador:
            ajustes.append("1o saque baixo: priorizar segurança no serviço.")
    elif pct_primeiro > 68 and winners <= stats_set_adv.winners:
        estrategia["saque"] = EstrategiaSaque.FORCAR
        if is_jogador:
            ajustes.append("boa taxa de 1o saque: aumentar pressão no 2o saque.")

    if erros >= max(6, winners + 2):
        estrategia["estilo"] = "atacar_pelo_meio"
        if is_jogador:
            ajustes.append("muitos erros não forçados: jogo mais controlado.")
    elif pct_devolucao < 28 and superficie != "grama":
        estrategia["estilo"] = "atacar_do_fundo"
        if is_jogador:
            ajustes.append("devolução baixa: alongar os pontos no fundo.")
    elif winners >= erros + 4 and superficie == "grama":
        estrategia["estilo"] = "atacar_na_rede"
        if is_jogador:
            ajustes.append("agressividade eficiente: subir mais à rede.")

    return estrategia, ajustes
