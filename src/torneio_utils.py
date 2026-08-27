import random
from src.jogador import normalizar_nome


def extrair_codigo_pais(valor):
    """Extrai o código do país de uma string formatada como '[CC] Nome'."""
    if not valor or not isinstance(valor, str):
        return ""
    if valor.startswith("[") and "]" in valor:
        fechamento = valor.find("]")
        return valor[1:fechamento].upper()
    return valor.upper()


def mesmo_pais(a, b):
    """Verifica se dois jogadores/países são o mesmo baseado no código do país."""
    return extrair_codigo_pais(a) == extrair_codigo_pais(b)


def deduplicar_jogadores(jogadores):
    """Garante que a lista de jogadores não contenha duplicatas (mesmo nome + nacionalidade)."""
    jogadores_unicos = {}
    for j in jogadores:
        nome = j.get("nome", "")
        if not nome:
            continue
        chave = (normalizar_nome(nome), j.get("nacionalidade", "??"))
        if chave not in jogadores_unicos:
            jogadores_unicos[chave] = j
        else:
            existente = jogadores_unicos[chave]
            if j.get("pontos_ranking", 0) > existente.get("pontos_ranking", 0):
                jogadores_unicos[chave] = j
    return list(jogadores_unicos.values())


def weighted_sample_sem_reposicao(itens, pesos, k):
    """Realiza amostragem ponderada sem reposição."""
    if not itens or k <= 0:
        return []
    k = min(k, len(itens))
    pool = list(itens)
    w = list(pesos)
    selecionados = []
    for _ in range(k):
        try:
            idx = random.choices(range(len(pool)), weights=w, k=1)[0]
            selecionados.append(pool.pop(idx))
            w.pop(idx)
        except (ValueError, IndexError):
            break
    return selecionados


def garantir_dados_completos(jogador, ranking):
    """Garante que um objeto de jogador tenha todos os atributos necessários, buscando no ranking se preciso."""
    if isinstance(jogador, dict):
        atributos = jogador.get("atributos")
        atributos_psicologicos = jogador.get("atributos_psicologicos")
        overall = int(jogador.get("overall", 0) or 0)
        tem_dados_completos = (
            isinstance(atributos, dict)
            and bool(atributos)
            and isinstance(atributos_psicologicos, dict)
            and bool(atributos_psicologicos)
            and overall > 0
        )
        if tem_dados_completos:
            return jogador

        nome = jogador.get("nome", str(jogador))
        if ranking is not None and hasattr(ranking, "buscar_jogador_por_nome"):
            obj = ranking.buscar_jogador_por_nome(nome)
            if obj:
                combinado = dict(obj)
                combinado.update(jogador)
                combinado["atributos"] = (
                    jogador.get("atributos")
                    if isinstance(jogador.get("atributos"), dict)
                    and jogador.get("atributos")
                    else obj.get("atributos", {})
                )
                combinado["atributos_psicologicos"] = (
                    jogador.get("atributos_psicologicos")
                    if isinstance(jogador.get("atributos_psicologicos"), dict)
                    and jogador.get("atributos_psicologicos")
                    else obj.get("atributos_psicologicos", {})
                )
                if not int(combinado.get("overall", 0) or 0):
                    combinado["overall"] = int(obj.get("overall", 0) or 0)
                return combinado
        return jogador
    if hasattr(jogador, "nome"):
        nacionalidade = getattr(jogador, "nacionalidade", "??")
        if ranking is not None and hasattr(ranking, "buscar_jogador_por_nome"):
            obj = ranking.buscar_jogador_por_nome(getattr(jogador, "nome", ""))
            if obj:
                return obj
        return {
            "nome": getattr(jogador, "nome", str(jogador)),
            "nacionalidade": nacionalidade,
        }
    nome = (
        jogador.get("nome", str(jogador)) if isinstance(jogador, dict) else str(jogador)
    )
    if ranking is None or not hasattr(ranking, "buscar_jogador_por_nome"):
        return {"nome": nome, "nacionalidade": "??"}
    obj = ranking.buscar_jogador_por_nome(nome)
    if obj:
        return obj
    return {"nome": nome, "nacionalidade": "??"}
