from src.calendario import obter_torneios_da_semana, avancar_semana
from src.torneio import criar_torneio, salvar_torneio
from src.save import salvar_jogo


def menu_temporada(jogador, nome_save, salvar_automaticamente=False):
    semana = getattr(jogador, "semana", 1)
    while True:
        print(f"\n📅 Semana {semana} da temporada")
        torneios = obter_torneios_da_semana(semana)
        print("Torneios disponíveis:")
        for idx, torneio in enumerate(torneios, 1):
            nome = torneio.get("nome", "??")
            pais = torneio.get("pais_sede", "??")
            premiacao = torneio.get("premiacao", "??")
            print(f"{idx}. {nome} | País: {pais} | Premiação: {premiacao}")

        print("[0] Avançar semana (descansar)")
        escolha = input(
            "Escolha um torneio para participar (número) ou 0 para avançar: "
        ).strip()

        if escolha == "0":
            semana = avancar_semana(semana)
            jogador["semana"] = semana
            salvar_jogo(nome_save, jogador)
            print("Semana avançada, jogador descansou!")
            continue

        try:
            escolha = int(escolha)
            if 1 <= escolha <= len(torneios):
                torneio_escolhido = torneios[escolha - 1]
                print(
                    f"\n📝 Você escolheu o torneio {torneio_escolhido['nome']} "
                    f"em {torneio_escolhido.get('pais_sede', '??')}!"
                )
                torneio = criar_torneio(torneio_escolhido, jogador, nome_save, semana)
                salvar_torneio(torneio)
                from interface.menu_torneio import (
                    menu_torneio,
                )  # ajuste o import se necessário

                # Chama o menu do torneio direto!
                menu_torneio(torneio, jogador, nome_save)

                break
            else:
                print("Número de torneio inválido.")
        except ValueError:
            print("Entrada inválida, tente novamente.")
