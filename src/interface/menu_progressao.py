from src.io_utils import (
    safe_input,
    clear_screen,
    print_blue,
    print_green,
    print_red,
    print_magenta,
    print_yellow,
)
from src.save import salvar_jogo

_W = 60


def menu_progressao(jogador, nome_save):
    """Menu para gastar Pontos de Skill e melhorar atributos."""
    if jogador is None:
        print_red("❌ Jogador não carregado.")
        return
    while True:
        clear_screen()
        print(f"\n{'═' * _W}")
        print_blue(f"{'PROGRESSÃO DE ATRIBUTOS':^{_W}}")
        print(f"{'═' * _W}")
        print()

        pts = jogador.pontos_de_skill
        if pts > 0:
            print_green(f"  🔥 Pontos de Skill disponíveis: {pts}")
        else:
            print_yellow("  Pontos de Skill: 0  —  jogue partidas para ganhar XP")
        print()

        opcoes = []

        print_magenta("  Técnicos:")
        for i, (attr, valor) in enumerate(jogador.atributos.items(), 1):
            opcoes.append(("tecnico", attr))
            sufixo = "  (MAX)" if valor >= 100 else ""
            print(f"  [{i:>2}] 💪 {attr.title():<14} {valor:>3}{sufixo}")

        print()
        print_magenta("  Psicológicos:")
        for j, (attr, valor) in enumerate(
            jogador.atributos_psicologicos.items(), len(opcoes) + 1
        ):
            opcoes.append(("psicologico", attr))
            nome_fmt = attr.replace("_", " ").title()
            sufixo = "  (MAX)" if valor >= 100 else ""
            print(f"  [{j:>2}] 🧠 {nome_fmt:<18} {valor:>3}{sufixo}")

        print()
        print(f"{'─' * _W}")
        print_yellow("  [0] 🔙 Voltar")
        print()

        escolha = safe_input("  Opção: ").strip()

        if escolha == "0":
            break

        try:
            idx = int(escolha) - 1
        except ValueError:
            print_red("\n  ❌ Opção inválida.")
            safe_input("\n  Pressione Enter para continuar...")
            continue

        if not (0 <= idx < len(opcoes)):
            print_red("\n  ❌ Opção inválida.")
            safe_input("\n  Pressione Enter para continuar...")
            continue

        if jogador.pontos_de_skill <= 0:
            print_red(
                "\n  ❌ Sem pontos de Skill. Jogue partidas para ganhar XP e subir de nível."
            )
            safe_input("\n  Pressione Enter para continuar...")
            continue

        tipo, attr_escolhido = opcoes[idx]
        if tipo == "tecnico":
            dicionario = jogador.atributos
            nome_fmt = attr_escolhido.title()
        else:
            dicionario = jogador.atributos_psicologicos
            nome_fmt = attr_escolhido.replace("_", " ").title()

        if dicionario[attr_escolhido] >= 100:
            print_red(f"\n  ❌ {nome_fmt} já está no máximo (100).")
            safe_input("\n  Pressione Enter para continuar...")
            continue

        qtd_pontos = 1
        if jogador.pontos_de_skill > 1:
            max_possivel = min(
                jogador.pontos_de_skill, 100 - dicionario[attr_escolhido]
            )
            print(f"\n  Quantos pontos deseja aplicar em {nome_fmt}?")
            print_yellow(
                f"  (Disponível: {jogador.pontos_de_skill} | Máximo para este atributo: {max_possivel})"
            )

            entrada_qtd = safe_input(
                f"  Quantidade [1-{max_possivel}] (padrão 1): "
            ).strip()
            if entrada_qtd == "":
                qtd_pontos = 1
            else:
                try:
                    qtd_pontos = int(entrada_qtd)
                    if qtd_pontos < 1:
                        print_red("\n  ❌ Quantidade deve ser pelo menos 1.")
                        safe_input("\n  Pressione Enter para continuar...")
                        continue
                    if qtd_pontos > max_possivel:
                        print_red(f"\n  ❌ Você não pode aplicar {qtd_pontos} pontos.")
                        safe_input("\n  Pressione Enter para continuar...")
                        continue
                except ValueError:
                    print_red("\n  ❌ Quantidade inválida.")
                    safe_input("\n  Pressione Enter para continuar...")
                    continue

        dicionario[attr_escolhido] += qtd_pontos
        jogador.pontos_de_skill -= qtd_pontos
        salvar_jogo(nome_save, jogador)

        print_green(f"\n  ✅ {nome_fmt} +{qtd_pontos} → {dicionario[attr_escolhido]}")
        print(f"     Pontos de Skill restantes: {jogador.pontos_de_skill}")

        safe_input("\n  Pressione Enter para continuar...")
