import os
from src.torneio import (
    carregar_torneio,
    salvar_torneio,
)
from src.ranking import carregar_ranking


def menu_torneio(torneio, jogador, nome_save):
    torneio = carregar_torneio(nome_save)

    while True:
        estado = torneio._carregar_estado()
        print(f"\n🏟️ Torneio: {torneio.nome_torneio} | Semana {torneio.semana}")
        print(f"Fase atual: {estado['fase_atual']}")
        print("Confrontos da fase:")
        torneio.exibir_confrontos_fase_atual()

        print("\nOpções:")
        print("[1] Jogar sua partida")
        print("[2] Ver confrontos da fase")
        print("[3] Ver resultados da última fase")
        print("[4] Salvar jogo")
        print("[5] Sair do menu torneio")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            mensagem = torneio.jogar_partida_do_jogador(jogador, nome_save)
            if mensagem:
                print(mensagem)
        elif opcao == "2":
            torneio.exibir_confrontos_fase_atual()
        elif opcao == "3":
            torneio.exibir_resultados(estado)
        elif opcao == "4":
            salvar_torneio(torneio)
            print("Jogo salvo com sucesso!")
        elif opcao == "5":
            print("Saindo do menu torneio...")
            break
        else:
            print("Opção inválida!")

        # >>>>>>> NOVO BLOCO UX: Checa se jogador foi eliminado
        if not torneio.jogador_ainda_ativo():
            print(f"\n😔 Fim de torneio para {torneio.jogador_nome}!")
            print(
                f"🎾 Sua jornada parou na fase {torneio._carregar_estado()['fase_atual']}, mas o show continua...\n"
            )
            print(
                "Quer ver quem será o campeão deste torneio? Você pode acompanhar rodada a rodada!"
            )

            resp = (
                input("📋 Simular o restante do torneio? (s/n): ")
                .strip()
                .lower()
            )
            if resp == "s":
                # Garante acesso à lista de todos jogadores
                todos_jogadores = carregar_ranking(nome_save)
                torneio.simular_torneio_restante(todos_jogadores)
            else:
                print(
                    "\n🔄 Voltando para a temporada... Pronto para o próximo desafio?\n"
                )
            break  # Sai do menu_torneio após simular ou recusar

        # Checar se torneio acabou (final natural), se sim, retornar ao controller
        estado = torneio._carregar_estado()
        if estado["fase_atual"] == "final" and not estado["rodadas"]["final"]:
            print("Torneio finalizado!")
            break
