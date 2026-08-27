import random
from src.match_state import ContextoPonto

SUPERFICIE_MODS = {
    "dura": {
        "saque": 1.05,
        "forehand": 1.02,
        "backhand": 1.02,
        "topspin": 1.0,
        "voleio": 1.0,
        "slice": 1.0,
        "movimento": 1.0,
        "lob": 1.0,
        "winner": 1.05,
    },
    "saibro": {
        "saque": 0.82,  # Penalidade drástica (era 0.92)
        "forehand": 1.08,
        "backhand": 1.08,
        "topspin": 1.25, # Bônus massivo para spin (era 1.12)
        "voleio": 0.85,  # Rede é muito mais difícil (era 0.93)
        "slice": 1.05,
        "movimento": 1.15,
        "lob": 1.15,
        "winner": 0.88,
    },
    "grama": {
        "saque": 1.25,  # Saque é dominante (era 1.12)
        "forehand": 1.05,
        "backhand": 1.0,
        "topspin": 0.90, # Topspin morre na grama (era 1.04)
        "voleio": 1.25,  # Rede é letal (era 1.12)
        "slice": 1.18,
        "movimento": 0.85, # Movimentação é instável (era 0.95)
        "lob": 0.82,
        "winner": 1.15,
    },
}

def calcular_bonus_psicologico(
    atributos_psicologicos: dict, contexto: ContextoPonto, eh_jogador: bool = True
) -> tuple[float, list[str]]:
    """
    Calcula o bônus psicológico baseado no contexto do ponto.
    """
    if not atributos_psicologicos:
        return 0, []

    psico = atributos_psicologicos
    bonus = 0
    insights = []
    pj, pa = contexto.placar_game

    # Pontos de Pressão: Break Points, Set/Match Points, Deuce e Vantagem
    is_pressure_point = contexto.is_break_point() or contexto.is_set_point() or contexto.is_match_point() or (pj >= 3 and pa >= 3)

    # Break point - concentração e determinação
    if contexto.is_break_point():
        b_bp = (psico.get("clutch", 50) - 50) / 8 # Aumentado impacto (era /10)
        b_bp += (psico.get("determinacao", 50) - 50) / 12 # Aumentado impacto (era /15)
        bonus += b_bp
        if b_bp > 1.5:
            insights.append("Entrou firme no break point")
        elif b_bp < -1.5:
            insights.append("Sentiu a pressão no break point")

    # Set point - concentração e agressividade
    if contexto.is_set_point():
        b_sp = (psico.get("clutch", 50) - 50) / 8
        b_sp += (psico.get("agressividade", 50) - 50) / 15
        bonus += b_sp
        if b_sp > 1.5:
            insights.append("Coragem para fechar o set")
        elif b_sp < -1.5:
            insights.append("Braço preso no set point")

    # Match point - todos os 4 atributos
    if contexto.is_match_point():
        b_mp = (psico.get("clutch", 50) - 50) / 6
        b_mp += (psico.get("agressividade", 50) - 50) / 12
        b_mp += (psico.get("leitura_de_jogo", 50) - 50) / 10
        b_mp += (psico.get("determinacao", 50) - 50) / 8
        bonus += b_mp
        if b_mp > 2.0:
            insights.append("Jogou grande no match point")
        elif b_mp < -2.0:
            insights.append("Travou quando podia fechar")

    # Pressão de Deuce / Vantagem
    if not (contexto.is_break_point() or contexto.is_set_point() or contexto.is_match_point()):
        if pj >= 3 and pa >= 3:
            b_pr = (psico.get("clutch", 50) - 50) / 12
            b_pr += (psico.get("determinacao", 50) - 50) / 15
            bonus += b_pr
            if b_pr < -1.0:
                insights.append("Titubeando nos pontos de iguais")

    # Perdendo por 2+ games - determinação
    perdendo = (
        contexto.jogador_perdendo() if eh_jogador else contexto.adversario_perdendo()
    )
    if perdendo:
        b_per = (psico.get("determinacao", 50) - 50) / 8
        bonus += b_per
        if b_per > 1.5:
            insights.append("Reagindo sob pressão")
        elif b_per < -1.5:
            insights.append("Perdeu confiança")

    # Penalidade base sempre ativa
    clutch = psico.get("clutch", 50)
    if clutch < 45:
        p_con = (45 - clutch) * 0.06
        bonus -= p_con
        if p_con > 1.0:
            insights.append("Concentração oscilando")

    agressividade_val = psico.get("agressividade", 50)
    if (
        agressividade_val > 80
        and not contexto.is_break_point()
        and not contexto.is_match_point()
    ):
        p_agr = (agressividade_val - 80) * 0.04
        bonus -= p_agr
        if p_agr > 1.0:
            insights.append("Arriscando além da conta")

    return bonus, insights
