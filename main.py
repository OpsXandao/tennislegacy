import sys
sys.path.append('./src')

from jogador import jogador
from dados import escolher_nacionalidade

def criar_jogador():
    print("🎾 Criação do Jogador")
    nome = input("Nome: ")
    idade = int(input("Idade: "))
    nacionalidade = escolher_nacionalidade()
    return jogador(nome, idade, nacionalidade)

def menu_principal(jogador):
    from calendario import obter_torneios_da_semana
    
    semana_atual = 1
    
    def jogar_temporada():
        print(f"\n📅 Semana {semana_atual} da temporada")
        torneios = obter_torneios_da_semana(semana_atual)
        if not torneios:
            print("📭 Nenhum torneio disponível nesta semana.")
            return
        
        print("🎾 Torneios disponíveis:")
        for idx, torneio in enumerate(torneios, 1):
            estrelas = "★" * torneio["dificuldade"]
            print(f"{idx}. {torneio['nome']} ({torneio['pais_sede']}) - {torneio['tipo']} - Popularidade: {torneio['popularidade']}⭐ | Dificuldade: {estrelas} | Premiação: ${torneio['premiacao']}")
        
        escolha = input("Escolha um torneio para participar (número ou Enter para cancelar): ")
        if escolha.isdigit() and 1 <= int(escolha) <= len(torneios):
            torneio_escolhido = torneios[int(escolha) - 1]
            print(f"\n📝 Você escolheu o torneio {torneio_escolhido['nome']} em {torneio_escolhido['pais_sede']}!")
            # Aqui no futuro: lógica de qualificação e partidas
        else:
            print("🚫 Ação cancelada.")
    
    opcoes = {
        "1": jogador.mostrar_status,
        "2": jogador.jogar_partida,
        "3": jogar_temporada,
        "4": lambda: print("👋 Saindo do jogo. Até a próxima!") or exit()
    }

    while True:
        print("\n🏟️ Menu Principal")
        print("1. Ver status do jogador")
        print("2. Jogar uma partida oficial")
        print("3. Jogar temporada")
        print("4. Sair")

        opcao = input("Escolha uma opção: ")

        acao = opcoes.get(opcao)
        if acao:
            acao()
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    jogador = criar_jogador()
    menu_principal(jogador)
