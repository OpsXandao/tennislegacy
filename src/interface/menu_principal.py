from src.io_utils import (
    safe_input,
    clear_screen,
    print_blue,
    print_yellow,
    print_green,
    print_red,
)
from src.interface.menu_temporada import menu_temporada
from src.interface.menu_jogador import menu_jogador
from src.ranking import SistemaRanking
from src.jogador import carregar_jogador
from src.dados import get_caminho_ranking_save, carregar_estado_torneio
from src.eventos_exibicao import evento_convite_duplas
from src.log_jogo import log_erro
from src.save import salvar_jogo


def _normalizar_nome(valor):
    return " ".join(str(valor or "").split()).lower()


def _torneio_ativo_do_jogador(estado, jogador_nome):
    if not isinstance(estado, dict):
        return False
    nome_estado = estado.get("jogador")
    if _normalizar_nome(nome_estado) != _normalizar_nome(jogador_nome):
        return False
    fase = str(estado.get("fase_atual", "") or "")
    return bool(fase) and fase != "finalizado"


def ver_ranking(jogador_obj, nome_save):
    while True:
        clear_screen()
        print_blue("\n--- 🏆 Opções de Ranking ---")
        print()
        print_green("[1] 👤 ATP Ranking (Masculino)")
        print_green("[2] 👤 WTA Ranking (Feminino)")
        print_green("[3] 🌍 Davis Cup Ranking (Nações)")
        print_green("[0] 🔙 Voltar")
        print()

        escolha_tour = safe_input("Escolha o tour: ").strip()

        if escolha_tour == "0":
            break
        elif escolha_tour == "3":
            ver_ranking_nacoes()
            continue

        genero_alvo = "masculino" if escolha_tour == "1" else "feminino"
        tour_label = "ATP" if genero_alvo == "masculino" else "WTA"

        while True:
            clear_screen()
            print_blue(f"\n--- 📊 Ranking {tour_label} ---")
            print_green("[1] 👤 Simples (Singles)")
            print_green("[2] 👥 Duplas (Doubles)")
            print_green("[0] 🔙 Voltar")
            print()

            modalidade_escolha = safe_input("Escolha a modalidade: ").strip()
            if modalidade_escolha == "0":
                break

            modalidade = "simples" if modalidade_escolha == "1" else "duplas"
            if modalidade == "duplas":
                from src.dados import get_caminho_ranking_duplas

                path = get_caminho_ranking_duplas(nome_save, genero=genero_alvo)
            else:
                path = get_caminho_ranking_save(nome_save, genero=genero_alvo)

            ranking = SistemaRanking(path, modalidade=modalidade)

            while True:
                clear_screen()
                label_mod = "SIMPLES" if modalidade == "simples" else "DUPLAS"
                print_blue(f"\n--- 🌍 RANKING MUNDIAL {tour_label} ({label_mod}) ---")
                print()
                print_green("[1] Top 10")
                print_green("[2] Top 11-50")
                print_green("[3] Ver meu ranking")
                print_green("[4] Ver todo o ranking")
                print_green("[0] Voltar")
                print()

                escolha = safe_input("Escolha uma opção: ").strip()

                if escolha == "1":
                    ranking.exibir_ranking(
                        start_pos=1, end_pos=10, player_name=jogador_obj.nome
                    )
                elif escolha == "2":
                    ranking.exibir_ranking(
                        start_pos=11, end_pos=50, player_name=jogador_obj.nome
                    )
                elif escolha == "3":
                    ranking.exibir_ranking(player_name=jogador_obj.nome)
                elif escolha == "4":
                    ranking.exibir_ranking()
                elif escolha == "0":
                    break
                else:
                    print_red("❌ Opção inválida.")

                safe_input("\nPressione Enter para continuar...")


def ver_ranking_nacoes():
    from src.dados import carregar_ranking_nacoes_davis

    while True:
        clear_screen()
        print_blue("\n--- 🌍 RANKING DE NAÇÕES (DAVIS CUP) ---")
        print()
        dados = carregar_ranking_nacoes_davis()
        nacoes = dados.get("nations", [])

        if not nacoes:
            print_yellow("Nenhuma nação ranqueada encontrada.")
        else:
            # Ordena por pontos
            nacoes_ord = sorted(nacoes, key=lambda x: x.get("points", 0), reverse=True)
            for i, n in enumerate(nacoes_ord[:20], 1):
                print(f"#{i:2} - {n['name']:20} | {n.get('points', 0):>5} pts")

        print("\n[0] Voltar")
        if safe_input("\nOpção: ").strip() == "0":
            break


def menu_principal(jogador, nome_save, salvar_automaticamente=False):
    """Menu principal que serve como hub de navegação."""
    if jogador is None:
        print_red("❌ Jogador não carregado.")
        return
    while True:
        clear_screen()
        estado_torneio = carregar_estado_torneio(nome_save, genero=jogador.genero)
        torneio_ativo = _torneio_ativo_do_jogador(estado_torneio, jogador.nome)
        print_blue("\n--- 🏠 Menu Principal ---")
        print()
        if torneio_ativo:
            print_yellow("[1] 🎾 Voltar ao Torneio Ativo")
        else:
            print_green("[1] 📅 Calendário da Temporada")
        print_green("[2] 🧑 Meu Jogador")
        print_green("[3] 🏆 Ver Ranking")
        print_green("[4] 🌐 Circuito Mundial")
        print_green("[9] 💾 Salvar e Sair")
        print()

        escolha = safe_input("Escolha uma opção: ").strip()

        if escolha == "1":
            if torneio_ativo:
                return False  # fluxo_principal detecta o arquivo e redireciona ao menu_torneio
            # Convite de exibição de duplas ocorre apenas ao entrar no menu da temporada.
            try:
                evento_convite_duplas(jogador, nome_save)
            except Exception as e:
                log_erro(
                    nome_save,
                    "menu_principal_evento_convite_duplas",
                    e,
                    {"jogador": getattr(jogador, "nome", "??")},
                )
            # Entra no loop do menu da temporada. Se sair de lá (ex: torneio concluído), volta pra cá.
            iniciou_torneio = menu_temporada(jogador, nome_save, salvar_automaticamente)
            jogador = carregar_jogador(nome_save)
            if iniciou_torneio:
                return False
        elif escolha == "2":
            menu_jogador(jogador, nome_save)
        elif escolha == "3":
            ver_ranking(jogador, nome_save)  # Calls the new ver_ranking function
        elif escolha == "4":
            from src.interface.menu_mundo import menu_mundo

            menu_mundo(jogador, nome_save)
        elif escolha == "9":
            print("💾 Salvando jogo...")
            salvar_jogo(nome_save, jogador)
            print("👋 Saindo do jogo...")
            return True
        else:
            print_red("❌ Opção inválida. Tente novamente.")
