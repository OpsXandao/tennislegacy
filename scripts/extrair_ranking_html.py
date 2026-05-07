"""
Extrai ranking ATP do HTML salvo e mescla com db/ranking_atp.json.
- Nome e país: do HTML (URL do perfil + flag)
- Pontos: do HTML
- Idade: do ranking_atp_raw.md (top ~200) ou JSON existente
- Atributos e overall: gerados para jogadores novos
"""

import json
import math
import random
import re
import os

random.seed(42)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Mapeamento: código 3 letras ATP → "[ISO-2] Nome em português"
# ---------------------------------------------------------------------------
PAISES = {
    "alg": "[DZ] Argélia",
    "ang": "[AO] Angola",
    "arg": "[AR] Argentina",
    "arm": "[AM] Armênia",
    "aus": "[AU] Austrália",
    "aut": "[AT] Áustria",
    "bah": "[BS] Bahamas",
    "bar": "[BB] Barbados",
    "bel": "[BE] Bélgica",
    "ber": "[BM] Bermuda",
    "bih": "[BA] Bósnia e Herzegovina",
    "blr": "[BY] Bielorrússia",
    "bol": "[BO] Bolívia",
    "bra": "[BR] Brasil",
    "bul": "[BG] Bulgária",
    "bur": "[BF] Burkina Faso",
    "can": "[CA] Canadá",
    "chi": "[CL] Chile",
    "chn": "[CN] China",
    "civ": "[CI] Costa do Marfim",
    "col": "[CO] Colômbia",
    "crc": "[CR] Costa Rica",
    "cro": "[HR] Croácia",
    "cyp": "[CY] Chipre",
    "cze": "[CZ] Czechia",
    "den": "[DK] Dinamarca",
    "dom": "[DO] República Dominicana",
    "ecu": "[EC] Equador",
    "egy": "[EG] Egito",
    "esa": "[SV] El Salvador",
    "esp": "[ES] Espanha",
    "est": "[EE] Estônia",
    "fin": "[FI] Finlândia",
    "fra": "[FR] França",
    "gbr": "[GB] Grã-Bretanha",
    "geo": "[GE] Geórgia",
    "ger": "[DE] Alemanha",
    "gha": "[GH] Gana",
    "gre": "[GR] Grécia",
    "gua": "[GT] Guatemala",
    "gud": "[GP] Guadalupe",
    "hkg": "[HK] Hong Kong",
    "hun": "[HU] Hungria",
    "ina": "[ID] Indonésia",
    "ind": "[IN] Índia",
    "iri": "[IR] Irã",
    "irl": "[IE] Irlanda",
    "isr": "[IL] Israel",
    "ita": "[IT] Itália",
    "jam": "[JM] Jamaica",
    "jor": "[JO] Jordânia",
    "jpn": "[JP] Japão",
    "kaz": "[KZ] Cazaquistão",
    "kor": "[KR] Coreia do Sul",
    "kos": "[XK] Kosovo",
    "ksa": "[SA] Arábia Saudita",
    "kuw": "[KW] Kuwait",
    "lat": "[LV] Letônia",
    "lbn": "[LB] Líbano",
    "ltu": "[LT] Lituânia",
    "lux": "[LU] Luxemburgo",
    "mar": "[MA] Marrocos",
    "mas": "[MY] Malásia",
    "mda": "[MD] Moldávia",
    "mex": "[MX] México",
    "mkd": "[MK] Macedônia do Norte",
    "mlt": "[MT] Malta",
    "mne": "[ME] Montenegro",
    "mon": "[MC] Mônaco",
    "nca": "[NI] Nicarágua",
    "ned": "[NL] Holanda",
    "nmi": "[MP] Ilhas Marianas do Norte",
    "nor": "[NO] Noruega",
    "nzl": "[NZ] Nova Zelândia",
    "pak": "[PK] Paquistão",
    "par": "[PY] Paraguai",
    "per": "[PE] Peru",
    "phi": "[PH] Filipinas",
    "pol": "[PL] Polônia",
    "por": "[PT] Portugal",
    "rou": "[RO] Romênia",
    "rsa": "[ZA] África do Sul",
    "rus": "[RU] Rússia",
    "sen": "[SN] Senegal",
    "sgp": "[SG] Cingapura",
    "slo": "[SI] Eslovênia",
    "srb": "[RS] Sérvia",
    "sui": "[CH] Suíça",
    "svk": "[SK] Eslováquia",
    "swe": "[SE] Suécia",
    "syr": "[SY] Síria",
    "tha": "[TH] Tailândia",
    "tpe": "[TW] Taipei Chinês",
    "tun": "[TN] Tunísia",
    "tur": "[TR] Turquia",
    "ukr": "[UA] Ucrânia",
    "uru": "[UY] Uruguai",
    "usa": "[US] USA",
    "uzb": "[UZ] Uzbequistão",
    "ven": "[VE] Venezuela",
    "vie": "[VN] Vietnã",
}


