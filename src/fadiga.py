import random
from dataclasses import dataclass
from typing import Any

from src.management import obter_profissional_da_equipe

# --- Constantes de Fadiga e Lesão ---
FADIGA_POR_PONTO = 0.085
CHANCE_LESAO_THRESHOLD = 80  # Acima desta fadiga, há risco de lesão
CHANCE_LESAO_PROB = 0.2  # 20% de chance de lesão se acima do threshold
ENERGIA_RECUP_BASE = 10
ENERGIA_RECUP_POR_FISICO = 0.4
ENERGIA_REFERENCIA_FADIGA = 40  # energia perdida "normal" que dá fator 1.0 de fadiga
PROTECTED_RANKING_MIN_SEMANAS = 4

STATUS_LESAO_PADRAO = {
    "lesionado": False,
    "semanas_restantes": 0,
    "nivel": "saudavel",
    "penalidade_atributos": 0.0,
}

PENALIDADE_POR_NIVEL = {
    "saudavel": 0.0,
    "desconforto": 0.06,
    "limitado": 0.12,
    "lesionado": 0.18,
}


@dataclass
class EventoProgressao:
    tipo: str
    mensagem: str
    payload: dict[str, Any]


def _normalizar_status_lesao(status):
    status = status if isinstance(status, dict) else {}
    normalizado = STATUS_LESAO_PADRAO.copy()
    normalizado.update(status)
    if normalizado.get("lesionado"):
        normalizado["nivel"] = "lesionado"
    elif normalizado.get("nivel") not in PENALIDADE_POR_NIVEL:
        normalizado["nivel"] = "saudavel"
    normalizado["penalidade_atributos"] = PENALIDADE_POR_NIVEL.get(
        normalizado["nivel"], 0.0
    )
    normalizado["semanas_restantes"] = max(
        0, int(normalizado.get("semanas_restantes", 0))
    )
    return normalizado


def _multiplicador_fadiga_contextual(fatores_partida: dict | None) -> float:
    if not isinstance(fatores_partida, dict):
        return 1.0

    mult = 1.0
    superficie = str(fatores_partida.get("superficie", "dura")).strip().lower()
    clima = str(fatores_partida.get("clima", "ameno")).strip().lower()
    vento = int(fatores_partida.get("vento", 0) or 0)
    umidade = int(fatores_partida.get("umidade", 50) or 50)
    indoor = bool(fatores_partida.get("indoor", False))
    pressao_adv = float(fatores_partida.get("pressao_adversario", 50.0) or 50.0)
    pontos_por_game = float(fatores_partida.get("pontos_por_game", 0.0) or 0.0)
    rally_longo_pct = float(fatores_partida.get("rally_longo_pct", 0.0) or 0.0)
    rally_medio_pct = float(fatores_partida.get("rally_medio_pct", 0.0) or 0.0)

    if superficie == "saibro":
        mult += 0.10
    elif superficie == "dura":
        mult += 0.06
    elif superficie == "grama":
        mult += 0.02

    if clima == "quente":
        mult += 0.12
    elif clima == "chuvoso":
        mult += 0.05
    elif clima == "frio":
        mult -= 0.03

    if vento >= 28:
        mult += 0.08
    elif vento >= 20:
        mult += 0.05

    if umidade >= 80:
        mult += 0.12
    elif umidade >= 70:
        mult += 0.08

    if not indoor:
        mult += 0.02

    # Adversário com estilo "pressionador" tende a alongar e endurecer trocas.
    mult += max(-0.05, min(0.12, (pressao_adv - 50.0) / 420.0))
    if pontos_por_game > 6.0:
        mult += min(0.13, (pontos_por_game - 6.0) * 0.04)
    mult += min(0.14, max(0.0, rally_longo_pct) * 0.22)
    mult += min(0.08, max(0.0, rally_medio_pct) * 0.08)

    return max(0.82, min(1.45, mult))


def _aumento_fadiga_nao_linear(
    fadiga_atual: int,
    pontos_disputados: int,
    fatores_partida: dict | None = None,
    energia_perdida: int | None = None,
) -> int:
    if pontos_disputados <= 0:
        return 0
    base = pontos_disputados * FADIGA_POR_PONTO
    # Partidas muito longas têm custo adicional, mas limitado para evitar saltos irreais.
    if pontos_disputados > 180:
        base += (pontos_disputados - 180) * 0.03
    if fadiga_atual >= 80:
        base *= 1.28
    elif fadiga_atual >= 65:
        base *= 1.15
    elif fadiga_atual >= 45:
        base *= 1.05
    base *= _multiplicador_fadiga_contextual(fatores_partida)
    # Escala pelo desgaste real de energia: perdeu pouca energia → pouca fadiga.
    if energia_perdida is not None:
        fator_energia = max(0.15, min(1.5, energia_perdida / ENERGIA_REFERENCIA_FADIGA))
        base *= fator_energia
    return min(32, int(round(base)))


