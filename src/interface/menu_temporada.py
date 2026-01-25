from src.calendario import (
    avancar_semana,
    obter_torneios_da_semana,
    carregar_temporada,
    salvar_temporada,
)
from src.io_utils import safe_input, clear_screen, print_blue, print_green, print_red, print_yellow, print_magenta
from src.save import salvar_jogo
from src.torneio import criar_torneio


def _exibir_detalhes_e_confirmar(torneio):
    """Mostra os detalhes de um torneio e pede confirmação."""
    clear_screen()
    print_magenta("\n--- 📝 Detalhes do Torneio ---")
    print()
    print(f"Nome: {torneio.get('nome', '??')}")
    print(f"País: {torneio.get('pais_sede', '??')}")
    print(f"Tipo: {torneio.get('tipo', '??')}")
    print(f"Premiação: ${torneio.get('premiacao', 0):,}")
    print(f"Popularidade: {'⭐' * torneio.get('popularidade', 0)}")
    print("----------------------------")
    print()

    confirmar = safe_input("Deseja entrar neste torneio? (s/n): ").strip().lower()
    return confirmar == 's'


def _exibir_detalhes_davis_cup(torneio, jogador):
    """Mostra os detalhes da Copa Davis e pede confirmação."""
    clear_screen()
    print_magenta("\n--- 🏆 Copa Davis ---")
    print()
    print_blue("A Copa Davis é a principal competição de tênis por equipes nacionais!")
    print()
    print(f"Você representará: {jogador.nacionalidade}")
    print(f"Local das finais: {torneio.get('local', '??')}")
    print(f"País sede: {torneio.get('pais_sede', '??')}")
    print(f"Formato: {torneio.get('formato_partida', 'Melhor de 3 sets')}")
    print(f"Equipes participantes: {torneio.get('numero_equipes', 18)}")
    print(f"Premiação total: ${torneio.get('premiacao', 0):,}")
    print()
    print_yellow("📋 Formato da competição:")
    print("   - Fase de grupos com 6 grupos de 3 equipes")
    print("   - Os 2 melhores de cada grupo avançam")
    print("   - Fase eliminatória até a final")
    print()
    print_yellow("📋 Cada confronto (tie):")
    print("   - 2 partidas de simples")
    print("   - 1 partida de duplas")
    print("   - Você jogará as partidas de simples pela sua seleção")
    print()
    print("----------------------------")
    print()

    confirmar = safe_input("Deseja inscrever sua seleção na Copa Davis? (s/n): ").strip().lower()
    return confirmar == 's'


def menu_temporada(jogador, nome_save, salvar_automaticamente=False):
    """Menu da temporada, onde o jogador escolhe torneios ou descansa."""
    while True:
        clear_screen()
        temporada = carregar_temporada(nome_save)
        ano, semana = temporada["ano"], temporada["semana"]

        print_blue(f"\n--- 📅 Calendário da Temporada: Ano {ano}, Semana {semana} ---")
        print()
        
        # Exibe status de fadiga e lesão
        status_str = f"Fadiga: {jogador.fadiga}% | Status: "
        if jogador.status_lesao["lesionado"]:
            status_str += f"Lesionado ({jogador.status_lesao['semanas_restantes']} semanas restantes)"
        else:
            status_str += "Saudável"
        print_yellow(status_str)
        print("-" * (len(status_str) if len(status_str) > 40 else 40))
        print()

        torneios = obter_torneios_da_semana(semana)
        
        if not torneios:
            print_yellow("  - Nenhum torneio disponível nesta semana.")
        for idx, torneio in enumerate(torneios, 1):
            nome = torneio.get("nome", "??")
            tipo = torneio.get("tipo", "??")
            # Marca Davis Cup como especial
            if tipo == "Davis Cup":
                if jogador.genero == "feminino":
                    print_yellow(f"[{idx}] 🏆 {nome} ({tipo}) - Apenas masculino")
                else:
                    print_green(f"[{idx}] 🏆 {nome} ({tipo}) - Por equipes")
            else:
                print_green(f"[{idx}] 🏆 {nome} ({tipo})")

        print_blue("\n--- 🎮 Opções ---")
        print()
        print_green("[0] 🔙 Voltar ao Menu Principal")
        print_green("[d] 😴 Descansar (avançar semana)")
        print_green("[s] 💾 Salvar Jogo")
        print()
        
        escolha = safe_input(
            "Escolha um torneio (número) ou uma opção: "
        ).strip().lower()

        if escolha == "0":
            return False  # Volta para o menu principal
        
        if escolha == 'd':
            avancar_semana(nome_save)
            # O jogador é recarregado dentro do loop na proxima iteração
            from src.jogador import carregar_jogador
            jogador = carregar_jogador(nome_save)
            continue  # Recarrega a temporada

        if escolha == 's':
            salvar_jogo(nome_save, jogador)
            salvar_temporada(nome_save, temporada)
            print_green("✅ Jogo salvo com sucesso!")
            continue

        try:
            escolha_idx = int(escolha)
            if 1 <= escolha_idx <= len(torneios):
                if jogador.status_lesao["lesionado"]:
                    print_red(f"\n❌ Você está lesionado e não pode competir por mais {jogador.status_lesao['semanas_restantes']} semana(s).")
                    safe_input("Pressione Enter para continuar...")
                    continue

                torneio_escolhido = torneios[escolha_idx - 1]

                # Verifica se é Davis Cup e se o jogador pode participar
                if torneio_escolhido.get("tipo") == "Davis Cup":
                    if jogador.genero == "feminino":
                        print_red("\n❌ A Copa Davis é um torneio exclusivamente masculino.")
                        print_yellow("   A Billie Jean King Cup (torneio feminino) será adicionada em breve!")
                        safe_input("Pressione Enter para continuar...")
                        continue

                    # Exibe detalhes especiais da Davis Cup
                    if _exibir_detalhes_davis_cup(torneio_escolhido, jogador):
                        from src.davis_cup import criar_torneio_davis
                        print_yellow(f"\n📝 Inscrevendo {jogador.nacionalidade} na Copa Davis...")
                        criar_torneio_davis(torneio_escolhido, jogador, nome_save, semana)

                        print_green("✅ Sua seleção foi inscrita! A Copa Davis vai começar.")
                        safe_input("Pressione Enter para continuar...")
                        return True
                    else:
                        print_yellow("Inscrição cancelada.")
                    continue

                if _exibir_detalhes_e_confirmar(torneio_escolhido):
                    print_yellow(f"\n📝 Inscrevendo-se no {torneio_escolhido['nome']}...")
                    criar_torneio(torneio_escolhido, jogador, nome_save, semana)

                    print_green("✅ Inscrição confirmada! O torneio vai começar.")
                    safe_input("Pressione Enter para continuar...")
                    return True
                else:
                    print_yellow("Inscrição cancelada.")
            else:
                print_red("❌ Número de torneio inválido.")
        except ValueError:
            print_red("❌ Entrada inválida, tente novamente.")
