"""
Parse o ranking ATP a partir do texto copiado do site (colado em docs/ranking_atp_raw.md)
e mescla com db/ranking_atp.json, adicionando/atualizando nome, idade e pontos.
O overall será gerado separadamente.
"""

import json
import re
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------------------
# 1. Lê o texto cru do MD
# ---------------------------------------------------------------------------
MD_PATH = os.path.join(BASE, "docs", "ranking_atp_raw.md")
with open(MD_PATH, encoding="utf-8") as f:
    texto = f.read()

# Remove delimitadores markdown
linhas = []
dentro_bloco = False
for linha in texto.splitlines():
    if linha.strip() == "```":
        dentro_bloco = not dentro_bloco
        continue
    if dentro_bloco:
        linhas.append(linha)

# ---------------------------------------------------------------------------
# 2. Parser do formato ATP:
#    RANK (linha)
#    [variação opcional — linha com só número/sinal]
#    NOME (linha)
#    IDADE    PONTOS    ...
# ---------------------------------------------------------------------------
RANK_RE = re.compile(r"^\s*(\d+)(?:T)?\s*$")  # "1" ou "100T"
CHANGE_RE = re.compile(r"^\s*[+-]?\d+\s*$")  # "-3" ou "18"
STATS_RE = re.compile(r"^\s*(\d+)\s+([\d,]+)\s")  # "22    13,550  ..."


def parse_linhas(linhas):
    jogadores = []
    i = 0
    while i < len(linhas):
        linha = linhas[i].strip()

        # Detecta linha de rank
        m_rank = RANK_RE.match(linha)
        if not m_rank:
            i += 1
            continue

        rank = int(m_rank.group(1))
        i += 1
        if i >= len(linhas):
            break

        # Pula linha de variação (opcional)
        prox = linhas[i].strip()
        if (
            CHANGE_RE.match(prox)
            and not prox.isdigit()
            or (CHANGE_RE.match(prox) and int(prox) != rank)
        ):
            # é variação (+10, -3, 18, etc.)
            i += 1
            if i >= len(linhas):
                break
            prox = linhas[i].strip()

        # Agora prox deve ser o nome
        # Nome: linha que não casa com RANK_RE, CHANGE_RE, STATS_RE
        # e tem letras
        nome = prox
        if not nome or not re.search(r"[A-Za-z]", nome):
            i += 1
            continue

        i += 1
        if i >= len(linhas):
            break

        # Próxima: stats (idade    pontos ...)
        stats_linha = linhas[i].strip()
        m_stats = STATS_RE.match(stats_linha)
        if not m_stats:
            # tenta avançar uma
            i += 1
            if i >= len(linhas):
                break
            stats_linha = linhas[i].strip()
            m_stats = STATS_RE.match(stats_linha)
            if not m_stats:
                continue

        idade = int(m_stats.group(1))
        pontos = int(m_stats.group(2).replace(",", ""))
        i += 1

        jogadores.append({"rank": rank, "nome": nome, "idade": idade, "pontos": pontos})

    return jogadores


jogadores_texto = parse_linhas(linhas)
print(f"Jogadores parseados do texto: {len(jogadores_texto)}")
if jogadores_texto:
    print(f"  Primeiro: {jogadores_texto[0]}")
    print(f"  Último:   {jogadores_texto[-1]}")

# ---------------------------------------------------------------------------
# 3. Carrega JSON existente
# ---------------------------------------------------------------------------
JSON_PATH = os.path.join(BASE, "db", "ranking_atp.json")
with open(JSON_PATH, encoding="utf-8") as f:
    jogadores_json = json.load(f)


# Índice por nome normalizado (lowercase, sem espaços extras)
def normalizar(nome):
    return " ".join(nome.lower().split())


existentes = {normalizar(p["nome"]): p for p in jogadores_json}
max_id = max(
    (p.get("id", 0) for p in jogadores_json if isinstance(p.get("id"), int)),
    default=200,
)

# ---------------------------------------------------------------------------
# 4. Mescla: atualiza existentes, adiciona novos
# ---------------------------------------------------------------------------
resultado = []
nomes_processados = set()

for item in jogadores_texto:
    nome = item["nome"]
    nome_norm = normalizar(nome)

    if nome_norm in existentes:
        p = existentes[nome_norm].copy()
        # Atualiza pontos e idade (se já não tiver)
        p["pontos"] = item["pontos"]
        p["pontos_ranking"] = item["pontos"]
        if "idade" not in p or p.get("idade") is None:
            p["idade"] = item["idade"]
        else:
            p["idade"] = item["idade"]  # sempre atualiza idade do texto
    else:
        # Novo jogador — estrutura mínima (overall será adicionado depois)
        max_id += 1
        p = {
            "nome": nome,
            "idade": item["idade"],
            "pontos": item["pontos"],
            "pontos_ranking": item["pontos"],
            "is_bot": False,
            "id": max_id,
        }

    resultado.append(p)
    nomes_processados.add(nome_norm)

# Adiciona jogadores do JSON que não apareceram no texto (saves existentes, etc.)
for p in jogadores_json:
    if normalizar(p["nome"]) not in nomes_processados:
        resultado.append(p)

# Ordena por pontos
resultado.sort(key=lambda x: x.get("pontos", 0), reverse=True)

# ---------------------------------------------------------------------------
# 5. Salva
# ---------------------------------------------------------------------------
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(resultado, f, indent=2, ensure_ascii=False)

total_novos = sum(
    1
    for p in resultado
    if "atributos" not in p
    and normalizar(p["nome"]) not in {normalizar(x["nome"]) for x in jogadores_json}
)
print(f"\n✅ Salvo: {len(resultado)} jogadores")
print(f"   Com atributos completos: {sum(1 for p in resultado if 'atributos' in p)}")
print(
    f"   Estrutura mínima (sem atributos): {sum(1 for p in resultado if 'atributos' not in p)}"
)
print(f"   Primeiro: {resultado[0]['nome']} ({resultado[0]['pontos']} pts)")
print(f"   Último:   {resultado[-1]['nome']} ({resultado[-1]['pontos']} pts)")
