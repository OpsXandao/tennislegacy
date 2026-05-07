import json
import os
import random
import sys

# Adiciona o diretório raiz ao sys.path para importar módulos do src se necessário
sys.path.append(os.getcwd())

# Mapeamento de dados reais para os principais jogadores (ATP e WTA)
# Altura (cm), Peso (kg), Mão (Destro/Canhoto), Reves (Uma mão/Duas mãos), Estilo
REAL_DATA_MAP = {
    # ATP Top
    "Carlos Alcaraz": (183, 74, "Destro", "Duas mãos", "All-court"),
    "Jannik Sinner": (188, 77, "Destro", "Duas mãos", "Baselines Aggressive"),
    "Novak Djokovic": (188, 77, "Destro", "Duas mãos", "Counter-puncher"),
    "Alexander Zverev": (198, 90, "Destro", "Duas mãos", "Baselines Aggressive"),
    "Daniil Medvedev": (198, 83, "Destro", "Duas mãos", "Counter-puncher"),
    "Rafael Nadal": (185, 85, "Canhoto", "Duas mãos", "Baselines Aggressive"),
    "Roger Federer": (185, 85, "Destro", "Uma mão", "All-court"),
    "Casper Ruud": (183, 77, "Destro", "Duas mãos", "Baselines Aggressive"),
    "Taylor Fritz": (196, 86, "Destro", "Duas mãos", "Baselines Aggressive"),
    "Alex de Minaur": (183, 69, "Destro", "Duas mãos", "Counter-puncher"),
    "Ben Shelton": (193, 88, "Canhoto", "Duas mãos", "Server-Volleyer"),
    "Stefanos Tsitsipas": (193, 90, "Destro", "Uma mão", "All-court"),
    "Hubert Hurkacz": (196, 81, "Destro", "Duas mãos", "Server-Volleyer"),
    "Holger Rune": (188, 77, "Destro", "Duas mãos", "Baselines Aggressive"),
    "Grigor Dimitrov": (191, 81, "Destro", "Uma mão", "All-court"),
    "Andrey Rublev": (188, 75, "Destro", "Duas mãos", "Baselines Aggressive"),
    "Lorenzo Musetti": (185, 78, "Destro", "Uma mão", "All-court"),
    "Frances Tiafoe": (188, 86, "Destro", "Duas mãos", "All-court"),
    "Jack Draper": (193, 85, "Canhoto", "Duas mãos", "All-court"),
    
    # WTA Top
    "Iga Swiatek": (176, 62, "Destra", "Duas mãos", "Baselines Aggressive"),
    "Aryna Sabalenka": (182, 80, "Destra", "Duas mãos", "Baselines Aggressive"),
    "Elena Rybakina": (184, 72, "Destra", "Duas mãos", "Baselines Aggressive"),
    "Coco Gauff": (175, 64, "Destra", "Duas mãos", "Counter-puncher"),
    "Jessica Pegula": (170, 70, "Destra", "Duas mãos", "Baselines Aggressive"),
    "Zheng Qinwen": (178, 70, "Destra", "Duas mãos", "Baselines Aggressive"),
    "Ons Jabeur": (167, 66, "Destra", "Duas mãos", "All-court"),
    "Maria Sakkari": (172, 62, "Destra", "Duas mãos", "Baselines Aggressive"),
    "Jelena Ostapenko": (177, 68, "Destra", "Duas mãos", "Baselines Aggressive"),
    "Beatriz Haddad Maia": (185, 80, "Canhota", "Duas mãos", "Baselines Aggressive"),
}

def normalizar_caminho(nome):
    return nome.lower().replace(" ", "_").replace("'", "").replace(".", "").replace("-", "_")

def gerar_bio_realista(nome, genero, atributos):
    # Se já temos no mapa, usa real
    if nome in REAL_DATA_MAP:
        alt, peso, mao, reves, estilo = REAL_DATA_MAP[nome]
        return {
            "altura": alt,
            "peso": peso,
            "mao_dominante": mao,
            "reves": reves,
            "estilo_jogo": estilo
        }
    
    # Senão, gera baseado em heurísticas do tênis
    # Saque alto -> altura geralmente maior
    saque = atributos.get("saque", 60)
    movimento = atributos.get("movimento", 60)
    
    if genero == "masculino":
        # Altura média entre 178 e 205 para homens
        alt_base = 180 + (saque - 60) * 0.5 + random.randint(-3, 3)
        alt = int(max(175, min(208, alt_base)))
        # Peso proporcional à altura
        peso = int(alt - 105 + random.randint(-5, 10))
        mao = "Canhoto" if random.random() < 0.15 else "Destro"
        reves = "Uma mão" if random.random() < 0.12 else "Duas mãos"
    else:
        # Altura média entre 165 e 188 para mulheres
        alt_base = 170 + (saque - 60) * 0.4 + random.randint(-3, 3)
        alt = int(max(160, min(192, alt_base)))
        peso = int(alt - 110 + random.randint(-5, 8))
        mao = "Canhota" if random.random() < 0.12 else "Destra"
        reves = "Uma mão" if random.random() < 0.05 else "Duas mãos"

    # Estilo de jogo baseado em atributos
    if saque > 85 and movimento < 75:
        estilo = "Serve & Volley"
    elif movimento > 85 and saque < 80:
        estilo = "Counter-puncher"
    elif atributos.get("forehand", 60) > 85:
        estilo = "Aggressive Baseliner"
    else:
        estilo = "All-court"
        
    return {
        "altura": alt,
        "peso": peso,
        "mao_dominante": mao,
        "reves": reves,
        "estilo_jogo": estilo
    }

def atualizar_todos_os_jogadores():
    folders = [("atp", "masculino"), ("wta", "feminino")]
    
    total_atualizado = 0
    for folder, genero in folders:
        dir_path = os.path.join("db", "master", folder)
        if not os.path.exists(dir_path):
            continue

        print(f"Processando todos os arquivos em {dir_path}...")
        arquivos = [f for f in os.listdir(dir_path) if f.endswith(".json")]
        
        for filename in arquivos:
            path = os.path.join(dir_path, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                nome = data.get("nome", "Desconhecido")
                # Aplica bio realista/baseada em atributos
                bio = gerar_bio_realista(nome, genero, data.get("atributos", {}))
                data.update(bio)
                
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                total_atualizado += 1
                if total_atualizado % 500 == 0:
                    print(f"... {total_atualizado} jogadores processados.")
            except Exception as e:
                print(f"Erro ao processar {filename}: {e}")

    print(f"\n✅ Concluído! {total_atualizado} jogadores agora possuem dados realistas em todo o banco de dados.")

def main():
    atualizar_todos_os_jogadores()

if __name__ == "__main__":
    main()
