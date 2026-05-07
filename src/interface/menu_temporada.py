import time

from src.calendario import (
    avancar_semana,
    obter_torneios_da_semana,
    carregar_temporada,
    salvar_temporada,
    badge_entry_status,
    calcular_melhor_resultado_por_torneio,
)
from src.io_utils import (
    safe_input,
    clear_screen,
    print_blue,
    print_green,
    print_red,
    print_yellow,
    print_magenta,
)
from src.save import salvar_jogo
from src.torneio import criar_torneio
from src.ranking import SistemaRanking
from src.dados import get_caminho_ranking_save, get_caminho_ranking_global
from src.jogador import normalizar_nome
from src.duplas import buscar_parceiros_disponiveis, tentar_convidar_parceiro
from src.log_jogo import log_erro


def _exibir_detalhes_e_confirmar(torneio, genero="masculino"):
    """Mostra os detalhes de um torneio e pede confirmação."""
    clear_screen()
    print_magenta("\n--- 📝 Detalhes do Torneio ---")
    print()
    print(f"Nome: {torneio.get('nome', '??')}")
    print(f"País: {torneio.get('pais_sede', '??')}")

    tipo = torneio.get("tipo", "??")
    if genero == "feminino":
        tipo = tipo.replace("ATP", "WTA")
    print(f"Tipo: {tipo}")

    print(f"Premiação: ${torneio.get('premiacao', 0):,}")
    print(f"Popularidade: {'⭐' * torneio.get('popularidade', 0)}")
    print("----------------------------")
    print()

    confirmar = safe_input("Deseja entrar neste torneio? (s/n): ").strip().lower()
    return confirmar == "s"


def _exibir_detalhes_davis_cup(torneio, jogador):
    """Mostra os detalhes da Copa Davis e pede confirmação."""
    clear_screen()
    nome_competicao = torneio.get("tipo", "Davis Cup")
    titulo = "Copa Davis" if nome_competicao == "Davis Cup" else "Billie Jean King Cup"
    print_magenta(f"\n--- 🏆 {titulo} ---")
    print()
    print_blue(
        f"{titulo} é a principal competição de tênis por equipes nacionais desta categoria!"
    )
    print()
    print(f"Você representará: {jogador.nacionalidade}")
    print(f"Local das finais: {torneio.get('local', '??')}")
    print(f"País sede: {torneio.get('pais_sede', '??')}")
    print(f"Formato: {torneio.get('formato_partida', 'Melhor de 3 sets')}")
    numero_equipes = torneio.get("numero_equipes")
    if numero_equipes:
        equipes_txt = str(numero_equipes)
    else:
        nome_torneio = str(torneio.get("nome", "")).lower()
        if "qualifiers" in nome_torneio:
            equipes_txt = "definido pela fase qualificatória"
        elif "final" in nome_torneio:
            equipes_txt = "8 (fase final)"
        else:
            equipes_txt = "definido pelo regulamento"
    print(f"Equipes participantes: {equipes_txt}")
    print(f"Premiação total: ${torneio.get('premiacao', 0):,}")
    print()
    print_yellow("📋 Formato da competição:")
    print("   - Qualifiers em confronto de ida única")
    print("   - Final 8 em chave eliminatória")
    print("   - Decisão em confrontos por equipes")
    print()
    print_yellow("📋 Cada confronto (tie):")
    print("   - 2 partidas de simples")
    print("   - 1 partida de duplas")
    print("   - Você jogará as partidas de simples pela sua seleção")
    print()
    print("----------------------------")
    print()

    confirmar = (
        safe_input(f"Deseja inscrever sua seleção na {titulo}? (s/n): ").strip().lower()
    )
    return confirmar == "s"


