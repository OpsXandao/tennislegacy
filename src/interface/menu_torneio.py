from src.interface.match_info import exibir_stats_adversario, exibir_review_partida
from src.ranking import SistemaRanking
from src.io_utils import (
    safe_input,
    clear_screen,
    print_blue,
    print_green,
    print_red,
    print_yellow,
    print_magenta,
)
from src.dados import get_caminho_ranking_save, carregar_ranking
from src.save import salvar_jogo
from src.torneio import carregar_torneio, salvar_torneio
from src.world_tour_sync import sincronizar_outros_torneios_com_dia


def _registrar_vinculo_dupla(jogador, nome_save, venceu):
    """Registra o resultado de uma partida de duplas no vínculo com o parceiro."""
    parceiro = getattr(jogador, "parceiro_duplas", None)
    if not isinstance(parceiro, dict):
        return
    nome_parceiro = parceiro.get("nome", "")
    if not nome_parceiro:
        return
    if hasattr(jogador, "registrar_resultado_dupla"):
        jogador.registrar_resultado_dupla(nome_parceiro, venceu)
        salvar_jogo(nome_save, jogador)


def _exibir_confrontos_duplas(estado, fase_duplas):
    print_magenta(f"Confrontos de duplas ({fase_duplas}):")
    confrontos = estado.get("rodadas_duplas", {}).get(fase_duplas, [])
    nome_par_humano = estado.get("nome_par_duplas", "").strip().lower()
    if not confrontos:
        print_yellow("Sem confrontos de duplas disponíveis nesta fase.")
        return
    for i, confronto in enumerate(confrontos, 1):
        par_a = (
            confronto[0]
            if isinstance(confronto[0], dict)
            else {"nome": str(confronto[0])}
        )
        par_b = (
            confronto[1]
            if isinstance(confronto[1], dict)
            else {"nome": str(confronto[1])}
        )
        linha = f"{i}. {par_a.get('nome', '??')} vs {par_b.get('nome', '??')}"
        if (
            par_a.get("nome", "").strip().lower() == nome_par_humano
            or par_b.get("nome", "").strip().lower() == nome_par_humano
        ):
            print_yellow(f"👉 {linha}  (SUA PARTIDA)")
        else:
            print(linha)


def _exibir_resultados_duplas(estado):
    fases = estado.get("fases_duplas", [])
    resultados_duplas = estado.get("resultados_duplas", {})
    ultima_fase = next((f for f in reversed(fases) if resultados_duplas.get(f)), None)

    if not ultima_fase:
        print("\n📊 Nenhum resultado de duplas disponível ainda.")
        return

    print(f"\n📊 Resultados das duplas ({ultima_fase}):")
    for r in resultados_duplas.get(ultima_fase, []):
        if isinstance(r, dict):
            nome_a = r.get("jogador_a", {}).get("nome", "??")
            nome_b = r.get("jogador_b", {}).get("nome", "??")
            nome_v = r.get("vencedor", {}).get("nome", "??")
            placar = r.get("resultado", "")
            print(f"- {nome_a} vs {nome_b} | 🏆 {nome_v} ({placar})")
        else:
            print(f"- {r}")


def _finalizar_torneio_duplas(torneio, estado, label_duplas, msg=None):
    if msg:
        print_red(msg)
    estado["fase_atual"] = "finalizado"
    # Se o jogador foi eliminado, jogador_vivo = False.
    # Se ele venceu (chegou ao fim vivo nas duplas), mantemos jogador_vivo=True
    # para que o controller mostre a mensagem de vitória.
    if not estado.get("jogador_vivo_duplas", False):
        estado["jogador_vivo"] = False
    else:
        estado["jogador_vivo"] = True

    torneio._salvar_estado(estado)
    print_yellow(f"Torneio finalizado ({label_duplas}).")


