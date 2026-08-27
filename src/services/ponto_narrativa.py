"""
Funções de narrativa e display para pontos de tênis.

Extraídas de SimuladorPonto para separar responsabilidade de apresentação
da lógica de simulação.
"""

from src.constants.match_constants import MatchPointStats
from src.match_state import ContextoPonto


def pn_append_insight(insights: list[str] | None, texto: str) -> None:
    """Adiciona insight à lista sem duplicatas."""
    if insights is None or not texto:
        return
    if texto not in insights:
        insights.append(texto)


def pn_momento_do_ponto(contexto: ContextoPonto) -> tuple[str, str]:
    """Classifica o momento do ponto (pressão, crítico, etc.)."""
    if contexto.is_match_point():
        return ("match_point", "alta")
    if contexto.is_set_point():
        return ("set_point", "alta")
    if contexto.is_break_point():
        return ("break_point", "alta")
    if contexto.is_tiebreak:
        return ("tiebreak", "alta")
    pj, pa = contexto.placar_game
    if pj >= 3 and pa >= 3:
        return ("deuce", "media")
    return ("normal", "baixa")


def pn_rotulo_estilo(estilo: str) -> str:
    """Traduz estilo de jogo para label legível."""
    if estilo == "atacar_na_rede":
        return "subidas à rede"
    if estilo == "atacar_pelo_meio":
        return "mudanças de direção"
    return "trocas do fundo"


def pn_padronizar_descricoes(descricoes: list) -> list[str]:
    """Normaliza textos de descrição com prefixos de categoria."""
    padronizadas = []
    for desc in descricoes:
        desc_str = str(desc).strip()
        lower = desc_str.lower()
        if lower.startswith("1o saque") or lower.startswith("2o saque"):
            padronizadas.append(f"[SAQUE] {desc_str}")
        elif lower.startswith("rally"):
            padronizadas.append(f"[RALLY] {desc_str}")
        elif "domina o rally" in lower:
            padronizadas.append(f"[MOMENTO] {desc_str}")
        else:
            padronizadas.append(f"[RESULTADO] {desc_str}")
    return padronizadas


def pn_registrar_narrativa_ponto(
    stats_info: MatchPointStats,
    contexto: ContextoPonto,
    vencedor: str,
    estrategia_j: dict,
    estrategia_a: dict,
    poder_saque: float,
    poder_devolucao: float,
    poder_rally_j: float,
    poder_rally_a: float,
) -> None:
    """Gera texto narrativo do ponto com insights táticos."""
    momento, pressao = pn_momento_do_ponto(contexto)
    stats_info.momento = momento
    stats_info.pressao = pressao
    stats_info.vencedor = vencedor
    padrao = ""
    estilo_j = estrategia_j.get("estilo", "atacar_do_fundo")
    estilo_a = estrategia_a.get("estilo", "atacar_do_fundo")
    diff_saque = poder_saque - poder_devolucao
    diff_rally = poder_rally_j - poder_rally_a
    if stats_info.ace:
        padrao = (
            "Seu saque abriu a quadra"
            if vencedor == "j"
            else "O rival te desmontou no saque"
        )
        pn_append_insight(stats_info.insights, padrao)
    elif stats_info.dupla_falta:
        padrao = (
            "Seu segundo saque cedeu a pressão"
            if vencedor != "j"
            else "O rival desabou no segundo saque"
        )
        pn_append_insight(stats_info.insights, padrao)
    elif abs(diff_saque) > 18:
        if contexto.sacador == "j":
            padrao = (
                "Seu saque está comandando os pontos"
                if diff_saque > 0
                else "O rival está devolvendo acima da média"
            )
        else:
            padrao = (
                "O rival está dominando com o saque"
                if diff_saque > 0
                else "Você está pressionando a devolução"
            )
        pn_append_insight(stats_info.insights, padrao)
    elif abs(diff_rally) > 12:
        if diff_rally > 0:
            padrao = f"Você está impondo {pn_rotulo_estilo(estilo_j)}"
        else:
            padrao = f"O rival está vencendo nas {pn_rotulo_estilo(estilo_a)}"
        pn_append_insight(stats_info.insights, padrao)
    elif stats_info.intensidade == "longo":
        padrao = (
            "Você ganhou depois de alongar a troca"
            if vencedor == "j"
            else "O rival te desgastou na troca longa"
        )
        pn_append_insight(stats_info.insights, padrao)
    elif stats_info.winner:
        padrao = (
            "Você acelerou no golpe decisivo"
            if vencedor == "j"
            else "O rival encontrou o golpe decisivo"
        )
        pn_append_insight(stats_info.insights, padrao)
    elif stats_info.erro_nao_forcado:
        padrao = (
            "Você cedeu o ponto sem pressão suficiente"
            if vencedor != "j"
            else "O rival vazou sob pressão controlada"
        )
        pn_append_insight(stats_info.insights, padrao)
    if pressao == "alta":
        if vencedor == "j":
            pn_append_insight(stats_info.insights, "Você respondeu bem no ponto grande")
        else:
            pn_append_insight(stats_info.insights, "O rival venceu o ponto grande")
    if not stats_info.insights:
        pn_append_insight(stats_info.insights, padrao or "Ponto decidido no detalhe")
    stats_info.padrao = padrao or stats_info.insights[-1]