def _exibir_resultados_semana(nome_save, semana, genero):
    """Exibe os campeões dos torneios NPC da semana que passou."""
    from src.tournament_manager import WeekTournamentManager

    genero_outro = "feminino" if genero == "masculino" else "masculino"
    label = "ATP" if genero == "masculino" else "WTA"
    label_outro = "WTA" if genero == "masculino" else "ATP"

    manager = WeekTournamentManager(nome_save, semana, genero=genero)
    manager_outro = WeekTournamentManager(nome_save, semana, genero=genero_outro)
    resumo = manager.obter_resumo_semanal()
    resumo_outro = manager_outro.obter_resumo_semanal()

    if not resumo and not resumo_outro:
        return

    print_blue(f"\n--- 🌐 Resultados da Semana {semana} ---")
    for label_t, res in [(label, resumo), (label_outro, resumo_outro)]:
        if not res:
            continue
        print_magenta(f"\n[ {label_t} ]")
        for t in res:
            if t.get("campeao"):
                linha = f"  🏆 {t['nome']} — {t['campeao']}"
                if t.get("campeao_duplas"):
                    linha += f"  |  Duplas: {t['campeao_duplas']}"
                print_green(linha)
            else:
                print(f"  ⏳ {t['nome']} ({t['tipo']}) — Fase: {t['fase']}")


def _exibir_race_to_finals(nome_save, jogador, ranking=None):
    """Exibe o Race to ATP Finals com top 8 por pontos YTD."""
    if ranking is None:
        ranking = SistemaRanking(
            get_caminho_ranking_save(nome_save, genero=jogador.genero)
        )
    top_8 = ranking.ranking_race(n=8)
    nome_norm = normalizar_nome(jogador.nome)

    circuito = "ATP" if jogador.genero == "masculino" else "WTA"
    print_magenta(f"\n--- 🏆 Race to {circuito} Finals ---")
    print_yellow("Top 8 da temporada (Race to Finals):")
    print()

    pos_jogador = None
    ytd_jogador = 0
    for idx, j in enumerate(top_8, 1):
        ytd = int(j.get("pontos_ytd", 0) or 0)
        nome = j.get("nome", "??")
        destaque = " ← Você" if normalizar_nome(nome) == nome_norm else ""
        if normalizar_nome(nome) == nome_norm:
            pos_jogador = idx
            ytd_jogador = ytd
        print(f"  ✅ #{idx} {nome} - {ytd} pts{destaque}")

    if pos_jogador is None:
        todos_ytd = sorted(
            ranking.ranking,
            key=lambda j: int(j.get("pontos_ytd", 0) or 0),
            reverse=True,
        )
        for idx, j in enumerate(todos_ytd, 1):
            if normalizar_nome(j.get("nome", "")) == nome_norm:
                pos_jogador = idx
                ytd_jogador = int(j.get("pontos_ytd", 0) or 0)
                break
        pts_8 = int(top_8[7].get("pontos_ytd", 0) or 0) if len(top_8) >= 8 else 0
        faltam = max(0, pts_8 - ytd_jogador + 1)
        pos_str = f"#{pos_jogador}" if pos_jogador else "fora do ranking"
        print_red(
            f"\n  ❌ Você: {pos_str} - {ytd_jogador} pts (faltam {faltam} pts para classificar)"
        )
    print()


