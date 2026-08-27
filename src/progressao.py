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


def handle_xp_e_level_up(
    jogador: Any, vitoria: bool, return_eventos: bool = False
) -> Union[Any, Tuple[Any, List[EventoProgressao]]]:
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


def processar_envelhecimento_anual(
    jogador_obj_ou_dict: Union[Any, Dict[str, Any]],
) -> None:
    """
    Aplica evolução ou declínio de atributos com base na idade e pico de carreira.
    Deve ser chamado na virada do ano.
    """
    is_dict = isinstance(jogador_obj_ou_dict, dict)
    idade = (
        jogador_obj_ou_dict.get("idade", 20)
        if is_dict
        else getattr(jogador_obj_ou_dict, "idade", 20)
    )
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
    # velocidade e aceleração declinam 1.2x mais rápido; resistência 0.85x; força 0.90x
    fisicos_rapidos = {"velocidade", "aceleracao"}
    fisicos_lentos = {"resistencia"}
    fisicos_medios = {"forca"}
    fisicos_todos = {"velocidade", "aceleracao", "resistencia", "forca", "agilidade"}
    for attr in atributos:
        if attr in fisicos_rapidos:
            change = int(round(fator_fisico * 1.2))
        elif attr in fisicos_lentos:
            change = int(round(fator_fisico * 0.85))
        elif attr in fisicos_medios:
            change = int(round(fator_fisico * 0.90))
        elif attr in fisicos_todos:
            change = fator_fisico
        else:
            change = fator_tecnico
        atributos[attr] = max(5, min(CAP_MAXIMO, atributos[attr] + change))

    # Incrementar idade e atualizar overall
    if is_dict:
        jogador_obj_ou_dict["idade"] = idade + 1
        from src.player_ratings import (
            ajustar_atributo_duplas,
            calcular_overall_contextual,
        )

        ajustar_atributo_duplas(jogador_obj_ou_dict)
        jogador_obj_ou_dict["overall"] = calcular_overall_contextual(
            jogador_obj_ou_dict
        )
    else:
        jogador_obj_ou_dict.idade += 1
        if hasattr(jogador_obj_ou_dict, "_sanitizar_atributos"):
            jogador_obj_ou_dict._sanitizar_atributos()
        if hasattr(jogador_obj_ou_dict, "calcular_overall"):
            jogador_obj_ou_dict.overall = jogador_obj_ou_dict.calcular_overall()


def evoluir_npc_pos_torneio(
    jogador_dict: Dict[str, Any], fase_alcancada: str
) -> Optional[Dict[str, Any]]:
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

            from src.player_ratings import (
                ajustar_atributo_duplas,
                calcular_overall_contextual,
            )

            ajustar_atributo_duplas(jogador_dict)
            jogador_dict["overall"] = calcular_overall_contextual(jogador_dict)

    return jogador_dict


def calcular_progressao_natural(
    jogador: Any,
    stats_j: Any,
    estrategia: Dict[str, Any],
    pontos_disputados: int,
    modalidade: Optional[str] = None,
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
        "vel_saque": min(
            0.28, getattr(stats_j, "aces", 0) / 15 + max(0, (pct_1st - 0.55) * 0.8)
        ),
        "pre_saque": min(0.22, max(0, (pct_1st - 0.55) * 0.7)),
        "segundo_saque": min(0.18, pts_fator * 0.5),
        "winner": min(0.25, win_rate * 3),
        "forehand": min(
            0.22,
            win_rate
            * (2.5 if estilo in ("atacar_do_fundo", "atacar_pelo_meio") else 1.2),
        ),
        "backhand": min(
            0.18,
            win_rate
            * (2.0 if estilo in ("atacar_do_fundo", "atacar_pelo_meio") else 1.0),
        ),
        "retorno": min(0.18, pts_fator * 0.6),
        "topspin": min(0.22, pts_fator * (1.2 if estilo == "atacar_do_fundo" else 0.5)),
        "voleio": min(
            0.28,
            (
                0.10
                + (
                    getattr(stats_j, "pontos_ganhos_saque", 0)
                    / max(1, getattr(stats_j, "pontos_total_saque", 1))
                )
                * 0.25
                if estilo == "atacar_na_rede"
                else pts_fator * 0.25
            ),
        ),
        "slice": min(
            0.22, (0.08 + win_rate if estilo == "atacar_na_rede" else pts_fator * 0.25)
        ),
        "lob": min(0.12, pts_fator * (0.6 if estilo == "atacar_na_rede" else 0.2)),
        "smash": min(0.15, pts_fator * (0.5 if estilo == "atacar_na_rede" else 0.2)),
        "resistencia": min(0.20, pts_fator * 0.9),
        "velocidade": min(
            0.18,
            pts_fator
            * (0.8 if estilo in ("atacar_do_fundo", "atacar_pelo_meio") else 0.35),
        ),
        "agilidade": min(
            0.22,
            pts_fator
            * (1.0 if estilo in ("atacar_do_fundo", "atacar_pelo_meio") else 0.45),
        ),
        "aceleracao": min(0.15, pts_fator * 0.4),
        "forca": min(0.15, pts_fator * 0.35),
    }

    # Se for partida de duplas
    if mod == "duplas" and "duplas" in atributos:
        chances["duplas"] = min(0.25, pts_fator * 0.8)

    treinador = obter_profissional_da_equipe(
        getattr(jogador, "equipe", []), "treinador"
    )
    preparador = obter_profissional_da_equipe(
        getattr(jogador, "equipe", []), "preparador"
    )

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
        if preparador and attr in (
            "resistencia",
            "velocidade",
            "aceleracao",
            "forca",
            "agilidade",
        ):
            chance_final += preparador.get("bonus_fisico_pct", 0)

        if random.random() < chance_final:
            melhorias[attr] = melhorias.get(attr, 0) + 1

    return melhorias


