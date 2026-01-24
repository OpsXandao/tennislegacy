import os

from src.dados import get_caminho_torneio_save
from src.save import carregar_estado_torneio
from src.interface.menu_temporada import menu_temporada
from src.interface.menu_torneio import menu_torneio


def fluxo_principal(jogador_inst, nome_save, salvar_automaticamente=False):
    caminho_torneio = get_caminho_torneio_save(nome_save)
    if not os.path.exists(caminho_torneio):
        # Nao ha torneio em andamento, vai para o menu da temporada
        return menu_temporada(jogador_inst, nome_save, salvar_automaticamente)

    estado = carregar_estado_torneio(caminho_torneio)
    fase = estado.get("fase_atual")
    jogador_vivo = estado.get("jogador_vivo", True)

    # Lista de fases onde o torneio está ativamente sendo jogado
    fases_ativas = ["qualy_1", "qualy_2", "pre_oitavas", "oitavas", "quartas", "semifinal", "final"]

    # Se o jogador foi eliminado OU a fase atual não é uma fase ativa válida,
    # o torneio é considerado encerrado para o jogador.
    if not jogador_vivo or fase not in fases_ativas:
        if not jogador_vivo:
            print("🟥 Você foi eliminado do torneio. Avançando para a próxima semana...")
        else:
            # Cobre fases como "finalizado", "fase_indefinida", None, etc.
            print("🏁 Torneio concluído. Avançando para a próxima semana...")
        
        # Opcional: Futuramente, adicionar aqui a lógica para limpar o arquivo do torneio.
        # Por exemplo: os.remove(caminho_torneio)
        
        return menu_temporada(jogador_inst, nome_save, salvar_automaticamente)

    # Se o jogador está vivo e o torneio está em uma fase ativa, vai para o menu do torneio.
    return menu_torneio(jogador_inst, nome_save, salvar_automaticamente=salvar_automaticamente)
