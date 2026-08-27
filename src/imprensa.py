# Alterado por Claude — extração de dados hardcoded para JSON externo
import random
import json
from pathlib import Path

_DB_DIR = Path(__file__).parent.parent / "db"

# Alterado por Claude — carrega opções compartilhadas (_OPT_*) do JSON externo
def _carregar_opcoes():
    caminho = _DB_DIR / "imprensa_opcoes.json"
    if caminho.exists():
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# Alterado por Claude — carrega perguntas do JSON externo e resolve referências _OPT_*
def _carregar_perguntas():
    caminho = _DB_DIR / "imprensa_perguntas.json"
    if not caminho.exists():
        # fallback para formato antigo
        caminho_antigo = _DB_DIR / "perguntas_imprensa.json"
        if caminho_antigo.exists():
            with open(caminho_antigo, "r", encoding="utf-8") as f:
                dados_antigos = json.load(f)
            return {
                "pre": dados_antigos.get("pre_jogo", []),
                "pos": dados_antigos.get("pos_jogo", []),
                "geral": dados_antigos.get("geral", []),
            }
        return {"pre": [], "pos": [], "geral": []}

    opcoes_map = _carregar_opcoes()

    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)

    # Reconstrói etiquetas como set e resolve referências _OPT_* nas opcoes
    resultado = {}
    for secao, perguntas in dados.items():
        lista = []
        for pergunta in perguntas:
            p = dict(pergunta)
            # Alterado por Claude — etiquetas armazenadas como lista no JSON,
            # reconstruídas como set em memória
            p["etiquetas"] = set(p.get("etiquetas", []))
            # Alterado por Claude — resolve referências de string tipo "_OPT_CONFIDENTE"
            opcoes = p.get("opcoes", [])
            if isinstance(opcoes, str):
                chave = opcoes.lstrip("_")
                p["opcoes"] = opcoes_map.get(chave, opcoes_map.get(opcoes, []))
            lista.append(p)
        resultado[secao] = lista
    return resultado


_DADOS_IMPRENSA = _carregar_perguntas()


def obter_pergunta_contextual(contexto_id, **kwargs):
    """
    Retorna uma pergunta aleatória do banco de dados baseada no contexto.
    Contextos: 'pre', 'pos', 'geral' (também aceita 'pre_jogo'/'pos_jogo' como alias).
    """
    # Alterado por Claude — mapeia aliases dos contextos antigos para as novas chaves
    _alias = {"pre_jogo": "pre", "pos_jogo": "pos"}
    contexto_id = _alias.get(contexto_id, contexto_id)

    pool = _DADOS_IMPRENSA.get(contexto_id, [])
    if not pool and contexto_id != "geral":
        pool = _DADOS_IMPRENSA.get("geral", [])

    if not pool:
        return None

    # Filtra por etiquetas se fornecidas
    etiquetas_alvo = kwargs.get("etiquetas")
    if etiquetas_alvo:
        pool_filtrado = [
            q
            for q in pool
            if any(tag in q.get("etiquetas", set()) for tag in etiquetas_alvo)
        ]
        if pool_filtrado:
            pool = pool_filtrado

    return random.choice(pool)


def processar_resposta_imprensa(jogador, pergunta, opcao_escolhida):
    """
    Aplica os efeitos da resposta escolhida ao jogador (moral, reputação e persona).
    """
    moral_ganha = opcao_escolhida.get("moral", 0)
    reputacao_ganha = opcao_escolhida.get("reputacao", 0)

    jogador.moral = max(0, min(100, (getattr(jogador, "moral", 70) or 70) + moral_ganha))
    jogador.reputacao = max(
        0, min(100, (getattr(jogador, "reputacao", 50) or 50) + reputacao_ganha)
    )

    # Lógica de Persona Narrativa
    persona = getattr(jogador, "persona", {"pontos": {"iceman": 0, "badboy": 0, "champ": 0}, "ativa": "Neutro", "titulo": "Promessa"})
    p_pts = persona["pontos"]
    
    p_pts["iceman"] += opcao_escolhida.get("iceman", 0)
    p_pts["badboy"] += opcao_escolhida.get("badboy", 0)
    p_pts["champ"] += opcao_escolhida.get("champ", 0)

    # Define persona ativa com base no maior pontuador
    maior = max(p_pts, key=p_pts.get)
    if p_pts[maior] > 0:
        try:
            from pathlib import Path
            import json
            caminho = Path(__file__).parent.parent / "db" / "narrativa_geral.json"
            with open(caminho, "r", encoding="utf-8") as f:
                narrativa = json.load(f)
            
            titulos = narrativa.get("titles", {})
            mapeamento_ids = {
                "iceman": "Iceman",
                "badboy": "Bad Boy",
                "champ": "People's Champ"
            }
            persona_id = mapeamento_ids[maior]
            persona["ativa"] = persona_id
            persona["titulo"] = titulos.get(persona_id, "Veterano")
        except Exception:
            # Fallback
            mapeamento = {
                "iceman": ("Iceman", "Foco Absoluto"),
                "badboy": ("Bad Boy", "Rebelde do Tour"),
                "champ": ("People's Champ", "Ídolo Local")
            }
            persona["ativa"], persona["titulo"] = mapeamento[maior]
    
    jogador.persona = persona

    return moral_ganha, reputacao_ganha


def disparar_entrevista(*args, **kwargs):
    if not args:
        return None

    if hasattr(args[0], "nome"):
        jogador = args[0]
        contexto_id = kwargs.pop("contexto", kwargs.pop("contexto_id", "geral"))
    else:
        if len(args) < 3:
            return None
        jogador = args[1]
        contexto_id = args[2]

    pergunta = obter_pergunta_contextual(contexto_id, **kwargs)
    if not pergunta:
        return None

    opcoes = pergunta.get("opcoes", [])
    if not opcoes:
        return {"pergunta": pergunta, "efeito": (0, 0)}

    efeito = processar_resposta_imprensa(jogador, pergunta, opcoes[0])
    return {"pergunta": pergunta, "efeito": efeito}