def _menu_treino(jogador, nome_save):
    """Menu de treino semanal. Retorna (jogador_atualizado, treinou)."""
    from src.progressao import treinar_semana
    from src.management import obter_profissional_da_equipe

    clear_screen()
    print_blue("\n--- 🏋️ Treino Semanal ---")
    print()
    energia = getattr(jogador, "energia", 100)
    fadiga = getattr(jogador, "fadiga", 0)
    print_yellow(f"Energia: {energia}% | Fadiga: {fadiga}%")

    status_lesao = getattr(jogador, "status_lesao", {})
    lesionado = (
        status_lesao.get("lesionado", False)
        if isinstance(status_lesao, dict)
        else False
    )
    if lesionado:
        print_yellow("(Lesionado — apenas treino Psicológico permitido)")

    if energia < 30:
        print_red("\n❌ Energia insuficiente para treinar (mínimo 30%).")
        safe_input("Pressione Enter para voltar...")
        return jogador, False

    equipe = getattr(jogador, "equipe", [])
    treinador = obter_profissional_da_equipe(equipe, "treinador")
    preparador = obter_profissional_da_equipe(equipe, "preparador")
    psicologo = obter_profissional_da_equipe(equipe, "psicologo")

    print()
    if treinador:
        foco = ", ".join(treinador.get("foco_atributos", [])) or "todos"
        bonus = int(treinador.get("bonus_progressao", 0) * 100)
        print(f"  Treinador: {treinador['nome']} | Foco: {foco} | Bônus: +{bonus}%")
    else:
        print("  Treinador: Nenhum (chance base 15%)")
    if preparador:
        print(
            f"  Preparador: {preparador['nome']} | Bônus físico: +{int(preparador.get('bonus_fisico_pct', 0) * 100)}%"
        )
    else:
        print("  Preparador: Nenhum (chance base 25%)")
    if psicologo:
        print(
            f"  Psicólogo: {psicologo['nome']} | Chance mental: {int(psicologo.get('chance_mental', 0) * 100)}%"
        )
    else:
        print("  Psicólogo: Nenhum (chance base 15%)")

    print()
    print_green("[1] Técnico  (atributos de jogo)")
    if lesionado:
        print_yellow("[2] Físico   (bloqueado — lesionado)")
    else:
        print_green("[2] Físico   (fisico e movimento)")
    print_green("[3] Psicológico (concentração, determinação...)")
    print_green("[0] Cancelar")
    print()

    opcao = safe_input("Escolha o foco do treino: ").strip()
    if opcao == "0":
        return jogador, False

    foco_map = {"1": "tecnico", "2": "fisico", "3": "psicologico"}
    foco = foco_map.get(opcao)
    if not foco:
        print_red("❌ Opção inválida.")
        safe_input("Pressione Enter para voltar...")
        return jogador, False

    if foco == "fisico" and lesionado:
        print_red("❌ Não é possível treinar fisicamente enquanto lesionado.")
        safe_input("Pressione Enter para continuar...")
        return jogador, False

    melhorias = treinar_semana(jogador, foco)
    salvar_jogo(nome_save, jogador)

    print()
    if melhorias:
        print_green("✨ Atributos melhorados:")
        for attr, novo_val in melhorias.items():
            print_green(f"   {attr}: {novo_val - 1} → {novo_val}")
    else:
        print_yellow("   Nenhum atributo melhorou desta vez. Continue treinando!")

    print_yellow(f"\nEnergia: {jogador.energia}% | Fadiga: {jogador.fadiga}%")
    safe_input("\nPressione Enter para avançar a semana...")

    avancar_semana(nome_save)
    from src.jogador import carregar_jogador

    jogador = carregar_jogador(nome_save)
    return jogador, True


def ver_calendario_completo(jogador, nome_save):
    from src.dados import carregar_calendario
    from src.constantes import FASES_NOMES

    # Carrega dados uma vez fora do loop
    cal = carregar_calendario(genero=jogador.genero)
    meu_hist = getattr(jogador, "historico_torneios", [])

    melhor_res_por_torneio = calcular_melhor_resultado_por_torneio(meu_hist)

    semanas_ordenadas = sorted([int(k) for k in cal.keys()])
    total_semanas = len(semanas_ordenadas)
    offset = 0
    limite = 13  # Mostra um trimestre por vez

    while True:
        clear_screen()
        tour_label = "ATP" if jogador.genero == "masculino" else "WTA"
        print_blue(
            f"\n--- 📅 Calendário {tour_label} (Semanas {semanas_ordenadas[offset]} a {semanas_ordenadas[min(offset+limite-1, total_semanas-1)]}) ---"
        )
        print()

        header = (
            f"{'SEM':<3} | {'TORNEIO':<25} | {'DEF. SIMPLES':<15} | "
            f"{'DEF. DUPLAS':<23} | {'MEU RECORDE'}"
        )
        print(header)
        print("-" * len(header))

        for i in range(offset, min(offset + limite, total_semanas)):
            sem = semanas_ordenadas[i]
            torneios = cal.get(str(sem), [])
            for t in torneios:
                t_nome = t.get("nome", "??")
                ultimo = t.get("ultimo_campeao") or "---"
                ultimo_duplas = t.get("ultimo_campeao_duplas") or "---"
                meu_recorde = melhor_res_por_torneio.get(t_nome, "---")
                if meu_recorde != "---":
                    meu_recorde = FASES_NOMES.get(meu_recorde, meu_recorde)

                print(
                    f"{sem:02}  | {t_nome:25.25} | {ultimo:15.15} | "
                    f"{ultimo_duplas:23.23} | {meu_recorde}"
                )

        print("\n" + "-" * len(header))
        print_green("[n] Próxima página" if offset + limite < total_semanas else "")
        print_green("[p] Página anterior" if offset > 0 else "")
        print_green("[0] Voltar ao menu")

        escolha = safe_input("\nOpção: ").strip().lower()
        if escolha == "0":
            break
        elif escolha == "n" and offset + limite < total_semanas:
            offset += limite
        elif escolha == "p" and offset > 0:
            offset -= limite


