from src.io_utils import (
    clear_screen,
    safe_input,
    print_blue,
    print_green,
    print_red,
    print_yellow,
    print_magenta,
)
from src.tournament_manager import WeekTournamentManager


def menu_mundo(jogador, nome_save):
    """Exibe o status de todos os torneios ocorrendo na semana atual."""
    if jogador is None:
        print_red("❌ Jogador não carregado.")
        return
    semana = getattr(jogador, "semana", 1)
    manager_atp = WeekTournamentManager(nome_save, semana, genero="masculino")
    manager_wta = WeekTournamentManager(nome_save, semana, genero="feminino")

    while True:
        clear_screen()
        print_blue(f"--- 🌐 CIRCUITO MUNDIAL - SEMANA {semana} ---")

        print_magenta("\n[ ATP TOUR ]")
        resumo_atp = manager_atp.obter_resumo_semanal()
        if not resumo_atp:
            print("  Nenhum torneio em andamento.")
        for i, t in enumerate(resumo_atp, 1):
            campeao_s = t.get("campeao")
            campeao_d = t.get("campeao_duplas")
            if campeao_s:
                status = "🏆 Simples: {}".format(campeao_s)
                if campeao_d:
                    status += " | 👥 Duplas: {}".format(campeao_d)
            else:
                status = "Fase: {}".format(t["fase"])

            print("  {}. {} ({}) - {}".format(i, t["nome"], t["tipo"], status))

        print_magenta("\n[ WTA TOUR ]")
        resumo_wta = manager_wta.obter_resumo_semanal()
        if not resumo_wta:
            print("  Nenhum torneio em andamento.")
        for i, t in enumerate(resumo_wta, 1):
            idx = i + len(resumo_atp)
            campeao_s = t.get("campeao")
            campeao_d = t.get("campeao_duplas")
            if campeao_s:
                status = "🏆 Simples: {}".format(campeao_s)
                if campeao_d:
                    status += " | 👥 Duplas: {}".format(campeao_d)
            else:
                status = "Fase: {}".format(t["fase"])

            print("  {}. {} ({}) - {}".format(idx, t["nome"], t["tipo"], status))

        print_blue("\n[8] Ver chaves de um torneio")
        print_blue("[0] Voltar")

        opcao = safe_input("\nEscolha: ").strip()

        if opcao == "0":
            break
        elif opcao == "8":
            idx_t = safe_input("Digite o numero do torneio: ").strip()
            try:
                idx_n = int(idx_t)
                target_manager = None
                target_name = None

                if 1 <= idx_n <= len(resumo_atp):
                    target_manager = manager_atp
                    target_name = resumo_atp[idx_n - 1]["nome"]
                elif len(resumo_atp) < idx_n <= len(resumo_atp) + len(resumo_wta):
                    target_manager = manager_wta
                    target_name = resumo_wta[idx_n - len(resumo_atp) - 1]["nome"]

                if target_manager and target_name:
                    _exibir_detalhes_torneio_externo(target_manager, target_name)
                else:
                    print_red("Torneio invalido.")
                    safe_input("Pressione Enter...")
            except ValueError:
                print_red("Entrada invalida.")
                safe_input("Pressione Enter...")
        else:
            print_red("Opcao invalida.")
            safe_input("Pressione Enter...")


def _exibir_detalhes_torneio_externo(manager, nome_torneio):
    estado = manager.obter_torneio(nome_torneio)
    if not estado:
        print_red("Erro ao carregar estado do torneio.")
        safe_input("Pressione Enter...")
        return

    while True:
        clear_screen()
        tipo = estado.get("tournament_data", {}).get("tipo", "")
        fase_atual = estado.get("fase_atual", "???")
        fase_atual_d = estado.get("fase_atual_duplas", "???")

        print_blue("--- Detalhes: {} ({}) ---".format(nome_torneio, tipo))
        print("Fase Atual (Simples): {}".format(fase_atual))
        if estado.get("campeao_simples"):
            print_green("🏆 Campeao Simples: {}".format(estado["campeao_simples"]))

        print("Fase Atual (Duplas): {}".format(fase_atual_d))
        if estado.get("campeao_duplas"):
            print_green("🏆 Campeao Duplas: {}".format(estado["campeao_duplas"]))

        print("\n[1] Ver confrontos Simples (atual)")
        print("[2] Ver resultados Simples (anteriores)")
        print("[3] Ver confrontos Duplas (atual)")
        print("[4] Ver resultados Duplas (anteriores)")
        print("[0] Voltar")

        op = safe_input("\nEscolha: ").strip()
        if op == "0":
            break
        elif op == "1":
            confrontos = estado.get("rodadas", {}).get(fase_atual, [])
            if not confrontos:
                print_yellow("Sem confrontos disponíveis para esta fase.")
            else:
                print_blue(f"\n--- Confrontos Simples ({fase_atual}) ---")
                for i, c in enumerate(confrontos, 1):
                    a = c[0] if isinstance(c[0], dict) else {"nome": str(c[0])}
                    b = c[1] if isinstance(c[1], dict) else {"nome": str(c[1])}
                    print(f"  {i}. {a.get('nome', '??')} vs {b.get('nome', '??')}")
            safe_input("\nPressione Enter...")
        elif op == "2":
            resultados = estado.get("resultados", {})
            fases = estado.get("fases", [])
            fases_com_resultado = [f for f in fases if resultados.get(f)]
            if not fases_com_resultado:
                print_yellow("Nenhum resultado disponível ainda.")
            else:
                for fase in fases_com_resultado:
                    print_blue(f"\n--- Resultados Simples ({fase}) ---")
                    for r in resultados[fase]:
                        print(
                            f"  {r.get('jogador_a', '??')} vs {r.get('jogador_b', '??')}"
                            f" | 🏆 {r.get('vencedor', '??')} ({r.get('placar', '')})"
                        )
            safe_input("\nPressione Enter...")
        elif op == "3":
            confrontos = estado.get("rodadas_duplas", {}).get(fase_atual_d, [])
            if not confrontos:
                print_yellow("Sem confrontos disponíveis para esta fase.")
            else:
                print_blue(f"\n--- Confrontos Duplas ({fase_atual_d}) ---")
                for i, c in enumerate(confrontos, 1):
                    a = c[0] if isinstance(c[0], dict) else {"nome": str(c[0])}
                    b = c[1] if isinstance(c[1], dict) else {"nome": str(c[1])}
                    print(f"  {i}. {a.get('nome', '??')} vs {b.get('nome', '??')}")
            safe_input("\nPressione Enter...")
        elif op == "4":
            resultados = estado.get("resultados_duplas", {})
            fases = estado.get("fases_duplas", [])
            fases_com_resultado = [f for f in fases if resultados.get(f)]
            if not fases_com_resultado:
                print_yellow("Nenhum resultado disponível ainda.")
            else:
                for fase in fases_com_resultado:
                    print_blue(f"\n--- Resultados Duplas ({fase}) ---")
                    for r in resultados[fase]:
                        print(
                            f"  {r.get('dupla_a', '??')} vs {r.get('dupla_b', '??')}"
                            f" | 🏆 {r.get('vencedor', '??')} ({r.get('placar', '')})"
                        )
            safe_input("\nPressione Enter...")
