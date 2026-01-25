from src.calendario import avancar_semana
from src.interface.menu_temporada import menu_temporada
from src.dados import carregar_ranking, get_caminho_ranking_save
from src.io_utils import safe_input, clear_screen, print_blue, print_green, print_red, print_yellow, print_magenta
from src.save import salvar_jogo
from src.torneio import carregar_torneio, salvar_torneio


def menu_torneio(jogador, nome_save, torneio=None, salvar_automaticamente=False):
    if torneio is None:
        torneio = carregar_torneio(nome_save)

    while True:
        clear_screen()
        estado = torneio._carregar_estado()
        print_blue(f"\n🏟️ Torneio: {torneio.nome_torneio} | Semana {torneio.semana}")
        print(f"Fase atual: {estado['fase_atual']}")
        print()
        print_magenta("Confrontos da fase:")
        torneio.exibir_confrontos_fase_atual()
        print()

        print_blue("\n--- 🎮 Opções ---")
        print()
        print_green("[1] 🎾 Jogar sua partida")
        print_green("[2] 📋 Ver confrontos da fase")
        print_green("[3] 📊 Ver resultados da última fase")
        print_green("[4] 💾 Salvar jogo")
        print_green("[5] ↩️ Sair do menu torneio")
        print()

        opcao = safe_input("Escolha uma opção: ").strip()

        if opcao == "1":
            resultado = torneio.jogar_partida_do_jogador(jogador, nome_save)
            if resultado and isinstance(resultado, dict):
                print(resultado.get("msg", ""))
            elif resultado:
                print(resultado)
            if salvar_automaticamente:
                salvar_torneio(torneio)
                salvar_jogo(nome_save, jogador)
        elif opcao == "2":
            torneio.exibir_confrontos_fase_atual()
        elif opcao == "3":
            torneio.exibir_resultados()
        elif opcao == "4":
            salvar_torneio(torneio)
            salvar_jogo(nome_save, jogador)
            print_green("Jogo salvo com sucesso!")
        elif opcao == "5":
            print_yellow("Saindo do menu torneio...")
            break
        else:
            print_red("Opção inválida!")

        # >>>>>>> NOVO BLOCO UX: Checa se jogador foi eliminado
        estado = torneio._carregar_estado()
        if not torneio.jogador_ainda_ativo():
            print_red(f"\n😔 Fim de torneio para {torneio.jogador_nome}!")
            print_yellow(
                f"🎾 Sua jornada parou na fase {torneio._carregar_estado()['fase_atual']}, mas o show continua...\n"
            )
            print_blue("Quer ver quem será o campeão deste torneio?!")

            resp = safe_input("📋 Simular o restante do torneio? (s/n): ").strip().lower()
            if resp == "s":
                # Garante acesso à lista de todos jogadores
                ranking_path = get_caminho_ranking_save(nome_save)
                todos_jogadores = carregar_ranking(ranking_path)
                torneio.simular_torneio_restante(todos_jogadores)
                print_yellow(
                    "\n🔄 Voltando para a temporada... Pronto para o próximo desafio?\n"
                )
            break

        # Checar se torneio acabou (final natural), se sim, retornar ao controller
        estado = torneio._carregar_estado()
        if estado["fase_atual"] == "final" and not estado["rodadas"]["final"]:
            print_yellow("Torneio finalizado!")
            break

    if isinstance(jogador, dict):
        semana_atual = jogador.get("semana", 1)
        temporada = avancar_semana(nome_save)
        jogador["semana"] = temporada["semana"]
        semana_msg = jogador["semana"]
    else:
        semana_atual = getattr(jogador, "semana", 1)
        temporada = avancar_semana(nome_save)
        jogador.semana = temporada["semana"]
        semana_msg = jogador.semana

    if salvar_automaticamente:
        salvar_jogo(nome_save, jogador)
        print_green(f"\n📅 Semana avançada para {semana_msg}. Voltando ao menu da temporada!")
    else:
        print_yellow(
            f"\n📅 Semana avançada para {semana_msg}. Use o menu de temporada para salvar."
        )
    menu_temporada(
        jogador, nome_save, salvar_automaticamente=salvar_automaticamente
    )