def nome_da_url(url):
    m = re.search(r"/players/([^/]+)/", url)
    if not m:
        return None
    slug = m.group(1)
    return " ".join(p.capitalize() for p in slug.split("-"))


def overall_por_pontos(pts):
    if pts >= 8000:
        return random.randint(86, 90)
    elif pts >= 4000:
        return random.randint(82, 87)
    elif pts >= 2000:
        return random.randint(77, 83)
    elif pts >= 1000:
        return random.randint(72, 78)
    elif pts >= 500:
        return random.randint(66, 73)
    elif pts >= 200:
        return random.randint(60, 66)
    elif pts >= 100:
        return random.randint(55, 61)
    elif pts >= 50:
        return random.randint(50, 56)
    else:
        return random.randint(43, 51)


def gerar_atributos(overall):
    def v(d=9):
        return max(40, min(99, overall + random.randint(-d, d)))

    return {
        "saque": v(10),
        "forehand": v(10),
        "backhand": v(10),
        "topspin": v(8),
        "voleio": v(12),
        "slice": v(10),
        "movimento": v(8),
        "lob": v(10),
        "winner": v(10),
        "fisico": 60,
    }


def gerar_psicologicos(overall):
    base = max(30, min(90, int(overall * 0.88)))

    def v():
        return max(30, min(99, base + random.randint(-12, 12)))

    return {
        "concentracao": v(),
        "agressividade": v(),
        "leitura_de_jogo": v(),
        "determinacao": v(),
    }


# ---------------------------------------------------------------------------
# 1. Parse HTML
# ---------------------------------------------------------------------------
HTML_PATH = os.path.join(
    BASE,
    "ATP Rankings _ PIF ATP Rankings (Singles) _ ATP Tour _ Tennis _ ATP Tour _ Tennis.html",
)
print(f"Lendo HTML: {os.path.basename(HTML_PATH)}")
with open(HTML_PATH, encoding="utf-8") as f:
    content = f.read()

rows = content.split('<tr class="lower-row">')

ROW_RANK = re.compile(r'class="rank bold heavy tiny-cell"[^>]*>(\d+)<')
ROW_FLAG = re.compile(r"flags\.svg#flag-([a-z]+)")
ROW_URL = re.compile(r'href="(https://www\.atptour\.com/en/players/[^"]+/overview)"')
ROW_PTS = re.compile(
    r'class="points center bold extrabold small-cell"[^>]*>.*?<a[^>]*>\s*([\d,]+)',
    re.DOTALL,
)

html_players = []
vistos = set()

for row in rows[1:]:
    m_rank = ROW_RANK.search(row)
    m_flag = ROW_FLAG.search(row)
    m_url = ROW_URL.search(row)
    m_pts = ROW_PTS.search(row)

    if not (m_rank and m_flag and m_url and m_pts):
        continue

    rank = int(m_rank.group(1))
    flag = m_flag.group(1)
    url = m_url.group(1)
    pontos = int(m_pts.group(1).replace(",", ""))
    nome = nome_da_url(url)
    if not nome:
        continue

    chave = (rank, nome)
    if chave in vistos:
        continue
    vistos.add(chave)

    html_players.append(
        {
            "rank": rank,
            "nome": nome,
            "nacionalidade": PAISES.get(flag, f"[??] {flag.upper()}"),
            "pontos": pontos,
        }
    )

print(f"Extraídos do HTML: {len(html_players)} jogadores")

# ---------------------------------------------------------------------------
# 2. Lê idades do MD (top ~200)
# ---------------------------------------------------------------------------
MD_PATH = os.path.join(BASE, "docs", "ranking_atp_raw.md")
idades_por_nome = {}

