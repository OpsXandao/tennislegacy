
import json
from calendario import obter_torneios_da_semana
from torneio import TorneioATP250
from ranking import SistemaRanking

def menu_principal(jogador):
    semana_atual = 1

    def jogar_temporada():
        nonlocal semana_atual
        print(f"\n📅 Semana {semana_atual} da temporada")
        torneios = obter_torneios_da_semana(semana_atual)
        if not torneios:
            print("📭 Nenhum torneio disponível nesta semana.")
            return

        print("🎾 Torneios disponíveis:")
        for idx, torneio in enumerate(torneios, 1):
            estrelas = "★" * torneio["dificuldade"]
            print(f"{idx}. {torneio['nome']} ({torneio['pais_sede']}) - {torneio['tipo']} - Popularidade: {torneio['popularidade']}⭐ | Dificuldade: {estrelas} | Premiação: ${torneio['premiacao']}")

        escolha = input("Escolha um torneio para participar (número ou Enter para cancelar): ")
        if escolha.isdigit() and 1 <= int(escolha) <= len(torneios):
            torneio_escolhido = torneios[int(escolha) - 1]
            print(f"\n📝 Você escolheu o torneio {torneio_escolhido['nome']} em {torneio_escolhido['pais_sede']}!")

            # Carrega jogadores do ranking com nacionalidade
            with open("save/atp.json", "r") as f:
                ranking_dados = json.load(f)
                jogadores_disponiveis = [
                    {"nome": p["nome"], "nacionalidade": p.get("nacionalidade", "N/A")}
                    for p in ranking_dados
                ]

            # Cria instância da classe de torneio
            ranking = SistemaRanking("save/atp.json")
            torneio_atp = TorneioATP250(semana_atual, jogador.nome, jogador.nacionalidade, ranking)
            classificados, lucky = torneio_atp.simular_torneio(jogadores_disponiveis)

            if lucky:
                print("🍀 Você entrou no torneio como Lucky Loser!")
            elif jogador.nome in [j["nome"] for j in classificados]:
                print("✅ Você se classificou para a chave principal!")
            else:
                print("🚫 Você não se classificou.")

        else:
            print("🚫 Ação cancelada.")

        semana_atual += 1

    opcoes = {
        "1": jogador.mostrar_status,
        "2": jogador.jogar_partida,
        "3": jogar_temporada,
        "4": lambda: print("👋 Saindo do jogo. Até a próxima!") or exit()
    }

    while True:
        print("\n🏟️ Menu Principal")
        print("1. Ver status do jogador")
        print("2. Jogar uma partida oficial")
        print("3. Jogar temporada")
        print("4. Sair")

        opcao = input("Escolha uma opção: ")

        acao = opcoes.get(opcao)
        if acao:
            acao()
        else:
            print("❌ Opção inválida!")