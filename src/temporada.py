from calendario import calendario_janeiro

def mostrar_torneios_da_semana(semana):
    print(f"\n📅 Semana {semana} — Torneios Disponíveis:")
    torneios = calendario_janeiro.get(semana, [])
    for i, torneio in enumerate(torneios, start=1):
        print(f"{i}. {torneio['nome']} ({torneio['tipo']}) — {torneio['local']}")
        print(f"   ⭐ Popularidade: {torneio['popularidade']} | 🔥 Dificuldade: {torneio['dificuldade']}")
        print(f"   💰 Premiação: ${torneio['premiacao']:,}\n")
    return torneios

def escolher_torneio(torneios):
    while True:
        try:
            escolha = int(input("🎾 Escolha o torneio (número): "))
            if 1 <= escolha <= len(torneios):
                torneio_escolhido = torneios[escolha - 1]
                print(f"\n📍 Você escolheu: {torneio_escolhido['nome']} em {torneio_escolhido['local']}")
                return torneio_escolhido
            else:
                print("❌ Número inválido. Tente novamente.")
        except ValueError:
            print("❌ Entrada inválida. Digite um número.")