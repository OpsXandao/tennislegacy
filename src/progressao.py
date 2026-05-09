import random
from typing import Any, Dict, List, Optional, Tuple, Union

from src.management import obter_profissional_da_equipe
from src.fadiga import (
    EventoProgressao,
    _normalizar_status_lesao,
    handle_fadiga_e_lesao,
    handle_fadiga_e_lesao_npc,
    recuperar_energia_entre_rodadas,
)

# Re-exports para compatibilidade
__all__ = [
    "handle_xp_e_level_up",
    "processar_envelhecimento_anual",
    "evoluir_npc_pos_torneio",
    "calcular_progressao_natural",
    "aplicar_melhorias_naturais",
    "handle_progressao_natural",
    "treinar_semana",
    "handle_fadiga_e_lesao",
    "handle_fadiga_e_lesao_npc",
    "recuperar_energia_entre_rodadas",
    "EventoProgressao",
]

# --- Constantes de Progressão ---
XP_VITORIA = 50
XP_DERROTA = 20
CAP_NATURAL = 98
CAP_MAXIMO = 100


def handle_xp_e_level_up(jogador: Any, vitoria: bool, return_eventos: bool = False) -> Union[Any, Tuple[Any, List[EventoProgressao]]]:
    """
    Adiciona XP ao jogador com base no resultado da partida e verifica se ele subiu de nível.
    """
    eventos: List[EventoProgressao] = []
    xp_ganho = XP_VITORIA if vitoria else XP_DERROTA

    # Bônus do Treinador
    equipe = getattr(jogador, "equipe", [])
    treinador = obter_profissional_da_equipe(equipe, "treinador")
    if treinador:
        xp_ganho = int(xp_ganho * treinador.get("bonus_xp", 1.0))

    # Bônus Lifestyle: Academia Própria
    lifestyle = getattr(jogador, "lifestyle", [])
    if isinstance(lifestyle, list) and "academia_propria" in lifestyle:
        xp_ganho = int(xp_ganho * 1.15)

    jogador.xp += xp_ganho
    eventos.append(
        EventoProgressao(
            tipo="xp_ganho",
            mensagem=f"Você ganhou {xp_ganho} de XP.",
            payload={"xp_ganho": xp_ganho, "vitoria": bool(vitoria)},
        )
    )

    # Verifica se o jogador subiu de nível
    xp_para_prox = getattr(jogador, "xp_para_proximo_nivel", 100)
    while jogador.xp >= xp_para_prox:
        jogador.nivel += 1
        jogador.pontos_de_skill += 5

        # Fórmula de progressão equilibrada (Game Designer recommendation)
        # 100 + (Nivel^1.8) * 10 -> Crescimento sustentável e planejado
        proximo_alvo = int(100 + (jogador.nivel**1.8) * 10)

        # Garante que sempre aumente pelo menos 5% em relação ao anterior se a fórmula falhar em ser maior
        if proximo_alvo <= xp_para_prox:
            proximo_alvo = int(xp_para_prox * 1.05)

        xp_excedente = jogador.xp - xp_para_prox
        jogador.xp = xp_excedente
        jogador.xp_para_proximo_nivel = proximo_alvo
        xp_para_prox = proximo_alvo

        eventos.append(
            EventoProgressao(
                tipo="level_up",
                mensagem=f"LEVEL UP! Você alcançou o Nível {jogador.nivel}.",
                payload={
                    "nivel": jogador.nivel,
                    "pontos_de_skill_ganhos": 5,
                    "pontos_de_skill_total": jogador.pontos_de_skill,
                },
            )
        )

    if return_eventos:
        return jogador, eventos
    return jogador


