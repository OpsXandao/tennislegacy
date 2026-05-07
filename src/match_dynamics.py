from src.math_utils import clamp
from src.superficie_utils import normalizar_superficie

STAMINA_CUSTO_BASE = {
    "curto": 0.35,
    "medio": 0.65,
    "longo": 0.95,
    "muito_longo": 1.55,  # rallies de 10+ trocas (saibro, dois baseliners)
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
    fisico = atributos.get("fisico", 50)
    movimento = atributos.get("movimento", 50)
    topspin = atributos.get("topspin", 50)
    agressividade = psico.get("agressividade", 50)
    estilo = estrategia.get("estilo", "atacar_do_fundo")

    fator = 1.0 - (fisico - 50) / 200.0
    fator *= 1.0 + (agressividade - 50) / 200.0

    if intensidade == "longo":
        bonus = 1.0 - ((movimento - 50) / 250.0 + (topspin - 50) / 300.0)
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
    stamina: float, fisico: float, indoor: bool, clima: str, umidade: int
) -> float:
    base = 0.9 if indoor else 1.0
    if (clima or "").lower() == "quente":
        base *= 0.9
    if int(umidade or 0) >= 75:
        base *= 0.92
    rec = base * clamp(0.12 + (fisico / 240.0), 0.2, 0.62)
    return clamp(stamina + rec, 0.0, 100.0)
