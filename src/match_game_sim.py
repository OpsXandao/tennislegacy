"""Simulação de games e tiebreaks individuais (modos rápido, detalhado, estrategista)."""

import logging
import time

from src.match_config import ConfigPartida, _nome_entidade
from src.match_state import ContextoPartida, ContextoPonto, EstatisticasPartida
from src.match_core import (
    _aplicar_custo_stamina,
    _atualizar_momentum,
    _recuperar_stamina_entre_games,
    atualizar_estatisticas,
    simular_game_rapido,
)
from src.constants.match_constants import TipoSaque
from src.services.simulador_ponto import SimuladorPonto

logger = logging.getLogger(__name__)

_PLACAR_TXT = {0: "0", 1: "15", 2: "30", 3: "40"}


def _placar_pontos_txt(ponto: int) -> str:
    return _PLACAR_TXT.get(ponto, str(ponto))


def _sacador_tiebreak(sacador_inicial: str, indice_ponto: int) -> str:
    if indice_ponto == 0:
        return sacador_inicial
    bloco = (indice_ponto - 1) // 2
    if bloco % 2 == 0:
        return "a" if sacador_inicial == "j" else "j"
    return sacador_inicial


def _alvo_tiebreak(sets: dict, sets_para_vencer: int, config: ConfigPartida) -> int:
    if sets["j"] == sets_para_vencer - 1 and sets["a"] == sets_para_vencer - 1:
        return config.tiebreak_decisivo_pontos
    return 7


def _simular_game_interativo(
    jogador,
    adversario,
    estrategia,
    sacador,
    placar_set,
    placar_partida,
    simulador: SimuladorPonto,
    contexto_partida: ContextoPartida,
    estrategia_adversario: dict,
    modo_ref: dict,
    stats_j: EstatisticasPartida = None,
    stats_a: EstatisticasPartida = None,
    sets_para_vencer: int = 2,
    estrategista: bool = False,
):
    """Base comum para os modos detalhado e estrategista."""
    pontos = {"j": 0, "a": 0}
    historico = []

    tipo_saque = (
        estrategia.get("saque_tipo", TipoSaque.VARIADO) if sacador == "j" else None
    )
    nome_j = _nome_entidade(jogador, "Jogador")
    nome_a = _nome_entidade(adversario, "Adversário")

    while True:
        pj_ctx, pa_ctx = pontos["j"], pontos["a"]
        if pj_ctx >= 3 and pa_ctx >= 3:
            if pj_ctx > pa_ctx:
                pj_ctx, pa_ctx = 4, 3
            elif pa_ctx > pj_ctx:
                pj_ctx, pa_ctx = 3, 4
            else:
                pj_ctx, pa_ctx = 3, 3

        contexto = ContextoPonto(
            sacador=sacador,
            placar_game=(pj_ctx, pa_ctx),
            placar_set=placar_set,
            placar_partida=placar_partida,
            sets_para_vencer=sets_para_vencer,
        )

        if contexto.is_match_point():
            logger.debug("\n*** MATCH POINT! ***")
        elif contexto.is_set_point():
            logger.debug("\n*** SET POINT! ***")
        elif contexto.is_break_point():
            logger.debug("\n*** BREAK POINT! ***")

        if estrategista:
            from src.jogar_partida import escolher_intencao_ponto

            estrategia["intencao"] = escolher_intencao_ponto()

        vencedor, descricoes, stats_info = simulador.simular_ponto_detalhado(
            estrategia, contexto, tipo_saque, contexto_partida, estrategia_adversario
        )
        historico.append(vencedor)
        _aplicar_custo_stamina(
            contexto_partida,
            stats_info,
            jogador,
            adversario,
            estrategia,
            estrategia_adversario,
            contexto,
        )
        _atualizar_momentum(contexto_partida, contexto, vencedor)

        if stats_j is not None and stats_a is not None:
            atualizar_estatisticas(stats_j, stats_a, vencedor, stats_info, contexto)

        for desc in descricoes:
            logger.debug(desc)

        pontos[vencedor] += 1
        if pontos[vencedor] >= 4 and abs(pontos["j"] - pontos["a"]) >= 2:
            nome_vencedor = nome_j if vencedor == "j" else nome_a
            logger.debug(f"Game para {nome_vencedor}!")
            return vencedor, historico, False

        if pontos["j"] >= 3 and pontos["a"] >= 3:
            if pontos["j"] == pontos["a"]:
                logger.debug("Deuce!")
            else:
                nome_vantagem = nome_j if pontos["j"] > pontos["a"] else nome_a
                logger.debug(f"Advantage {nome_vantagem}")
        else:
            logger.debug(
                f"Placar: {nome_j} {_placar_pontos_txt(pontos['j'])} x"
                f" {_placar_pontos_txt(pontos['a'])} {nome_a}"
            )

        interrupted = False
        start_time = time.time()
        while time.time() - start_time < 2.3:
            if False:
                interrupted = True
                ""  # Consume the character
                break
            time.sleep(0.1)

        if interrupted:
            from src.jogar_partida import show_pause_menu, verificar_abandono

            action, estrategia, novo_modo = show_pause_menu(
                jogador, adversario, stats_j, stats_a, estrategia, modo_ref["modo"]
            )
            modo_ref["modo"] = novo_modo
            if action == "abandon":
                if verificar_abandono():
                    return "abandono", historico, True


