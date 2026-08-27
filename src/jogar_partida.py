import logging
import random
import time
from typing import Optional

from src.constants.match_constants import (
    ModoSimulacao,
    TipoSaque,
    EstrategiaSaque,
    IntencaoPonto,
)
from src.match_state import ContextoPartida, ContextoPonto, EstatisticasPartida
from src.services.simulador_ponto import SimuladorPonto
from src.utils.superficie_utils import normalizar_superficie
from src.utils.entidade_utils import (
    obter_atributos,
    obter_atributos_psicologicos,
)
from src.match_config import (
    ConfigPartida,
    criar_config_partida,
    _nome_entidade,
)  # noqa: F401
from src.jogador import obter_bonus_rivalidade
from src.player_ratings import aplicar_bonus_carta
from src.match_dynamics import (
    normalizar_energia_pos_partida as core_normalizar_energia_pos_partida,
)
from src.match_physics import (
    aplicar_impacto_moral_por_sets as _core_aplicar_impacto_moral_por_sets,
    aplicar_impacto_mental_set_em_andamento as _core_aplicar_impacto_mental_set_em_andamento,
    aplicar_impacto_moral_por_resultado_ranking as _core_aplicar_impacto_moral_por_resultado_ranking,
)
from src.match_core import (
    _aplicar_custo_stamina as core_aplicar_custo_stamina,
    _atualizar_momentum as core_atualizar_momentum,
    _recuperar_stamina_entre_games as core_recuperar_stamina_entre_games,
    atualizar_estatisticas as core_atualizar_estatisticas,
    _definir_estrategia_auto as core_definir_estrategia_auto,
    simular_game_rapido as core_simular_game_rapido,
)

# Re-exports de sub-módulos extraídos
from src.match_strategy import (
    ajustar_estrategia_entre_sets as _ajustar_estrategia_entre_sets,
)  # noqa: F401
from src.match_game_sim import (  # noqa: F401
    simular_game_detalhado,
    simular_game_estrategista,
    simular_tiebreak,
    simular_resto_do_set,
    _sacador_tiebreak,
    _alvo_tiebreak,
    _placar_pontos_txt,
)

logger = logging.getLogger(__name__)

_ESTRATEGIA_PADRAO = {
    "estilo": "atacar_do_fundo",
    "saque": "seguro",
    "saque_tipo": "variado",
    "intencao": "paciente",
}


def escolher_modo_simulacao():
    return ModoSimulacao.AUTO


def escolher_estrategias():
    return dict(_ESTRATEGIA_PADRAO)


def escolher_intencao_ponto():
    return "EQUILIBRADO"


def verificar_abandono():
    return False


def atualizar_estatisticas(
    stats_j: EstatisticasPartida,
    stats_a: EstatisticasPartida,
    vencedor: str,
    stats_info: dict,
    contexto: ContextoPonto,
):
    return core_atualizar_estatisticas(stats_j, stats_a, vencedor, stats_info, contexto)


def show_pause_menu(*_args, **_kwargs):
    return None


def exibir_estatisticas_set(*_args, **_kwargs):
    return None


_PLACAR_TXT = {0: "0", 1: "15", 2: "30", 3: "40"}


def _atualizar_momentum(
    contexto_partida: ContextoPartida, contexto: ContextoPonto, vencedor: str
):
    return core_atualizar_momentum(contexto_partida, contexto, vencedor)


def _get_atributos_entidade(entidade) -> dict:
    return obter_atributos(entidade)


def _aplicar_custo_stamina(
    contexto_partida: ContextoPartida,
    stats_info: dict,
    jogador,
    adversario,
    estrategia: dict,
    estrategia_adversario: dict,
    contexto: ContextoPonto = None,
):
    return core_aplicar_custo_stamina(
        contexto_partida,
        stats_info,
        jogador,
        adversario,
        estrategia,
        estrategia_adversario,
        contexto,
    )


def _recuperar_stamina_entre_games(
    contexto_partida: ContextoPartida, jogador, adversario
):
    return core_recuperar_stamina_entre_games(contexto_partida, jogador, adversario)


