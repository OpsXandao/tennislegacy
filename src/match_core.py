from __future__ import annotations

from src.utils.entidade_utils import obter_atributos, obter_atributos_psicologicos
from src.match_config import _nome_entidade
from src.constants.match_constants import EstrategiaSaque, IntencaoPonto, TipoSaque
from src.match_dynamics import (
    aplicar_custo_stamina_contextual,
    atualizar_momentum_contextual,
    calcular_stamina_pos_recuperacao,
)
from src.match_state import ContextoPartida, ContextoPonto, EstatisticasPartida
from src.services.simulador_ponto import SimuladorPonto
from src.utils.superficie_utils import normalizar_superficie


def atualizar_estatisticas(
    stats_j: EstatisticasPartida,
    stats_a: EstatisticasPartida,
    vencedor: str,
    stats_info: dict,
    contexto: ContextoPonto,
):
    """Atualiza estatísticas baseado no resultado do ponto."""
    sacador = stats_info.get("sacador", contexto.sacador)

    stats_sacador = stats_j if sacador == "j" else stats_a

    stats_sacador.primeiro_saque_total += 1
    if stats_info.get("primeiro_saque_in"):
        stats_sacador.primeiro_saque_in += 1

    if stats_info.get("ace"):
        stats_sacador.aces += 1
    if stats_info.get("dupla_falta"):
        stats_sacador.duplas_faltas += 1

    if vencedor == "j":
        if stats_info.get("winner"):
            stats_j.winners += 1
        if stats_info.get("erro_nao_forcado"):
            stats_a.erros_nao_forcados += 1
    else:
        if stats_info.get("winner"):
            stats_a.winners += 1
        if stats_info.get("erro_nao_forcado"):
            stats_j.erros_nao_forcados += 1

    if sacador == "j":
        stats_j.pontos_total_saque += 1
        stats_a.pontos_total_devolucao += 1
        if vencedor == "j":
            stats_j.pontos_ganhos_saque += 1
        else:
            stats_a.pontos_ganhos_devolucao += 1
    else:
        stats_a.pontos_total_saque += 1
        stats_j.pontos_total_devolucao += 1
        if vencedor == "a":
            stats_a.pontos_ganhos_saque += 1
        else:
            stats_j.pontos_ganhos_devolucao += 1

    if contexto.is_break_point():
        if sacador == "j":
            stats_a.break_points_total += 1
            stats_j.break_points_enfrentados += 1
            if vencedor == "a":
                stats_a.break_points_convertidos += 1
            else:
                stats_j.break_points_salvos += 1
        else:
            stats_j.break_points_total += 1
            stats_a.break_points_enfrentados += 1
            if vencedor == "j":
                stats_j.break_points_convertidos += 1
            else:
                stats_a.break_points_salvos += 1

    intensidade = str(stats_info.get("intensidade", "")).strip().lower()
    if intensidade == "curto":
        stats_j.rallies_curtos += 1
        stats_a.rallies_curtos += 1
    elif intensidade == "medio":
        stats_j.rallies_medios += 1
        stats_a.rallies_medios += 1
    elif intensidade in {"longo", "muito_longo"}:
        stats_j.rallies_longos += 1
        stats_a.rallies_longos += 1


def _definir_estrategia_auto(jogador, superficie: str) -> dict:
    atributos = obter_atributos(jogador)
    psico = obter_atributos_psicologicos(jogador)
    vel_saque = atributos.get("vel_saque", 50)
    voleio = atributos.get("voleio", 50)
    slice_ = atributos.get("slice", 50)
    forehand = atributos.get("forehand", 50)
    backhand = atributos.get("backhand", 50)
    topspin = atributos.get("topspin", 50)
    velocidade = atributos.get("velocidade", 50)
    winner = atributos.get("winner", 50)
    agressividade = psico.get("agressividade", 50)
    leitura = psico.get("leitura_de_jogo", 50)
    determinacao = psico.get("determinacao", 50)

    superficie = normalizar_superficie(superficie)
    rede_score = vel_saque * 0.4 + voleio * 0.4 + slice_ * 0.2
    fundo_score = forehand * 0.35 + backhand * 0.35 + topspin * 0.3
    variado_score = velocidade * 0.4 + winner * 0.3 + vel_saque * 0.3

    if superficie == "grama":
        rede_score *= 1.1
    elif superficie == "saibro":
        fundo_score *= 1.1

    if rede_score >= fundo_score and rede_score >= variado_score:
        estilo = "atacar_na_rede"
    elif fundo_score >= variado_score:
        estilo = "atacar_do_fundo"
    else:
        estilo = "atacar_pelo_meio"

    intencao = IntencaoPonto.PACIENTE
    if agressividade >= 68 or winner >= 74:
        intencao = IntencaoPonto.ARRISCAR
    elif leitura >= 68 and velocidade >= 66:
        intencao = IntencaoPonto.DEFENSIVO

    saque_tipo = TipoSaque.VARIADO
    if vel_saque >= 74 and agressividade >= 62:
        saque_tipo = TipoSaque.AGRESSIVO
    elif determinacao < 45 or vel_saque < 48:
        saque_tipo = TipoSaque.SEGURO

    segundo_saque = (
        EstrategiaSaque.FORCAR
        if agressividade >= 66 and vel_saque >= 70
        else EstrategiaSaque.SEGURO
    )

    return {
        "estilo": estilo,
        "intencao": intencao,
        "saque_tipo": saque_tipo,
        "saque": segundo_saque,
    }