def menu_temporada(jogador, nome_save, salvar_automaticamente=False):
    """Menu da temporada, onde o jogador escolhe torneios ou descansa."""
    if jogador is None:
        print_red("❌ Jogador não carregado.")
        return
    semana_resultados_exibida = None
    while True:
        clear_screen()
        temporada = carregar_temporada(nome_save)
        ano, semana = temporada["ano"], temporada["semana"]

        tour_name = "ATP Tour" if jogador.genero == "masculino" else "WTA Tour"
        print_blue(
            f"\n--- 📅 Calendário da Temporada ({tour_name}): Ano {ano}, Semana {semana} ---"
        )
        print()

        # Exibe os resultados da semana anterior uma única vez por semana
        if semana != semana_resultados_exibida and semana > 1:
            try:
                _exibir_resultados_semana(nome_save, semana - 1, jogador.genero)
            except Exception:
                pass
            semana_resultados_exibida = semana

        # Exibe status de fadiga e lesão
        status_str = f"Fadiga: {jogador.fadiga}% | Status: "
        nivel_lesao = jogador.status_lesao.get("nivel", "saudavel")
        if jogador.status_lesao.get("lesionado"):
            status_str += f"Lesionado ({jogador.status_lesao.get('semanas_restantes', 0)} semanas restantes)"
        elif nivel_lesao == "limitado":
            status_str += "Limitado fisicamente"
        elif nivel_lesao == "desconforto":
            status_str += "Desconforto muscular"
        else:
            status_str += "Saudável"
        status_doenca = (
            jogador.status_doenca
            if isinstance(getattr(jogador, "status_doenca", {}), dict)
            else {}
        )
        if status_doenca.get("doente"):
            tipo = status_doenca.get("tipo", "doenca")
            rest = status_doenca.get("semanas_restantes", 1)
            status_str += f" | Doença: {tipo} ({rest} sem.)"
        print_yellow(status_str)
        print("-" * (len(status_str) if len(status_str) > 40 else 40))
        print()

        torneios = obter_torneios_da_semana(semana, genero=jogador.genero)

        # Cache de Ranking: Carrega uma única vez para uso em badges e Race
        ranking_obj = None
        pos_jogador = None
        pos_ytd_jogador = None
        nomes_top8 = []

        try:
            ranking_obj = SistemaRanking(
                get_caminho_ranking_save(nome_save, genero=jogador.genero)
            )
            pos_jogador = ranking_obj.obter_posicao(jogador.nome)

            # Prepara dados da Race se for relevante (semana 30+)
            tem_finals = any(
                t.get("tipo") == "ATP Finals" or t.get("tipo") == "WTA Finals"
                for t in torneios
            )
            if semana >= 30 and tem_finals:
                top_8_cache = ranking_obj.ranking_race(n=8)
                nomes_top8 = [normalizar_nome(j.get("nome", "")) for j in top_8_cache]

                todos_ytd_cache = sorted(
                    ranking_obj.ranking,
                    key=lambda j: int(j.get("pontos_ytd", 0) or 0),
                    reverse=True,
                )
                nome_h_norm = normalizar_nome(jogador.nome)
                for i, j in enumerate(todos_ytd_cache, 1):
                    if normalizar_nome(j.get("nome", "")) == nome_h_norm:
                        pos_ytd_jogador = i
                        break
        except Exception as e:
            log_erro(nome_save, "menu_temporada_cache_ranking", e, {"semana": semana})

        # Race to Finals: exibe quando relevante
        if semana >= 30 and nomes_top8:
            _exibir_race_to_finals(nome_save, jogador, ranking=ranking_obj)

        if not torneios:
            print_yellow("  - Nenhum torneio disponível nesta semana.")
        for idx, torneio in enumerate(torneios, 1):
            nome = torneio.get("nome", "??")
            tipo = torneio.get("tipo", "??")

            # Ajustar nome do tipo para WTA se necessário
            if jogador.genero == "feminino":
                tipo = tipo.replace("ATP", "WTA")

            # Competições por seleções
            if tipo in {"Davis Cup", "Billie Jean King Cup", "United Cup"}:
                print_green(f"[{idx}] 🏆 {nome} ({tipo}) - Por equipes")
            elif tipo == "ATP Finals" or tipo == "WTA Finals":
                if normalizar_nome(jogador.nome) in nomes_top8:
                    badge_finals = "[Classificado!]"
                    print_green(f"[{idx}] 🏆 {nome} ({tipo})  {badge_finals}")
                else:
                    badge_finals = (
                        f"[Fora YTD #{pos_ytd_jogador}]"
                        if pos_ytd_jogador
                        else "[Fora YTD]"
                    )
                    print_yellow(f"[{idx}] 🏆 {nome} ({tipo})  {badge_finals}")
            else:
                badge = badge_entry_status(pos_jogador, torneio)
                badge_str = f"  {badge}" if badge else ""
                print_green(f"[{idx}] 🏆 {nome} ({tipo}){badge_str}")

        print_blue("\n--- 🎮 Opções ---")
        print()
        print_green("[0] 🔙 Voltar ao Menu Principal")
        print_green("[c] 📅 Ver Calendário Completo")
        print_green("[d] 😴 Descansar (avançar semana)")
        print_green("[t] 🏋️ Treinar (avançar semana treinando)")
        print_green("[s] 💾 Salvar Jogo")
        print()

        escolha = (
            safe_input("Escolha um torneio (número) ou uma opção: ").strip().lower()
        )

        if escolha == "0":
            return False  # Volta para o menu principal

        if escolha == "c":
            ver_calendario_completo(jogador, nome_save)
            continue

        if escolha == "d":
            avancar_semana(nome_save)
            # O jogador é recarregado dentro do loop na proxima iteração
            from src.jogador import carregar_jogador

            jogador = carregar_jogador(nome_save)
            continue  # Recarrega a temporada

        if escolha == "t":
            jogador, treinou = _menu_treino(jogador, nome_save)
            continue

        if escolha == "s":
            salvar_jogo(nome_save, jogador)
            salvar_temporada(nome_save, temporada)
            print_green("✅ Jogo salvo com sucesso!")
            continue

        if not escolha.isdigit() or not (1 <= int(escolha) <= len(torneios)):
            if torneios:
                print_red(
                    f"❌ Opção inválida. Escolha um número de 1 a {len(torneios)}, 'd', 't' ou 's'."
                )
            else:
                print_red(
                    "❌ Não há torneios disponíveis nesta semana. Use 'd' para descansar ou 't' para treinar."
                )
            safe_input("Pressione Enter para continuar...")
            continue

        escolha_idx = int(escolha)
        torneio_escolhido = torneios[escolha_idx - 1]

        if jogador.status_lesao.get("lesionado"):
            semanas = jogador.status_lesao.get("semanas_restantes", 0)
            print_red(
                f"\n❌ Você está lesionado e não pode competir por mais {semanas} semana(s)."
            )
            safe_input("Pressione Enter para continuar...")
            continue

        # Verifica se é ATP/WTA Finals e se o jogador está classificado (top 8 YTD)
        if torneio_escolhido.get("tipo") in {"ATP Finals", "WTA Finals"}:
            try:
                if normalizar_nome(jogador.nome) not in nomes_top8:
                    nome_finals = torneio_escolhido.get("tipo")
                    print_red(
                        f"\n❌ Você não está classificado para o {nome_finals} (precisa estar no top 8 YTD)."
                    )
                    if pos_ytd_jogador:
                        print_yellow(f"   Sua posição na Race: #{pos_ytd_jogador}")
                    safe_input("Pressione Enter para continuar...")
                    continue
            except Exception as e:
                log_erro(
                    nome_save,
                    "menu_temporada_validacao_atp_finals",
                    e,
                    {"torneio": torneio_escolhido.get("nome"), "jogador": jogador.nome},
                )

        # Verifica se é competição por seleções e se o gênero é compatível
        tipo_equipes = torneio_escolhido.get("tipo")
        if tipo_equipes in {"Davis Cup", "Billie Jean King Cup", "United Cup"}:
            if tipo_equipes == "United Cup":
                print_yellow(
                    "\n⚠️ O modo jogável da United Cup ainda não está implementado."
                )
                print_yellow(
                    "   O torneio seguirá apenas na simulação mundial por enquanto."
                )
                safe_input("Pressione Enter para continuar...")
                continue
            if tipo_equipes == "Davis Cup" and jogador.genero == "feminino":
                print_red("\n❌ A Copa Davis é exclusiva do circuito masculino.")
                safe_input("Pressione Enter para continuar...")
                continue
            if tipo_equipes == "Billie Jean King Cup" and jogador.genero != "feminino":
                print_red(
                    "\n❌ A Billie Jean King Cup é exclusiva do circuito feminino."
                )
                safe_input("Pressione Enter para continuar...")
                continue

            if _exibir_detalhes_davis_cup(torneio_escolhido, jogador):
                from src.davis_cup import criar_torneio_davis

                print_yellow(
                    f"\n📝 Inscrevendo {jogador.nacionalidade} em {tipo_equipes}..."
                )
                criar_torneio_davis(torneio_escolhido, jogador, nome_save, semana)
                print_green(
                    "✅ Sua seleção foi inscrita! A competição por equipes vai começar."
                )
                safe_input("Pressione Enter para continuar...")
                return True
            else:
                print_yellow("Inscrição cancelada.")
            continue

        if _exibir_detalhes_e_confirmar(torneio_escolhido, genero=jogador.genero):
            modalidade, parceiro, tipo_duplas = menu_escolha_modalidade(
                jogador, nome_save, torneio_escolhido
            )
            if not modalidade:
                print_yellow("Inscrição cancelada.")
                continue

            jogador.modalidade_atual = modalidade
            jogador.parceiro_duplas = parceiro
            jogador.tipo_duplas_atual = tipo_duplas

            print_yellow(
                f"\n📝 Inscrevendo-se no {torneio_escolhido['nome']} ({modalidade.upper()})..."
            )
            criar_torneio(torneio_escolhido, jogador, nome_save, semana)
            print_green("✅ Inscrição confirmada! O torneio vai começar.")
            safe_input("Pressione Enter para continuar...")
            return True
        else:
            print_yellow("Inscrição cancelada.")


