from src.utils.entidade_utils import obter_atributos, obter_atributos_psicologicos
from src.constants.match_constants import MatchPointStats
from src.match_state import ContextoPonto
from src.repositories.ranking_repository import load_singles_ranking


def eh_dupla_entidade(entidade) -> bool:
    if isinstance(entidade, dict):
        return (
            bool(entidade.get("is_dupla"))
            or len(entidade.get("jogadores", []) or []) >= 2
        )
    return False


def integrantes_dupla(entidade) -> list[dict]:
    if isinstance(entidade, dict):
        integrantes = entidade.get("jogadores", []) or []
        return [item for item in integrantes if isinstance(item, dict)]
    return []


def perfil_duplas_entidade(entidade) -> dict:
    if not eh_dupla_entidade(entidade):
        return {
            "ativa": False,
            "duplas": 60.0,
            "voleio": 50.0,
            "velocidade": 50.0,
            "leitura": 50.0,
            "quimica": 0.0,
            "vel_saque": 50.0,
            "fragilidade_retorno": 0.0,
            "fragilidade_rede": 0.0,
        }

    atributos = obter_atributos(entidade)
    psico = obter_atributos_psicologicos(entidade, copiar=True)
    integrantes = integrantes_dupla(entidade)
    quimica = 0.0
    if isinstance(entidade, dict):
        quimica = float((entidade.get("quimica", {}) or {}).get("bonus_total", 0) or 0)

    fragilidade_retorno = 0.0
    fragilidade_rede = 0.0
    if integrantes:
        retorno_vals = []
        rede_vals = []
        for item in integrantes:
            atr = obter_atributos(item)
            retorno_vals.append(
                atr.get("backhand", 50) * 0.45
                + atr.get("velocidade", 50) * 0.35
                + atr.get("slice", 50) * 0.20
            )
            rede_vals.append(
                atr.get("voleio", 50) * 0.55
                + atr.get("velocidade", 50) * 0.25
                + atr.get("duplas", 60) * 0.20
            )
        fragilidade_retorno = max(
            0.0, sum(retorno_vals) / len(retorno_vals) - min(retorno_vals)
        )
        fragilidade_rede = max(0.0, sum(rede_vals) / len(rede_vals) - min(rede_vals))

    return {
        "ativa": True,
        "duplas": float(atributos.get("duplas", 60) or 60),
        "voleio": float(atributos.get("voleio", 50) or 50),
        "velocidade": float(atributos.get("velocidade", 50) or 50),
        "leitura": float(psico.get("leitura_de_jogo", 50) or 50),
        "quimica": quimica,
        "vel_saque": float(atributos.get("vel_saque", 50) or 50),
        "fragilidade_retorno": fragilidade_retorno,
        "fragilidade_rede": fragilidade_rede,
    }


def ajuste_duplas_saque_devolucao(
    contexto: ContextoPonto,
    equipe_sacadora,
    equipe_receptora,
    estrategia_sacador: dict,
    poder_saque: float,
    chance_ace: float,
    poder_devolucao: float,
    stats_info: MatchPointStats,
) -> tuple[float, float, float]:
    perfil_sacador = perfil_duplas_entidade(equipe_sacadora)
    perfil_receptor = perfil_duplas_entidade(equipe_receptora)

    if not perfil_sacador["ativa"] and not perfil_receptor["ativa"]:
        return poder_saque, chance_ace, poder_devolucao

    estilo = estrategia_sacador.get("estilo", "atacar_do_fundo")

    if perfil_sacador["ativa"]:
        bonus_formacao = (perfil_sacador["duplas"] - 60.0) / 220.0 + perfil_sacador[
            "quimica"
        ] / 120.0
        poder_saque *= 1.0 + max(0.0, bonus_formacao)
        if estilo == "atacar_na_rede":
            chance_ace *= 1.0 + max(0.02, (perfil_sacador["voleio"] - 58.0) / 220.0)
            msg = (
                "Sua dupla está servindo para subir e fechar a rede"
                if contexto.sacador == "j"
                else "O rival está servindo para atacar a rede"
            )
            if msg not in stats_info.insights:
                stats_info.insights.append(msg)

    if perfil_receptor["ativa"]:
        alvo_fraco = perfil_receptor["fragilidade_retorno"]
        if alvo_fraco > 4:
            poder_saque *= 1.0 + min(0.08, alvo_fraco / 220.0)
            chance_ace *= 1.0 + min(0.06, alvo_fraco / 260.0)
            msg = (
                "Você está mirando no devolvedor mais vulnerável"
                if contexto.sacador == "j"
                else "O rival está escolhendo seu lado mais exposto na devolução"
            )
            if msg not in stats_info.insights:
                stats_info.insights.append(msg)
        cobertura = (
            (perfil_receptor["velocidade"] - 55.0) / 260.0
            + (perfil_receptor["leitura"] - 55.0) / 320.0
            + perfil_receptor["quimica"] / 180.0
        )
        poder_devolucao *= 1.0 + max(0.0, cobertura)

    return poder_saque, chance_ace, poder_devolucao


