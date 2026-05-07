"""
Importa ranking de duplas (ATP/WTA, texto bruto) e sincroniza no ranking base.

Entrada esperada:
- Arquivo texto/markdown com linhas no formato:
  "# ... Nome  Idade  PAIS3  Pontos ..."
  Ex.: "1   MR   Neal Skupski   36   GBR   8280 ..."

Saídas:
- Atualiza campos de duplas em db/ranking_<tour>.json:
  - pontos_duplas
  - pontos_ranking_duplas
- Salva snapshot parseado em db/ranking_<tour>_duplas_live.json

Uso:
  python3 scripts/importar_ranking_atp_duplas.py \
    --tour atp \
    --input docs/ranking_atp_duplas_raw.md

  python3 scripts/importar_ranking_atp_duplas.py \
    --tour wta \
    --input docs/ranking_wta_duplas_raw.md
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
from typing import Dict, List, Optional

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from src.constantes import DEFAULT_ATRIBUTOS, DEFAULT_ATRIBUTOS_PSICOLOGICOS
from src.nome_utils import normalizar_nome

TRI_TO_ISO2 = {
    "ARG": "AR",
    "AUS": "AU",
    "AUT": "AT",
    "BEL": "BE",
    "BOL": "BO",
    "BRA": "BR",
    "BUL": "BG",
    "CAN": "CA",
    "CHI": "CL",
    "CHN": "CN",
    "COL": "CO",
    "CRO": "HR",
    "CZE": "CZ",
    "DEN": "DK",
    "ECU": "EC",
    "ESA": "SV",
    "ESP": "ES",
    "EST": "EE",
    "FIN": "FI",
    "FRA": "FR",
    "GBR": "GB",
    "GER": "DE",
    "GRE": "GR",
    "HKG": "HK",
    "HUN": "HU",
    "IND": "IN",
    "ISR": "IL",
    "ITA": "IT",
    "JPN": "JP",
    "KAZ": "KZ",
    "KOR": "KR",
    "LAT": "LV",
    "LBN": "LB",
    "LTU": "LT",
    "MAR": "MA",
    "MEX": "MX",
    "MON": "MC",
    "NED": "NL",
    "NMI": "MP",
    "NOR": "NO",
    "NZL": "NZ",
    "PER": "PE",
    "PHI": "PH",
    "POL": "PL",
    "POR": "PT",
    "ROU": "RO",
    "RSA": "ZA",
    "RUS": "RU",
    "SRB": "RS",
    "SUI": "CH",
    "SVK": "SK",
    "SWE": "SE",
    "THA": "TH",
    "TUN": "TN",
    "TWN": "TW",
    "UKR": "UA",
    "URU": "UY",
    "USA": "US",
    "UZB": "UZ",
    "VEN": "VE",
}


def _slug_nome_pais(nacionalidades_path: str) -> Dict[str, str]:
    with open(nacionalidades_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    mapa = {}
    for continente in data.values():
        for entrada in continente:
            if not isinstance(entrada, str) or not entrada.startswith("["):
                continue
            codigo = entrada[1 : entrada.find("]")]
            mapa[codigo.upper()] = entrada
    return mapa


def _to_int_pontos(valor: str) -> int:
    return int(re.sub(r"[^\d]", "", valor or "0") or "0")


def _parse_linhas_duplas(texto: str) -> List[dict]:
    linhas = texto.splitlines()
    rows: List[dict] = []

    # Aceita nomes com acentos, hífen, apóstrofo e ponto.
    row_re_compacto_com_pais = re.compile(
        r"^\s*(\d{1,4})(?:T)?\s+([A-Za-zÀ-ÖØ-öø-ÿ'’.\- ]+?)\s+"
        r"(\d{1,2})\s+([A-Z]{3})\s+([\d.,]+)\s*$"
    )
    row_re_sem_pais = re.compile(
        r"^\s*(\d{1,4})(?:T)?\s+([A-Za-zÀ-ÖØ-öø-ÿ'’.\- ]+?)\s+(\d{1,2})\s+([\d.,]+)\b"
    )

    i = 0
    while i < len(linhas):
        linha = linhas[i].strip()
        if not re.match(r"^\d{1,4}(?:T)?\b", linha):
            i += 1
            continue

        # Formato em linha única (com ou sem colunas extras no meio):
        # rank ... nome ... idade PAIS3 pontos ...
        toks = linha.split()
        if toks:
            m_first = re.match(r"^(\d{1,4})(?:T)?$", toks[0])
            if m_first:
                rank = int(m_first.group(1))
                age_idx = None
                for k in range(1, len(toks) - 2):
                    if (
                        re.fullmatch(r"\d{1,2}", toks[k])
                        and re.fullmatch(r"[A-Z]{3}", toks[k + 1])
                        and re.fullmatch(r"[\d.,]+", toks[k + 2])
                    ):
                        age_idx = k
                        break

                if age_idx is not None:
                    idade = int(toks[age_idx])
                    pais3 = toks[age_idx + 1].upper()
                    pontos = _to_int_pontos(toks[age_idx + 2])
                    nome_tokens = []
                    for t in toks[1:age_idx]:
                        if re.fullmatch(
                            r"(?:MR|NMR|\(\d+\)|\d+/\d+/\d+|[+-]?\d+|#|NMR:|MR:)",
                            t,
                            re.IGNORECASE,
                        ):
                            continue
                        nome_tokens.append(t)
                    if nome_tokens:
                        rows.append(
                            {
                                "rank_duplas": rank,
                                "nome": " ".join(nome_tokens).strip(),
                                "idade": idade,
                                "pais3": pais3,
                                "pontos_duplas": pontos,
                            }
                        )
                        i += 1
                        continue

        mc = row_re_compacto_com_pais.match(linha)
        if mc:
            rank = int(mc.group(1))
            nome = " ".join(mc.group(2).split())
            idade = int(mc.group(3))
            pais3 = mc.group(4).upper()
            pontos = _to_int_pontos(mc.group(5))
            rows.append(
                {
                    "rank_duplas": rank,
                    "nome": nome,
                    "idade": idade,
                    "pais3": pais3,
                    "pontos_duplas": pontos,
                }
            )
            i += 1
            continue

        m2 = row_re_sem_pais.match(linha)
        if m2:
            rank = int(m2.group(1))
            nome = " ".join(m2.group(2).split())
            idade = int(m2.group(3))
            pontos = _to_int_pontos(m2.group(4))
            rows.append(
                {
                    "rank_duplas": rank,
                    "nome": nome,
                    "idade": idade,
                    "pais3": "RUS",
                    "pontos_duplas": pontos,
                }
            )
        i += 1

    if not rows:
        # Fallback: formato sem país (Rank | Nome | Idade | Pontos | ...).
        linhas_limpa = [l.strip() for l in linhas if l.strip()]
        i = 0
        while i < len(linhas_limpa):
            m_rank = re.match(r"^(\d{1,4})(?:T)?$", linhas_limpa[i])
            if not m_rank:
                i += 1
                continue

            rank = int(m_rank.group(1))
            j = i + 1
            nome_partes: List[str] = []
            idade = None
            pontos = None

            while j < len(linhas_limpa):
                s = linhas_limpa[j]
                m_stats = re.match(r"^(\d{1,2})\s+([\d.,]+)\b", s)
                if m_stats:
                    idade = int(m_stats.group(1))
                    pontos = _to_int_pontos(m_stats.group(2))
                    break

                # Ignora ruído comum do dump (variação de ranking/headers)
                if not re.match(
                    r"^(?:\+?\-?\d+|[-+]\d+|[-]|Rank|Player|Age|Official Points|Tourn Played|Dropping|Next Best|ATP Rankings Doubles|Singles|Doubles|Race To Turin|Doubles Race|Next Gen Race|No 1s|Live Live|All Countries|\d{4}\.\d{2}\.\d{2})$",
                    s,
                    re.IGNORECASE,
                ):
                    nome_partes.append(s)
                j += 1

            if nome_partes and idade is not None and pontos is not None:
                rows.append(
                    {
                        "rank_duplas": rank,
                        "nome": " ".join(nome_partes).strip(),
                        "idade": idade,
                        "pais3": "RUS",
                        "pontos_duplas": pontos,
                    }
                )
                i = j + 1
                continue

            i += 1

    # Dedup conservando melhor rank/pontos
    by_nome: Dict[str, dict] = {}
    for r in rows:
        chave = normalizar_nome(r["nome"])
        prev = by_nome.get(chave)
        if prev is None:
            by_nome[chave] = r
            continue
        if r["rank_duplas"] < prev["rank_duplas"] or (
            r["rank_duplas"] == prev["rank_duplas"]
            and r["pontos_duplas"] > prev["pontos_duplas"]
        ):
            by_nome[chave] = r

    return sorted(
        by_nome.values(), key=lambda x: (x["rank_duplas"], -x["pontos_duplas"])
    )


def _overall_por_duplas(pontos: int) -> int:
    # Curva suave para especialistas de duplas sem inflar absurdamente.
    if pontos >= 7000:
        return 87
    if pontos >= 5000:
        return 83
    if pontos >= 3000:
        return 79
    if pontos >= 1800:
        return 75
    if pontos >= 1000:
        return 71
    if pontos >= 500:
        return 66
    if pontos >= 250:
        return 61
    return 56


def _atributos_base_por_nome(nome: str, overall: int) -> dict:
    # Determinístico por nome para evitar variações a cada import.
    rnd = random.Random(normalizar_nome(nome))
    attrs = {}
    for k in DEFAULT_ATRIBUTOS:
        delta = rnd.randint(-8, 8)
        attrs[k] = max(35, min(99, overall + delta))
    return attrs


def _psico_base_por_nome(nome: str, overall: int) -> dict:
    rnd = random.Random(f"psico:{normalizar_nome(nome)}")
    base = max(35, min(95, int(overall * 0.85)))
    psico = {}
    for k in DEFAULT_ATRIBUTOS_PSICOLOGICOS:
        psico[k] = max(30, min(99, base + rnd.randint(-10, 10)))
    return psico


def _novo_jogador_real(
    entry: dict, nacionalidades_map: Dict[str, str], next_id: int
) -> dict:
    pais3 = (entry.get("pais3") or "RUS").upper()
    iso2 = TRI_TO_ISO2.get(pais3, pais3)
    nacionalidade = nacionalidades_map.get(iso2, f"[{iso2}] {pais3}")
    overall = _overall_por_duplas(entry["pontos_duplas"])
    return {
        "id": next_id,
        "nome": entry["nome"],
        "idade": entry["idade"],
        "nacionalidade": nacionalidade,
        "overall": overall,
        "pontos": 0,
        "pontos_ranking": 0,
        "pontos_detalhados": [],
        "trofeus": [],
        "historico_torneios": [],
        "pontos_ytd": 0,
        "dinheiro": 0,
        "pontos_duplas": entry["pontos_duplas"],
        "pontos_ranking_duplas": entry["pontos_duplas"],
        "pontos_detalhados_duplas": [],
        "is_bot": False,
        "e_ficticio": False,
        "atributos": _atributos_base_por_nome(entry["nome"], overall),
        "atributos_psicologicos": _psico_base_por_nome(entry["nome"], overall),
    }


def _apply_duplas(
    ranking_path: str,
    entries: List[dict],
    nacionalidades_path: str,
    reset_others: bool = True,
) -> dict:
    with open(ranking_path, "r", encoding="utf-8") as f:
        ranking = json.load(f)

    nacionalidades_map = _slug_nome_pais(nacionalidades_path)
    by_nome = {
        normalizar_nome(j.get("nome", "")): j for j in ranking if isinstance(j, dict)
    }
    importados = {normalizar_nome(e["nome"]): e for e in entries}

    max_id = max(
        [int(j.get("id", 0) or 0) for j in ranking if isinstance(j, dict)] or [0]
    )
    novos = 0
    atualizados = 0

    if reset_others:
        for j in ranking:
            if not isinstance(j, dict):
                continue
            if j.get("is_bot") or j.get("e_ficticio"):
                continue
            j["pontos_duplas"] = 0
            j["pontos_ranking_duplas"] = 0
            j.setdefault("pontos_detalhados_duplas", [])

    for nome_norm, e in importados.items():
        alvo = by_nome.get(nome_norm)
        if alvo:
            alvo["pontos_duplas"] = e["pontos_duplas"]
            alvo["pontos_ranking_duplas"] = e["pontos_duplas"]
            alvo.setdefault("pontos_detalhados_duplas", [])
            # Atualiza idade quando vier no feed.
            if e.get("idade"):
                alvo["idade"] = e["idade"]
            if e.get("pais3"):
                iso2 = TRI_TO_ISO2.get(e["pais3"], e["pais3"])
                nova_nac = nacionalidades_map.get(iso2, f"[{iso2}] {e['pais3']}")
                atual_nac = (alvo.get("nacionalidade") or "").strip()
                if (
                    not atual_nac
                    or atual_nac in {"[None] None", "[XX] Internacional"}
                    or atual_nac.startswith("[??]")
                ):
                    alvo["nacionalidade"] = nova_nac
            alvo["is_bot"] = False
            alvo["e_ficticio"] = False
            atualizados += 1
            continue

        max_id += 1
        novo = _novo_jogador_real(e, nacionalidades_map, max_id)
        ranking.append(novo)
        by_nome[nome_norm] = novo
        novos += 1

    # Mantém ordenação principal por simples para não quebrar expectativas da UI.
    ranking.sort(
        key=lambda j: int(j.get("pontos_ranking", j.get("pontos", 0)) or 0),
        reverse=True,
    )

    with open(ranking_path, "w", encoding="utf-8") as f:
        json.dump(ranking, f, indent=2, ensure_ascii=False)

    return {
        "total_entries_duplas": len(entries),
        "atualizados": atualizados,
        "novos": novos,
        "total_ranking": len(ranking),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tour",
        choices=["atp", "wta"],
        default="atp",
        help="Tour de destino para atualizar o ranking base.",
    )
    parser.add_argument(
        "--input",
        default=None,
        help="Arquivo bruto com ranking de duplas (ATP/WTA).",
    )
    parser.add_argument(
        "--ranking",
        default=None,
        help="Arquivo base do ranking alvo (sobrescreve o default do tour).",
    )
    parser.add_argument(
        "--nacionalidades",
        default=os.path.join(BASE, "db", "nacionalidades.json"),
        help="Arquivo de nacionalidades.",
    )
    parser.add_argument(
        "--snapshot",
        default=None,
        help="Snapshot parseado de duplas (sobrescreve o default do tour).",
    )
    parser.add_argument(
        "--no-reset-others",
        action="store_true",
        help="Não zera pontos de duplas dos jogadores fora do feed importado.",
    )
    args = parser.parse_args()

    if args.input is None:
        args.input = os.path.join(BASE, "docs", f"ranking_{args.tour}_duplas_raw.md")
    if args.ranking is None:
        args.ranking = os.path.join(BASE, "db", f"ranking_{args.tour}.json")
    if args.snapshot is None:
        args.snapshot = os.path.join(
            BASE, "db", f"ranking_{args.tour}_duplas_live.json"
        )

    with open(args.input, "r", encoding="utf-8") as f:
        texto = f.read()

    if "Cole aqui o ranking" in texto and len(texto.splitlines()) < 30:
        raise SystemExit(
            f"Arquivo de entrada sem dados reais: {args.input}. "
            "Cole o ranking bruto de duplas antes de rodar o import."
        )

    entries = _parse_linhas_duplas(texto)
    if not entries:
        raise SystemExit(
            "Nenhuma linha de ranking de duplas foi reconhecida no arquivo de entrada. "
            "Verifique se o dump foi colado no formato bruto."
        )

    # Snapshot parseado para auditoria/debug.
    with open(args.snapshot, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    stats = _apply_duplas(
        ranking_path=args.ranking,
        entries=entries,
        nacionalidades_path=args.nacionalidades,
        reset_others=not args.no_reset_others,
    )

    print("✅ Importação de duplas concluída")
    print(f"   Tour atualizado: {args.tour.upper()}")
    print(f"   Entradas de duplas parseadas: {stats['total_entries_duplas']}")
    print(f"   Jogadores atualizados: {stats['atualizados']}")
    print(f"   Jogadores novos adicionados: {stats['novos']}")
    print(f"   Total no ranking base: {stats['total_ranking']}")
    print(f"   Snapshot salvo em: {args.snapshot}")


if __name__ == "__main__":
    main()