def menu_escolha_modalidade(jogador, nome_save, torneio_data):
    """Escolha unificada de inscrição para evitar ambiguidades de combinação."""
    if jogador is None:
        print_red("❌ Jogador não carregado.")
        return None, None, None

    tipo_torneio = torneio_data.get("tipo", "")
    # Permite mistas se o campo existir ou se for Grand Slam (fallback)
    tem_mistas = (
        torneio_data.get("permite_mistas", False) or tipo_torneio == "Grand Slam"
    )

    while True:
        clear_screen()
        print_blue(f"\n--- 🎾 Inscrição: {torneio_data['nome']} ---")
        print("Escolha o formato da sua inscrição:")
        print()
        print_green("[1] 👤 Só SIMPLES")
        print_green("[2] 👥 Só DUPLAS (mesmo gênero)")
        print_green("[3] 🎾+👥 SIMPLES + DUPLAS (mesmo gênero)")

        if tem_mistas:
            print_magenta("[4] 👥 Só DUPLAS MISTAS")
            print_magenta("[5] 🎾+👥 SIMPLES + DUPLAS MISTAS")

        print_green("[0] 🔙 Cancelar inscrição")
        print()

        escolha = safe_input("Sua escolha: ").strip()
        if escolha == "0":
            return None, None, None

        opcoes_validas = {"1", "2", "3"}
        if tem_mistas:
            opcoes_validas.update({"4", "5"})

        if escolha in opcoes_validas:
            break
        print_red("❌ Opção inválida.")
        safe_input("Pressione Enter para tentar novamente...")

    # Mapeamento da escolha para os estados internos
    config = {
        "1": {"simples": True, "duplas": False, "tipo": None},
        "2": {"simples": False, "duplas": True, "tipo": "mesmo_genero"},
        "3": {"simples": True, "duplas": True, "tipo": "mesmo_genero"},
        "4": {"simples": False, "duplas": True, "tipo": "mista"},
        "5": {"simples": True, "duplas": True, "tipo": "mista"},
    }

    escolhido = config[escolha]
    jogar_simples = escolhido["simples"]
    jogar_duplas = escolhido["duplas"]
    tipo_duplas = escolhido["tipo"]

    parceiro = None
    if jogar_duplas:
        parceiro = _buscar_parceiro_menu(
            jogador, nome_save, torneio_data, tipo_duplas=tipo_duplas
        )
        if not parceiro:
            return None, None, None

    modalidade = "simples"
    if jogar_simples and jogar_duplas:
        modalidade = "ambos"
    elif jogar_duplas:
        modalidade = "duplas"

    return modalidade, parceiro, tipo_duplas


