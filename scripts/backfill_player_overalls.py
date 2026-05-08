import json
import sys
from pathlib import Path
from typing import Dict, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.dados import (
    SAVES_DIR,
    carregar_json,
    carregar_ranking,
    get_caminho_jogador_save,
    get_caminho_ranking_duplas,
    get_caminho_ranking_global,
    get_caminho_ranking_global_duplas,
    get_caminho_ranking_save,
)
from src.utils.nome_utils import normalizar_nome
from src.player_ratings import ajustar_atributo_duplas, calcular_overall_contextual


RankingRef = Dict[str, dict]


def carregar_refs(ranking_path: str, modalidade: str) -> RankingRef:
    data = carregar_ranking(ranking_path)
    refs: RankingRef = {}
    for idx, entry in enumerate(data, start=1):
        nome = entry.get("nome")
        if not nome:
            continue
        pos = int(entry.get("rank_duplas") or entry.get("rank") or idx)
        pontos = int(
            entry.get("pontos_ranking_duplas")
            or entry.get("pontos_duplas")
            or entry.get("pontos_ranking")
            or entry.get("pontos")
            or 0
        )
        refs[normalizar_nome(nome)] = {
            "posicao": pos,
            "pontos": pontos,
            "modalidade": modalidade,
        }
    return refs


def atualizar_jogador(
    path: Path,
    ranking_simples: RankingRef,
    ranking_duplas: RankingRef,
) -> bool:
    data = carregar_json(str(path))
    if not isinstance(data, dict):
        return False

    nome = data.get("nome")
    if not nome:
        return False

    chave = normalizar_nome(nome)
    ref_s = ranking_simples.get(chave, {})
    ref_d = ranking_duplas.get(chave, {})

    trabalho = json.loads(json.dumps(data))
    trabalho.setdefault("atributos", {})
    trabalho.setdefault("atributos_psicologicos", {})

    if ref_s:
        trabalho["pontos_ranking"] = max(
            int(trabalho.get("pontos_ranking", 0) or 0),
            int(ref_s.get("pontos", 0) or 0),
        )
    if ref_d:
        trabalho["pontos_ranking_duplas"] = max(
            int(trabalho.get("pontos_ranking_duplas", 0) or 0),
            int(ref_d.get("pontos", 0) or 0),
        )
        trabalho["pontos_duplas"] = max(
            int(trabalho.get("pontos_duplas", 0) or 0),
            int(ref_d.get("pontos", 0) or 0),
        )
        trabalho["rank_duplas"] = int(ref_d.get("posicao", 0) or 0)

    mudou = ajustar_atributo_duplas(trabalho)
    overall_novo = calcular_overall_contextual(
        trabalho, ranking_pos=ref_s.get("posicao") or None
    )

    if int(data.get("overall", 0) or 0) != overall_novo:
        trabalho["overall"] = overall_novo
        mudou = True

    if trabalho.get("atributos") != data.get("atributos"):
        mudou = True

    if not mudou:
        return False

    with open(path, "w", encoding="utf-8") as f:
        json.dump(trabalho, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return True


def processar_base_global() -> Tuple[int, int]:
    alterados = 0
    total = 0

    for genero, tour in (("masculino", "atp"), ("feminino", "wta")):
        refs_s = carregar_refs(get_caminho_ranking_global(genero), "simples")
        refs_d = carregar_refs(get_caminho_ranking_global_duplas(genero), "duplas")
        pasta = Path("db") / "master" / tour
        for path in sorted(pasta.glob("*.json")):
            total += 1
            if atualizar_jogador(path, refs_s, refs_d):
                alterados += 1

    return alterados, total


def processar_saves() -> Tuple[int, int]:
    alterados = 0
    total = 0
    saves_dir = Path(SAVES_DIR)
    if not saves_dir.exists():
        return 0, 0

    for save_dir in sorted(p for p in saves_dir.iterdir() if p.is_dir()):
        for genero, tour in (("masculino", "atp"), ("feminino", "wta")):
            path_s = get_caminho_ranking_save(save_dir.name, genero)
            path_d = get_caminho_ranking_duplas(save_dir.name, genero)
            refs_s = carregar_refs(path_s, "simples") if Path(path_s).exists() else {}
            refs_d = carregar_refs(path_d, "duplas") if Path(path_d).exists() else {}

            pasta = save_dir / "jogadores" / tour
            if pasta.exists():
                for path in sorted(pasta.glob("*.json")):
                    total += 1
                    if atualizar_jogador(path, refs_s, refs_d):
                        alterados += 1

        jogador_path = Path(get_caminho_jogador_save(save_dir.name))
        if jogador_path.exists():
            data = carregar_json(str(jogador_path), {})
            genero = data.get("genero", "masculino")
            refs_s = carregar_refs(get_caminho_ranking_save(save_dir.name, genero), "simples")
            refs_d = carregar_refs(get_caminho_ranking_duplas(save_dir.name, genero), "duplas")
            total += 1
            if atualizar_jogador(jogador_path, refs_s, refs_d):
                alterados += 1

    return alterados, total


def main():
    globais_alt, globais_total = processar_base_global()
    saves_alt, saves_total = processar_saves()

    print(
        f"Globais: {globais_alt}/{globais_total} jogadores atualizados | "
        f"Saves: {saves_alt}/{saves_total} jogadores atualizados"
    )


if __name__ == "__main__":
    main()
