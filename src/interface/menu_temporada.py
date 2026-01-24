from src.calendario import avancar_semana, obter_torneios_da_semana
from src.io_utils import safe_input
from src.save import salvar_jogo
from src.torneio import criar_torneio, salvar_torneio


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
        print("[9] Salvar jogo")
        escolha = safe_input(
            "Escolha um torneio (número), 0 para avançar ou 9 para salvar: "
        ).strip()

        if escolha == "0":
            semana = avancar_semana(semana)
            if isinstance(jogador, dict):
                jogador["semana"] = semana
            else:
                jogador.semana = semana
            if salvar_automaticamente:
                salvar_jogo(nome_save, jogador)
                print("Semana avançada, jogador descansou!")
            else:
                print("Semana avançada, jogador descansou! (use a opção 9 para salvar)")
            continue
        if escolha == "9":
            salvar_jogo(nome_save, jogador)
            print("Jogo salvo com sucesso!")
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
                from src.interface.menu_torneio import menu_torneio

                # Chama o menu do torneio direto!
                menu_torneio(
                    jogador,
                    nome_save,
                    torneio=torneio,
                    salvar_automaticamente=salvar_automaticamente,
                )

                break
            else:
                print("Número de torneio inválido.")
        except ValueError:
            print("Entrada inválida, tente novamente.")