def _buscar_parceiro_menu(jogador, nome_save, torneio_data, tipo_duplas="mesmo_genero"):
    """Interface para convidar um parceiro de duplas com múltiplas opções de busca."""
    genero_parceiro = jogador.genero
    if tipo_duplas == "mista":
        genero_parceiro = "feminino" if jogador.genero == "masculino" else "masculino"

    caminho_ranking = get_caminho_ranking_save(nome_save, genero=genero_parceiro)
    ranking = SistemaRanking(caminho_ranking)
    if not ranking.ranking:
        ranking = SistemaRanking(get_caminho_ranking_global(genero=genero_parceiro))

    from src.dados import get_caminho_ranking_duplas

    caminho_ranking_duplas = get_caminho_ranking_duplas(
        nome_save, genero=genero_parceiro
    )
    ranking_duplas = SistemaRanking(caminho_ranking_duplas, modalidade="duplas")
    if not ranking_duplas.ranking:
        ranking_duplas = ranking

    while True:
        clear_screen()
        label_gen = (
            "Misto"
            if tipo_duplas == "mista"
            else ("Masculino" if genero_parceiro == "masculino" else "Feminino")
        )
        print_blue(f"\n--- 🤝 Buscar Parceiro de Duplas ({label_gen}) ---")
        print()
        print_green("[1] ⭐ Sugestões e Parceiros Anteriores")
        print_green("[2] 🌍 Ver Ranking de Duplas")
        print_green("[3] 👤 Ver Ranking de Simples")
        print_green("[4] 🇧🇷 Buscar por Nacionalidade")
        print_green("[5] 🔍 Buscar por Nome")
        print_green("[0] 🔙 Cancelar")
        print()

        opcao = safe_input("Opção: ").strip()
        if opcao == "0":
            return None

        candidatos = []
        vinculos = getattr(jogador, "vinculos_dupla", {})

        if opcao == "1":
            candidatos = buscar_parceiros_disponiveis(
                jogador, ranking_duplas.ranking, vinculos=vinculos
            )
        elif opcao == "2":
            # Usa ranking de duplas se disponível
            from src.duplas import buscar_parceiro_por_ranking

            candidatos = buscar_parceiro_por_ranking(
                ranking_duplas.ranking, n=50, nome_jogador_excluir=jogador.nome
            )
        elif opcao == "3":
            from src.duplas import buscar_parceiro_por_ranking

            candidatos = buscar_parceiro_por_ranking(
                ranking.ranking, n=50, nome_jogador_excluir=jogador.nome
            )
        elif opcao == "4":
            from src.duplas import buscar_parceiro_por_nacionalidade

            print(f"Sua nacionalidade: {jogador.nacionalidade}")
            nac = safe_input("Digite o país ou código (ex: Brasil ou [BR]): ").strip()
            if not nac:
                nac = jogador.nacionalidade
            candidatos = buscar_parceiro_por_nacionalidade(
                ranking.ranking, nac, nome_jogador_excluir=jogador.nome
            )
        elif opcao == "5":
            busca = safe_input("Digite o nome (ou parte dele): ").strip().lower()
            candidatos = [
                p for p in ranking.ranking if busca in p.get("nome", "").lower()
            ]
        else:
            continue

        # Injeta vínculos nos resultados da busca manual
        for c in candidatos:
            nome_norm = normalizar_nome(c.get("nome", ""))
            c["_vinculo"] = vinculos.get(c.get("nome", "")) or vinculos.get(
                next((k for k in vinculos if normalizar_nome(k) == nome_norm), ""), None
            )

        parceiro = _menu_selecao_final_parceiro(
            jogador, candidatos, ranking, torneio_data
        )
        if parceiro:
            return parceiro


