"""
Menu da Copa Davis - Interface para o torneio por equipes.
"""

from src.dados import get_caminho_ranking_save
from src.interface.match_info import exibir_stats_adversario, exibir_review_partida
from src.ranking import SistemaRanking
from src.io_utils import (
    safe_input,
    clear_screen,
    print_blue,
    print_green,
    print_red,
    print_yellow,
)
from src.save import salvar_jogo
from src.davis_cup import carregar_davis_cup


def menu_davis(jogador, nome_save, davis=None, salvar_automaticamente=False):
    """Menu principal da Copa Davis."""
    if davis is None:
        davis = carregar_davis_cup(nome_save, jogador)

    if davis is None:
        print_red("Erro ao carregar a competição por equipes.")
        return

    saiu_manual = False
    competicao_encerrada = False

    while True:
        clear_screen()
        estado = davis._carregar_estado()
        fase = estado.get("fase_atual", "qualifiers")
        pais_jogador = estado.get("pais_jogador", jogador.nacionalidade)
        tipo_competicao = estado.get("tipo", "Davis Cup")
        nome_competicao = (
            "Copa Davis" if tipo_competicao == "Davis Cup" else "Billie Jean King Cup"
        )

        print_blue(f"\n{'=' * 60}")
        print_blue(
            f"          🏆 {nome_competicao.upper()} - {estado.get('torneio', tipo_competicao)}"
        )
        print_blue(f"{'=' * 60}")
        print()
        print(f"📍 Sua seleção: {pais_jogador}")
        print(f"📍 Fase atual: {_formatar_fase(fase)}")
        info_confronto = davis.obter_info_confronto_atual()
        if info_confronto:
            cidade = info_confronto.get("cidade")
            pais_sede = info_confronto.get("pais_sede")
            superficie = info_confronto.get("superficie")
            if cidade and pais_sede:
                print(f"📍 Sede do tie: {cidade}, {pais_sede}")
            if superficie:
                print(f"📍 Superfície: {superficie}")
        print()
        davis.exibir_tabela_grupo()

        # Verifica próximo confronto
        proximo = davis.obter_proximo_confronto()

        print_blue("\n--- 🎮 Opções ---")
        print()

        if proximo:
            adversario = proximo.get("adversario", "??")
            print_green(f"[1] 🎾 Jogar confronto vs {adversario}")
            print_green("[2] 🔎 Ver stats do adversário")
            print_green("[3] 🧪 Review do confronto")
        else:
            print_yellow("[1] 🎾 Nenhum confronto disponível")
            print_yellow("[2] 🔎 Ver stats do adversário")
            print_yellow("[3] 🧪 Review do confronto")

        print_green("[4] 📊 Ver chave/classificação")
        print_green("[5] 📋 Ver resultados")
        print_green("[6] 💾 Salvar jogo")
        print_green("[7] ↩️ Sair do menu")
        print()

        opcao = safe_input("Escolha uma opção: ").strip()

        if opcao == "1":
            if proximo:
                adversario = proximo.get("adversario")
                resultado = davis.jogar_confronto(adversario)

                if resultado.get("eliminado"):
                    print_red(
                        f"\n😔 {pais_jogador} foi eliminado da {nome_competicao}!"
                    )
                    safe_input("Pressione Enter para continuar...")
                    break

                if salvar_automaticamente:
                    davis._salvar_estado(davis._carregar_estado())
                    salvar_jogo(nome_save, jogador)
            else:
                print_yellow("Não há confronto disponível no momento.")
                safe_input("Pressione Enter para continuar...")

        elif opcao in ("2", "3"):
            if not proximo:
                print_yellow("Nenhum confronto disponível no momento.")
                safe_input("Pressione Enter para continuar...")
                continue
            adversario_principal = _obter_adversario_principal(proximo, davis)
            if not adversario_principal:
                safe_input("Pressione Enter para continuar...")
                continue
            ranking = SistemaRanking(get_caminho_ranking_save(nome_save))
            if opcao == "2":
                exibir_stats_adversario(jogador, adversario_principal, ranking)
            else:
                exibir_review_partida(jogador, adversario_principal, ranking)
            safe_input("\nPressione Enter para continuar...")
        elif opcao == "4":
            davis.exibir_tabela_grupo()
            safe_input("\nPressione Enter para continuar...")

        elif opcao == "5":
            _exibir_resultados_davis(davis)
            safe_input("\nPressione Enter para continuar...")

        elif opcao == "6":
            davis._salvar_estado(davis._carregar_estado())
            salvar_jogo(nome_save, jogador)
            print_green("Jogo salvo com sucesso!")
            safe_input("Pressione Enter para continuar...")

        elif opcao == "7":
            print_yellow(f"Saindo do menu da {nome_competicao}...")
            saiu_manual = True
            break

        else:
            print_red("Opção inválida!")
            safe_input("Pressione Enter para continuar...")

        # Verifica se o jogador ainda está ativo
        if not davis.jogador_ainda_ativo():
            estado = davis._carregar_estado()
            fase_atual = estado.get("fase_eliminacao") or estado.get("fase_atual", "")

            if fase_atual == "eliminado_grupos":
                print_red(
                    f"\n😔 {pais_jogador} não se classificou para as eliminatórias!"
                )
            elif fase_atual == "eliminado_qualifiers":
                print_red(
                    f"\n😔 {pais_jogador} foi eliminado nos Qualifiers da {nome_competicao}!"
                )
            else:
                print_red(
                    f"\n😔 {pais_jogador} foi eliminado na fase {_formatar_fase(fase_atual)}!"
                )

            print_yellow("\n💪 Volte mais forte na próxima edição!")
            safe_input("Pressione Enter para continuar...")
            competicao_encerrada = True
            break

        # Verifica se a Copa Davis terminou
        estado = davis._carregar_estado()
        if estado.get("fase_atual") == "finalizado":
            print_green(f"\n🎉 A {nome_competicao} foi concluída!")
            if estado.get("jogador_vivo"):
                print_green(
                    f"🏆 {pais_jogador} É CAMPEÃO DA {nome_competicao.upper()}!"
                )
            safe_input("Pressione Enter para continuar...")
            competicao_encerrada = True
            break

    if saiu_manual:
        return "saiu"
    if competicao_encerrada:
        return "finalizado"
    return "saiu"


