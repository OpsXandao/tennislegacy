import builtins

from src.controller import fluxo_principal
from src.io_utils import safe_input, clear_screen, print_blue, print_green, print_red
from src.jogador import carregar_jogador, criar_jogador

def menu_inicial():
    clear_screen()
    print_blue("\n🎾 Bem-vindo ao TennisLegacy!")
    print()
    print_green("1. 🆕 Iniciar novo jogo")
    print_green("2. 📂 Carregar jogo salvo")
    print()

    escolha = safe_input("Escolha uma opção (1 ou 2): ").strip()
    nome_save = safe_input("🎮 Nome do seu save: ").strip()
    salvar_automaticamente = (
        safe_input(
            "📎 Deseja salvar automaticamente após cada partida ou torneio? (s/n): "
        )
        .strip()
        .lower()
        == "s"
    )

    builtins.nome_save = nome_save

    if escolha == "1":
        jogador_inst = criar_jogador(nome_save)
    elif escolha == "2":
        jogador_inst = carregar_jogador(nome_save)
    else:
        print_red("❌ Opção inválida.")
        return menu_inicial()

    builtins.jogador = jogador_inst
    # Agora chama o fluxo principal do controller:
    fluxo_principal(jogador_inst, nome_save, salvar_automaticamente)