def _exibir_outros_torneios(estado):
    outros = estado.get("outros_torneios_semana", [])
    if not outros:
        print_yellow("Nenhum torneio externo em andamento nesta semana.")
        return

    print_blue("\n--- 🌐 Andamento de Outros Torneios ---")
    for t in outros:
        fases = t.get("fases", [])
        idx = int(t.get("fase_idx", 0) or 0)
        fase_atual = (
            "finalizado"
            if t.get("finalizado")
            else (fases[idx] if idx < len(fases) else "finalizado")
        )
        print(
            f"\n[{t.get('tour', '?')}] {t.get('nome', 'Torneio')} ({t.get('tipo', '?')})"
        )
        if t.get("finalizado"):
            label_camp = "Campeã" if t.get("tour") == "WTA" else "Campeão"
            print_green(f"  {label_camp}: {t.get('campeao', '??')}")
        else:
            print_yellow(f"  Fase atual: {fase_atual}")

        resultados = t.get("resultados", {})
        ultima_fase = next((f for f in reversed(fases) if resultados.get(f)), None)
        if ultima_fase:
            print(f"  Última rodada simulada ({ultima_fase}):")
            for r in resultados.get(ultima_fase, [])[:8]:
                print(
                    f"    - {r.get('jogador_a')} vs {r.get('jogador_b')} | 🏆 {r.get('vencedor')} ({r.get('placar')})"
                )