if os.path.exists(MD_PATH):
    with open(MD_PATH, encoding="utf-8") as f:
        texto = f.read()

    linhas_md = []
    dentro = False
    for linha in texto.splitlines():
        if linha.strip() == "```":
            dentro = not dentro
            continue
        if dentro:
            linhas_md.append(linha)

    RANK_RE = re.compile(r"^\s*\d+(?:T)?\s*$")
    CHANGE_RE = re.compile(r"^\s*[+-]?\d+\s*$")
    STATS_RE = re.compile(r"^\s*(\d+)\s+([\d,]+)\s")

    i = 0
    while i < len(linhas_md):
        l = linhas_md[i].strip()
        if RANK_RE.match(l):
            i += 1
            if i >= len(linhas_md):
                break
            prox = linhas_md[i].strip()
            if CHANGE_RE.match(prox):
                i += 1
                if i >= len(linhas_md):
                    break
                prox = linhas_md[i].strip()
            nome = prox
            i += 1
            if i >= len(linhas_md):
                break
            stats = linhas_md[i].strip()
            m = STATS_RE.match(stats)
            if m and re.search(r"[A-Za-z]", nome):
                idades_por_nome[nome.lower()] = int(m.group(1))
            i += 1
        else:
            i += 1

    print(f"Idades lidas do MD: {len(idades_por_nome)}")

# ---------------------------------------------------------------------------
# 3. Carrega JSON existente
# ---------------------------------------------------------------------------
JSON_PATH = os.path.join(BASE, "db", "ranking_atp.json")
with open(JSON_PATH, encoding="utf-8") as f:
    existentes_lista = json.load(f)

existentes = {" ".join(p["nome"].lower().split()): p for p in existentes_lista}
max_id = max(
    (p.get("id", 0) for p in existentes_lista if isinstance(p.get("id"), int)),
    default=200,
)

# ---------------------------------------------------------------------------
# 4. Mescla
# ---------------------------------------------------------------------------
resultado = []
processados = set()

for item in html_players:
    nome = item["nome"]
    nome_norm = " ".join(nome.lower().split())

    # Idade: MD > JSON existente > aleatório
    idade = idades_por_nome.get(nome_norm)

    if nome_norm in existentes:
        p = existentes[nome_norm].copy()
        p["pontos"] = item["pontos"]
        p["pontos_ranking"] = item["pontos"]
        if "nacionalidade" not in p:
            p["nacionalidade"] = item["nacionalidade"]
        if idade is not None:
            p["idade"] = idade  # atualiza com o dado real
        # Preenche campos faltando para entradas mínimas
        if "overall" not in p:
            p["overall"] = overall_por_pontos(item["pontos"])
        if "atributos" not in p:
            p["atributos"] = gerar_atributos(p["overall"])
        if "id" not in p:
            max_id += 1
            p["id"] = max_id
        if "atributos_psicologicos" not in p:
            p["atributos_psicologicos"] = gerar_psicologicos(p["overall"])
        for campo, val in [
            ("pontos_detalhados", []),
            ("trofeus", []),
            ("historico_torneios", []),
            ("pontos_ytd", 0),
            ("dinheiro", 0),
            ("pontos_duplas", 0),
            ("pontos_detalhados_duplas", []),
            ("pico_carreira", item["rank"]),
            ("is_bot", False),
        ]:
            if campo not in p:
                p[campo] = val
    else:
        # Novo jogador
        max_id += 1
        overall = overall_por_pontos(item["pontos"])
        idade_final = idade if idade is not None else random.randint(18, 33)
        p = {
            "nome": nome,
            "nacionalidade": item["nacionalidade"],
            "idade": idade_final,
            "overall": overall,
            "pontos": item["pontos"],
            "atributos": gerar_atributos(overall),
            "id": max_id,
            "atributos_psicologicos": gerar_psicologicos(overall),
            "pontos_detalhados": [],
            "trofeus": [],
            "historico_torneios": [],
            "pontos_ytd": 0,
            "dinheiro": 0,
            "pontos_duplas": 0,
            "pontos_detalhados_duplas": [],
            "pico_carreira": item["rank"],
            "pontos_ranking": item["pontos"],
            "is_bot": False,
        }

    resultado.append(p)
    processados.add(nome_norm)

# ---------------------------------------------------------------------------
# 5. Salva
# ---------------------------------------------------------------------------
resultado.sort(key=lambda x: x.get("pontos", 0), reverse=True)

with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(resultado, f, indent=2, ensure_ascii=False)

print(f"\n✅ ranking_atp.json salvo com {len(resultado)} jogadores")
print(f"   Já existiam (mantidos): {len(processados & set(existentes.keys()))}")
print(f"   Novos adicionados: {len(resultado) - len(existentes_lista)}")
print(f"   Com atributos completos: {sum(1 for p in resultado if 'atributos' in p)}")
print(
    f"   Primeiro: {resultado[0]['nome']} ({resultado[0]['pontos']} pts, overall {resultado[0].get('overall','?')})"
)
print(f"   100º:     {resultado[99]['nome']} ({resultado[99]['pontos']} pts)")
print(f"   Último:   {resultado[-1]['nome']} ({resultado[-1]['pontos']} pts)")
