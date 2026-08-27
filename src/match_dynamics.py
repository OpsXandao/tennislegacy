from src.utils.math_utils import clamp
from src.utils.superficie_utils import normalizar_superficie
from src.fadiga import (
    calcular_recuperacao_energia,
    calcular_penalidade_energia,
    calcular_condicao_pre_partida,
    calcular_multiplicador_condicao,
)

STAMINA_CUSTO_BASE = {
    "curto": 0.5,
    "medio": 1.0,
    "longo": 1.6,
    "muito_longo": 2.5,
}

SUPERFICIE_FADIGA = {
    "dura": 1.0,
    "saibro": 1.12,
    "grama": 0.9,
}

ESTILO_FADIGA_SUPERFICIE = {
    "dura": {
        "atacar_do_fundo": 1.0,
        "atacar_pelo_meio": 0.98,
        "atacar_na_rede": 1.0,
    },
    "saibro": {
        "atacar_do_fundo": 0.92,
        "atacar_pelo_meio": 1.0,
        "atacar_na_rede": 1.08,
    },
    "grama": {
        "atacar_do_fundo": 1.06,
        "atacar_pelo_meio": 0.98,
        "atacar_na_rede": 0.92,
    },
}


def calcular_fator_desgaste_nao_linear(stamina_atual: float) -> float:
    stamina_atual = clamp(stamina_atual, 0.0, 100.0)
    if stamina_atual >= 70:
        return 1.0
    if stamina_atual >= 50:
        return 1.10
    if stamina_atual >= 35:
        return 1.18
    if stamina_atual >= 20:
        return 1.30
    return 1.45


def calcular_fator_custo_stamina(
    atributos: dict, psico: dict, estrategia: dict, intensidade: str, superficie: str
) -> float:
    estrategia = estrategia or {}
    resistencia = atributos.get("resistencia", 50)
    velocidade = atributos.get("velocidade", 50)
    topspin = atributos.get("topspin", 50)
    agressividade = psico.get("agressividade", 50)
    estilo = estrategia.get("estilo", "atacar_do_fundo")

    fator = 1.0 - (resistencia - 50) / 200.0
    fator *= 1.0 + (agressividade - 50) / 200.0

    if intensidade == "longo":
        bonus = 1.0 - ((velocidade - 50) / 250.0 + (topspin - 50) / 300.0)
        if estilo == "atacar_do_fundo":
            bonus -= 0.05
        elif estilo == "atacar_na_rede":
            bonus += 0.05
        fator *= clamp(bonus, 0.75, 1.15)
    elif intensidade == "curto":
        if estilo == "atacar_na_rede":
            fator *= 1.05
        elif estilo == "atacar_do_fundo":
            fator *= 0.98

    superficie = normalizar_superficie(superficie)
    fator *= ESTILO_FADIGA_SUPERFICIE.get(superficie, {}).get(estilo, 1.0)
    return clamp(fator, 0.6, 1.5)


def atualizar_momentum_contextual(
    momentum_j: int,
    momentum_a: int,
    sequencia_j: int,
    sequencia_a: int,
    ultimo_vencedor,
    vencedor: str,
    is_match_point: bool,
    is_set_point: bool,
    is_break_point: bool,
    is_tiebreak: bool,
    jogador_perdendo: bool,
    adversario_perdendo: bool,
    pj: int,
    pa: int,
    limite: int = 6,
):
    ganho = 1
    perda = 1

    if is_match_point:
        ganho += 3
        perda += 2
    elif is_set_point:
        ganho += 2
        perda += 1
    elif is_break_point:
        ganho += 2
        perda += 1
    elif not is_tiebreak and pj >= 2 and pa >= 2:
        ganho += 1

    if vencedor == "j" and jogador_perdendo:
        ganho += 1
    if vencedor == "a" and adversario_perdendo:
        ganho += 1

    if ultimo_vencedor == vencedor:
        if vencedor == "j":
            sequencia_j += 1
        else:
            sequencia_a += 1
    else:
        if vencedor == "j":
            sequencia_j = 1
            sequencia_a = 0
        else:
            sequencia_a = 1
            sequencia_j = 0

    ultimo_vencedor = vencedor
    sequencia = sequencia_j if vencedor == "j" else sequencia_a
    if sequencia >= 5:
        ganho += 2
    elif sequencia >= 3:
        ganho += 1

    if vencedor == "j":
        momentum_j = min(limite, momentum_j + ganho)
        momentum_a = max(0, momentum_a - perda)
    else:
        momentum_a = min(limite, momentum_a + ganho)
        momentum_j = max(0, momentum_j - perda)

    return momentum_j, momentum_a, sequencia_j, sequencia_a, ultimo_vencedor


