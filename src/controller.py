import os
from save import carregar_estado_torneio
from interface.menu_temporada import menu_temporada
from interface.menu_torneio import menu_torneio


def fluxo_principal(jogador_inst, nome_save, salvar_automaticamente):
    caminho_torneio = f"saves/{nome_save}/torneio_atp.json"
    if not os.path.exists(caminho_torneio):
        print("📁 Nenhum torneio salvo encontrado. Indo para a temporada.")
        return menu_temporada(jogador_inst, nome_save)

    estado = carregar_estado_torneio(caminho_torneio)
    fase = estado.get("fase_atual")
    jogador_vivo = estado.get("jogador_vivo", True)
    confrontos = estado.get("confrontos", [])
    resultados = estado.get("resultados", [])

    if not jogador_vivo:
        print("🟥 Você foi eliminado. Indo para a próxima semana...")
        return menu_temporada(jogador_inst, nome_save, salvar_automaticamente)

    if fase in ["final", "fase_indefinida"]:
        return menu_temporada(jogador_inst, nome_save, salvar_automaticamente)

    # Agora chama menu_torneio SEMPRE para qualquer estado válido do torneio
    return menu_torneio(resultados, confrontos, jogador_inst, nome_save)