def ajuste_duplas_rally(
    equipe_j,
    equipe_a,
    poder_rally_j: float,
    poder_rally_a: float,
    estrategia_j: dict,
    estrategia_a: dict,
    stats_info: MatchPointStats,
    descricoes: list[str] | None = None,
) -> tuple[float, float]:
    perfil_j = perfil_duplas_entidade(equipe_j)
    perfil_a = perfil_duplas_entidade(equipe_a)
    if not perfil_j["ativa"] and not perfil_a["ativa"]:
        return poder_rally_j, poder_rally_a

    def _bonus_rede(perfil: dict, estrategia_lado: dict) -> float:
        if not perfil["ativa"]:
            return 0.0
        estilo = estrategia_lado.get("estilo", "atacar_do_fundo")
        base = perfil["quimica"] / 150.0 + (perfil["duplas"] - 60.0) / 260.0
        if estilo == "atacar_na_rede":
            base += (perfil["voleio"] - 58.0) / 200.0
        elif estilo == "atacar_pelo_meio":
            base += (perfil["leitura"] - 55.0) / 340.0
        else:
            base += (perfil["velocidade"] - 55.0) / 360.0
        return max(0.0, base)

    poder_rally_j *= 1.0 + _bonus_rede(perfil_j, estrategia_j)
    poder_rally_a *= 1.0 + _bonus_rede(perfil_a, estrategia_a)

    if perfil_j["ativa"] and perfil_a["ativa"]:
        if (
            perfil_a["fragilidade_rede"] > 5
            and estrategia_j.get("estilo") == "atacar_na_rede"
        ):
            poder_rally_j *= 1.0 + min(0.09, perfil_a["fragilidade_rede"] / 180.0)
            if "Sua dupla está ganhando a frente da rede" not in stats_info.insights:
                stats_info.insights.append("Sua dupla está ganhando a frente da rede")
            if descricoes is not None:
                descricoes.append("A dupla fecha a rede e encurta o espaço do rival.")
        if (
            perfil_j["fragilidade_rede"] > 5
            and estrategia_a.get("estilo") == "atacar_na_rede"
        ):
            poder_rally_a *= 1.0 + min(0.09, perfil_j["fragilidade_rede"] / 180.0)
            if "O rival está vencendo na cobertura de rede" not in stats_info.insights:
                stats_info.insights.append("O rival está vencendo na cobertura de rede")
            if descricoes is not None:
                descricoes.append(
                    "O rival intercepta a bola cedo e toma a frente da rede."
                )

    return poder_rally_j, poder_rally_a


def buscar_jogador_por_nome_ranking(
    nome_save: str, nome: str, generos: list[str]
) -> dict | None:
    from src.jogador import normalizar_nome

    alvo = normalizar_nome(nome)
    if not alvo:
        return None
    for genero in generos:
        try:
            ranking = load_singles_ranking(nome_save, genero=genero)
            for entrada in getattr(ranking, "ranking", []) or []:
                if normalizar_nome(entrada.get("nome", "")) == alvo:
                    return dict(entrada)
        except Exception:
            continue
    return None


