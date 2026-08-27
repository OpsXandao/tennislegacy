from enum import Enum
from typing import Any
from src.jogador import normalizar_nome

SCORE_MAP = ("0", "15", "30", "40")

def pontuacao_texto(pontos_a: int, pontos_b: int) -> tuple[str, str]:
    if pontos_a >= 3 and pontos_b >= 3:
        if pontos_a == pontos_b: return ("40", "40")
        if pontos_a > pontos_b: return ("AD", "40")
        return ("40", "AD")
    return (SCORE_MAP[min(pontos_a, 3)], SCORE_MAP[min(pontos_b, 3)])

def resumo_textual_evento(payload: dict[str, Any]) -> str:
    headline = str(payload.get("headline", "") or "").strip()
    detail = str(payload.get("detail", "") or "").strip()
    if headline and detail and detail != headline:
        return f"{headline} {detail}".strip()
    return headline or detail or "Ponto confirmado."

def valor_entidade(entidade: Any, chave: str, default: Any = None) -> Any:
    if isinstance(entidade, dict): return entidade.get(chave, default)
    return getattr(entidade, chave, default)

def entidade_para_dict(entidade: Any) -> dict[str, Any]:
    if isinstance(entidade, dict): return dict(entidade)
    return {
        "nome": getattr(entidade, "nome", ""),
        "nacionalidade": getattr(entidade, "nacionalidade", ""),
        "energia": getattr(entidade, "energia", 100),
        "moral": getattr(entidade, "moral", 70),
        "ritmo_jogo": getattr(entidade, "ritmo_jogo", 50),
        "atributos": dict(getattr(entidade, "atributos", {}) or {}),
        "atributos_psicologicos": dict(getattr(entidade, "atributos_psicologicos", {}) or {}),
        "status_lesao": dict(getattr(entidade, "status_lesao", {}) or {}),
        "overall": getattr(entidade, "overall", None),
        "ranking_pos": getattr(entidade, "ranking", None),
    }

def atualizar_historico_torneios(destino: Any, entrada: dict[str, Any]) -> None:
    historico = list(getattr(destino, "historico_torneios", []) or [])
    chave = (
        normalizar_nome(entrada.get("nome", "")),
        int(entrada.get("ano", 0) or 0),
        int(entrada.get("semana", 0) or 0),
        str(entrada.get("modalidade", "simples") or "simples"),
    )
    for idx, item in enumerate(historico):
        if not isinstance(item, dict):
            continue
        chave_item = (
            normalizar_nome(item.get("nome", item.get("torneio", ""))),
            int(item.get("ano", 0) or 0),
            int(item.get("semana", 0) or 0),
            str(item.get("modalidade", "simples") or "simples"),
        )
        if chave_item == chave:
            historico[idx] = {**item, **entrada}
            destino.historico_torneios = historico
            return
    historico.append(entrada)
    destino.historico_torneios = historico

def fase_alcancada_apos_partida(instancia: Any, fase_atual: str, jogador_venceu: bool) -> str:
    from src.utils.log_jogo import log_erro
    fase_norm = str(fase_atual or "").strip().lower()
    if not fase_norm: return ""
    if not jogador_venceu: return fase_norm
    if fase_norm == "final": return "campeao"
    try:
        fases = list(instancia._fases_ordem())
        idx = fases.index(fase_norm)
        if idx + 1 < len(fases): return str(fases[idx + 1]).lower()
    except Exception as e:
        log_erro(None, "_fase_alcancada_apos_partida", e)
    return fase_norm
