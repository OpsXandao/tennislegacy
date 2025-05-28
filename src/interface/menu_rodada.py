from jogar_partida import jogar_partida
from jogador import Jogador, reidratar_jogador

def menu_rodadas(resultados_rodada, confrontos_atuais, jogador, nome_save, torneio):
    import os
    from src.save import carregar_estado_torneio
    from jogador import reidratar_jogador

    # 🔍 Garantia adicional de tipo correto
    if isinstance(jogador, dict):
        print("🔧 Reidratando jogador a partir de dict no menu_rodadas...")
        jogador = reidratar_jogador(jogador, nome_save)
    else:
        print(f"✅ Jogador já é instância de {type(jogador)}")

    def normalizar_jogador(j):
        if isinstance(j, dict):
            return {
                "nome": j.get("nome", "??"),
                "nacionalidade": j.get("nacionalidade", "??")
            }
        elif hasattr(j, "nome") and hasattr(j, "nacionalidade"):
            return {
                "nome": getattr(j, "nome", "??"),
                "nacionalidade": getattr(j, "nacionalidade", "??")
            }
        elif isinstance(j, str):
            return {"nome": j, "nacionalidade": "??"}
        else:
            return {"nome": "??", "nacionalidade": "??"}


    def jogar():
        if not confrontos_atuais:
            print("📭 Nenhum confronto restante.")
            return "fase_concluida"

        nome_jogador = jogador.nome.strip().lower()
        for a, b in confrontos_atuais:
            obj_a = normalizar_jogador(a)
            obj_b = normalizar_jogador(b)

            nomes = (obj_a["nome"].strip().lower(), obj_b["nome"].strip().lower())
            if nome_jogador in nomes:
                jogador_nome = jogador.nome.strip().lower()
                if obj_a["nome"].strip().lower() == jogador_nome:
                    adversario = obj_b
                else:
                    adversario = obj_a

                vencedor, placar = jogar_partida(jogador, adversario, nome_save)

                print(f"\n📋 {placar}")

                # Atualiza estado do torneio
                torneio.processar_resultado_partida(jogador, adversario, vencedor, placar)
                torneio.simular_npcs_na_fase_atual(jogador.nome) 
                break

        # Atualiza confrontos e resultados
        estado = carregar_estado_torneio(os.path.join("saves", nome_save, "torneio_atp.json"))
        nova_fase = estado["fase_atual"]

        if nova_fase == "pre_oitavas":
            if estado.get("jogador_vivo", False):
                print("🎉 Classificado no qualifying! Avançando para a chave principal...")
                torneio.jogar_chave_principal(torneio.ranking.carregar_ranking())
            else:
                print("❌ Desclassificado no qualifying.")
            return "fase_concluida"

        return None

    while True:
        print("\n🏟️ Menu:")
        print("1. ▶️ Jogar próxima partida")
        print("2. 📊 Rever resultados da última rodada")
        print("3. 🗓️ Ver confrontos da próxima fase")
        print("4. 💾 Salvar jogo")
        print("5. 🚪 Sair do torneio")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            resultado = jogar()
            if resultado == "fase_concluida":
                return "fase_concluida"

        elif opcao == "2":
            torneio.exibir_resultados()

        elif opcao == "3":
            torneio.exibir_confrontos_restantes()

        elif opcao == "4":
            from src.save import salvar_jogo
            salvar_jogo(nome_save, jogador)

        elif opcao == "5":
            return "sair_para_temporada"

        else:
            print("❌ Opção inválida!")
            