def _normalizar_energia_pos_partida(
    stamina_final: float,
    fisico: int,
    pontos_disputados: int,
    superficie: str = "dura",
    energia_inicial: float | None = None,
) -> int:
    return core_normalizar_energia_pos_partida(
        stamina_final,
        fisico,
        pontos_disputados,
        superficie=superficie,
        energia_inicial=energia_inicial,
    )


def _aplicar_impacto_moral_por_sets(jogador, resultado_sets, venceu_partida: bool):
    _core_aplicar_impacto_moral_por_sets(jogador, resultado_sets, venceu_partida)


def _aplicar_impacto_mental_set_em_andamento(
    contexto_partida: ContextoPartida, games_j: int, games_a: int
):
    """Aplica impacto psicológico imediato no momentum após cada set."""
    _core_aplicar_impacto_mental_set_em_andamento(contexto_partida, games_j, games_a)


def _aplicar_impacto_moral_por_resultado_ranking(
    jogador, adversario, venceu_partida: bool
):
    _core_aplicar_impacto_moral_por_resultado_ranking(
        jogador, adversario, venceu_partida
    )


def _exibir_tela_pre_partida(*_args, **_kwargs):
    return None


def _exibir_cabecalho_game(*_args, **_kwargs):
    return None


def _definir_estrategia_auto(jogador, superficie: str) -> dict:
    return core_definir_estrategia_auto(jogador, superficie)


def _pct(numerador: int, denominador: int) -> float:
    if denominador <= 0:
        return 0.0
    return (numerador / denominador) * 100.0


def simular_game_rapido(
    jogador,
    adversario,
    estrategia,
    sacador,
    placar_set,
    placar_partida,
    simulador: SimuladorPonto,
    contexto_partida: ContextoPartida,
    estrategia_adversario: dict,
    stats_j: EstatisticasPartida = None,
    stats_a: EstatisticasPartida = None,
    silencioso: bool = False,
    sets_para_vencer: int = 2,
):
    return core_simular_game_rapido(
        jogador,
        adversario,
        estrategia,
        sacador,
        placar_set,
        placar_partida,
        simulador,
        contexto_partida,
        estrategia_adversario,
        stats_j=stats_j,
        stats_a=stats_a,
        silencioso=silencioso,
        sets_para_vencer=sets_para_vencer,
        placar_pontos_fn=_placar_pontos_txt,
        log_fn=logger.debug,
    )


