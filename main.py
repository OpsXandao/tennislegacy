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
    while True:
        print("\n🏟️ Menu Principal")
        print("1. Ver status do jogador")
        print("2. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            jogador.mostrar_status()
        elif opcao == "2":
            print("👋 Saindo do jogo. Até a próxima!")
            break
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    j = criar_jogador()
    menu_principal(j)