def processar_envelhecimento_anual(jogador_obj_ou_dict: Union[Any, Dict[str, Any]]) -> None:
    """
    Aplica evolução ou declínio de atributos com base na idade e pico de carreira.
    Deve ser chamado na virada do ano.
    """
    is_dict = isinstance(jogador_obj_ou_dict, dict)
    idade = jogador_obj_ou_dict.get("idade", 20) if is_dict else getattr(jogador_obj_ou_dict, "idade", 20)
    pico = (
        jogador_obj_ou_dict.get("pico_carreira", 27)
        if is_dict
        else getattr(jogador_obj_ou_dict, "pico_carreira", 27)
    )
    atributos = (
        jogador_obj_ou_dict.get("atributos", {})
        if is_dict
        else getattr(jogador_obj_ou_dict, "atributos", {})
    )

    # Fatores de mudança
    if idade < 21:
        fator_tecnico = random.randint(3, 7)
        fator_fisico = random.randint(2, 5)
    elif idade < pico:
        fator_tecnico = random.randint(1, 4)
        fator_fisico = random.randint(0, 2)
    elif idade <= pico + 2:
        # Ápice: ganha técnica, perde um pouco de físico
        fator_tecnico = random.randint(0, 2)
        fator_fisico = random.randint(-2, 0)
    else:
        # Declínio
        anos_pos_pico = idade - pico
        fator_tecnico = -random.randint(1, max(2, anos_pos_pico // 2))
        fator_fisico = -random.randint(2, max(3, anos_pos_pico))

    # Aplicar mudanças
    fisicos = ["movimento", "fisico"]
    for attr in atributos:
        change = fator_fisico if attr in fisicos else fator_tecnico
        atributos[attr] = max(5, min(CAP_MAXIMO, atributos[attr] + change))

    # Incrementar idade e atualizar overall
    if is_dict:
        jogador_obj_ou_dict["idade"] = idade + 1
        from src.player_ratings import ajustar_atributo_duplas, calcular_overall_contextual

        ajustar_atributo_duplas(jogador_obj_ou_dict)
        jogador_obj_ou_dict["overall"] = calcular_overall_contextual(jogador_obj_ou_dict)
    else:
        jogador_obj_ou_dict.idade += 1
        if hasattr(jogador_obj_ou_dict, "_sanitizar_atributos"):
            jogador_obj_ou_dict._sanitizar_atributos()
        if hasattr(jogador_obj_ou_dict, "calcular_overall"):
            jogador_obj_ou_dict.overall = jogador_obj_ou_dict.calcular_overall()


def evoluir_npc_pos_torneio(jogador_dict: Dict[str, Any], fase_alcancada: str) -> Optional[Dict[str, Any]]:
    """
    Aplica evolução orgânica em NPCs após torneios.
    Jovens evoluem mais rápido. Vencer torneios dá bônus.
    """
    if not isinstance(jogador_dict, dict):
        return jogador_dict

    if jogador_dict.get("e_jogador_principal"):
        # Jogador humano usa o fluxo próprio de XP/progressão.
        return jogador_dict

    idade = jogador_dict.get("idade", 25)
    pico = jogador_dict.get("pico_carreira", 28)

    # Se já passou do pico, não evolui organicamente pos-torneio
    if idade > pico:
        return jogador_dict

    # Chance de melhorar um atributo aleatório
    chances = {
        "campeao": 0.8,
        "final": 0.6,
        "semifinal": 0.4,
        "quartas": 0.2,
        "oitavas": 0.1,
    }
    chance = chances.get(fase_alcancada, 0.05)

    # Bônus para jovens (under 21)
    if idade < 21:
        chance *= 2.0

    chance = min(0.95, max(0.0, chance))

    if random.random() < chance:
        attrs = jogador_dict.get("atributos", {})
        if attrs:
            lista_at = list(attrs.keys())
            escolhido = random.choice(lista_at)
            attrs[escolhido] = min(CAP_MAXIMO - 1, attrs[escolhido] + 1)

            from src.player_ratings import ajustar_atributo_duplas, calcular_overall_contextual

            ajustar_atributo_duplas(jogador_dict)
            jogador_dict["overall"] = calcular_overall_contextual(jogador_dict)

    return jogador_dict


def calcular_progressao_natural(
    jogador: Any, stats_j: Any, estrategia: Dict[str, Any], pontos_disputados: int, modalidade: Optional[str] = None
) -> Dict[str, int]:
    """
    Aplica ganhos naturais de atributos baseados na performance na partida.
    Retorna dict {atributo: incremento} com os ganhos pendentes.
    """
    if pontos_disputados < 15:
        return {}

    atributos = getattr(jogador, "atributos", {})
    estilo = estrategia.get("estilo", "atacar_do_fundo")
    mod = modalidade or getattr(jogador, "modalidade_atual", "simples")

    total_srv = max(1, getattr(stats_j, "primeiro_saque_total", 1))
    pct_1st = getattr(stats_j, "primeiro_saque_in", 0) / total_srv
    win_rate = getattr(stats_j, "winners", 0) / max(1, pontos_disputados)
    pts_fator = pontos_disputados / 250  # ~1.0 numa partida de 250 pontos

    chances = {
        "saque": min(0.28, getattr(stats_j, "aces", 0) / 15 + max(0, (pct_1st - 0.55) * 0.8)),
        "winner": min(0.25, win_rate * 3),
        "forehand": min(0.22, win_rate * (2.5 if estilo in ("atacar_do_fundo", "atacar_pelo_meio") else 1.2)),
        "backhand": min(0.18, win_rate * (2.0 if estilo in ("atacar_do_fundo", "atacar_pelo_meio") else 1.0)),
        "topspin": min(0.22, pts_fator * (1.2 if estilo == "atacar_do_fundo" else 0.5)),
        "voleio": min(0.28, (0.10 + (getattr(stats_j, "pontos_ganhos_saque", 0) / max(1, getattr(stats_j, "pontos_total_saque", 1))) * 0.25 if estilo == "atacar_na_rede" else pts_fator * 0.25)),
        "slice": min(0.22, (0.08 + win_rate if estilo == "atacar_na_rede" else pts_fator * 0.25)),
        "lob": min(0.12, pts_fator * (0.6 if estilo == "atacar_na_rede" else 0.2)),
        "fisico": min(0.20, pts_fator * 0.9),
        "movimento": min(0.22, pts_fator * (1.0 if estilo in ("atacar_do_fundo", "atacar_pelo_meio") else 0.45)),
    }

    # Se for partida de duplas
    if mod == "duplas" and "duplas" in atributos:
        chances["duplas"] = min(0.25, pts_fator * 0.8)

    treinador = obter_profissional_da_equipe(getattr(jogador, "equipe", []), "treinador")
    preparador = obter_profissional_da_equipe(getattr(jogador, "equipe", []), "preparador")

    melhorias = {}
    for attr, chance in chances.items():
        if attr not in atributos:
            continue
        valor_atual = atributos[attr]
        if valor_atual >= CAP_NATURAL:
            continue
            
        # Quanto mais alto o atributo, mais difícil crescer
        chance_final = chance * max(0.15, (CAP_NATURAL - valor_atual) / 38)

        # Bônus do treinador
        if treinador:
            foco = treinador.get("foco_atributos", [])
            if not foco or attr in foco:
                chance_final *= 1 + treinador.get("bonus_progressao", 0)

        # Bônus do preparador físico
        if preparador and attr in ("fisico", "movimento"):
            chance_final += preparador.get("bonus_fisico_pct", 0)

        if random.random() < chance_final:
            melhorias[attr] = melhorias.get(attr, 0) + 1

    return melhorias


def aplicar_melhorias_naturais(jogador: Any, melhorias: Dict[str, int]) -> Dict[str, int]:
    """
    Aplica melhorias naturais acumuladas e retorna dict {atributo: novo_valor}.
    """
    if not isinstance(melhorias, dict) or not melhorias:
        return {}

    atributos = getattr(jogador, "atributos", {})
    aplicadas = {}

    for attr, incremento in melhorias.items():
        if attr not in atributos:
            continue
        ganho = max(0, int(incremento))
        if ganho <= 0:
            continue

        valor_atual = int(atributos[attr])
        novo_valor = min(CAP_NATURAL, valor_atual + ganho)
        if novo_valor > valor_atual:
            atributos[attr] = novo_valor
            aplicadas[attr] = novo_valor

    if aplicadas and hasattr(jogador, "_sanitizar_atributos"):
        jogador._sanitizar_atributos()
        
    return aplicadas


def handle_progressao_natural(
    jogador: Any, stats_j: Any, estrategia: Dict[str, Any], pontos_disputados: int, modalidade: Optional[str] = None
) -> Dict[str, int]:
    """
    Calcula e aplica progressão natural imediatamente.
    """
    melhorias_pendentes = calcular_progressao_natural(
        jogador, stats_j, estrategia, pontos_disputados, modalidade=modalidade
    )
    return aplicar_melhorias_naturais(jogador, melhorias_pendentes)


def treinar_semana(jogador: Any, foco: str) -> Dict[str, int]:
    """
    Aplica treino semanal ao jogador fora de torneio.
    foco: "tecnico" | "fisico" | "psicologico"
    """
    ENERGIA_MINIMA = 30
    CUSTO_ENERGIA = 15
    CUSTO_FADIGA = 8

    energia = getattr(jogador, "energia", 100)
    if energia < ENERGIA_MINIMA:
        return {}

    status_lesao = _normalizar_status_lesao(getattr(jogador, "status_lesao", {}))
    if status_lesao.get("lesionado", False) and foco != "psicologico":
        return {}

    if foco not in {"tecnico", "fisico", "psicologico"}:
        return {}

    jogador.energia = max(0, energia - CUSTO_ENERGIA)
    jogador.fadiga = min(100, getattr(jogador, "fadiga", 0) + CUSTO_FADIGA)

    atributos = getattr(jogador, "atributos", {})
    atributos_psico = getattr(jogador, "atributos_psicologicos", {})
    melhorias = {}

    equipe = getattr(jogador, "equipe", [])
    treinador = obter_profissional_da_equipe(equipe, "treinador")
    preparador = obter_profissional_da_equipe(equipe, "preparador")
    psicologo = obter_profissional_da_equipe(equipe, "psicologo")

    if foco == "tecnico":
        attrs_tecnicos = [a for a in atributos if a not in ("fisico", "movimento")]
        if treinador is not None:
            foco_attrs = treinador.get("foco_atributos", [])
            pool = (
                foco_attrs if foco_attrs else attrs_tecnicos
            )
            if pool:
                num_tentativas = min(random.randint(2, 3), len(pool))
                candidatos = random.sample(pool, num_tentativas)
                chance = 0.50 + treinador.get("bonus_progressao", 0)
                for attr in candidatos:
                    if attr not in atributos:
                        continue
                    if atributos[attr] >= CAP_NATURAL:
                        continue
                    if random.random() < chance:
                        atributos[attr] += 1
                        melhorias[attr] = atributos[attr]
        else:
            if attrs_tecnicos:
                attr = random.choice(attrs_tecnicos)
                if atributos.get(attr, 0) < CAP_NATURAL and random.random() < 0.15:
                    atributos[attr] += 1
                    melhorias[attr] = atributos[attr]

    elif foco == "fisico":
        bonus_prep = preparador.get("bonus_fisico_pct", 0) if preparador else 0
        chance_base = 0.25 + bonus_prep
        for attr in ("fisico", "movimento"):
            if attr not in atributos:
                continue
            if atributos[attr] >= CAP_NATURAL:
                continue
            if random.random() < chance_base:
                atributos[attr] += 1
                melhorias[attr] = atributos[attr]

    elif foco == "psicologico":
        attrs_psico = list(atributos_psico.keys())
        if attrs_psico:
            if psicologo:
                chance = psicologo.get("chance_mental", 0.20)
                bonus = psicologo.get("bonus_mental", 0)
            else:
                chance = 0.15
                bonus = 0
            attr = random.choice(attrs_psico)
            valor_atual = atributos_psico.get(attr, 0)
            if valor_atual < CAP_NATURAL and random.random() < chance:
                atributos_psico[attr] = min(CAP_NATURAL, valor_atual + 1 + bonus)
                melhorias[attr] = atributos_psico[attr]
                jogador.atributos_psicologicos = atributos_psico

            # Treino psicológico sempre sobe moral
            ganho_moral = 10 if psicologo else 5
            jogador.moral = min(100, (getattr(jogador, "moral", 70) or 70) + ganho_moral)
            melhorias["moral"] = jogador.moral

    if melhorias and hasattr(jogador, "_sanitizar_atributos"):
        jogador._sanitizar_atributos()

    return melhorias
