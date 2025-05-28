import os,builtins
from src.calendario import obter_torneios_da_semana
from interface.menu_rodada import menu_rodadas
from src.save import salvar_jogo, carregar_estado_torneio
from src.ranking import SistemaRanking
from src.torneio import TorneioATP250

def exibir_torneios_disponiveis(torneios):
    print("🎾 Torneios disponíveis:")
    for idx, t in enumerate(torneios, 1):
        estrelas = "⭐" * t["dificuldade"]
        print(f"{idx}. {t['nome']} ({t['pais_sede']}) - {t['tipo']} - Popularidade: {t['popularidade']} ⭐ | Dificuldade: {estrelas} | Premiação: ${t['premiacao']}")

def menu_temporada(jogador, nome_save, salvar_automaticamente, semana_atual):
    try:
        from src.jogador import criar_jogador, carregar_jogador, reidratar_jogador

        if isinstance(jogador, dict):
            jogador = reidratar_jogador(jogador, nome_save)

        if not jogador:
            jogador = criar_jogador(nome_save)
            from src.jogador import reidratar_jogador
            jogador = reidratar_jogador(jogador.to_dict(), nome_save)



        print(f"\n🗕️ Semana {semana_atual} da temporada")


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

        # Carrega ranking e jogadores
        ranking_path = os.path.join("saves", nome_save, "ranking_atp.json")
        ranking = SistemaRanking(ranking_path)
        jogadores_disponiveis = ranking.carregar_ranking()
        jogadores_info = [{"nome": j["nome"], "nacionalidade": j.get("nacionalidade", "??")} for j in jogadores_disponiveis]

        # Inicializa ou retoma torneio
        torneio = TorneioATP250(semana_atual, jogador.nome, jogador.nacionalidade, ranking, nome_save)
        caminho_torneio = os.path.join("saves", nome_save, "torneio_atp.json")

        if not os.path.exists(caminho_torneio) or os.path.getsize(caminho_torneio) == 0:
            torneio.iniciar_torneio(torneio_escolhido["nome"], jogadores_info)

        estado = carregar_estado_torneio(caminho_torneio)
        if not estado:
            print("⚠️ Estado inválido do torneio. Pulando semana.")
            return None

        # 🔄 Sincroniza a semana com o JSON salvo

        if "semana" in estado:
            semana_atual = estado["semana"]
            builtins.semana_atual = semana_atual  # 👈 persiste no jogo inteiro


        if not estado.get("jogador_vivo", True):
            print("📴 Você já foi eliminado deste torneio.")
            torneio.simular_torneio_restante(jogadores_info)
            return jogador

        # Monta confrontos para o jogador
        confrontos_obj = [
            (
                next((j for j in jogadores_info if j["nome"] == a), {"nome": a, "nacionalidade": "??"}),
                next((j for j in jogadores_info if j["nome"] == b), {"nome": b, "nacionalidade": "??"})
            ) for a, b in estado["confrontos"]
        ]

        menu_rodadas(estado["resultados"], confrontos_obj, jogador, nome_save, torneio)

        if salvar_automaticamente:
            salvar_jogo(nome_save, jogador)

        return jogador

    except Exception as e:
        print(f"❌ Erro no menu da temporada: {e}")
        return None


def simular_torneio(self, jogador_inst):
    estado = self._carregar_estado()
    fases = ["qualy_1", "qualy_2", "pre_oitavas", "oitavas", "quartas", "semifinal", "final"]

    try:
        while True:
            fase = estado["fase_atual"]
            confrontos = estado["rodadas"].get(fase, [])
            resultados = estado["resultados"].get(fase, [])

            if not confrontos:
                self._atualizar_fase_se_necessario(estado)
                estado = self._carregar_estado()
                if estado["fase_atual"] == "finalizado":
                    break
                continue

            jogador_vivo = estado.get("jogador_vivo", True)
            nome_jogador = jogador_inst.nome.strip().lower()
            ainda_disputa = any(
                nome_jogador in [a.strip().lower(), b.strip().lower()]
                for a, b in confrontos
            )

            if jogador_vivo and ainda_disputa:
                from jogador import reidratar_jogador

                if isinstance(jogador_inst, dict):
                    jogador_inst = reidratar_jogador(jogador_inst, self.nome_save)

                resultado = menu_rodadas(resultados[fase], confrontos, jogador_inst, self.nome_save, self)


                if resultado == "sair_para_temporada":
                    break

                estado = self._carregar_estado()
                continue

            else:
                print("📴 Jogador eliminado. Simulando as rodadas restantes...")
                self.simular_torneio_restante([{"nome": a} for a, _ in confrontos] + [{"nome": b} for _, b in confrontos])
                break

        return estado.get("jogador_vivo", False), estado["resultados"]["final"][0].split(" ")[0] if estado["resultados"]["final"] else None

    except Exception as e:
        print(f"❌ Erro ao simular torneio: {e}")
        return False, None