def aplicar_melhorias_naturais(
    jogador: Any, melhorias: Dict[str, int]
) -> Dict[str, int]:
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
    jogador: Any,
    stats_j: Any,
    estrategia: Dict[str, Any],
    pontos_disputados: int,
    modalidade: Optional[str] = None,
) -> Dict[str, int]:
    """
    Calcula e aplica progressão natural imediatamente.
    """
    melhorias_pendentes = calcular_progressao_natural(
        jogador, stats_j, estrategia, pontos_disputados, modalidade=modalidade
    )
    return aplicar_melhorias_naturais(jogador, melhorias_pendentes)


def _get_diminishing_returns_factor(valor_atual: int) -> float:
    """Retorna fator de dificuldade: quanto maior o atributo, menor o ganho."""
    if valor_atual >= 95:
        return 0.15
    if valor_atual >= 90:
        return 0.25
    if valor_atual >= 80:
        return 0.45
    if valor_atual >= 60:
        return 0.80
    return 1.0


def _get_age_multiplier(jogador: Any, foco: str) -> float:
    """Jovens ganham mais em tudo; Veteranos ganham menos em físico."""
    idade = getattr(jogador, "idade", 20)
    pico = getattr(jogador, "pico_carreira", 28)

    if idade < 21:
        return 1.4
    if idade <= pico:
        return 1.0

    # Após o pico
    if foco == "fisico":
        return max(0.3, 1.0 - (idade - pico) * 0.15)
    if foco == "tecnico":
        return max(0.6, 1.0 - (idade - pico) * 0.08)
    # Psicológico/Mental veteranos mantêm ou até melhoram foco
    return 1.1


def processar_erosao_semanal(jogador: Any, participou: bool) -> List[str]:
    """Atributos não treinados ou usados sofrem erosão leve (realismo de manutenção)."""
    if participou:
        return []

    eventos = []
    atributos = getattr(jogador, "atributos", {})
    # Chance de erosão se não jogou nem treinou especificamente
    for attr, valor in atributos.items():
        if valor > 85 and random.random() < 0.08:
            atributos[attr] = max(85, valor - 1)
            eventos.append(
                f"Falta de ritmo: Seu nível de {attr.capitalize()} caiu levemente."
            )

    return eventos