def resolver_integrante_dupla(
    nome_save: str,
    item,
    genero_padrao: str,
    incluir_genero_oposto: bool = False,
) -> dict:
    from src.utils.match_runtime_utils import entidade_para_dict

    base = entidade_para_dict(item)
    if base.get("atributos"):
        return base
    generos = [genero_padrao]
    if incluir_genero_oposto:
        generos.append("feminino" if genero_padrao == "masculino" else "masculino")
    encontrado = buscar_jogador_por_nome_ranking(
        nome_save, base.get("nome", ""), generos
    )
    if not encontrado:
        return base
    encontrado.update({k: v for k, v in base.items() if v not in (None, "", {}, [])})
    return encontrado


def compor_dupla_efetiva(save_name: str, jogador, adversario: dict) -> tuple:
    from src.duplas import fundir_dupla
    from src.jogador import normalizar_nome
    from src.utils.match_runtime_utils import valor_entidade

    parceiro_ref = getattr(jogador, "parceiro_duplas", None)
    if not parceiro_ref:
        return jogador, adversario
    genero_jogador = str(getattr(jogador, "genero", "masculino") or "masculino")
    tipo_duplas = str(getattr(jogador, "tipo_duplas_atual", "mesmo_genero") or "")
    genero_parceiro = (
        ("feminino" if genero_jogador == "masculino" else "masculino")
        if tipo_duplas == "mista"
        else genero_jogador
    )
    parceiro = resolver_integrante_dupla(
        save_name,
        parceiro_ref,
        genero_padrao=genero_parceiro,
        incluir_genero_oposto=(tipo_duplas == "mista"),
    )
    vinculo = None
    parceiro_nome = parceiro.get("nome", "")
    parceiro_norm = normalizar_nome(parceiro_nome)
    for chave, valor in (getattr(jogador, "vinculos_dupla", {}) or {}).items():
        if normalizar_nome(str(chave)) == parceiro_norm:
            vinculo = valor
            break
    equipe_j = fundir_dupla(
        jogador,
        parceiro,
        nome_equipe=f"{getattr(jogador, 'nome', 'Jogador')} / {parceiro_nome or 'Parceiro'}",
        vinculo=vinculo,
    )
    equipe_j["moral"] = round(
        (
            float(valor_entidade(jogador, "moral", 70) or 70)
            + float(valor_entidade(parceiro, "moral", 70) or 70)
        )
        / 2.0,
        1,
    )
    equipe_j["ritmo_jogo"] = round(
        (
            float(valor_entidade(jogador, "ritmo_jogo", 50) or 50)
            + float(valor_entidade(parceiro, "ritmo_jogo", 50) or 50)
        )
        / 2.0,
        1,
    )

    integrantes_adv = list(adversario.get("jogadores", []) or [])
    if len(integrantes_adv) < 2:
        partes = [
            p.strip()
            for p in str(adversario.get("nome", "") or "").split("/")
            if p.strip()
        ]
        if len(partes) >= 2:
            integrantes_adv = [{"nome": nome} for nome in partes[:2]]
    if len(integrantes_adv) < 2:
        return equipe_j, adversario

    adv_a = resolver_integrante_dupla(
        save_name,
        integrantes_adv[0],
        genero_padrao=genero_jogador,
        incluir_genero_oposto=(tipo_duplas == "mista"),
    )
    adv_b = resolver_integrante_dupla(
        save_name,
        integrantes_adv[1],
        genero_padrao=genero_parceiro,
        incluir_genero_oposto=(tipo_duplas == "mista"),
    )
    equipe_a = fundir_dupla(
        adv_a,
        adv_b,
        nome_equipe=adversario.get("nome")
        or f"{adv_a.get('nome', 'A')} / {adv_b.get('nome', 'B')}",
    )
    equipe_a["moral"] = round(
        (
            float(valor_entidade(adv_a, "moral", 70) or 70)
            + float(valor_entidade(adv_b, "moral", 70) or 70)
        )
        / 2.0,
        1,
    )
    equipe_a["ritmo_jogo"] = round(
        (
            float(valor_entidade(adv_a, "ritmo_jogo", 50) or 50)
            + float(valor_entidade(adv_b, "ritmo_jogo", 50) or 50)
        )
        / 2.0,
        1,
    )
    equipe_a.update(
        {
            "ranking_pos": adversario.get("ranking_pos", adversario.get("ranking")),
            "historico_partidas": list(adversario.get("historico_partidas", []) or []),
            "jogadores": [adv_a, adv_b],
        }
    )
    return equipe_j, equipe_a