def jogar_partida(
    jogador,
    adversario,
    nome_save,
    config: Optional[ConfigPartida] = None,
    adiar_progressao_natural: bool = False,
):
    config = config or ConfigPartida()
    config.superficie = normalizar_superficie(config.superficie)
    sets_para_vencer = config.melhor_de // 2 + 1
    nome_j = _nome_entidade(jogador, "Jogador")
    nome_a = _nome_entidade(adversario, "Adversário")

    # --- Bônus de carta EA FC -------------------------------------------
    # Aplica temporariamente os bônus da carta de cada jogador nos atributos.
    # Para o adversario (dict) fazemos uma cópia do dict antes de modificar.
    # Para o jogador (Jogador) salvamos os originais e restauramos após a partida.
    modalidade = getattr(config, "modalidade", "simples")

    pos_a = int(
        (adversario.get("ranking_pos") or adversario.get("posicao", 9999))
        if isinstance(adversario, dict)
        else 9999
    )
    adv_dict_orig = adversario if isinstance(adversario, dict) else None
    if adv_dict_orig is not None:
        adversario = aplicar_bonus_carta(adv_dict_orig, pos_a, modalidade)

    _atributos_j_orig = dict(jogador.atributos)
    _psico_j_orig = dict(jogador.atributos_psicologicos)
    j_boosted = aplicar_bonus_carta(jogador.to_dict(), 9999, modalidade)
    jogador.atributos.update(j_boosted.get("atributos", {}))
    jogador.atributos_psicologicos.update(j_boosted.get("atributos_psicologicos", {}))
    jogador._overall_cache = None
    # --------------------------------------------------------------------

    _exibir_tela_pre_partida(jogador, adversario, config)

    modo = escolher_modo_simulacao()
    modo_ref = {"modo": modo}
    estrategias = escolher_estrategias()
    estrategia_adversario = _definir_estrategia_auto(adversario, config.superficie)

    sets = {"j": 0, "a": 0}
    resultado = []

    stats_total_j = EstatisticasPartida()
    stats_total_a = EstatisticasPartida()

    sacador_inicial = random.choice(["j", "a"])
    sacador_atual = sacador_inicial

    stamina_inicial = getattr(jogador, "energia", 100)
    stamina_adv = (
        float(adversario.get("energia") or 100)
        if isinstance(adversario, dict)
        else 100.0
    )
    contexto_partida = ContextoPartida(
        superficie=config.superficie,
        stamina_j=float(stamina_inicial),
        stamina_a=stamina_adv,
        moral_j=float(getattr(jogador, "moral", 70)),
        moral_a=float(
            adversario.get("moral", 70) if isinstance(adversario, dict) else 70.0
        ),
        ritmo_j=float(getattr(jogador, "ritmo_jogo", 50)),
        ritmo_a=float(
            adversario.get("ritmo_jogo", 50) if isinstance(adversario, dict) else 50.0
        ),
        clima=config.clima,
        vento=config.vento,
        umidade=config.umidade,
        altitude_m=config.altitude_m,
        indoor=config.indoor,
    )
    bonus_rival = obter_bonus_rivalidade(jogador, nome_a)
    if bonus_rival.get("ativa"):
        contexto_partida.moral_j = min(
            100.0, contexto_partida.moral_j + bonus_rival["bonus_mental"]
        )
        contexto_partida.momentum_j = min(
            6, contexto_partida.momentum_j + bonus_rival["bonus_momentum"]
        )
    simulador = SimuladorPonto(jogador, adversario)

    while sets["j"] < sets_para_vencer and sets["a"] < sets_para_vencer:
        games = {"j": 0, "a": 0}
        stamina_ref_j = contexto_partida.stamina_j
        stamina_ref_a = contexto_partida.stamina_a

        stats_set_j = EstatisticasPartida()
        stats_set_a = EstatisticasPartida()

        while True:
            _exibir_cabecalho_game(
                jogador,
                adversario,
                games,
                sets,
                sacador_atual,
                config,
                contexto_partida,
                modo_ref["modo"],
                resultado_sets=resultado,
                stamina_ref_j=stamina_ref_j,
                stamina_ref_a=stamina_ref_a,
            )

            placar_set = (games["j"], games["a"])
            placar_partida = (sets["j"], sets["a"])

            if modo_ref["modo"] == ModoSimulacao.ESTRATEGISTA:
                vencedor, historico, abandonou = simular_game_estrategista(
                    jogador,
                    adversario,
                    estrategias,
                    sacador_atual,
                    placar_set,
                    placar_partida,
                    simulador,
                    contexto_partida,
                    estrategia_adversario,
                    modo_ref,
                    stats_set_j,
                    stats_set_a,
                    sets_para_vencer=sets_para_vencer,
                )
            elif modo_ref["modo"] == ModoSimulacao.DETALHADO:
                vencedor, historico, abandonou = simular_game_detalhado(
                    jogador,
                    adversario,
                    estrategias,
                    sacador_atual,
                    placar_set,
                    placar_partida,
                    simulador,
                    contexto_partida,
                    estrategia_adversario,
                    modo_ref,
                    stats_set_j,
                    stats_set_a,
                    sets_para_vencer=sets_para_vencer,
                )
            else:
                vencedor, historico, abandonou = simular_game_rapido(
                    jogador,
                    adversario,
                    estrategias,
                    sacador_atual,
                    placar_set,
                    placar_partida,
                    simulador,
                    contexto_partida,
                    estrategia_adversario,
                    stats_set_j,
                    stats_set_a,
                    sets_para_vencer=sets_para_vencer,
                )

            if abandonou:
                logger.debug(f"\n{nome_j} abandonou a partida!")
                logger.debug(f"Vitoria por W.O. para {nome_a}")
                return nome_a, f"{nome_a} venceu por W.O.", 0

            games[vencedor] += 1
            _recuperar_stamina_entre_games(contexto_partida, jogador, adversario)
            sacador_atual = "a" if sacador_atual == "j" else "j"

            if modo_ref["modo"] != ModoSimulacao.DETALHADO:
                start_time = time.time()
                while time.time() - start_time < 0.8:
                    if False:
                        tecla = "".lower()
                        if tecla == "m":
                            modo_ref["modo"] = (
                                ModoSimulacao.DETALHADO
                                if modo_ref["modo"] == ModoSimulacao.RAPIDO
                                else ModoSimulacao.RAPIDO
                            )
                        break
                    time.sleep(0.05)

            if (games["j"] >= 6 or games["a"] >= 6) and abs(
                games["j"] - games["a"]
            ) >= 2:
                break

            if games["j"] == 6 and games["a"] == 6:
                alvo_tb = _alvo_tiebreak(sets, sets_para_vencer, config)
                logger.debug(f"\nTIEBREAK (ate {alvo_tb})!")
                vencedor_tb, _, abandonou = simular_tiebreak(
                    jogador,
                    adversario,
                    estrategias,
                    sacador_atual,
                    (sets["j"], sets["a"]),
                    simulador,
                    contexto_partida,
                    stats_set_j,
                    stats_set_a,
                    alvo_tb,
                    silencioso=False,
                    detalhado=(modo_ref["modo"] == ModoSimulacao.DETALHADO),
                    sets_para_vencer=sets_para_vencer,
                    estrategia_adversario=estrategia_adversario,
                )

                if abandonou:
                    logger.debug(f"\n{nome_j} abandonou a partida!")
                    logger.debug(f"Vitoria por W.O. para {nome_a}")
                    return nome_a, f"{nome_a} venceu por W.O.", 0

                games[vencedor_tb] += 1
                _recuperar_stamina_entre_games(contexto_partida, jogador, adversario)
                sacador_atual = "a" if sacador_atual == "j" else "j"
                break

        winner = "j" if games["j"] > games["a"] else "a"
        sets[winner] += 1
        resultado.append((games["j"], games["a"]))
        _aplicar_impacto_mental_set_em_andamento(
            contexto_partida, games["j"], games["a"]
        )

        stamina_fim_j = contexto_partida.stamina_j
        stamina_fim_a = contexto_partida.stamina_a
        partida_continua = sets["j"] < sets_para_vencer and sets["a"] < sets_para_vencer
        if partida_continua:
            # Pausa entre sets: 2× recuperação (~90 s de descanso, como em partidas reais)
            _recuperar_stamina_entre_games(contexto_partida, jogador, adversario)
            _recuperar_stamina_entre_games(contexto_partida, jogador, adversario)

        exibir_estatisticas_set(
            jogador,
            adversario,
            games["j"],
            games["a"],
            stats_set_j,
            stats_set_a,
            len(resultado),
            stamina_fim_j=stamina_fim_j,
            stamina_fim_a=stamina_fim_a,
            stamina_pos_j=contexto_partida.stamina_j if partida_continua else None,
            stamina_pos_a=contexto_partida.stamina_a if partida_continua else None,
        )

        estrategias, dicas_ajuste = _ajustar_estrategia_entre_sets(
            estrategias, stats_set_j, stats_set_a, config.superficie, is_jogador=True
        )
        estrategia_adversario, _ = _ajustar_estrategia_entre_sets(
            estrategia_adversario,
            stats_set_a,
            stats_set_j,
            config.superficie,
            is_jogador=False,
        )
        if dicas_ajuste:
            logger.debug("\nAjustes táticos sugeridos/aplicados para o próximo set:")
            for dica in dicas_ajuste:
                logger.debug(f" - {dica}")

        if partida_continua:
            logger.debug(f"\n{'='*54}")
            logger.debug("  [c] Continuar")
            logger.debug("  [e] Mudar estratégia")
            logger.debug(f"{'='*54}")
            escolha = ""  # CLI removed
            if escolha == "e":
                estrategias = escolher_estrategias()
        else:
            None  # CLI removed

        stats_total_j.merge(stats_set_j)
        stats_total_a.merge(stats_set_a)

    vencedor_final = nome_j if sets["j"] > sets["a"] else nome_a
    perdedor_final = nome_a if vencedor_final == nome_j else nome_j
    placar_sets = "  ".join(f"{sj}-{sa}" for sj, sa in resultado)
    placar_final = f"{vencedor_final} {max(sets['j'], sets['a'])} x {min(sets['j'], sets['a'])} {perdedor_final}"

    None
    linha = "=" * 54
    logger.debug(f"\n{linha}")
    logger.debug(f"{'PARTIDA FINALIZADA':^54}")
    logger.debug(f"{linha}")
    logger.debug()
    if vencedor_final == nome_j:
        logger.debug("  🏆  VITÓRIA!")
    else:
        logger.debug("  😔  Derrota")
    logger.debug(f"\n  {nome_j}  vs  {nome_a}")
    logger.debug(f"  {placar_sets}")
    logger.debug()
    logger.debug(f"{linha}")
    logger.debug(f"{'ESTATÍSTICAS DA PARTIDA':^54}")
    logger.debug(f"{linha}")
    logger.debug(stats_total_j.exibir(nome_j, nome_a, stats_total_a))

    pontos_disputados = (
        stats_total_j.pontos_total_saque + stats_total_j.pontos_total_devolucao
    )
    total_games = max(1, sum((sj + sa) for sj, sa in resultado))
    pontos_por_game = pontos_disputados / total_games
    total_rallies = (
        stats_total_j.rallies_curtos
        + stats_total_j.rallies_medios
        + stats_total_j.rallies_longos
    )
    if total_rallies > 0:
        rally_longo_pct = stats_total_j.rallies_longos / total_rallies
        rally_medio_pct = stats_total_j.rallies_medios / total_rallies
    else:
        rally_longo_pct = 0.0
        rally_medio_pct = 0.0

    config.fatores_fadiga_match = {
        "pontos_por_game": round(pontos_por_game, 3),
        "rally_longo_pct": round(rally_longo_pct, 4),
        "rally_medio_pct": round(rally_medio_pct, 4),
    }

    fisico_j = _get_atributos_entidade(jogador).get("fisico", 50)
    energia_final_j = _normalizar_energia_pos_partida(
        contexto_partida.stamina_j,
        fisico_j,
        pontos_disputados,
        superficie=config.superficie,
        energia_inicial=stamina_inicial,
    )
    if hasattr(jogador, "energia"):
        jogador.energia = energia_final_j
    elif isinstance(jogador, dict):
        jogador["energia"] = energia_final_j

    fisico_a = _get_atributos_entidade(adversario).get("fisico", 50)
    energia_final_a = _normalizar_energia_pos_partida(
        contexto_partida.stamina_a,
        fisico_a,
        pontos_disputados,
        superficie=config.superficie,
        energia_inicial=stamina_adv,
    )
    if isinstance(adversario, dict):
        adversario["energia"] = energia_final_a

    # Progressão natural baseada no uso real de atributos
    # Duplas: jogador é um dict fundido — progressão não se aplica aqui
    _eh_dupla = isinstance(jogador, dict) and jogador.get("is_dupla")
    if adiar_progressao_natural:
        if not _eh_dupla:
            from src.progressao import calcular_progressao_natural

            melhorias_pendentes = calcular_progressao_natural(
                jogador, stats_total_j, estrategias, pontos_disputados
            )
            setattr(
                jogador, "_melhorias_naturais_pendentes_partida", melhorias_pendentes
            )
            if melhorias_pendentes:
                logger.debug(
                    "\n📌 Progressão natural registrada para aplicar após o torneio."
                )
    else:
        from src.progressao import handle_progressao_natural

        melhorias = (
            handle_progressao_natural(
                jogador, stats_total_j, estrategias, pontos_disputados
            )
            if not _eh_dupla
            else {}
        )
        if melhorias:
            logger.debug(f"\n{linha}")
            logger.debug(f"{'📈  PROGRESSÃO NATURAL':^54}")
            logger.debug(f"{linha}")
            for attr, novo_val in melhorias.items():
                logger.debug(f"  +1 {attr:<12} → {novo_val}")
            logger.debug(f"{linha}")

    _aplicar_impacto_moral_por_sets(jogador, resultado, vencedor_final == nome_j)
    _aplicar_impacto_moral_por_resultado_ranking(
        jogador, adversario, vencedor_final == nome_j
    )

    # --- Restaurar atributos originais do jogador (desfaz bônus de carta) ---
    jogador.atributos = _atributos_j_orig
    jogador.atributos_psicologicos = _psico_j_orig
    jogador._overall_cache = None
    # -------------------------------------------------------------------------

    return vencedor_final, placar_final, pontos_disputados