def _menu_selecao_final_parceiro(jogador, candidatos, ranking, torneio_data):
    """Sub-menu para listar candidatos filtrados e realizar o convite."""
    if not candidatos:
        print_red("\nNenhum jogador encontrado com esses critérios.")
        safe_input("Pressione Enter...")
        return None

    while True:
        clear_screen()
        print_blue(f"\n--- 🤝 Selecionar Parceiro ({len(candidatos)} encontrados) ---")
        print()

        # Paginação simples se houver muitos
        limite = 20
        candidatos_exibidos = candidatos[:limite]
        for c in candidatos_exibidos:
            # Candidatos do ranking podem vir em modo "lean" com overall padrão.
            # Hidrata os dados exibidos para mostrar OVR/Nacionalidade reais.
            try:
                npc_completo = ranking.buscar_jogador_por_nome(c.get("nome", ""))
                if isinstance(npc_completo, dict):
                    c["overall"] = npc_completo.get("overall", c.get("overall", 50))
                    c["nacionalidade"] = npc_completo.get(
                        "nacionalidade", c.get("nacionalidade", "??")
                    )
            except Exception:
                pass

        for i, c in enumerate(candidatos_exibidos, 1):
            vinculo = c.get("_vinculo")
            info_v = ""
            if vinculo:
                p = vinculo.get("partidas", 0)
                v = vinculo.get("vitorias", 0)
                taxa = int(v / p * 100) if p else 0
                info_v = f" | ⭐ Vínculo: {p}j ({taxa}%)"

            print(
                f"{i:2}. {c['nome']:25} | OVR: {c.get('overall', 50)} | {c.get('nacionalidade', '??')}{info_v}"
            )

        if len(candidatos) > limite:
            print(f"... e mais {len(candidatos)-limite} jogadores.")

        print_green("\n[0] Voltar")
        print()

        escolha = safe_input("Quem você deseja convidar? ").strip()
        if escolha == "0":
            return None

        if escolha.isdigit() and 1 <= int(escolha) <= min(len(candidatos), limite):
            candidato_original = candidatos[int(escolha) - 1]
            vinculo_salvo = candidato_original.get("_vinculo")
            # Garante dados completos (hidrata NPCs 'lean'); mantém o original se não encontrado
            npc = (
                ranking.buscar_jogador_por_nome(candidato_original["nome"])
                or candidato_original
            )

            pos_npc = ranking.obter_posicao(npc["nome"]) or 999

            print_yellow(f"\nEnviando convite para {npc['nome']}...")
            time.sleep(0.8)

            sucesso, msg = tentar_convidar_parceiro(
                jogador,
                npc,
                ranking_pos=pos_npc,
                torneio_tipo=torneio_data.get("tipo"),
                vinculo=vinculo_salvo,
            )
            if sucesso:
                print_green(f"\n✅ {msg}")
                safe_input("\nPressione Enter para continuar...")
                return npc
            else:
                print_red(f"\n❌ {msg}")
                safe_input("\nEnter para tentar outro...")
                # Remove o que recusou desta lista temporária
                if candidato_original in candidatos:
                    candidatos.remove(candidato_original)
                if not candidatos:
                    return None
        else:
            print_red("Escolha inválida.")
