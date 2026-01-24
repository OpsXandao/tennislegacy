from src.dados import carregar_nacionalidades
from src.io_utils import safe_input


def escolher_nacionalidade_menu():
    nacionalidades = carregar_nacionalidades()
    print("\n🌍 Escolha um continente:")
    continentes = list(nacionalidades.keys())

    for i, cont in enumerate(continentes, 1):
        print(f"{i}. {cont}")

    while True:
        try:
            opcao = int(safe_input("Número do continente: ")) - 1
            continente_escolhido = continentes[opcao]
            break
        except (ValueError, IndexError):
            print("❌ Escolha inválida. Tente novamente.")

    print(f"\n🌎 Países em {continente_escolhido}:")
    paises = nacionalidades[continente_escolhido]

    for i, pais in enumerate(paises, 1):
        print(f"{i}. {pais}")

    while True:
        try:
            opc_pais = int(safe_input("Número do país: ")) - 1
            pais_escolhido = paises[opc_pais]
            break
        except (ValueError, IndexError):
            print("❌ Escolha inválida. Tente novamente.")

    return pais_escolhido
