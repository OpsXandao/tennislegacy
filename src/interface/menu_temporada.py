import os
from interface import menu_torneio
from src.calendario import obter_torneios_semana, avancar_semana
from src.torneio import criar_torneio, salvar_torneio
from src.save import salvar_jogo, carregar_jogo


def menu_temporada(jogador, nome_save):
    semana = jogador.get("semana", 1)
    while True:
        print(f"\n📅 Semana {semana} da temporada")
        torneios = obter_torneios_semana(semana)
        print("Torneios disponíveis:")
        for idx, torneio in enumerate(torneios, 1):
            print(
                f"{idx}. {torneio['nome']} | País: {torneio['pais']} | Premiação: {torneio['premiacao']}"
            )

        print("\n[0] Avançar semana (descansar)")
        escolha = input(
            "Escolha um torneio para participar (número) ou 0 para avançar: "
        ).strip()

        if escolha == "0":
            semana = avancar_semana(semana)
            jogador["semana"] = semana
            salvar_jogo(jogador, nome_save)
            print("Semana avançada, jogador descansou!")
            continue

        try:
            escolha = int(escolha)
            if 1 <= escolha <= len(torneios):
                torneio_escolhido = torneios[escolha - 1]
                print(
                    f"\n📝 Você escolheu o torneio {torneio_escolhido['nome']} em {torneio_escolhido['pais']}!"
                )
                torneio = criar_torneio(torneio_escolhido, jogador, nome_save, semana)
                salvar_torneio(torneio, nome_save)
                print("Torneio iniciado! Indo para o menu do torneio...")
                # Aqui você chama seu menu_torneio.py, passando nome_save e/ou jogador
                menu_torneio(nome_save)
                break
            else:
                print("Número de torneio inválido.")
        except ValueError:
            print("Entrada inválida, tente novamente.")