def treinar_semana(
    jogador: Any, foco: str, atributo_foco: Optional[str] = None
) -> Dict[str, int]:
    """
    Aplica treino semanal ao jogador fora de torneio.
    foco: "tecnico" | "fisico" | "psicologico"
    """
    from src.services.staff_realism_service import training_fit_summary

    ENERGIA_MINIMA = 30
    CUSTO_ENERGIA = 15
    CUSTO_FADIGA = 8

    if foco not in {"tecnico", "fisico", "psicologico"}:
        return {}

    energia = getattr(jogador, "energia", 100)
    fadiga = getattr(jogador, "fadiga", 0)

    # Risco de Over-training (Lesão de Treino)
    # Se treinar exausto, chance de estiramento
    if energia < 45 or fadiga > 60:
        chance_lesao = (45 - energia) * 0.01 + (fadiga - 60) * 0.015
        if random.random() < chance_lesao:
            from src.fadiga import aplicar_lesao_aleatoria

            res_lesao = aplicar_lesao_aleatoria(jogador)
            if res_lesao.get("lesionado"):
                # Treino interrompido por lesão
                return {"LESIONADO": 1}

    if energia < ENERGIA_MINIMA:
        return {}

    status_lesao = _normalizar_status_lesao(getattr(jogador, "status_lesao", {}))
    if status_lesao.get("lesionado", False) and foco != "psicologico":
        return {}

    jogador.energia = max(0, energia - CUSTO_ENERGIA)
    jogador.fadiga = min(100, fadiga + CUSTO_FADIGA)

    atributos = getattr(jogador, "atributos", {})
    atributos_psico = getattr(jogador, "atributos_psicologicos", {})
    melhorias = {}

    age_mod = _get_age_multiplier(jogador, foco)
    equipe = getattr(jogador, "equipe", [])
    treinador = obter_profissional_da_equipe(equipe, "treinador")
    preparador = obter_profissional_da_equipe(equipe, "preparador")
    psicologo = obter_profissional_da_equipe(equipe, "psicologo")

    fit_bonus = 0.0
    if treinador and foco == "tecnico":
        fit_bonus = training_fit_summary(jogador, treinador, foco, atributo_foco).get(
            "bonus", 0.0
        )
    elif preparador and foco == "fisico":
        fit_bonus = training_fit_summary(jogador, preparador, foco, atributo_foco).get(
            "bonus", 0.0
        )
    elif psicologo and foco == "psicologico":
        fit_bonus = training_fit_summary(jogador, psicologo, foco, atributo_foco).get(
            "bonus", 0.0
        )

    fisicos_chave = {"velocidade", "aceleracao", "resistencia", "forca", "agilidade"}
    if foco == "tecnico":
        # Se escolheu um atributo foco, ganho é quase garantido (se não estiver no cap)
        if (
            atributo_foco
            and atributo_foco in atributos
            and atributo_foco not in fisicos_chave
        ):
            val = atributos[atributo_foco]
            if val < CAP_MAXIMO:
                chance = (
                    (0.85 + fit_bonus) * _get_diminishing_returns_factor(val) * age_mod
                )
                if random.random() < chance:
                    atributos[atributo_foco] += 1
                    melhorias[atributo_foco] = atributos[atributo_foco]

        # Ganhos residuais em outros técnicos
        attrs_tecnicos = [
            a for a in atributos if a not in fisicos_chave and a != atributo_foco
        ]
        num_residuais = 1 if treinador else 0
        if attrs_tecnicos and num_residuais > 0:
            candidatos = random.sample(
                attrs_tecnicos, min(num_residuais, len(attrs_tecnicos))
            )
            for attr in candidatos:
                val = atributos[attr]
                if val < CAP_NATURAL:
                    chance = (
                        (0.30 + (fit_bonus * 0.5))
                        * _get_diminishing_returns_factor(val)
                        * age_mod
                    )
                    if random.random() < chance:
                        atributos[attr] += 1
                        melhorias[attr] = atributos[attr]

    elif foco == "fisico":
        # Atributo foco físico
        if atributo_foco in fisicos_chave:
            val = atributos.get(atributo_foco, 50)
            if val < CAP_MAXIMO:
                bonus_prep = preparador.get("bonus_fisico_pct", 0) if preparador else 0
                chance = (
                    (0.75 + bonus_prep + fit_bonus)
                    * _get_diminishing_returns_factor(val)
                    * age_mod
                )
                if random.random() < chance:
                    atributos[atributo_foco] = val + 1
                    melhorias[atributo_foco] = atributos[atributo_foco]
        else:
            # Treino físico geral: todos os atributos físicos
            for attr in fisicos_chave:
                if attr not in atributos:
                    continue
                val = atributos[attr]
                if val < CAP_NATURAL:
                    bonus_prep = (
                        preparador.get("bonus_fisico_pct", 0) if preparador else 0
                    )
                    chance = (
                        (0.40 + bonus_prep + (fit_bonus * 0.5))
                        * _get_diminishing_returns_factor(val)
                        * age_mod
                    )
                    if random.random() < chance:
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

            # Se tiver atributo foco mental
            target = (
                atributo_foco
                if atributo_foco in attrs_psico
                else random.choice(attrs_psico)
            )
            valor_atual = atributos_psico.get(target, 0)

            if valor_atual < CAP_NATURAL:
                chance_final = (
                    (chance + fit_bonus) * 2 if atributo_foco else chance + fit_bonus
                ) * age_mod
                if random.random() < chance_final:
                    atributos_psico[target] = min(CAP_NATURAL, valor_atual + 1 + bonus)
                    melhorias[target] = atributos_psico[target]

            # Treino psicológico sempre sobe moral
            ganho_moral = 12 if psicologo else 6
            jogador.moral = min(
                100, (getattr(jogador, "moral", 70) or 70) + ganho_moral
            )
            melhorias["moral"] = jogador.moral

    if melhorias and hasattr(jogador, "_sanitizar_atributos"):
        jogador._sanitizar_atributos()

    return melhorias