def _atualizar_momentum(
    contexto_partida: ContextoPartida, contexto: ContextoPonto, vencedor: str
):
    pj, pa = contexto.placar_game
    (
        contexto_partida.momentum_j,
        contexto_partida.momentum_a,
        contexto_partida.sequencia_j,
        contexto_partida.sequencia_a,
        contexto_partida.ultimo_vencedor,
    ) = atualizar_momentum_contextual(
        contexto_partida.momentum_j,
        contexto_partida.momentum_a,
        contexto_partida.sequencia_j,
        contexto_partida.sequencia_a,
        contexto_partida.ultimo_vencedor,
        vencedor=vencedor,
        is_match_point=contexto.is_match_point(),
        is_set_point=contexto.is_set_point(),
        is_break_point=contexto.is_break_point(),
        is_tiebreak=contexto.is_tiebreak,
        jogador_perdendo=contexto.jogador_perdendo(),
        adversario_perdendo=contexto.adversario_perdendo(),
        pj=pj,
        pa=pa,
    )


def _aplicar_custo_stamina(
    contexto_partida: ContextoPartida,
    stats_info: dict,
    jogador,
    adversario,
    estrategia: dict,
    estrategia_adversario: dict,
    contexto: ContextoPonto | None = None,
):
    atributos_j = obter_atributos(jogador)
    atributos_a = obter_atributos(adversario)
    psico_j = obter_atributos_psicologicos(jogador)
    psico_a = obter_atributos_psicologicos(adversario)
    contexto_flags = {
        "is_break_point": bool(contexto and contexto.is_break_point()),
        "is_set_point": bool(contexto and contexto.is_set_point()),
        "is_match_point": bool(contexto and contexto.is_match_point()),
    }
    contexto_partida.stamina_j, contexto_partida.stamina_a = (
        aplicar_custo_stamina_contextual(
            contexto_partida.stamina_j,
            contexto_partida.stamina_a,
            stats_info=stats_info,
            superficie=contexto_partida.superficie,
            clima=contexto_partida.clima,
            umidade=contexto_partida.umidade,
            contexto_flags=contexto_flags,
            atributos_j=atributos_j,
            atributos_a=atributos_a,
            psico_j=psico_j,
            psico_a=psico_a,
            estrategia_j=estrategia,
            estrategia_a=estrategia_adversario,
        )
    )


def _tem_fisioterapeuta(entidade) -> bool:
    """Verifica se a entidade tem fisioterapeuta ativo na equipe."""
    from src.management import obter_profissional_da_equipe

    equipe = (
        entidade.get("equipe", [])
        if isinstance(entidade, dict)
        else getattr(entidade, "equipe", [])
    )
    return obter_profissional_da_equipe(equipe or [], "fisioterapeuta") is not None


def _recuperar_stamina_entre_games(
    contexto_partida: ContextoPartida,
    jogador,
    adversario,
    tipo: str = "game",
):
    fisico_j = obter_atributos(jogador).get("resistencia", 50)
    fisico_a = obter_atributos(adversario).get("resistencia", 50)
    tem_fisio_j = _tem_fisioterapeuta(jogador)
    tem_fisio_a = _tem_fisioterapeuta(adversario)
    contexto_partida.stamina_j = calcular_stamina_pos_recuperacao(
        contexto_partida.stamina_j,
        fisico=fisico_j,
        indoor=contexto_partida.indoor,
        clima=contexto_partida.clima,
        umidade=contexto_partida.umidade,
        tipo=tipo,
        tem_fisioterapeuta=tem_fisio_j,
    )
    contexto_partida.stamina_a = calcular_stamina_pos_recuperacao(
        contexto_partida.stamina_a,
        fisico=fisico_a,
        indoor=contexto_partida.indoor,
        clima=contexto_partida.clima,
        umidade=contexto_partida.umidade,
        tipo=tipo,
        tem_fisioterapeuta=tem_fisio_a,
    )


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
    stats_j: EstatisticasPartida | None = None,
    stats_a: EstatisticasPartida | None = None,
    silencioso: bool = False,
    sets_para_vencer: int = 2,
    placar_pontos_fn=None,
    log_fn=None,
):
    """Simula um game completo no modo rápido."""
    pontos = {"j": 0, "a": 0}
    historico = []
    nome_j = _nome_entidade(jogador, "Jogador")
    nome_a = _nome_entidade(adversario, "Adversário")
    placar_pontos_fn = placar_pontos_fn or str
    log_fn = log_fn or (lambda *_args, **_kwargs: None)

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
        if pontos[vencedor] >= 4 and abs(pontos["j"] - pontos["a"]) >= 2:
            return vencedor, historico, False

        if not silencioso:
            if pontos["j"] >= 3 and pontos["a"] >= 3:
                if pontos["j"] == pontos["a"]:
                    log_fn("Deuce!")
                else:
                    nome_vantagem = nome_j if pontos["j"] > pontos["a"] else nome_a
                    log_fn(f"Advantage {nome_vantagem}")
            else:
                log_fn(
                    f"Placar: {nome_j} {placar_pontos_fn(pontos['j'])} x {placar_pontos_fn(pontos['a'])} {nome_a}"
                )
