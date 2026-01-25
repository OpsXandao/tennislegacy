from src.io_utils import safe_input, clear_screen, print_blue, print_green, print_red
from src.save import salvar_jogo

def menu_progressao(jogador, nome_save):
    """Menu para gastar Pontos de Skill e melhorar atributos."""
    while True:
        clear_screen()
        print_blue("\n--- 🔥 Menu de Progressão 🔥 ---")
        print(f"Pontos de Skill disponíveis: {jogador.pontos_de_skill}")
        print("---------------------------------")
        print()
        
        # Lista os atributos atuais para o jogador escolher
        atributos_list = list(jogador.atributos.keys())
        for i, attr in enumerate(atributos_list, 1):
            valor = jogador.atributos[attr]
            print_green(f"[{i}] 💪 {attr.title():<12}: {valor} {'(MAX)' if valor >= 100 else ''}")

        print()
        print_green("\n[0] 🔙 Voltar ao Menu do Jogador")
        print()
        
        escolha = safe_input("Escolha um atributo para melhorar ou '0' para voltar: ").strip()

        if escolha == '0':
            break

        try:
            escolha_idx = int(escolha) - 1
            if 0 <= escolha_idx < len(atributos_list):
                if jogador.pontos_de_skill > 0:
                    attr_escolhido = atributos_list[escolha_idx]
                    
                    if jogador.atributos[attr_escolhido] < 100:
                        jogador.atributos[attr_escolhido] += 1
                        jogador.pontos_de_skill -= 1
                        print_green(f"✅ {attr_escolhido.title()} aumentado para {jogador.atributos[attr_escolhido]}!")
                        # Salva o progresso
                        salvar_jogo(nome_save, jogador)
                    else:
                        print_red(f"❌ O atributo '{attr_escolhido.title()}' já está no máximo (100).")
                else:
                    print_red("❌ Você não tem Pontos de Skill para gastar. Jogue partidas para ganhar XP e subir de nível.")
            else:
                print_red("❌ Opção inválida.")
        except ValueError:
            print_red("❌ Entrada inválida. Por favor, escolha um número da lista.")
