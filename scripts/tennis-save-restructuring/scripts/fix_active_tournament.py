import os
import json
from pathlib import Path
from src.utils.nome_utils import normalizar_nome


def fix_tournament(save_name):
    save_path = Path("saves") / save_name
    if not save_path.exists():
        print(f"❌ Save {save_name} not found.")
        return

    # 1. Carrega o jogador humano (fonte da verdade para o player)
    with open(save_path / "jogador.json", "r", encoding="utf-8") as f:
        jogador_humano = json.load(f)
    nome_humano = normalizar_nome(jogador_humano["nome"])

    for tour_file in ["torneio_atp.json", "torneio_wta.json"]:
        caminho = save_path / tour_file
        if not caminho.exists():
            continue

        print(f"🛠️ Fixing active tournament: {tour_file}")
        with open(caminho, "r", encoding="utf-8") as f:
            estado = json.load(f)

        genero = "masculino" if "atp" in tour_file else "feminino"
        tour = "atp" if genero == "masculino" else "wta"

        def fix_entidade(ent):
            if not isinstance(ent, dict):
                return ent

            nome = ent.get("nome", "")
            if not nome:
                return ent

            nome_n = normalizar_nome(nome)

            # Se for o humano
            if nome_n == nome_humano:
                print(f"  ✨ Restoring HUMAN: {nome}")
                # Atualiza com dados do jogador.json
                for k in [
                    "atributos",
                    "atributos_psicologicos",
                    "idade",
                    "nacionalidade",
                ]:
                    if k in jogador_humano:
                        ent[k] = jogador_humano[k]

                # Recalcula overall
                tec = ent["atributos"].values()
                psi = ent["atributos_psicologicos"].values()
                ent["overall"] = round(
                    (sum(tec) / len(tec) * 0.8) + (sum(psi) / len(psi) * 0.2)
                )
                return ent

            # Se for NPC
            safe_name = nome.lower().replace(" ", "_").replace("'", "").replace(".", "")
            shard_path = save_path / "jogadores" / tour / f"{safe_name}.json"

            if shard_path.exists():
                with open(shard_path, "r", encoding="utf-8") as sf:
                    detalhes = json.load(sf)

                print(f"  👤 Restoring NPC: {nome} (OVR {detalhes.get('overall')})")
                # Preserva campos de estado do torneio (fadiga, energia no torneio)
                # mas restaura os estruturais
                campos_restaurar = [
                    "atributos",
                    "atributos_psicologicos",
                    "overall",
                    "idade",
                    "nacionalidade",
                ]
                for k in campos_restaurar:
                    if k in detalhes:
                        ent[k] = detalhes[k]
                ent["is_lean"] = False
            return ent

        # Corrigir rodadas
        if "rodadas" in estado:
            for fase, confrontos in estado["rodadas"].items():
                novos_confrontos = []
                for a, b in confrontos:
                    novos_confrontos.append((fix_entidade(a), fix_entidade(b)))
                estado["rodadas"][fase] = novos_confrontos

        # Corrigir resultados
        if "resultados" in estado:
            for fase, partidas in estado["resultados"].items():
                for p in partidas:
                    if isinstance(p, dict):
                        p["jogador_a"] = fix_entidade(p.get("jogador_a"))
                        p["jogador_b"] = fix_entidade(p.get("jogador_b"))
                        p["vencedor"] = fix_entidade(p.get("vencedor"))

        # Corrigir direct_entries
        if "direct_entries" in estado:
            estado["direct_entries"] = [
                fix_entidade(j) for j in estado["direct_entries"]
            ]

        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(estado, f, indent=2, ensure_ascii=False)

    print("✨ Tournament state fixed!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        fix_tournament(sys.argv[1])
    else:
        print("Usage: python fix_active_tournament.py <save_name>")
