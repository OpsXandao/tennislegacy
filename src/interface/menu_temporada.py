import json
import os, builtins
from src.calendario import obter_torneios_da_semana
from interface.menu_torneio import menu_rodadas
from src.save import salvar_jogo, carregar_estado_torneio
from src.ranking import SistemaRanking
from src.torneio import TorneioATP250
from src.jogador import criar_jogador, reidratar_jogador

def exibir_torneios_disponiveis(torneios):
    print("🎾 Torneios disponíveis:")
    for idx, t in enumerate(torneios, 1):
        estrelas = "⭐" * t["dificuldade"]
        print(f"{idx}. {t['nome']} ({t['pais_sede']}) - {t['tipo']} - Popularidade: {t['popularidade']} ⭐ | Dificuldade: {estrelas} | Premiação: ${t['premiacao']}")

def menu_temporada(jogador, nome_save, salvar_automaticamente, semana_atual):
    try:
        print(f"🔁 DEBUG: Tipo do jogador recebido: {type(jogador)}")
        if isinstance(jogador, dict):
            jogador = reidratar_jogador(jogador, nome_save)

        print(f"🎯 DEBUG: Jogador atual: {jogador.nome} ({jogador.nacionalidade})")
        print(f"\n🗕️ Semana {semana_atual} da temporada")

        caminho_torneio = os.path.join("saves", nome_save, "torneio_atp.json")
        if os.path.exists(caminho_torneio):
            print("📂 DEBUG: Arquivo de estado do torneio encontrado.")
            estado = carregar_estado_torneio(caminho_torneio)

            if estado and estado.get("fase_atual") and estado.get("jogador_vivo", True):
                print(f"📄 DEBUG: Estado carregado: {estado.get('fase_atual', 'sem fase')}")
                print("📂 Retomando o torneio salvo da Fase atual...")

                ranking_path = os.path.join("saves", nome_save, "ranking_atp.json")
                ranking = SistemaRanking(ranking_path)
                torneio = TorneioATP250(semana_atual, jogador.nome, jogador.nacionalidade, ranking, nome_save)
                jogadores_disponiveis = ranking.carregar_ranking()

                if not estado.get("jogador_vivo", True):
                    print("📴 Você já foi eliminado deste torneio.")
                    torneio.simular_torneio_restante(jogadores_disponiveis)
                    return jogador

                confrontos_raw = estado.get("confrontos", [])
                confrontos_obj = torneio.normalizar_confrontos(confrontos_raw)

                menu_rodadas(estado["resultados"], confrontos_obj, jogador, nome_save, torneio)

                if salvar_automaticamente:
                    salvar_jogo(nome_save, jogador)

                return jogador

        torneios = obter_torneios_da_semana(semana_atual)
        if not torneios:
            print("📍 Nenhum torneio disponível nesta semana.")
            return None

        exibir_torneios_disponiveis(torneios)
        escolha = input("Escolha um torneio (número ou Enter para pular semana): ").strip()

        try:
            idx = int(escolha) - 1
            torneio_escolhido = torneios[idx]
        except (ValueError, IndexError):
            print("⏭️ Pulando semana...")
            return None

        print(f"\n📝 Você escolheu o torneio {torneio_escolhido['nome']} em {torneio_escolhido['pais_sede']}!")

        ranking_path = os.path.join("saves", nome_save, "ranking_atp.json")
        ranking = SistemaRanking(ranking_path)
        jogadores_disponiveis = ranking.carregar_ranking()
        jogadores_info = [{"nome": j["nome"], "nacionalidade": j.get("nacionalidade", "??")} for j in jogadores_disponiveis]

        torneio = TorneioATP250(semana_atual, jogador.nome, jogador.nacionalidade, ranking, nome_save)
        torneio.iniciar_torneio(torneio_escolhido["nome"], jogadores_info)

        estado = carregar_estado_torneio(caminho_torneio)
        if not estado:
            print("⚠️ Estado inválido do torneio. Pulando semana.")
            return None

        if "semana" in estado:
            semana_atual = estado["semana"]
            builtins.semana_atual = semana_atual

        if not estado.get("jogador_vivo", True):
            print("📴 Você já foi eliminado deste torneio.")
            torneio.simular_torneio_restante(jogadores_info)
            return jogador

        confrontos_raw = estado.get("confrontos", [])
        confrontos_obj = torneio.normalizar_confrontos(confrontos_raw)
        menu_rodadas(estado["resultados"], confrontos_obj, jogador, nome_save, torneio)

        if salvar_automaticamente:
            salvar_jogo(nome_save, jogador)

        return jogador

    except Exception as e:
        print(f"❌ Erro no menu da temporada: {e}")
        return None