def simular_partida_npc(
    jogador_a: dict, jogador_b: dict, config: Optional[ConfigPartida] = None
):
    config = config or ConfigPartida()
    config.superficie = normalizar_superficie(config.superficie)
    sets_para_vencer = config.melhor_de // 2 + 1

    estrategia_a = _definir_estrategia_auto(jogador_a, config.superficie)
    estrategia_b = _definir_estrategia_auto(jogador_b, config.superficie)

    simulador = SimuladorPonto(jogador_a, jogador_b)
    contexto_partida = ContextoPartida(
        superficie=config.superficie,
        stamina_j=100.0,
        stamina_a=100.0,
        moral_j=float(jogador_a.get("moral", 70)),
        moral_a=float(jogador_b.get("moral", 70)),
        ritmo_j=float(jogador_a.get("ritmo_jogo", 50)),
        ritmo_a=float(jogador_b.get("ritmo_jogo", 50)),
        clima=config.clima,
        vento=config.vento,
        umidade=config.umidade,
        altitude_m=config.altitude_m,
        indoor=config.indoor,
    )

    sets = {"j": 0, "a": 0}
    sacador_atual = random.choice(["j", "a"])

    while sets["j"] < sets_para_vencer and sets["a"] < sets_para_vencer:
        games = {"j": 0, "a": 0}
        stats_set_j = EstatisticasPartida()
        stats_set_a = EstatisticasPartida()

        while True:
            vencedor, _, _ = simular_game_rapido(
                jogador_a,
                jogador_b,
                estrategia_a,
                sacador_atual,
                (games["j"], games["a"]),
                (sets["j"], sets["a"]),
                simulador,
                contexto_partida,
                estrategia_b,
                stats_set_j,
                stats_set_a,
                silencioso=True,
                sets_para_vencer=sets_para_vencer,
            )
            games[vencedor] += 1
            _recuperar_stamina_entre_games(contexto_partida, jogador_a, jogador_b)
            sacador_atual = "a" if sacador_atual == "j" else "j"

            if (games["j"] >= 6 or games["a"] >= 6) and abs(
                games["j"] - games["a"]
            ) >= 2:
                break

            if games["j"] == 6 and games["a"] == 6:
                alvo_tb = _alvo_tiebreak(sets, sets_para_vencer, config)
                vencedor_tb, _, _ = simular_tiebreak(
                    jogador_a,
                    jogador_b,
                    estrategia_a,
                    sacador_atual,
                    (sets["j"], sets["a"]),
                    simulador,
                    contexto_partida,
                    stats_set_j,
                    stats_set_a,
                    alvo_tb,
                    silencioso=True,
                    detalhado=False,
                    sets_para_vencer=sets_para_vencer,
                    estrategia_adversario=estrategia_b,
                )
                games[vencedor_tb] += 1
                _recuperar_stamina_entre_games(contexto_partida, jogador_a, jogador_b)
                sacador_atual = "a" if sacador_atual == "j" else "j"
                break

        winner = "j" if games["j"] > games["a"] else "a"
        sets[winner] += 1

    vencedor_final = jogador_a if sets["j"] > sets["a"] else jogador_b
    perdedor_final = jogador_b if vencedor_final == jogador_a else jogador_a

    def limpar_nome(nome):
        return nome.strip().rstrip("0123456789").strip()

    nome_vencedor = limpar_nome(vencedor_final["nome"])
    nome_perdedor = limpar_nome(perdedor_final["nome"])
    placar_final = f"{nome_vencedor} {max(sets['j'], sets['a'])} x {min(sets['j'], sets['a'])} {nome_perdedor}"

    return vencedor_final, perdedor_final, placar_final
