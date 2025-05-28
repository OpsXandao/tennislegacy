import os,json

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "saves")
DB_DIR = os.path.join(os.path.dirname(__file__), "..", "db")

def criar_pasta_save(nome_save):
    caminho = os.path.join(BASE_DIR, nome_save)
    os.makedirs(caminho, exist_ok=True)
    return caminho

def salvar_jogo(nome_save, jogador_inst):
    try:
        caminho = criar_pasta_save(nome_save)
        ranking_path = os.path.join(caminho, "ranking_atp.json")

        with open(ranking_path, encoding="utf-8") as f:
            ranking = json.load(f)

        for j in ranking:
            if j["nome"].strip().lower() == jogador_inst.nome.strip().lower():
                j.update({
                    "idade": jogador_inst.idade,
                    "xp": jogador_inst.xp,
                    "nivel": jogador_inst.nivel,
                    "energia": jogador_inst.energia,
                    "ritmo_jogo": jogador_inst.ritmo_jogo,
                    "moral": jogador_inst.moral,
                    "dinheiro": jogador_inst.dinheiro,
                    "atributos": jogador_inst.atributos
                })

        with open(ranking_path, "w", encoding="utf-8") as f:
            json.dump(ranking, f, indent=2, ensure_ascii=False)

        jogador_path = os.path.join(caminho, "jogador.json")
        with open(jogador_path, "w", encoding="utf-8") as f:
            json.dump(jogador_inst.to_dict(), f, indent=2, ensure_ascii=False)

        print("💾 Jogo salvo automaticamente")

    except Exception as e:
        print(f"❌ Erro ao salvar jogo: {e}")

def salvar_estado_atual_torneio(nome_save, fase_atual, confrontos, resultados, jogador_vivo=True):
    try:
        caminho = os.path.join(BASE_DIR, nome_save, "torneio_atp.json")
        with open(caminho, "r", encoding="utf-8") as f:
            estado = json.load(f)

        estado["rodadas"][fase_atual] = [
    (
        a["nome"] if isinstance(a, dict) else a,
        b["nome"] if isinstance(b, dict) else b
    )
    for a, b in confrontos
]

        estado["resultados"][fase_atual] = resultados
        estado["jogador_vivo"] = jogador_vivo

        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(estado, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Erro ao salvar estado atual do torneio: {e}")


def carregar_estado_torneio(caminho):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            estado = json.load(f)

        fase = estado.get("fase_atual")
        rodadas = estado.get("rodadas", {}).get(fase)
        resultados = estado.get("resultados", {}).get(fase)
        jogador_vivo = estado.get("jogador_vivo", True)

        if any(x is None for x in [fase, rodadas, resultados]):
            return None

        return {
            "fase_atual": fase,
            "confrontos": rodadas,
            "resultados": resultados,
            "jogador_vivo": jogador_vivo
        }

    except (FileNotFoundError, json.JSONDecodeError, TypeError) as e:
        print(f"⚠️ Estado inválido ou ausente ({e.__class__.__name__}). Retomada ignorada.")
    except Exception as e:
        print(f"❌ Erro inesperado ao carregar estado do torneio: {e}")

    return None

def atualizar_estado_jogador(caminho, vivo=True, fase_finalizada=False):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            estado = json.load(f)
        estado["jogador_vivo"] = vivo
        if fase_finalizada:
            estado["fase_atual"] = "finalizado"
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(estado, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Erro ao atualizar status do jogador: {e}")

from jogador import reidratar_jogador

def carregar_ou_redirecionar(jogador_inst, nome_save, salvar_automaticamente):
    try:
        from interface.menu_temporada import menu_temporada
        from interface.menu_rodada import menu_rodadas
        from src.torneio import TorneioATP250
        import os, json

        caminho_torneio = os.path.join("saves", nome_save, "torneio_atp.json")
        if not os.path.exists(caminho_torneio):
            print("📁 Nenhum torneio salvo encontrado. Indo para a temporada.")
            return menu_temporada(jogador_inst, nome_save, salvar_automaticamente, 1)

        with open(caminho_torneio, "r", encoding="utf-8") as f:
            estado = json.load(f)
            
        # 🧠 Aqui aplicamos a reidratação definitiva
        if isinstance(jogador_inst, dict):
            jogador_inst = reidratar_jogador(jogador_inst, nome_save)

        torneio = TorneioATP250(
            semana=estado["semana"],
            jogador_nome=jogador_inst.nome,
            jogador_nacionalidade=jogador_inst.nacionalidade,
            ranking=None,  # Carrega dentro do menu_temporada normalmente
            nome_save=nome_save
        )

        fase = estado.get("fase_atual")
        jogador_vivo = estado.get("jogador_vivo", True)
        confrontos = estado["rodadas"].get(fase, [])

        if not jogador_vivo:
            print("🟥 Você foi eliminado. Indo para a próxima semana...")
            return menu_temporada(jogador_inst, nome_save, salvar_automaticamente)

        return menu_rodadas(estado["resultados"], confrontos, jogador_inst, nome_save, torneio)

    except Exception as e:
        print(f"❌ Erro ao carregar save ou redirecionar: {e}")
        return menu_temporada(jogador_inst, nome_save, salvar_automaticamente, 1)