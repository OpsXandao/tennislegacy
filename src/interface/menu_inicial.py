from src.controller import fluxo_principal
from src.io_utils import safe_input, clear_screen, print_blue, print_green, print_red
from src.jogador import carregar_jogador, criar_jogador, criar_jogador_alexandre_paiva
from src.dados import listar_saves, excluir_save


def menu_inicial():
    while True:
        clear_screen()
        print_blue("\n🎾 Bem-vindo ao TennisLegacy!")
        print()
        print_green("1. 🆕 Iniciar novo jogo")
        print_green("2. 📂 Carregar jogo salvo")
        print_green("3. ⚡ Carregar Alexandre Paiva (lll)")
        print_red("4. 🗑️ Excluir save")
        print()

        escolha = safe_input("Escolha uma opção (1, 2, 3 ou 4): ").strip()

        if escolha == "3":
            nome_save = safe_input("🎮 Nome do novo save: ").strip()
            if not nome_save:
                print_red("❌ O nome do save não pode ser vazio.")
                continue
            if nome_save in listar_saves():
                print_red(f"❌ O save '{nome_save}' já existe. Escolha outro nome.")
                safe_input("\nPressione Enter para continuar...")
                continue
            jogador_inst = criar_jogador_alexandre_paiva(nome_save)
        elif escolha == "1":
            nome_save = safe_input("🎮 Nome do novo save: ").strip()
            if not nome_save:
                print_red("❌ O nome do save não pode ser vazio.")
                continue

            if nome_save in listar_saves():
                print_red(
                    f"❌ O save '{nome_save}' já existe. Escolha outro nome ou carregue o existente."
                )
                safe_input("\nPressione Enter para continuar...")
                continue

            jogador_inst = criar_jogador(nome_save)
        elif escolha == "2":
            saves = listar_saves()
            if not saves:
                print_red("❌ Nenhum save encontrado. Inicie um novo jogo.")
                safe_input("\nPressione Enter para continuar...")
                continue

            print("\n📂 Escolha o seu save:")
            for idx, save in enumerate(saves, 1):
                print(f"{idx}. {save}")
            print("0. 🔙 Voltar")

            nome_save = None
            while True:
                idx_escolha = safe_input("\nNúmero do save: ").strip()
                if idx_escolha == "0":
                    break
                if idx_escolha.isdigit() and 1 <= int(idx_escolha) <= len(saves):
                    nome_save = saves[int(idx_escolha) - 1]
                    break
                print_red("❌ Escolha inválida.")

            if nome_save is None:
                continue
            jogador_inst = carregar_jogador(nome_save)
        elif escolha == "4":
            saves = listar_saves()
            if not saves:
                print_red("❌ Nenhum save encontrado.")
                safe_input("\nPressione Enter para continuar...")
                continue

            print("\n🗑️ Escolha o save para EXCLUIR:")
            for idx, save in enumerate(saves, 1):
                print(f"{idx}. {save}")
            print("0. 🔙 Voltar")

            idx_escolha = safe_input("\nNúmero do save: ").strip()
            if idx_escolha == "0":
                continue

            if idx_escolha.isdigit() and 1 <= int(idx_escolha) <= len(saves):
                nome_save_excluir = saves[int(idx_escolha) - 1]
                confirmacao = (
                    safe_input(
                        f"⚠️ Tem certeza que deseja excluir o save '{nome_save_excluir}'? (s/n): "
                    )
                    .strip()
                    .lower()
                )
                if confirmacao == "s":
                    if excluir_save(nome_save_excluir):
                        print_green(
                            f"✅ Save '{nome_save_excluir}' excluído com sucesso!"
                        )
                    else:
                        print_red(
                            f"❌ Não foi possível excluir o save '{nome_save_excluir}'."
                        )
                else:
                    print_blue("Exclusão cancelada.")
                safe_input("\nPressione Enter para continuar...")
                continue
            else:
                print_red("❌ Escolha inválida.")
                safe_input("\nPressione Enter para continuar...")
                continue
        else:
            print_red("❌ Opção inválida.")
            continue

        break

    salvar_automaticamente = (
        safe_input(
            "📎 Deseja salvar automaticamente após cada partida ou torneio? (s/n): "
        )
        .strip()
        .lower()
        == "s"
    )

    fluxo_principal(jogador_inst, nome_save, salvar_automaticamente)
