from jogador import carregar_jogador, criar_jogador
from save import carregar_ou_redirecionar
import builtins


def menu_inicial():
    print("\n🎾 Bem-vindo ao TennisLegacy!")
    print("1. Iniciar novo jogo")
    print("2. Carregar jogo salvo")

    escolha = input("Escolha uma opção (1 ou 2): ").strip()
    nome_save = input("🎮 Nome do seu save: ").strip()
    salvar_automaticamente = (
        input("📎 Deseja salvar automaticamente após cada partida ou torneio? (s/n): ")
        .strip()
        .lower()
        == "s"
    )

    builtins.nome_save = nome_save

    if escolha == "1":
        jogador_inst = criar_jogador(nome_save)
    elif escolha == "2":
        jogador_inst = carregar_jogador(nome_save)
    else:
        print("❌ Opção inválida.")
        return menu_inicial()

    builtins.jogador = jogador_inst
    carregar_ou_redirecionar(jogador_inst, nome_save, salvar_automaticamente)