def simular_game_detalhado(
    jogador,
    adversario,
    estrategia,
    sacador,
    placar_set,
    placar_partida,
    simulador: SimuladorPonto,
    contexto_partida: ContextoPartida,
    estrategia_adversario: dict,
    modo_ref: dict,
    stats_j: EstatisticasPartida = None,
    stats_a: EstatisticasPartida = None,
    sets_para_vencer: int = 2,
):
    """Simula um game completo no modo detalhado com descrições."""
    return _simular_game_interativo(
        jogador=jogador,
        adversario=adversario,
        estrategia=estrategia,
        sacador=sacador,
        placar_set=placar_set,
        placar_partida=placar_partida,
        simulador=simulador,
        contexto_partida=contexto_partida,
        estrategia_adversario=estrategia_adversario,
        modo_ref=modo_ref,
        stats_j=stats_j,
        stats_a=stats_a,
        sets_para_vencer=sets_para_vencer,
        estrategista=False,
    )


def simular_game_estrategista(
    jogador,
    adversario,
    estrategia,
    sacador,
    placar_set,
    placar_partida,
    simulador: SimuladorPonto,
    contexto_partida: ContextoPartida,
    estrategia_adversario: dict,
    modo_ref: dict,
    stats_j: EstatisticasPartida = None,
    stats_a: EstatisticasPartida = None,
    sets_para_vencer: int = 2,
):
    """Simula um game completo no modo estrategista com descrições."""
    return _simular_game_interativo(
        jogador=jogador,
        adversario=adversario,
        estrategia=estrategia,
        sacador=sacador,
        placar_set=placar_set,
        placar_partida=placar_partida,
        simulador=simulador,
        contexto_partida=contexto_partida,
        estrategia_adversario=estrategia_adversario,
        modo_ref=modo_ref,
        stats_j=stats_j,
        stats_a=stats_a,
        sets_para_vencer=sets_para_vencer,
        estrategista=True,
    )