def menu_torneio(jogador, nome_save, torneio=None, salvar_automaticamente=False):
    if torneio is None:
        torneio = carregar_torneio(nome_save)

    torneio_encerrado = False

    while True:
        clear_screen()
        estado = torneio._carregar_estado()
        modalidade = estado.get("modalidade_torneio") or getattr(
            jogador, "modalidade_atual", "simples"
        )
        tipo_duplas_estado = estado.get("tipo_duplas", "mesmo_genero")
        label_duplas = "duplas mistas" if tipo_duplas_estado == "mista" else "duplas"
        jogador_em_entrada_direta = False
        if modalidade in ("simples", "ambos") and estado.get(
            "fase_atual", ""
        ).startswith("qualy"):
            direct_entries = estado.get("direct_entries", [])
            jogador_em_entrada_direta = any(
                j
                and j.get("nome")
                and j.get("nome", "").lower() == jogador.nome.lower()
                for j in direct_entries
                if isinstance(j, dict)
            )
        fase_duplas = estado.get("fase_atual_duplas")
        tem_draw_duplas = fase_duplas is not None and fase_duplas != "finalizado"
        jogador_vivo_duplas = estado.get("jogador_vivo_duplas", False)
        mostrar_opcao_duplas = tem_draw_duplas and jogador_vivo_duplas
        fase_simples = estado.get("fase_atual")
        jogador_vivo_simples = bool(estado.get("jogador_vivo", False))
        simples_ativo = jogador_vivo_simples and fase_simples not in (
            None,
            "finalizado",
        )

        print_blue(f"\n🏟️ Torneio: {torneio.nome_torneio} | Semana {torneio.semana}")
        print_yellow(f"Modo inscrito: {modalidade.upper()}")
        agenda_dia = estado.get("agenda_dia", {}) if isinstance(estado, dict) else {}
        dia_torneio = int(agenda_dia.get("dia", 1) or 1)
        jogos_hoje = agenda_dia.get("jogos_realizados", [])
        if not isinstance(jogos_hoje, list):
            jogos_hoje = []
        jogos_txt = ", ".join(jogos_hoje) if jogos_hoje else "nenhum"
        print(f"Dia do torneio: {dia_torneio} | Jogados hoje: {jogos_txt}")
        _semana_t = int(getattr(torneio, "semana", 1) or 1)
        _genero_t = getattr(torneio, "genero", "masculino")
        _nome_t = str(getattr(torneio, "nome_torneio", "") or "")
        if sincronizar_outros_torneios_com_dia(
            estado, nome_save, _semana_t, _genero_t, _nome_t, dia_torneio
        ):
            torneio._salvar_estado(estado)
        if modalidade == "duplas" and tem_draw_duplas:
            print(f"Fase atual ({label_duplas}): {fase_duplas}")
        else:
            print(f"Fase atual: {estado.get('fase_atual', '?')}")
        if tem_draw_duplas:
            status_duplas = fase_duplas if jogador_vivo_duplas else "eliminado"
            print(f"Duplas: {status_duplas}")
        print()
        if modalidade == "duplas" and tem_draw_duplas:
            _exibir_confrontos_duplas(estado, fase_duplas)
        else:
            print_magenta("Confrontos da fase:")
            torneio.exibir_confrontos_fase_atual()
        print()

        pode_jogar_simples = modalidade in ("simples", "ambos") and simples_ativo
        pode_jogar_duplas = modalidade in ("duplas", "ambos") and mostrar_opcao_duplas
        mostrar_stats_review = pode_jogar_simples

        print_blue("\n--- 🎮 Opções ---")
        print()
        if modalidade == "duplas":
            print_green(f"[1] 👥 Jogar partida de {label_duplas}")
        else:
            if pode_jogar_simples:
                print_green("[1] 🎾 Jogar sua partida de simples")
            else:
                print_yellow("[1] 🎾 Sem partida de simples disponível")
            if pode_jogar_duplas:
                print_green(f"[d] 👥 Jogar partida de {label_duplas}")
        print_green("[2] 📋 Ver confrontos da fase")
        print_green("[3] 📊 Ver resultados da última fase")
        if mostrar_stats_review:
            print_green("[4] 🔎 Ver stats do adversário")
            print_green("[5] 🧪 Review da partida")
        if jogador_em_entrada_direta:
            print_green("[6] ⏩ Simular rodada do qualy")
        print_green("[o] 🌐 Ver rodadas dos outros torneios")
        print_green("[m] 🌐 Circuito Mundial")
        print_green("[7] 💾 Salvar jogo")
        print_green("[8] ↩️ Sair do menu torneio")
        print_red("[9] 🏳️ Desistir do torneio")
        print()

        opcao = safe_input("Escolha uma opção: ").strip()

        if opcao == "1":
            if modalidade == "duplas":
                if not pode_jogar_duplas:
                    print_red(f"Nenhuma partida de {label_duplas} disponível agora.")
                    safe_input("\nPressione Enter para continuar...")
                    continue
                resultado_duplas = torneio.jogar_partida_duplas_do_jogador(
                    jogador, nome_save
                )
                jogador = resultado_duplas.get("jogador", jogador)
                print(resultado_duplas.get("msg", ""))
                if resultado_duplas.get("eliminado_duplas"):
                    print_yellow(f"Eliminados das {label_duplas}.")
                _registrar_vinculo_dupla(
                    jogador,
                    nome_save,
                    not resultado_duplas.get("eliminado_duplas", True),
                )
            else:
                if not pode_jogar_simples:
                    print_red("Nenhuma partida de simples disponível agora.")
                    safe_input("\nPressione Enter para continuar...")
                    continue
                resultado = torneio.jogar_partida_do_jogador(jogador, nome_save)
                if resultado and isinstance(resultado, dict):
                    print(resultado.get("msg", ""))
                    jogador = resultado.get("jogador", jogador)
                elif resultado:
                    print(resultado)
                proximo = torneio.obter_proximo_adversario(jogador.nome)
                if proximo:
                    proximo = torneio.garantir_dados_completos(proximo)
                    nome_prox = proximo.get("nome", "??")
                    overall_prox = proximo.get("overall", "?")
                    print_blue(
                        f"\n🎯 Próximo adversário: {nome_prox} (Overall: {overall_prox})"
                    )
            safe_input("\nPressione Enter para continuar...")
            if salvar_automaticamente:
                salvar_torneio(torneio)
                salvar_jogo(nome_save, jogador)
        elif opcao == "d" and pode_jogar_duplas and modalidade != "duplas":
            resultado_duplas = torneio.jogar_partida_duplas_do_jogador(
                jogador, nome_save
            )
            jogador = resultado_duplas.get("jogador", jogador)
            print(resultado_duplas.get("msg", ""))
            if resultado_duplas.get("eliminado_duplas"):
                print_yellow(f"Eliminados das {label_duplas}.")
            _registrar_vinculo_dupla(
                jogador, nome_save, not resultado_duplas.get("eliminado_duplas", True)
            )
            safe_input("\nPressione Enter para continuar...")
            if salvar_automaticamente:
                salvar_torneio(torneio)
                salvar_jogo(nome_save, jogador)
        elif opcao == "2":
            if modalidade == "duplas" and tem_draw_duplas:
                _exibir_confrontos_duplas(estado, fase_duplas)
            else:
                torneio.exibir_confrontos_fase_atual()
            safe_input("\nPressione Enter para continuar...")
        elif opcao == "3":
            if modalidade == "duplas":
                _exibir_resultados_duplas(estado)
            else:
                torneio.exibir_resultados()
            safe_input("\nPressione Enter para continuar...")
        elif opcao == "4" and mostrar_stats_review:
            adversario = torneio.obter_proximo_adversario(jogador.nome)
            if not adversario:
                print_red("Nenhum adversário disponível nesta fase.")
                safe_input("Pressione Enter para continuar...")
                continue
            adversario = torneio.garantir_dados_completos(adversario)
            ranking = SistemaRanking(
                get_caminho_ranking_save(nome_save, genero=jogador.genero)
            )
            superficie = torneio.tournament_data.get("quadra", "")
            exibir_stats_adversario(jogador, adversario, ranking, superficie=superficie)
            safe_input("\nPressione Enter para continuar...")
        elif opcao == "5" and mostrar_stats_review:
            adversario = torneio.obter_proximo_adversario(jogador.nome)
            if not adversario:
                print_red("Nenhum adversário disponível nesta fase.")
                safe_input("Pressione Enter para continuar...")
                continue
            adversario = torneio.garantir_dados_completos(adversario)
            ranking = SistemaRanking(
                get_caminho_ranking_save(nome_save, genero=jogador.genero)
            )
            superficie = torneio.tournament_data.get("quadra", "")
            exibir_review_partida(jogador, adversario, ranking, superficie=superficie)
            safe_input("\nPressione Enter para continuar...")
        elif opcao == "6" and jogador_em_entrada_direta:
            fase_antes = estado.get("fase_atual")
            torneio.simular_npcs_na_fase_atual(jogador.nome)
            estado_pos = torneio._carregar_estado()
            resultados_fase = estado_pos.get("resultados", {}).get(fase_antes, [])

            qualy_final_phase = (
                "qualy_r3"
                if torneio.tournament_data["tipo"] == "Grand Slam"
                else "qualy_2"
            )
            if fase_antes == qualy_final_phase and resultados_fase:
                classificados = []
                for r in resultados_fase:
                    if isinstance(r, dict):
                        vencedor = r.get("vencedor", {})
                        nome_vencedor = (
                            vencedor.get("nome")
                            if isinstance(vencedor, dict)
                            else str(vencedor)
                        )
                        classificados.append(nome_vencedor)
                    else:
                        classificados.append(str(r))
                print(f"\n✅ Classificados do qualifying ({len(classificados)}):")
                for idx, nome_classificado in enumerate(classificados, 1):
                    print(f"  {idx}. {nome_classificado}")
            else:
                print("\n✅ Rodada do qualy simulada.")
            safe_input("\nPressione Enter para continuar...")
        elif opcao == "m":
            from src.interface.menu_mundo import menu_mundo

            menu_mundo(jogador, nome_save)
        elif opcao == "o":
            _exibir_outros_torneios(estado)
            safe_input("\nPressione Enter para continuar...")
        elif opcao == "7":
            salvar_torneio(torneio)
            salvar_jogo(nome_save, jogador)
            print_green("✅ Jogo salvo com sucesso!")
            safe_input("\nPressione Enter para continuar...")
        elif opcao == "8":
            print_yellow("Saindo do menu torneio...")
            break
        elif opcao == "9":
            print_red(
                "\n⚠️ ATENÇÃO: Desistir do torneio contará como derrota na rodada atual."
            )
            confirmar = (
                safe_input("Tem certeza que deseja desistir? (s/n): ").strip().lower()
            )
            if confirmar == "s":
                if modalidade == "duplas":
                    torneio.desistir_das_duplas()
                    estado = torneio._carregar_estado()
                    _finalizar_torneio_duplas(
                        torneio,
                        estado,
                        label_duplas,
                        msg=f"\n😔 Você desistiu das {label_duplas}.",
                    )
                else:
                    torneio.desistir_do_torneio()
                    print_red("🏳️ Você desistiu do torneio.")
                torneio_encerrado = True
                break
        else:
            print_red("Opção inválida!")
            safe_input("Pressione Enter para continuar...")

        # >>>>>>> NOVO BLOCO UX: Checa se jogador foi eliminado
        estado = torneio._carregar_estado()
        if modalidade == "duplas" and not estado.get("jogador_vivo_duplas", False):
            _finalizar_torneio_duplas(
                torneio,
                estado,
                label_duplas,
                msg=f"\n😔 Fim de torneio para {torneio.jogador_nome} nas {label_duplas}!",
            )
            torneio_encerrado = True
            break

        if modalidade != "duplas" and not torneio.jogador_ainda_ativo():
            duplas_ativo = (
                modalidade == "ambos"
                and estado.get("fase_atual_duplas") not in (None, "finalizado")
                and estado.get("jogador_vivo_duplas", False)
            )
            if duplas_ativo:
                print_yellow(
                    f"\n😔 Eliminado do simples na fase {estado.get('fase_atual', '?')}! "
                    "Mas você ainda está vivo nas duplas."
                )
                safe_input("Pressione Enter para continuar...")
            else:
                print_red(f"\n😔 Fim de torneio para {torneio.jogador_nome}!")
                print_yellow(
                    f"🎾 Sua jornada parou na fase {estado.get('fase_atual', '?')}, mas o show continua...\n"
                )
                print_blue("Quer ver quem será o campeão deste torneio?!")
                resp = (
                    safe_input("📋 Simular o restante do torneio? (s/n): ")
                    .strip()
                    .lower()
                )
                if resp == "s":
                    ranking_path = get_caminho_ranking_save(
                        nome_save, genero=jogador.genero
                    )
                    todos_jogadores = carregar_ranking(ranking_path)
                    campeao = torneio.simular_torneio_restante(todos_jogadores)
                    print_green(f"\n🏆 O torneio terminou! O campeão foi: {campeao}")
                    safe_input("Pressione Enter para ver o resultado...")
                if modalidade == "ambos" and estado.get("fases_duplas"):
                    torneio.simular_duplas_restante()
                print_yellow(
                    "\n🔄 Voltando para a temporada... Pronto para o próximo desafio?\n"
                )
                torneio_encerrado = True
                break

        # Checar se torneio acabou (final natural), se sim, retornar ao controller
        estado = torneio._carregar_estado()
        fase_simples_encerrada = estado.get("fase_atual") == "finalizado" or (
            estado.get("fase_atual") == "final"
            and not estado.get("rodadas", {}).get("final")
        )
        fase_duplas_encerrada = estado.get("fase_atual_duplas") in (
            None,
            "finalizado",
        ) or not estado.get("jogador_vivo_duplas", False)

        if modalidade == "duplas":
            if fase_duplas_encerrada:
                _finalizar_torneio_duplas(torneio, estado, label_duplas)
                torneio_encerrado = True
                break
            continue

        if fase_simples_encerrada:
            duplas_pendente = (
                modalidade in ("duplas", "ambos")
                and estado.get("fase_atual_duplas") not in (None, "finalizado")
                and estado.get("jogador_vivo_duplas", False)
            )
            if not duplas_pendente:
                print_yellow("Torneio finalizado!")
                torneio_encerrado = True
                break

    if not torneio_encerrado:
        # Jogador saiu manualmente — torneio segue em andamento, não avança semana
        return "saiu"

    # Retorna para o controller processar a finalização e pontos
    return "finalizado"