def _atualizar_status_lesao_por_risco(
    status: dict, fadiga: int, energia_atual: int = 100
):
    status = _normalizar_status_lesao(status)
    if status["lesionado"]:
        return status, None

    risco = 0.0
    if fadiga > CHANCE_LESAO_THRESHOLD:
        risco = CHANCE_LESAO_PROB + ((fadiga - CHANCE_LESAO_THRESHOLD) / 160.0)
    energia = max(0, min(100, int(energia_atual)))
    if energia <= 55:
        # Energia perto de 50% aumenta risco agudo de desconforto/lesão.
        risco += (55 - energia) / 120.0

    nivel_atual = status.get("nivel", "saudavel")

    if fadiga >= 90 and random.random() < risco:
        semanas_lesionado = random.randint(2, 5)
        status["lesionado"] = True
        status["nivel"] = "lesionado"
        status["semanas_restantes"] = semanas_lesionado
        status["penalidade_atributos"] = PENALIDADE_POR_NIVEL["lesionado"]
        return status, "lesionado"

    if (
        fadiga >= 82
        and nivel_atual in ("saudavel", "desconforto")
        and random.random() < risco * 0.7
    ):
        status["nivel"] = "limitado"
        status["penalidade_atributos"] = PENALIDADE_POR_NIVEL["limitado"]
        status["semanas_restantes"] = max(
            status.get("semanas_restantes", 0), random.randint(1, 2)
        )
        return status, "limitado"

    if fadiga >= 70 and nivel_atual == "saudavel" and random.random() < risco * 0.9:
        status["nivel"] = "desconforto"
        status["penalidade_atributos"] = PENALIDADE_POR_NIVEL["desconforto"]
        return status, "desconforto"

    return status, None


def handle_fadiga_e_lesao(
    jogador,
    pontos_disputados=None,
    fatores_partida=None,
    energia_perdida=None,
    ranking=None,
    return_eventos: bool = False,
):
    """
    Aumenta a fadiga do jogador após uma partida e verifica a ocorrência de lesões.
    """
    eventos: list[EventoProgressao] = []
    if pontos_disputados is None:
        pontos_disputados = 0
    aumento = _aumento_fadiga_nao_linear(
        getattr(jogador, "fadiga", 0),
        pontos_disputados,
        fatores_partida=fatores_partida,
        energia_perdida=energia_perdida,
    )
    jogador.fadiga = min(100, jogador.fadiga + aumento)
    eventos.append(
        EventoProgressao(
            tipo="fadiga_atualizada",
            mensagem=f"Sua fadiga aumentou para {jogador.fadiga}%.",
            payload={"fadiga": jogador.fadiga, "aumento": aumento},
        )
    )
    jogador.status_lesao = _normalizar_status_lesao(
        getattr(jogador, "status_lesao", {})
    )

    jogador.status_lesao, evento = _atualizar_status_lesao_por_risco(
        jogador.status_lesao,
        jogador.fadiga,
        getattr(jogador, "energia", 100),
    )
    if evento == "desconforto":
        eventos.append(
            EventoProgressao(
                tipo="lesao_desconforto",
                mensagem="Você sentiu desconforto físico. Pequena penalidade temporária aplicada.",
                payload={"status_lesao": dict(jogador.status_lesao)},
            )
        )
    elif evento == "limitado":
        eventos.append(
            EventoProgressao(
                tipo="lesao_limitado",
                mensagem="Você está fisicamente limitado. Seu desempenho caiu até recuperar.",
                payload={"status_lesao": dict(jogador.status_lesao)},
            )
        )
    elif evento == "lesionado":
        semanas = jogador.status_lesao["semanas_restantes"]
        eventos.append(
            EventoProgressao(
                tipo="lesao_critica",
                mensagem=f"LESÃO! Você se lesionou e ficará fora por {semanas} semanas.",
                payload={
                    "status_lesao": dict(jogador.status_lesao),
                    "semanas": semanas,
                },
            )
        )

        # Ranking Protegido (PR) ATP/WTA: Ativado para lesões longas (>= 20 semanas)
        if semanas >= PROTECTED_RANKING_MIN_SEMANAS and ranking:
            pos_atual = ranking.obter_posicao(jogador.nome) or 999
            jogador.protected_ranking = pos_atual
            jogador.protected_ranking_semanas = 52  # 1 ano de proteção pós-retorno
            eventos.append(
                EventoProgressao(
                    tipo="ranking_protegido",
                    mensagem=f"Ranking Protegido ativado: #{pos_atual} (usável após retorno).",
                    payload={"protected_ranking": pos_atual, "duracao_semanas": 52},
                )
            )

    if return_eventos:
        return jogador, eventos
    return jogador