def simular_tiebreak(
    jogador,
    adversario,
    estrategia,
    sacador_inicial: str,
    placar_partida: tuple,
    simulador: SimuladorPonto,
    contexto_partida: ContextoPartida,
    stats_j: EstatisticasPartida,
    stats_a: EstatisticasPartida,
    alvo_pontos: int,
    silencioso: bool = False,
    detalhado: bool = False,
    sets_para_vencer: int = 2,
    estrategia_adversario: dict = None,
):
    pontos = {"j": 0, "a": 0}
    historico = []
    nome_j = _nome_entidade(jogador, "Jogador")
    nome_a = _nome_entidade(adversario, "Adversário")

    while True:
        idx = pontos["j"] + pontos["a"]
        sacador = _sacador_tiebreak(sacador_inicial, idx)
        contexto = ContextoPonto(
            sacador=sacador,
            placar_game=(pontos["j"], pontos["a"]),
            placar_set=(6, 6),
            placar_partida=placar_partida,
            sets_para_vencer=sets_para_vencer,
            is_tiebreak=True,
            tiebreak_alvo=alvo_pontos,
        )

        if detalhado:
            vencedor, descricoes, stats_info = simulador.simular_ponto_detalhado(
                estrategia, contexto, None, contexto_partida, estrategia_adversario
            )
            for desc in descricoes:
                if not silencioso:
                    logger.debug(desc)
        else:
            vencedor, stats_info = simulador.simular_ponto_rapido(
                estrategia, contexto, contexto_partida, estrategia_adversario
            )

        historico.append(vencedor)
        _aplicar_custo_stamina(
            contexto_partida,
            stats_info,
            jogador,
            adversario,
            estrategia,
            estrategia_adversario,
            contexto,
        )
        _atualizar_momentum(contexto_partida, contexto, vencedor)

        if stats_j is not None and stats_a is not None:
            atualizar_estatisticas(stats_j, stats_a, vencedor, stats_info, contexto)

        pontos[vencedor] += 1
        if not silencioso:
            logger.debug(f"Tiebreak: {nome_j} {pontos['j']} x {pontos['a']} {nome_a}")

        if (pontos["j"] >= alvo_pontos or pontos["a"] >= alvo_pontos) and abs(
            pontos["j"] - pontos["a"]
        ) >= 2:
            return ("j" if pontos["j"] > pontos["a"] else "a"), historico, False


def simular_resto_do_set(
    jogador,
    adversario,
    games: dict,
    sacador_atual: str,
    estrategias: dict,
    stats_j: EstatisticasPartida,
    stats_a: EstatisticasPartida,
    placar_partida: tuple,
    simulador: SimuladorPonto,
    contexto_partida: ContextoPartida,
    config: ConfigPartida,
    sets_para_vencer: int,
    estrategia_adversario: dict,
):
    """Simula todos os games restantes do set atual no modo rápido.

    Returns:
        (games, sacador_atual, stats_j, stats_a)
    """
    logger.debug("\nSimulando resto do set...")
    nome_j = _nome_entidade(jogador, "Jogador")
    nome_a = _nome_entidade(adversario, "Adversário")

    while True:
        placar_set = (games["j"], games["a"])

        vencedor, _historico, _ = simular_game_rapido(
            jogador,
            adversario,
            estrategias,
            sacador_atual,
            placar_set,
            placar_partida,
            simulador,
            contexto_partida,
            estrategia_adversario,
            stats_j,
            stats_a,
            silencioso=True,
        )

        games[vencedor] += 1
        _recuperar_stamina_entre_games(contexto_partida, jogador, adversario)
        sacador_atual = "a" if sacador_atual == "j" else "j"

        logger.debug(f"  {nome_j} {games['j']} x {games['a']} {nome_a}")

        if (games["j"] >= 6 or games["a"] >= 6) and abs(games["j"] - games["a"]) >= 2:
            break

        if games["j"] == 6 and games["a"] == 6:
            logger.debug("  Tiebreak!")
            sets_dict = {"j": placar_partida[0], "a": placar_partida[1]}
            alvo = _alvo_tiebreak(sets_dict, sets_para_vencer, config)
            vencedor_tb, _, _ = simular_tiebreak(
                jogador,
                adversario,
                estrategias,
                sacador_atual,
                placar_partida,
                simulador,
                contexto_partida,
                stats_j,
                stats_a,
                alvo,
                silencioso=True,
                sets_para_vencer=sets_para_vencer,
                estrategia_adversario=estrategia_adversario,
            )
            games[vencedor_tb] += 1
            _recuperar_stamina_entre_games(contexto_partida, jogador, adversario)
            sacador_atual = "a" if sacador_atual == "j" else "j"
            logger.debug(f"  Tiebreak: {nome_j} {games['j']} x {games['a']} {nome_a}")
            break

    logger.debug("Simulacao do set concluida!")
    return games, sacador_atual, stats_j, stats_a