def _obter_adversario_principal(proximo, davis):
    """Retorna o jogador principal do próximo adversário ou None com mensagem de erro."""
    adversario = proximo.get("adversario")
    equipe = davis._gerar_equipe_adversaria(adversario)
    adversario_principal = equipe[0] if equipe else None
    if not adversario_principal:
        print_red("Não foi possível carregar o adversário.")
    return adversario_principal


def _formatar_fase(fase):
    """Formata o nome da fase para exibição."""
    fases = {
        "qualifiers": "Qualifiers",
        "quartas": "Quartas de Final",
        "semifinal": "Semifinal",
        "final": "Final",
        "eliminado_qualifiers": "Eliminado nos Qualifiers",
        "eliminado_grupos": "Eliminado na Fase de Grupos",
        "finalizado": "Torneio Finalizado",
    }
    return fases.get(fase, fase.capitalize())


def _exibir_resultados_davis(davis):
    """Exibe os resultados dos confrontos da Copa Davis."""
    estado = davis._carregar_estado()
    resultados = estado.get("resultados_confrontos", [])
    tipo_competicao = estado.get("tipo", "Davis Cup")
    nome_competicao = (
        "Copa Davis" if tipo_competicao == "Davis Cup" else "Billie Jean King Cup"
    )

    print_blue(f"\n{'=' * 60}")
    print_blue(f"              📊 RESULTADOS DA {nome_competicao.upper()}")
    print_blue(f"{'=' * 60}")

    if not resultados:
        print_yellow("\nNenhum resultado ainda.")
        return

    for i, r in enumerate(resultados, 1):
        equipe_a = r.get("equipe_a", "??")
        equipe_b = r.get("equipe_b", "??")
        vencedor = r.get("vencedor", "??")
        placar = r.get("placar", "?-?")
        cidade = r.get("cidade")
        pais_sede = r.get("pais_sede")
        superficie = r.get("superficie")

        marcador = " 🏆" if vencedor == equipe_a else ""
        marcador_b = " 🏆" if vencedor == equipe_b else ""

        print(f"\n{i}. {equipe_a}{marcador} {placar} {equipe_b}{marcador_b}")
        if cidade and pais_sede:
            local_txt = f"   📍 {cidade}, {pais_sede}"
            if superficie:
                local_txt += f" | {superficie}"
            print(local_txt)

        # Mostra detalhes das partidas
        partidas = r.get("partidas", [])
        for p in partidas:
            tipo = p.get("tipo", "?")
            if tipo == "simples":
                jog_a = p.get("jogador_a", "??")
                jog_b = p.get("jogador_b", "??")
                venc = p.get("vencedor", "??")
                pl = p.get("placar", "?")
                vencedor_marca = "✓" if venc == jog_a else ""
                vencedor_marca_b = "✓" if venc == jog_b else ""
                print(
                    f"   └ {tipo.capitalize()}: {jog_a} {vencedor_marca} vs {jog_b} {vencedor_marca_b} ({pl})"
                )
            else:
                pl = p.get("placar", "?")
                print(f"   └ {tipo.capitalize()}: {pl}")

    print()
