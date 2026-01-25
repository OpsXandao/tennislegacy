import os

from src.dados import get_caminho_torneio_save, carregar_estado_torneio
from src.interface.menu_principal import menu_principal
from src.interface.menu_torneio import menu_torneio
from src.interface.menu_davis import menu_davis
from src.pontuacao import distribuir_pontos_torneio


def fluxo_principal(jogador_inst, nome_save, salvar_automaticamente=False):
    """
    Controlador principal que direciona o jogador para o menu apropriado.
    """
    while True:
        caminho_torneio = get_caminho_torneio_save(nome_save)

        if not os.path.exists(caminho_torneio):
            # Não há torneio em andamento, vai para o menu principal (hub)
            sair_jogo = menu_principal(jogador_inst, nome_save, salvar_automaticamente)
            # Se o jogador sair do menu_principal (ex: com a opção "Sair"), o loop termina.
            if sair_jogo:
                break
            continue

        # Se existe um arquivo de torneio, vamos processá-lo.
        estado = carregar_estado_torneio(nome_save)
        fase = estado.get("fase_atual")
        jogador_vivo = estado.get("jogador_vivo", True)
        tipo_torneio = estado.get("tipo", "")

        # Verifica se é Copa Davis
        if tipo_torneio == "Davis Cup":
            fases_davis_ativas = ["grupos", "quartas", "semifinal", "final"]
            jogador_convocado = estado.get("jogador_convocado", False)

            if jogador_vivo and jogador_convocado and fase in fases_davis_ativas:
                menu_davis(jogador_inst, nome_save, salvar_automaticamente=salvar_automaticamente)
                continue
            else:
                # Davis Cup terminou ou jogador não foi convocado/eliminado
                if not jogador_convocado:
                    print("\n⚠️ Você não foi convocado para a Copa Davis.")
                elif not jogador_vivo:
                    print("\n🟥 Sua seleção foi eliminada da Copa Davis.")
                else:
                    print("\n🏁 Copa Davis concluída.")

                # Remove o arquivo do torneio
                try:
                    os.remove(caminho_torneio)
                    print(f"🗑️ Arquivo do torneio removido.")
                except OSError as e:
                    print(f"❌ Erro ao remover o arquivo do torneio: {e}")
                continue

        # Torneios normais (ATP, Grand Slam)
        fases_ativas = ["qualy_1", "qualy_2", "qualy_r1", "qualy_r2", "qualy_r3",
                        "pre_oitavas", "oitavas", "r128", "r64", "r32", "r16",
                        "quartas", "semifinal", "final"]

        if jogador_vivo and fase in fases_ativas:
            # Jogador está ativo em um torneio, vai para o menu do torneio.
            menu_torneio(jogador_inst, nome_save, salvar_automaticamente=salvar_automaticamente)
            # Após o menu_torneio, o loop continua, forçando a reavaliação do estado.
            continue
        else:
            # O torneio terminou ou o jogador foi eliminado.
            if not jogador_vivo:
                print("\n🟥 Você foi eliminado do torneio. Avançando para a próxima semana...")
            else:
                print("\n🏁 Torneio concluído. Avançando para a próxima semana...")

            # 1. Distribui os pontos
            distribuir_pontos_torneio(nome_save)

            # 2. Remove o arquivo do torneio
            try:
                os.remove(caminho_torneio)
                print(f"🗑️ Arquivo do torneio '{os.path.basename(caminho_torneio)}' removido.")
            except OSError as e:
                print(f"❌ Erro ao remover o arquivo do torneio: {e}")
            
            # Após finalizar o torneio, o loop vai continuar e, como o arquivo não existe mais,
            # ele vai chamar o menu_principal na próxima iteração.
            continue
