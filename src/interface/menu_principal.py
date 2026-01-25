from src.io_utils import safe_input, clear_screen, print_blue, print_yellow, print_green, print_red
from src.interface.menu_temporada import menu_temporada
from src.interface.menu_jogador import menu_jogador
from src.ranking import SistemaRanking
from src.dados import get_caminho_ranking_save


def ver_ranking(jogador_obj, nome_save):
    ranking = SistemaRanking(get_caminho_ranking_save(nome_save))
    
    while True:
        clear_screen()
        print_blue("\n--- 🏆 Opcoes de Ranking ---")
        print()
        print_green("[1] Top 10")
        print_green("[2] Top 11-50")
        print_green("[3] Top 51-100")
        print_green("[4] Ver meu ranking")
        print_green("[5] Ver todo o ranking")
        print_green("[9] Voltar")
        print()

        escolha = safe_input("Escolha uma opção: ").strip()

        if escolha == "1":
            ranking.exibir_ranking(start_pos=1, end_pos=10)
        elif escolha == "2":
            ranking.exibir_ranking(start_pos=11, end_pos=50)
        elif escolha == "3":
            ranking.exibir_ranking(start_pos=51, end_pos=100)
        elif escolha == "4":
            ranking.exibir_ranking(player_name=jogador_obj.nome)
        elif escolha == "5":
            ranking.exibir_ranking() # Shows all ranks
        elif escolha == "9":
            break
        else:
            print_red("❌ Opção inválida. Tente novamente.")
        
        safe_input("\nPressione Enter para continuar...")


def menu_principal(jogador, nome_save, salvar_automaticamente=False):
    """Menu principal que serve como hub de navegação."""
    while True:
        clear_screen()
        print_blue("\n--- 🏠 Menu Principal ---")
        print()
        print_green("[1] 📅 Calendário da Temporada")
        print_green("[2] 🧑 Meu Jogador")
        print_green("[3] 🏆 Ver Ranking")
        print_green("[9] 💾 Salvar e Sair")
        print()

        escolha = safe_input("Escolha uma opção: ").strip()

        if escolha == "1":
            # Entra no loop do menu da temporada. Se sair de lá (ex: torneio concluído), volta pra cá.
            iniciou_torneio = menu_temporada(jogador, nome_save, salvar_automaticamente)
            if iniciou_torneio:
                return False
        elif escolha == "2":
            menu_jogador(jogador, nome_save)
        elif escolha == "3":
            ver_ranking(jogador, nome_save) # Calls the new ver_ranking function
        elif escolha == "9":
            print("Saindo do jogo...")
            # A lógica de salvar já deve ter sido tratada nos menus anteriores ou aqui se necessário.
            return True
        else:
            print_red("❌ Opção inválida. Tente novamente.")