def aplicar_custo_stamina_contextual(
    stamina_j: float,
    stamina_a: float,
    stats_info: dict,
    superficie: str,
    clima: str,
    umidade: int,
    contexto_flags: dict,
    atributos_j: dict,
    atributos_a: dict,
    psico_j: dict,
    psico_a: dict,
    estrategia_j: dict,
    estrategia_a: dict,
):
    intensidade = stats_info.get("intensidade", "medio")
    base = STAMINA_CUSTO_BASE.get(intensidade, STAMINA_CUSTO_BASE["medio"])
    superficie_n = normalizar_superficie(superficie)
    custo_base = base * SUPERFICIE_FADIGA.get(superficie_n, 1.0)

    if stats_info.get("ace") or stats_info.get("dupla_falta"):
        custo_base *= 0.72
    elif stats_info.get("winner"):
        custo_base *= 0.9
    elif stats_info.get("erro_nao_forcado"):
        custo_base *= 1.02

    if (clima or "").lower() == "quente":
        custo_base *= 1.05
    if int(umidade or 0) >= 75:
        custo_base *= 1.04
    if (
        contexto_flags.get("is_break_point")
        or contexto_flags.get("is_set_point")
        or contexto_flags.get("is_match_point")
    ):
        custo_base *= 1.12

    fator_j = calcular_fator_custo_stamina(
        atributos_j, psico_j, estrategia_j, intensidade, superficie_n
    )
    fator_a = calcular_fator_custo_stamina(
        atributos_a, psico_a, estrategia_a, intensidade, superficie_n
    )

    custo_j = custo_base * fator_j * calcular_fator_desgaste_nao_linear(stamina_j)
    custo_a = custo_base * fator_a * calcular_fator_desgaste_nao_linear(stamina_a)
    return max(15.0, stamina_j - custo_j), max(15.0, stamina_a - custo_a)


def calcular_stamina_pos_recuperacao(
    stamina: float,
    fisico: float = 50,
    indoor: bool = False,
    clima: str = "ameno",
    umidade: int = 50,
    tipo: str = "game",
    tem_fisioterapeuta: bool = False,
) -> float:
    """Recuperação de stamina entre games ou sets.

    Delega o cálculo base para calcular_recuperacao_energia (fadiga.py) e
    aplica penalidades ambientais (indoor/clima/umidade).
    """
    rec_base = float(
        calcular_recuperacao_energia(int(fisico), tipo, tem_fisioterapeuta)
    )
    fator_amb = 1.0
    if indoor:
        fator_amb *= 0.9
    if (clima or "").lower() == "quente":
        fator_amb *= 0.9
    if int(umidade or 0) >= 75:
        fator_amb *= 0.92
    rec = rec_base * fator_amb
    return clamp(stamina + rec, 0.0, 100.0)


def normalizar_energia_pos_partida(
    stamina_final: float,
    resistencia: int,
    pontos_disputados: int,
    superficie: str = "dura",
    energia_inicial: float | None = None,
) -> int:
    energia = max(0.0, min(100.0, float(stamina_final)))
    if energia_inicial is not None:
        energia = min(energia, max(0.0, min(100.0, float(energia_inicial))))
    if pontos_disputados < 20:
        return int(round(energia))

    superficie_n = normalizar_superficie(superficie)
    ajuste_superficie = 0
    if superficie_n == "saibro":
        ajuste_superficie = -3
    elif superficie_n == "grama":
        ajuste_superficie = 2

    bonus_resistencia = max(0, min(7, int(round((int(resistencia) - 55) / 6.5))))
    alvo = 58 + bonus_resistencia + ajuste_superficie
    intensidade = min(1.0, max(0.55, pontos_disputados / 145.0))

    if energia > alvo:
        excesso = energia - alvo
        # Puxa energia para faixa realista pós-jogo; partidas longas aproximam mais do alvo.
        energia = energia - (excesso * (0.72 + (0.28 * intensidade)))

    teto_pos_partida = 60 + ajuste_superficie
    if int(resistencia) >= 85:
        teto_pos_partida = 65 + ajuste_superficie
    elif int(resistencia) >= 75:
        teto_pos_partida = 62 + ajuste_superficie
    if pontos_disputados >= 170:
        teto_pos_partida -= 2
    energia = min(energia, teto_pos_partida)

    return max(15, min(100, int(round(energia))))


