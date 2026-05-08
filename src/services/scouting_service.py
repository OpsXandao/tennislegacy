from __future__ import annotations

from typing import Any, Dict, List


def calcular_metricas_scouting(
    atributos: Dict[str, Any] | None = None,
    atributos_psicologicos: Dict[str, Any] | None = None,
    resumo_fifa: Dict[str, Any] | None = None,
) -> Dict[str, int]:
    atributos = atributos or {}
    atributos_psicologicos = atributos_psicologicos or {}
    resumo_fifa = resumo_fifa or {}

    saque = int(resumo_fifa.get("SAQ", atributos.get("saque", 50)) or 50)
    fundo = round(
        (
            int(resumo_fifa.get("FOR", atributos.get("forehand", 50)) or 50)
            + int(resumo_fifa.get("BAC", atributos.get("backhand", 50)) or 50)
            + int(resumo_fifa.get("MOV", atributos.get("movimento", 50)) or 50)
            + int(atributos.get("winner", 50) or 50)
        )
        / 4
    )
    mental = round(
        (
            int(atributos_psicologicos.get("concentracao", 50) or 50)
            + int(atributos_psicologicos.get("determinacao", 50) or 50)
            + int(atributos_psicologicos.get("leitura_de_jogo", 50) or 50)
        )
        / 3
    )
    voleio = int(atributos.get("voleio", 50) or 50)
    winner = int(atributos.get("winner", 50) or 50)
    movimento = int(atributos.get("movimento", 50) or 50)

    return {
        "saque": saque,
        "fundo": fundo,
        "mental": mental,
        "voleio": voleio,
        "winner": winner,
        "movimento": movimento,
    }


def detectar_superficie_favorita(atributos: Dict[str, Any] | None = None) -> str:
    atributos = atributos or {}
    if not atributos:
        return "Hard"

    clay_score = int(atributos.get("topspin", 0) or 0) + int(
        atributos.get("slice", 0) or 0
    )
    grass_score = int(atributos.get("saque", 0) or 0) + int(
        atributos.get("voleio", 0) or 0
    )
    hard_score = int(atributos.get("forehand", 0) or 0) + int(
        atributos.get("backhand", 0) or 0
    )
    melhor = max(clay_score, grass_score, hard_score)

    if melhor == clay_score:
        return "Clay"
    if melhor == grass_score:
        return "Grass"
    return "Hard"


def montar_relatorio_scouting(
    adversario: Dict[str, Any],
    superficie: str = "",
) -> Dict[str, Any]:
    atributos = adversario.get("atributos") or {}
    atributos_psicologicos = adversario.get("atributos_psicologicos") or {}
    resumo_fifa = adversario.get("resumo_fifa") or {}
    energia = int(adversario.get("energia", 100) or 100)
    superficie_norm = str(superficie or "").strip().lower()
    if "saibro" in superficie_norm:
        superficie_norm = "clay"
    elif "grama" in superficie_norm:
        superficie_norm = "grass"
    else:
        superficie_norm = "hard"

    metricas = calcular_metricas_scouting(
        atributos,
        atributos_psicologicos,
        resumo_fifa,
    )
    saque = metricas["saque"]
    fundo = metricas["fundo"]
    mental = metricas["mental"]
    voleio = metricas["voleio"]
    winner = metricas["winner"]
    movimento = metricas["movimento"]

    pontos_fortes: List[str] = []
    fraquezas: List[str] = []
    dicas: List[str] = []

    if saque >= 82:
        pontos_fortes.append("CANHÃO DE SAQUE")
        dicas.append("Prepare devoluções curtas e priorize colocar a bola em jogo.")
        if superficie_norm in {"grass", "hard"}:
            dicas.append("Em quadra rápida, ele deve forçar o saque nos pontos grandes.")
    elif saque >= 74:
        pontos_fortes.append("SAQUE PRECISO")
        dicas.append("Evite antecipar o lado da devolução; ele varia bem o alvo.")
    elif saque <= 55:
        fraquezas.append("2º SAQUE FRÁGIL")
        dicas.append("Entre na quadra para atacar o segundo saque dele.")

    if fundo >= 80:
        pontos_fortes.append("MURO NO FUNDO")
        dicas.append("Crie ângulos curtos para tirá-lo da zona de conforto.")
        if superficie_norm == "clay":
            dicas.append("No saibro, curtinhas podem quebrar o ritmo dele.")

    if winner >= 78:
        pontos_fortes.append("GOLPES EXPLOSIVOS")
        dicas.append("Mantenha profundidade; bola curta no meio tende a ser punida.")
        if int(atributos_psicologicos.get("agressividade", 50) or 50) > 70:
            dicas.append("Se você sustentar consistência, ele pode exagerar no risco.")
    elif winner <= 50:
        fraquezas.append("POUCO PODER DE FOGO")
        dicas.append("Há espaço para subir à rede sem tanta exposição.")

    if movimento >= 80:
        pontos_fortes.append("COBERTURA ELITE")
        dicas.append("Use contra-pé e mudança de direção para quebrar a recuperação.")
    elif movimento <= 58:
        fraquezas.append("MOBILIDADE REDUZIDA")
        dicas.append("Mova-o lateralmente; ele perde precisão correndo.")
        if saque >= 75:
            dicas.append("Se a devolução voltar funda, ele tende a sofrer no rally.")

    if voleio >= 75:
        pontos_fortes.append("MESTRE DO VOLEIO")
        dicas.append("Se ele subir, mire nos pés com bola baixa.")
    elif voleio <= 50:
        fraquezas.append("INSEGURO NA REDE")
        dicas.append("Curtinhas podem forçá-lo a decidir mal perto da fita.")

    if mental >= 80:
        pontos_fortes.append("GELO NAS VEIAS")
        dicas.append("Não espere presentes em pontos decisivos.")
    elif mental <= 60:
        fraquezas.append("MENTAL OSCILANTE")
        dicas.append("Sets longos e pressão contínua tendem a derrubar a confiança dele.")
        if int(atributos_psicologicos.get("determinacao", 50) or 50) < 50:
            dicas.append("Uma quebra abaixo já pode afetar bastante a postura dele.")

    if energia < 60:
        fraquezas.append("EXAUSTÃO VISÍVEL")
        dicas.append("Alongue trocas para explorar o desgaste físico.")

    if not pontos_fortes:
        pontos_fortes.append("EQUILIBRADO")

    nome = adversario.get("nome", "Adversário")
    if saque >= 75 and voleio >= 70:
        texto = (
            f"{nome} tem perfil de saque e rede, buscando encurtar pontos desde o início."
        )
    elif fundo >= 75 and movimento >= 75:
        texto = (
            f"{nome} atua como contra-atacador sólido, sustentando trocas longas com muita cobertura."
        )
    elif winner >= 75 and saque >= 70:
        texto = f"{nome} joga de forma agressiva e tenta ditar o ritmo com potência."
    else:
        texto = f"{nome} apresenta perfil versátil e tende a se adaptar ao contexto da partida."

    return {
        "metricas": {
            "saque": saque,
            "fundo": fundo,
            "mental": mental,
        },
        "texto": texto,
        "dicas": dicas[:3],
        "pontos_fortes": pontos_fortes[:3],
        "fraquezas": fraquezas[:3],
        "superficie_favorita": detectar_superficie_favorita(atributos),
    }
