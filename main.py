import sys
sys.path.append('./src')

from jogador import criar_jogador
from menu import menu_principal

if __name__ == "__main__":
    jogador = criar_jogador()
    menu_principal(jogador)