def calcular_impacto_moral_sets(jogador, resultado_sets, venceu_partida: bool) -> int:
    """Calcula ajuste de moral com base na diferença de games em cada set."""
    psico = (
        getattr(jogador, "atributos_psicologicos", {})
        if not isinstance(jogador, dict)
        else jogador.get("atributos_psicologicos", {})
    )
    determinacao = int(psico.get("determinacao", 50) or 50)
    clutch = int(psico.get("clutch", 50) or 50)
    agressividade = int(psico.get("agressividade", 50) or 50)

    # Resiliência mental reduz impacto negativo; mental baixo amplia.
    resiliencia = ((determinacao - 50) * 0.012) + ((clutch - 50) * 0.008)
    fator_negativo = max(0.65, min(1.35, 1.0 - resiliencia))
    # Agressividade alta acelera recuperação de confiança em sets dominantes.
    fator_positivo = max(0.8, min(1.25, 1.0 + ((agressividade - 50) * 0.005)))

    delta = 0
    for games_j, games_a in resultado_sets:
        diff = abs(int(games_j) - int(games_a))
        if games_j < games_a:
            # Set perdido: quanto maior a diferença, maior a queda.
            if diff >= 5:
                delta -= int(round(4 * fator_negativo))
            elif diff >= 3:
                delta -= int(round(3 * fator_negativo))
            else:
                delta -= int(round(1 * fator_negativo))
        elif games_j > games_a and diff >= 4:
            # Set ganho dominante ajuda confiança, mas bem menos que o impacto da derrota.
            delta += int(round(1 * fator_positivo))

    if not venceu_partida:
        delta = int(round(delta * 1.2))

    return delta


def calcular_impacto_moral_ranking(jogador, adversario, venceu_partida: bool) -> int:
    """Calcula ajuste de moral por resultado relativo ao ranking/força do adversário."""
    from src.utils.entidade_utils import obter_atributos

    attrs_j = obter_atributos(jogador)
    attrs_a = obter_atributos(adversario)

    overall_j = (
        int(round(sum(attrs_j.values()) / max(1, len(attrs_j)))) if attrs_j else 50
    )
    overall_a = (
        int(round(sum(attrs_a.values()) / max(1, len(attrs_a)))) if attrs_a else 50
    )

    pontos_j = int(getattr(jogador, "pontos", 0) or 0)
    if isinstance(adversario, dict):
        pontos_a = int(adversario.get("pontos", 0) or 0)
        pos_j = int(getattr(jogador, "ranking_pos", 0) or 0)
        pos_a = int(adversario.get("ranking_pos", 0) or 0)
    else:
        pontos_a = int(getattr(adversario, "pontos", 0) or 0)
        pos_j = int(getattr(jogador, "ranking_pos", 0) or 0)
        pos_a = int(getattr(adversario, "ranking_pos", 0) or 0)

    impacto = 0
    if pos_j > 0 and pos_a > 0:
        # positivo: adversário melhor rankeado (número menor)
        diff_rank = pos_j - pos_a
        if diff_rank >= 180:
            impacto += 5
        elif diff_rank >= 90:
            impacto += 4
        elif diff_rank >= 40:
            impacto += 3
        elif diff_rank >= 15:
            impacto += 2
        elif diff_rank >= 5:
            impacto += 1
        elif diff_rank <= -180:
            impacto -= 5
        elif diff_rank <= -90:
            impacto -= 4
        elif diff_rank <= -40:
            impacto -= 3
        elif diff_rank <= -15:
            impacto -= 2
        elif diff_rank <= -5:
            impacto -= 1
    else:
        # Fallback quando posição não estiver disponível: usa pontos/overall.
        if pontos_a - pontos_j >= 1200:
            impacto += 3
        elif pontos_a - pontos_j >= 400:
            impacto += 2
        elif pontos_j - pontos_a >= 1200:
            impacto -= 3
        elif pontos_j - pontos_a >= 400:
            impacto -= 2

        if overall_a - overall_j >= 6:
            impacto += 2
        elif overall_a - overall_j >= 3:
            impacto += 1
        elif overall_j - overall_a >= 6:
            impacto -= 2
        elif overall_j - overall_a >= 3:
            impacto -= 1

    delta = impacto if venceu_partida else -impacto
    # Regra de sanidade:
    # - Vitória não pode reduzir moral.
    # - Derrota não pode aumentar moral.
    if venceu_partida and delta < 0:
        delta = 0
    if not venceu_partida and delta > 0:
        delta = 0

    return delta
