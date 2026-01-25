"""
Menu da Copa Davis - Interface para o torneio por equipes.
"""

from src.calendario import avancar_semana
from src.interface.menu_temporada import menu_temporada
from src.dados import carregar_ranking, get_caminho_ranking_save
from src.io_utils import safe_input, clear_screen, print_blue, print_green, print_red, print_yellow, print_magenta
from src.save import salvar_jogo
from src.davis_cup import carregar_davis_cup


def menu_davis(jogador, nome_save, davis=None, salvar_automaticamente=False):
    """Menu principal da Copa Davis."""
    if davis is None:
        davis = carregar_davis_cup(nome_save, jogador)

    if davis is None:
        print_red("Erro ao carregar a Copa Davis.")
        return

    while True:
        clear_screen()
        estado = davis._carregar_estado()
        fase = estado.get("fase_atual", "grupos")
        pais_jogador = estado.get("pais_jogador", jogador.nacionalidade)

        print_blue(f"\n{'=' * 60}")
        print_blue(f"          🏆 COPA DAVIS - {estado.get('torneio', 'Davis Cup')}")
        print_blue(f"{'=' * 60}")
        print()
        print(f"📍 Sua seleção: {pais_jogador}")
        print(f"📍 Fase atual: {_formatar_fase(fase)}")
        print(f"📍 Grupo: {estado.get('grupo_jogador', '?')}")
        print()

        # Exibe a tabela do grupo se estiver na fase de grupos
        if fase == "grupos":
            davis.exibir_tabela_grupo()

        # Verifica próximo confronto
        proximo = davis.obter_proximo_confronto()

        print_blue("\n--- 🎮 Opções ---")
        print()

        if proximo:
            adversario = proximo.get("adversario", "??")
            print_green(f"[1] 🎾 Jogar confronto vs {adversario}")
        else:
            print_yellow("[1] 🎾 Nenhum confronto disponível")

        print_green("[2] 📊 Ver tabela do grupo")
        print_green("[3] 📋 Ver resultados")
        print_green("[4] 💾 Salvar jogo")
        print_green("[5] ↩️ Sair do menu")
        print()

        opcao = safe_input("Escolha uma opção: ").strip()

        if opcao == "1":
            if proximo:
                adversario = proximo.get("adversario")
                resultado = davis.jogar_confronto(adversario)

                if resultado.get("eliminado"):
                    print_red(f"\n😔 {pais_jogador} foi eliminado da Copa Davis!")
                    safe_input("Pressione Enter para continuar...")
                    break

                if salvar_automaticamente:
                    davis._salvar_estado(davis._carregar_estado())
                    salvar_jogo(nome_save, jogador)
            else:
                print_yellow("Não há confronto disponível no momento.")
                safe_input("Pressione Enter para continuar...")

        elif opcao == "2":
            davis.exibir_tabela_grupo()
            safe_input("\nPressione Enter para continuar...")

        elif opcao == "3":
            _exibir_resultados_davis(davis)
            safe_input("\nPressione Enter para continuar...")

        elif opcao == "4":
            davis._salvar_estado(davis._carregar_estado())
            salvar_jogo(nome_save, jogador)
            print_green("Jogo salvo com sucesso!")
            safe_input("Pressione Enter para continuar...")

        elif opcao == "5":
            print_yellow("Saindo do menu da Copa Davis...")
            break

        else:
            print_red("Opção inválida!")
            safe_input("Pressione Enter para continuar...")

        # Verifica se o jogador ainda está ativo
        if not davis.jogador_ainda_ativo():
            estado = davis._carregar_estado()
            fase_atual = estado.get("fase_atual", "")

            if fase_atual == "eliminado_grupos":
                print_red(f"\n😔 {pais_jogador} não se classificou para as eliminatórias!")
            else:
                print_red(f"\n😔 {pais_jogador} foi eliminado na fase {_formatar_fase(fase_atual)}!")

            print_yellow("\n💪 Volte mais forte na próxima edição!")
            safe_input("Pressione Enter para continuar...")
            break

        # Verifica se a Copa Davis terminou
        estado = davis._carregar_estado()
        if estado.get("fase_atual") == "finalizado":
            print_green(f"\n🎉 A Copa Davis foi concluída!")
            if estado.get("jogador_vivo"):
                print_green(f"🏆 {pais_jogador} É CAMPEÃO DA COPA DAVIS!")
            safe_input("Pressione Enter para continuar...")
            break

    # Avança a semana após a Copa Davis
    if isinstance(jogador, dict):
        temporada = avancar_semana(nome_save)
        jogador["semana"] = temporada["semana"]
        semana_msg = jogador["semana"]
    else:
        temporada = avancar_semana(nome_save)
        jogador.semana = temporada["semana"]
        semana_msg = jogador.semana

    if salvar_automaticamente:
        salvar_jogo(nome_save, jogador)
        print_green(f"\n📅 Semana avançada para {semana_msg}.")
    else:
        print_yellow(f"\n📅 Semana avançada para {semana_msg}.")

    menu_temporada(jogador, nome_save, salvar_automaticamente=salvar_automaticamente)


def _formatar_fase(fase):
    """Formata o nome da fase para exibição."""
    fases = {
        "grupos": "Fase de Grupos",
        "quartas": "Quartas de Final",
        "semifinal": "Semifinal",
        "final": "Final",
        "eliminado_grupos": "Eliminado na Fase de Grupos",
        "finalizado": "Torneio Finalizado",
    }
    return fases.get(fase, fase.capitalize())


def _exibir_resultados_davis(davis):
    """Exibe os resultados dos confrontos da Copa Davis."""
    estado = davis._carregar_estado()
    resultados = estado.get("resultados_confrontos", [])

    print_blue(f"\n{'=' * 60}")
    print_blue("              📊 RESULTADOS DA COPA DAVIS")
    print_blue(f"{'=' * 60}")

    if not resultados:
        print_yellow("\nNenhum resultado ainda.")
        return

    for i, r in enumerate(resultados, 1):
        equipe_a = r.get("equipe_a", "??")
        equipe_b = r.get("equipe_b", "??")
        vencedor = r.get("vencedor", "??")
        placar = r.get("placar", "?-?")

        marcador = " 🏆" if vencedor == equipe_a else ""
        marcador_b = " 🏆" if vencedor == equipe_b else ""

        print(f"\n{i}. {equipe_a}{marcador} {placar} {equipe_b}{marcador_b}")

        # Mostra detalhes das partidas
        partidas = r.get("partidas", [])
        for p in partidas:
            tipo = p.get("tipo", "?")
            if tipo == "simples":
                jog_a = p.get("jogador_a", "??")
                jog_b = p.get("jogador_b", "??")
                venc = p.get("vencedor", "??")
                pl = p.get("placar", "?")
                vencedor_marca = "✓" if venc == jog_a else ""
                vencedor_marca_b = "✓" if venc == jog_b else ""
                print(f"   └ {tipo.capitalize()}: {jog_a} {vencedor_marca} vs {jog_b} {vencedor_marca_b} ({pl})")
            else:
                pl = p.get("placar", "?")
                print(f"   └ {tipo.capitalize()}: {pl}")

    print()
