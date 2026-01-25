from src.io_utils import safe_input, clear_screen, print_blue, print_green, print_red, print_magenta
from src.ranking import SistemaRanking
from src.dados import carregar_nacionalidades, get_caminho_ranking_save
from src.interface.menu_progressao import menu_progressao
from src.save import salvar_jogo


def escolher_nacionalidade_menu():
    """Exibe um menu simples de nacionalidades e retorna a opção escolhida."""
    nacionalidades_por_continente = carregar_nacionalidades()
    continentes = list(nacionalidades_por_continente.keys())

    while True:
        clear_screen()
        print_blue("\n🌍 Escolha o continente:")
        print()
        for idx, continente in enumerate(continentes, 1):
            print_green(f"{idx}. {continente}")
        print()

        escolha_cont = safe_input("Continente: ").strip()
        if not escolha_cont.isdigit() or not (1 <= int(escolha_cont) <= len(continentes)):
            print_red("❌ Opção inválida. Tente novamente.")
            continue

        continente_escolhido = continentes[int(escolha_cont) - 1]
        paises = nacionalidades_por_continente[continente_escolhido]

        while True:
            clear_screen()
            print_blue(f"\n🏳️ Nacionalidades em {continente_escolhido}:")
            print()
            for idx, pais in enumerate(paises, 1):
                print_green(f"{idx}. {pais}")
            print()

            escolha_pais = safe_input("Nacionalidade: ").strip()
            if escolha_pais.isdigit() and 1 <= int(escolha_pais) <= len(paises):
                return paises[int(escolha_pais) - 1]

            print_red("❌ Opção inválida. Tente novamente.")

def menu_jogador(jogador, nome_save):
    """Exibe as informações e atributos do jogador e permite o acesso ao menu de progressão."""
    
    while True:
        clear_screen()
        # Recarrega os dados do jogador e do ranking para garantir que estão atualizados
        # (especialmente após gastar pontos de skill)
        ranking = SistemaRanking(get_caminho_ranking_save(nome_save))
        jogador_ranking = ranking.buscar_jogador_por_nome(jogador.nome)
        
        # Atualiza o 'overall' do jogador no ranking com base nos atributos do objeto jogador
        if jogador_ranking:
            overall_calculado = jogador.calcular_overall()
            if jogador_ranking.get('overall') != overall_calculado:
                jogador_ranking['overall'] = overall_calculado
                jogador_ranking['atributos'] = jogador.atributos
                ranking.salvar_ranking()


        print_blue("\n--- 🧑 Meu Jogador ---")
        
        if jogador_ranking:
            posicao = ranking.obter_posicao(jogador.nome)
            print()
            print(f"Nome: {jogador.nome} ({jogador.nacionalidade})")
            print(f"Ranking: #{posicao} | Pontos: {jogador_ranking.get('pontos', 0)}")
            print(f"Nível: {jogador.nivel} | XP: {jogador.xp}/{jogador.xp_para_proximo_nivel}")
            print(f"Pontos de Skill: {jogador.pontos_de_skill}")
            print(f"Overall: {jogador.calcular_overall()}")
            
            print_magenta("\n--- ⚕️ Status Físico ---")
            print()
            print(f"Fadiga: {jogador.fadiga}%")
            if jogador.status_lesao["lesionado"]:
                print(f"Status: Lesionado ({jogador.status_lesao['semanas_restantes']} semanas restantes)")
            else:
                print("Status: Saudável")

            print_magenta("\n--- 📊 Atributos ---")
            print()
            for attr, valor in jogador.atributos.items():
                print(f"  - {attr.title():<12}: {valor}")
            
            print_magenta("\n--- 🤔 Psicológico ---")
            print()
            for attr, valor in jogador.atributos_psicologicos.items():
                print(f"  - {attr.replace('_', ' ').title():<18}: {valor}")
        else:
            print_red("Não foi possível encontrar os dados do jogador no ranking.")

        print_blue("\n--- 🎮 Opções ---")
        print()
        if jogador.pontos_de_skill > 0:
            print_green(f"[1] 🔥 Gastar Pontos de Skill ({jogador.pontos_de_skill} disponíveis)")
        print_green("[0] 🔙 Voltar ao Menu Principal")
        print()
        
        escolha = safe_input("Escolha uma opção: ").strip()

        if escolha == "0":
            break
        elif escolha == "1" and jogador.pontos_de_skill > 0:
            menu_progressao(jogador, nome_save)
            # Após voltar do menu_progressao, o loop vai recarregar e mostrar os dados atualizados
        else:
            print_red("Opção inválida.")
