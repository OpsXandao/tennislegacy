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
    opcoes = {
        "1": jogador.mostrar_status,
        "2": jogador.jogar_partida,
        "3": lambda: print("👋 Saindo do jogo. Até a próxima!") or exit()
    }

    while True:
        print("\n🏟️ Menu Principal")
        print("1. Ver status do jogador")
        print("2. Jogar uma partida oficial")
        print("3. Sair")

        opcao = input("Escolha uma opção: ")

        acao = opcoes.get(opcao)
        if acao:
            acao()
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    jogador = criar_jogador()
    menu_principal(jogador)