def handle_fadiga_e_lesao_npc(
    jogador_dict,
    pontos_disputados=None,
    fatores_partida=None,
    energia_perdida=None,
    rank_atual=None,
):
    """
    Aplica fadiga e possível lesão em NPCs (dict), sem prints.
    """
    if jogador_dict is None or not isinstance(jogador_dict, dict):
        return jogador_dict
    if pontos_disputados is None:
        pontos_disputados = 0
    aumento = _aumento_fadiga_nao_linear(
        int(jogador_dict.get("fadiga", 0)),
        pontos_disputados,
        fatores_partida=fatores_partida,
        energia_perdida=energia_perdida,
    )
    fadiga_atual = jogador_dict.get("fadiga", 0)
    jogador_dict["fadiga"] = min(100, fadiga_atual + aumento)
    status = _normalizar_status_lesao(jogador_dict.get("status_lesao", {}))
    status, evento = _atualizar_status_lesao_por_risco(
        status,
        jogador_dict["fadiga"],
        jogador_dict.get("energia", 100),
    )
    jogador_dict["status_lesao"] = status

    # Ranking Protegido (PR) para NPCs
    if evento == "lesionado":
        semanas = status.get("semanas_restantes", 0)
        if semanas >= PROTECTED_RANKING_MIN_SEMANAS and rank_atual:
            jogador_dict["protected_ranking"] = rank_atual
            jogador_dict["protected_ranking_semanas"] = 52  # Ativa após recuperação

    return jogador_dict


def recuperar_energia_entre_rodadas(
    jogador, multiplicador: float = 1.0, return_eventos: bool = False
):
    eventos: list[EventoProgressao] = []
    if isinstance(jogador, dict):
        atributos = jogador.get("atributos", {}) or {}
        fisico = atributos.get("fisico", 50)
        fadiga = int(jogador.get("fadiga", 0) or 0)
        energia_antes = int(jogador.get("energia", 100) or 100)
        equipe = jogador.get("equipe", []) or []
    else:
        atributos = getattr(jogador, "atributos", {}) or {}
        fisico = atributos.get("fisico", 50)
        fadiga = int(getattr(jogador, "fadiga", 0) or 0)
        energia_antes = int(getattr(jogador, "energia", 100) or 100)
        equipe = getattr(jogador, "equipe", []) or []
    multiplicador = max(0.2, min(1.5, float(multiplicador)))
    recuperacao_base = int(
        round(ENERGIA_RECUP_BASE + fisico * ENERGIA_RECUP_POR_FISICO)
    )
    fator_fadiga = 1.0
    if fadiga <= 20:
        fator_fadiga = 1.12
    elif fadiga <= 40:
        fator_fadiga = 1.0
    elif fadiga <= 60:
        fator_fadiga = 0.85
    elif fadiga <= 75:
        fator_fadiga = 0.70
    elif fadiga <= 90:
        fator_fadiga = 0.55
    else:
        fator_fadiga = 0.45
    recuperacao = int(round(recuperacao_base * multiplicador * fator_fadiga))

    status_bruto = (
        jogador.get("status_lesao", {})
        if isinstance(jogador, dict)
        else getattr(jogador, "status_lesao", {})
    )
    status_lesao = _normalizar_status_lesao(status_bruto)
    if status_lesao.get("nivel") == "desconforto":
        recuperacao = int(round(recuperacao * 0.9))
    elif status_lesao.get("nivel") in {"limitado", "lesionado"}:
        recuperacao = int(round(recuperacao * 0.75))
    recuperacao = max(2, recuperacao)

    # Bônus do Treinador
    treinador = obter_profissional_da_equipe(
        equipe, "treinador"
    )
    if treinador:
        bonus = treinador.get("bonus_recuperacao", 0)
        recuperacao += bonus
        if bonus > 0:
            eventos.append(
                EventoProgressao(
                    tipo="bonus_recuperacao_treinador",
                    mensagem=f"Bônus de recuperação do treinador: +{bonus}",
                    payload={"bonus": int(bonus)},
                )
            )

    energia_depois = min(100, energia_antes + recuperacao)
    if isinstance(jogador, dict):
        jogador["energia"] = energia_depois
    else:
        jogador.energia = energia_depois
    if multiplicador < 1.0:
        eventos.append(
            EventoProgressao(
                tipo="recuperacao_parcial",
                mensagem="Recuperação parcial: ainda houve jogo no mesmo dia de torneio.",
                payload={"multiplicador": multiplicador},
            )
        )
    if fadiga >= 70:
        eventos.append(
            EventoProgressao(
                tipo="fadiga_reduz_recuperacao",
                mensagem="Fadiga alta reduziu a velocidade de recuperação de energia.",
                payload={"fadiga": fadiga},
            )
        )
    eventos.append(
        EventoProgressao(
            tipo="energia_recuperada",
            mensagem=f"Energia recuperada para a próxima rodada: {energia_antes}% -> {energia_depois}%.",
            payload={
                "energia_antes": int(energia_antes),
                "energia_depois": int(energia_depois),
                "recuperacao_aplicada": int(recuperacao),
            },
        )
    )
    if return_eventos:
        return jogador, eventos
    return jogador
