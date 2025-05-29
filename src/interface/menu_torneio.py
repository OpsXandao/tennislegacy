import os
from src.torneio import (
    carregar_torneio,
    salvar_torneio,
    simular_partidas_npc,
    avancar_fase,
)
from src.ranking import carregar_ranking, get_jogador_by_id


def menu_torneio(nome_save):
    caminho_torneio = os.path.join("db", "torneio_atp.json")
    torneio = carregar_torneio(caminho_torneio)
    ranking = carregar_ranking(os.path.join("db", "ranking_atp.json"))

    while True:
        print(f"\n🏟️ Torneio: {torneio['torneio']} | Semana {torneio['semana']}")
        print(f"Fase atual: {torneio['fase_atual']}")
        print("Confrontos da fase:")

        for idx, confronto in enumerate(
            torneio["rodadas"][torneio["fase_atual"]], start=1
        ):
            jogador_a = get_jogador_by_id(ranking, confronto["jogador_a_id"])
            jogador_b = get_jogador_by_id(ranking, confronto["jogador_b_id"])
            resultado = confronto.get("resultado", "pendente")
            print(
                f"{idx}. {jogador_a['nome']} vs {jogador_b['nome']} | "
                f"Resultado: {resultado}"
            )

        print("\nOpções:")
        print("[1] Jogar sua partida")
        print("[2] Ver confrontos da fase")
        print("[3] Ver resultados da fase")
        print("[4] Salvar jogo")
        print("[5] Sair do menu torneio")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            print("Jogando partida do player...")
            # Aqui chama sua função de jogar a partida do jogador
            simular_partidas_npc(torneio, ranking)
            avancar_fase(torneio)
            salvar_torneio(caminho_torneio, torneio)
        elif opcao == "2":
            continue  # Já exibidos no print inicial
        elif opcao == "3":
            print("\nResultados da fase:")
            for resultado in torneio["resultados"][torneio["fase_atual"]]:
                print(resultado)
        elif opcao == "4":
            salvar_torneio(caminho_torneio, torneio)
            print("Jogo salvo com sucesso!")
        elif opcao == "5":
            print("Saindo do menu torneio...")
            break
        else:
            print("Opção inválida!")

        # Checar se torneio acabou, se sim, retornar ao controller (break)
        if torneio["fase_atual"] == "final" and all(
            c.get("resultado") for c in torneio["rodadas"]["final"]
        ):
            print("Torneio finalizado!")
            break
