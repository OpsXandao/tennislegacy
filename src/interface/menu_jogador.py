import textwrap

from src.io_utils import (
    safe_input,
    clear_screen,
    print_blue,
    print_green,
    print_red,
    print_magenta,
    print_yellow,
    print_cyan,
)
from src.ranking import SistemaRanking
from src.dados import (
    carregar_nacionalidades,
    get_caminho_ranking_save,
    carregar_temporada,
)
from src.interface.menu_progressao import menu_progressao
from src.save import salvar_jogo
from src.management import (
    estrelas_display,
    obter_max_equipe,
)
from src.patrocinios import (
    PATROCINADORES_DISPONIVEIS,
    migrar_patrocinios,
    pode_assinar_patrocinio,
    processar_acao_email_carreira,
)
from src.staff_constants import EMPRESARIOS_DISPONIVEIS, PROFISSIONAIS_DISPONIVEIS

_W = 60


# ── Helpers de apresentação ──────────────────────────────────────────────────


def _header(titulo):
    print(f"\n{'═' * _W}")
    print_blue(f"{titulo:^{_W}}")
    print(f"{'═' * _W}")


def _sep():
    print(f"  {'─' * (_W - 4)}")


def _label_fadiga(fadiga):
    if fadiga <= 30:
        return "Descansado"
    elif fadiga <= 60:
        return "Cansado — leve redução de rendimento"
    elif fadiga <= 80:
        return "Esgotado — rendimento comprometido"
    else:
        return "Crítico — risco de lesão!"


def _formatar_fase(fase):
    fases = {
        "qualy_1": "Qualy 1",
        "qualy_2": "Qualy 2",
        "qualy_r1": "Qualy R1",
        "qualy_r2": "Qualy R2",
        "qualy_r3": "Qualy R3",
        "pre_oitavas": "Pré-oitavas",
        "oitavas": "Oitavas",
        "r128": "R128",
        "r96": "R96",
        "r64": "R64",
        "r32": "R32",
        "r16": "Oitavas",
        "quartas": "Quartas",
        "semifinal": "Semifinal",
        "final": "Final",
        "grupos": "Fase de grupos",
        "eliminado_grupos": "Eliminado nos grupos",
        "finalizado": "Finalizado",
    }
    return fases.get(fase, str(fase).replace("_", " ").title())


def _fase_carreira(idade):
    if idade < 19:
        return "Promessa 🌱"
    elif idade <= 22:
        return "Em Ascensão 🚀"
    elif idade <= 27:
        return "No Ápice 🔥"
    elif idade <= 31:
        return "Veterano ⚔️"
    elif idade <= 34:
        return "Início do Declínio 📉"
    else:
        return "Lenda 🏆"


def _barra_atributo(valor, largura=10):
    """Gera uma barra visual colorida para o atributo."""
    preenchido = round((valor / 100) * largura)
    barra = "█" * preenchido + "░" * (largura - preenchido)
    if valor >= 80:
        return f"\033[92m{barra}\033[0m"  # Verde
    if valor >= 60:
        return f"\033[93m{barra}\033[0m"  # Amarelo
    return f"\033[91m{barra}\033[0m"  # Vermelho


def _resumo_financeiro_semanal(jogador):
    equipe = getattr(jogador, "equipe", [])
    patrocinios = migrar_patrocinios(getattr(jogador, "patrocinios", []))
    empres = getattr(jogador, "empresario", None)

    despesa_equipe = 0
    for c in equipe:
        pid = c.get("id") if isinstance(c, dict) else c
        prof = PROFISSIONAIS_DISPONIVEIS.get(pid, {})
        despesa_equipe += (
            c.get("salario", prof.get("salario_semanal", 0))
            if isinstance(c, dict)
            else prof.get("salario_semanal", 0)
        )

    comissao_empresario = 0
    bonus_patrocinio_pct = 0.0
    if isinstance(empres, dict):
        emp_data = EMPRESARIOS_DISPONIVEIS.get(empres.get("id", ""), {})
        despesa_equipe += empres.get("salario", emp_data.get("salario_semanal", 0))
        comissao_pct = emp_data.get("comissao_agenciamento", 0.15)
        bonus_patrocinio_pct = emp_data.get("bonus_patrocinio", 0.0)

    receita_patrocinio_bruta = 0
    for pid in patrocinios:
        p = PATROCINADORES_DISPONIVEIS.get(pid, {})
        val_base = int(p.get("pagamento_semanal", 0) or 0)
        receita_patrocinio_bruta += int(val_base * (1.0 + bonus_patrocinio_pct))

    comissao_empresario = int(
        receita_patrocinio_bruta * (comissao_pct if isinstance(empres, dict) else 0.0)
    )
    receita_patrocinio_liquida = receita_patrocinio_bruta - comissao_empresario

    saldo_liquido = receita_patrocinio_liquida - despesa_equipe
    return {
        "despesa_equipe": despesa_equipe,
        "receita_patrocinio": receita_patrocinio_liquida,
        "comissao_empresario": comissao_empresario,
        "saldo_liquido": saldo_liquido,
    }


def _descricao_efeito_profissional(prof):
    cat = prof.get("categoria", "")
    if cat == "treinador":
        foco = prof.get("foco_atributos", [])
        if not isinstance(foco, list):
            foco = []
        foco_str = (
            ", ".join(foco[:3]) + ("..." if len(foco) > 3 else "") if foco else "todos"
        )
        return f"Foco: {foco_str} | +{int(prof.get('bonus_progressao', 0) * 100)}% progressão"
    elif cat == "psicologo":
        return (
            f"{int(prof.get('chance_mental', 0) * 100)}% chance"
            f" +{prof.get('bonus_mental', 1)} mental/sem"
        )
    elif cat == "preparador":
        return (
            f"-{prof.get('bonus_fadiga', 0)} fadiga/sem"
            f" | +{int(prof.get('bonus_fisico_pct', 0) * 100)}% físico"
        )
    elif cat == "fisioterapeuta":
        return (
            f"-{prof.get('bonus_fadiga', 0)} fadiga/sem"
            f" | -{prof.get('bonus_recuperacao_lesao', 0)} sem. lesão"
        )
    elif cat == "marketing":
        return (
            f"+{prof.get('seguidores_min', 0):,}–{prof.get('seguidores_max', 0):,}"
            f" seg./sem"
        )
    return prof.get("descricao", "")


def _patrocinio_visivel_no_momento(patrocinador, posicao, seguidores, temporada):
    return True


# ── Escolha de nacionalidade ─────────────────────────────────────────────────


def escolher_nacionalidade_menu():
    """Exibe um menu simples de nacionalidades e retorna a opção escolhida."""
    nacionalidades_por_continente = carregar_nacionalidades()
    continentes = list(nacionalidades_por_continente.keys())

    while True:
        clear_screen()
        _header("ESCOLHER NACIONALIDADE")
        print()
        for idx, continente in enumerate(continentes, 1):
            print_green(f"  {idx}. {continente}")
        print()

        escolha_cont = safe_input("  Continente: ").strip()
        if not escolha_cont.isdigit() or not (
            1 <= int(escolha_cont) <= len(continentes)
        ):
            print_red("  ❌ Opção inválida.")
            safe_input("\n  Pressione Enter para continuar...")
            continue

        continente_escolhido = continentes[int(escolha_cont) - 1]
        paises = nacionalidades_por_continente[continente_escolhido]

        while True:
            clear_screen()
            _header(f"NACIONALIDADES — {continente_escolhido.upper()}")
            print()
            for idx, pais in enumerate(paises, 1):
                print_green(f"  {idx}. {pais}")
            print()

            escolha_pais = safe_input("  Nacionalidade: ").strip()
            if escolha_pais.isdigit() and 1 <= int(escolha_pais) <= len(paises):
                return paises[int(escolha_pais) - 1]

            print_red("  ❌ Opção inválida.")
            safe_input("\n  Pressione Enter para continuar...")


# ── Menu principal do jogador ────────────────────────────────────────────────


def menu_jogador(jogador, nome_save):
    """Exibe informações e atributos do jogador."""
    if jogador is None:
        print_red("❌ Jogador não carregado.")
        return
    while True:
        clear_screen()
        ranking = SistemaRanking(
            get_caminho_ranking_save(nome_save, genero=jogador.genero)
        )
        jogador_ranking = ranking.buscar_jogador_por_nome(jogador.nome)

        if jogador_ranking:
            overall_calculado = jogador.calcular_overall()
            if jogador_ranking.get("overall") != overall_calculado:
                jogador_ranking["overall"] = overall_calculado
                jogador_ranking["atributos"] = jogador.atributos
                ranking.salvar_ranking()

        _header("MEU JOGADOR")
        print()

        if not jogador_ranking:
            print_red("  Dados do jogador não encontrados no ranking.")
        else:
            posicao = ranking.obter_posicao(jogador.nome)
            pts = jogador.pontos_de_skill

            print(f"  {jogador.nome}  ({jogador.nacionalidade})")
            print(
                f"  Ranking: #{posicao}"
                f"  ·  Pontos: {jogador_ranking.get('pontos', 0):,}"
            )
            print(
                f"  Nível {jogador.nivel}"
                f"  ·  XP: {jogador.xp}/{jogador.xp_para_proximo_nivel}"
                f"  ·  Overall: {jogador.calcular_overall()}"
            )
            if pts > 0:
                print_green(
                    f"  🔥 {pts} ponto{'s' if pts != 1 else ''} de skill"
                    f" disponível{'is' if pts != 1 else ''}"
                )
            else:
                print("  Pontos de Skill: 0")

            # Físico
            print()
            print_magenta("  FÍSICO & STATUS")
            _sep()
            fadiga = jogador.fadiga
            print(f"  Fadiga : {fadiga}%  —  {_label_fadiga(fadiga)}")

            ritmo = getattr(jogador, "ritmo_jogo", 50)
            print(
                f"  Ritmo  : {ritmo}%  —  {'Em forma' if ritmo >= 70 else 'Falta ritmo' if ritmo <= 35 else 'Normal'}"
            )

            moral = getattr(jogador, "moral", 70)
            print(
                f"  Moral  : {moral}%  —  {'Confiante' if moral >= 80 else 'Desanimado' if moral <= 30 else 'Estável'}"
            )

            nivel_lesao = jogador.status_lesao.get("nivel", "saudavel")
            penalidade = int(
                round(jogador.status_lesao.get("penalidade_atributos", 0.0) * 100)
            )
            if jogador.status_lesao.get("lesionado"):
                semanas = jogador.status_lesao.get("semanas_restantes", 0)
                s = "s" if semanas != 1 else ""
                print_red(
                    f"  Lesão  : {semanas} semana{s} restante{s}"
                    "  (atributos penalizados)"
                )
            elif nivel_lesao == "limitado":
                print_yellow(f"  Lesão  : Limitado  (-{penalidade}% atributos)")
            elif nivel_lesao == "desconforto":
                print_yellow(f"  Lesão  : Desconforto  (-{penalidade}% atributos)")
            else:
                print_green("  Lesão  : Saudável ✓")

            status_doenca = (
                jogador.status_doenca
                if isinstance(getattr(jogador, "status_doenca", {}), dict)
                else {}
            )
            if status_doenca.get("doente"):
                tipo = status_doenca.get("tipo", "doença").title()
                p_d = int(round(status_doenca.get("penalidade_atributos", 0.0) * 100))
                sem_d = status_doenca.get("semanas_restantes", 1)
                s = "s" if sem_d != 1 else ""
                print_yellow(
                    f"  Doença : {tipo}  (-{p_d}% atributos, {sem_d} semana{s})"
                )
            else:
                print_green("  Doença : Saudável ✓")

            # Atributos técnicos — 2 colunas com barras
            print()
            print_magenta("  TÉCNICO")
            _sep()
            items_t = list(jogador.atributos.items())
            for k in range(0, len(items_t), 2):
                a1, v1 = items_t[k]
                b1 = _barra_atributo(v1)
                if k + 1 < len(items_t):
                    a2, v2 = items_t[k + 1]
                    b2 = _barra_atributo(v2)
                    print(
                        f"  {a1.title():<10} {v1:>2} {b1}    {a2.title():<10} {v2:>2} {b2}"
                    )
                else:
                    print(f"  {a1.title():<10} {v1:>2} {b1}")

            # Atributos psicológicos — 2 colunas com barras
            print()
            print_magenta("  PSICOLÓGICO")
            _sep()
            items_p = list(jogador.atributos_psicologicos.items())
            for k in range(0, len(items_p), 2):
                a1, v1 = items_p[k]
                n1 = a1.replace("_", " ").title()
                b1 = _barra_atributo(v1)
                if k + 1 < len(items_p):
                    a2, v2 = items_p[k + 1]
                    n2 = a2.replace("_", " ").title()
                    b2 = _barra_atributo(v2)
                    print(f"  {n1:<14} {v1:>2} {b1}    {n2:<14} {v2:>2} {b2}")
                else:
                    print(f"  {n1:<14} {v1:>2} {b1}")

        # Opções
        print()
        print(f"{'═' * _W}")
        pts = jogador.pontos_de_skill
        if pts > 0:
            print_green(f"  [1] 🔥 Gastar Pontos de Skill  ({pts} disponíveis)")
        else:
            print("  [1] 🔥 Gastar Pontos de Skill  (0 disponíveis)")
        print_green("  [2] 📜 Histórico de Partidas")
        print_green("  [3] 📈 Ranking ATP")
        print_green("  [4] 💼 Painel de Carreira")
        print_green("  [5] 💰 Financeiro")
        print_green("  [6] 👨‍💼 Gestão de Equipe e Patrocínios")
        print_yellow("  [0] 🔙 Voltar")
        print(f"{'═' * _W}")
        print()

        escolha = safe_input("  Opção: ").strip().lower()

        if escolha == "0":
            break
        elif escolha == "1":
            if jogador.pontos_de_skill > 0:
                menu_progressao(jogador, nome_save)
            else:
                print_red(
                    "\n  Você não tem Pontos de Skill."
                    " Jogue partidas para ganhar XP e subir de nível."
                )
                safe_input("\n  Pressione Enter para continuar...")
        elif escolha == "2":
            _exibir_historico(jogador)
        elif escolha == "3":
            _dashboard_ranking(jogador, jogador_ranking, ranking, nome_save)
        elif escolha == "4":
            _painel_carreira(jogador, jogador_ranking)
        elif escolha == "5":
            _dashboard_financeiro(jogador)
        elif escolha in {"6", "g"}:
            menu_gestao(jogador, nome_save)
        else:
            print_red("  ❌ Opção inválida.")
            safe_input("\n  Pressione Enter para continuar...")


# ── Histórico ────────────────────────────────────────────────────────────────


def _exibir_historico(jogador, pagina_size=10):
    historico = jogador.historico_partidas
    total = len(historico)

    clear_screen()
    _header("HISTÓRICO DE PARTIDAS")
    print()

    if not historico:
        print_yellow("  Nenhuma partida registrada ainda.")
        safe_input("\n  Pressione Enter para voltar...")
        return

    def _imprimir_bloco(fatia, offset=0):
        for i, h in enumerate(fatia, offset + 1):
            torneio = h.get("torneio", "Torneio Desconhecido")
            ano = h.get("ano", "??")
            semana = h.get("semana", "??")
            fase = _formatar_fase(h.get("fase", "fase_desconhecida"))
            adversario = h.get("adversario", "??")
            placar = h.get("placar", "?")
            resultado = h.get("resultado", "?")
            print(f"  {i}. {torneio}  (Ano {ano}, S{semana})")
            print(f"     {fase}  ·  vs {adversario}  ·  {placar}  ·  {resultado}")

    inicio = max(0, total - pagina_size)
    _imprimir_bloco(historico[inicio:], inicio)

    if total > pagina_size:
        print()
        print_yellow(f"  (Últimas {pagina_size} de {total} partidas)")
        if safe_input("  Ver todas? [s/n]: ").strip().lower() == "s":
            clear_screen()
            _header("HISTÓRICO COMPLETO")
            print()
            _imprimir_bloco(historico)

    safe_input("\n  Pressione Enter para voltar...")


# ── Painel de carreira ───────────────────────────────────────────────────────


def _painel_carreira(jogador, jogador_ranking):
    """Exibe fase da carreira, pico técnico, progressão e status físico."""
    clear_screen()
    _header("PAINEL DE CARREIRA")
    print()

    idade = getattr(jogador, "idade", 20)
    pico = getattr(jogador, "pico_carreira", 28)
    fase = _fase_carreira(idade)
    nivel = getattr(jogador, "nivel", 1)
    xp = getattr(jogador, "xp", 0)
    xp_prox = getattr(jogador, "xp_para_proximo_nivel", 100)

    print(f"  {jogador.nome}  |  {jogador.nacionalidade}")
    print(f"  Fase da Carreira : {fase}")
    print(f"  Idade atual      : {idade} anos")
    print(f"  Pico esperado    : {pico} anos")
    print()

    # Timeline visual
    INICIO, FIM, BAR = 16, 40, 26

    def _pos(a):
        return max(0, min(BAR - 1, round((a - INICIO) / (FIM - INICIO) * BAR)))

    pos_a = _pos(idade)
    pos_p = _pos(pico)
    tl = ["─"] * BAR
    tl[pos_p] = "P"
    tl[pos_a] = "★" if pos_a == pos_p else "▲"
    print(f"  16{''.join(tl):^{BAR}}40")
    print(f"     ▲=você agora   P=pico ({pico}a)   ★=no pico")

    distancia = pico - idade
    if distancia > 3:
        print_green(f"\n  ↑ Evolução ativa — {distancia} anos até o pico técnico")
    elif distancia > 0:
        print_green(f"\n  ↑ Pico chegando — aproveite os próximos {distancia} anos!")
    elif distancia == 0:
        print_green("\n  ★ Você está no seu auge técnico!")
    elif distancia >= -4:
        print_yellow(f"\n  → Declínio leve — {-distancia} anos após o pico")
    else:
        print_red("\n  ↓ Declínio avançado — mantenha a consistência")

    # XP
    print()
    print_magenta("  PROGRESSÃO DE NÍVEL")
    _sep()
    print(f"  Nível {nivel}  —  {xp}/{xp_prox} XP")
    pct = xp / xp_prox if xp_prox > 0 else 0
    filled = round(pct * 24)
    barra = "█" * filled + "░" * (24 - filled)
    print(f"  [{barra}] {pct:.0%}")

    # Status físico
    print()
    print_magenta("  STATUS FÍSICO")
    _sep()
    fadiga = getattr(jogador, "fadiga", 0)
    print(f"  Fadiga : {fadiga}%  —  {_label_fadiga(fadiga)}")

    nivel_lesao = jogador.status_lesao.get("nivel", "saudavel")
    penalidade = int(round(jogador.status_lesao.get("penalidade_atributos", 0.0) * 100))
    if jogador.status_lesao.get("lesionado"):
        semanas = jogador.status_lesao.get("semanas_restantes", 0)
        s = "s" if semanas != 1 else ""
        print_red(f"  Lesão  : {semanas} semana{s} restante{s}")
    elif nivel_lesao == "limitado":
        print_yellow(f"  Lesão  : Limitado (-{penalidade}% atributos)")
    elif nivel_lesao == "desconforto":
        print_yellow(f"  Lesão  : Desconforto (-{penalidade}% atributos)")
    else:
        print_green("  Lesão  : Saudável ✓")

    status_doenca = (
        jogador.status_doenca
        if isinstance(getattr(jogador, "status_doenca", {}), dict)
        else {}
    )
    if status_doenca.get("doente"):
        tipo = status_doenca.get("tipo", "doença").title()
        p_d = int(round(status_doenca.get("penalidade_atributos", 0.0) * 100))
        sem = status_doenca.get("semanas_restantes", 1)
        print_yellow(f"  Doença : {tipo} (-{p_d}% atributos, {sem} sem.)")
    else:
        print_green("  Doença : Saudável ✓")

    # Títulos
    trofeus = jogador_ranking.get("trofeus", []) if jogador_ranking else []
    if trofeus:
        print()
        print_magenta(f"  TÍTULOS  ({len(trofeus)})")
        _sep()
        for t in list(reversed(trofeus[-3:])):
            print(
                f"  🏆 {t.get('torneio', '?')} ({t.get('tipo', '')})"
                f" — {t.get('ano', '?')}"
            )

    print(f"\n{'═' * _W}")
    safe_input("\n  Pressione Enter para voltar...")


# ── Dashboard de Ranking ATP ─────────────────────────────────────────────────


def _dashboard_ranking(jogador, jogador_ranking, ranking, nome_save):
    """Exibe posição ATP/WTA, pontos e resultados de simples e duplas."""
    clear_screen()
    _header("RANKING " + ("ATP" if jogador.genero == "masculino" else "WTA"))
    print()

    temporada = carregar_temporada(nome_save)
    ano_atual = temporada.get("ano", 2026)

    # Carrega ranking de duplas também
    from src.dados import get_caminho_ranking_duplas

    path_d = get_caminho_ranking_duplas(nome_save, genero=jogador.genero)
    ranking_duplas = SistemaRanking(path_d, modalidade="duplas")
    jogador_ranking_duplas = ranking_duplas.buscar_jogador_por_nome(jogador.nome)

    pos_s = ranking.obter_posicao(jogador.nome)
    pos_d = ranking_duplas.obter_posicao(jogador.nome)

    print(f"  Posição Simples : #{pos_s or 'N/A'}")
    print(f"  Posição Duplas  : #{pos_d or 'N/A'}")
    print()

    # --- SIMPLES ---
    print_magenta("  PONTOS SIMPLES (Best-18)")
    _sep()
    pontos_s = jogador_ranking.get("pontos", 0) if jogador_ranking else 0
    pts_rk_s = jogador_ranking.get("pontos_ranking", pontos_s) if jogador_ranking else 0
    print(f"  Ranking: {pts_rk_s:>6,} pts | Total: {pontos_s:>6,} pts")

    # --- DUPLAS ---
    print()
    print_magenta("  PONTOS DUPLAS")
    _sep()
    pontos_d = (
        jogador_ranking_duplas.get(
            "pontos_duplas", jogador_ranking_duplas.get("pontos", 0)
        )
        if jogador_ranking_duplas
        else 0
    )
    pts_rk_d = (
        jogador_ranking_duplas.get("pontos_ranking_duplas", pontos_d)
        if jogador_ranking_duplas
        else 0
    )
    print(f"  Ranking: {pts_rk_d:>6,} pts | Total: {pontos_d:>6,} pts")

    if getattr(jogador, "pontos_ytd", 0) > 0:
        print()
        print(f"  Race to Turin (YTD) : {jogador.pontos_ytd:>6,} pts")

    # Melhores resultados (Unificado ou Abas?)
    # Vamos mostrar os resultados de Simples primeiro, e depois Duplas se houver.
    print()
    print_magenta(f"  RESULTADOS SIMPLES (temporada {ano_atual})")
    _sep()

    def _exibir_resultados_mod(j_rk, mod_label):
        historico = j_rk.get("historico_torneios", []) if j_rk else []
        resultados_ano = [e for e in historico if e.get("ano") == ano_atual]

        # Fallback pontos detalhados
        if not resultados_ano:
            c_pts = (
                "pontos_detalhados"
                if mod_label == "Simples"
                else "pontos_detalhados_duplas"
            )
            detalhado = j_rk.get(c_pts, []) if j_rk else []
            for b in detalhado:
                if b.get("ano_origem") == ano_atual and int(b.get("pontos", 0)) > 0:
                    resultados_ano.append(
                        {
                            "nome": b.get("torneio", "?"),
                            "tipo": b.get("tipo", "ATP 250"),
                            "fase": b.get("fase", "?"),
                            "pontos": int(b.get("pontos", 0)),
                            "obrigatorio": b.get("tipo") in ("Grand Slam", "ATP 1000"),
                        }
                    )

        if resultados_ano:
            top = sorted(
                resultados_ano, key=lambda x: x.get("pontos", 0), reverse=True
            )[:18]
            for i, e in enumerate(top, 1):
                obrig = "●" if e.get("obrigatorio") else " "
                print(
                    f"    {obrig}{i:>2}. {e['nome'][:22]:<22}  {_formatar_fase(e['fase'])[:14]:<14}  {e['pontos']:>4} pts"
                )
        else:
            print(f"    Nenhum resultado de {mod_label.lower()} registrado.")

    _exibir_resultados_mod(jogador_ranking, "Simples")

    print()
    print_magenta(f"  RESULTADOS DUPLAS (temporada {ano_atual})")
    _sep()
    _exibir_resultados_mod(jogador_ranking_duplas, "Duplas")

    print()
    print_yellow("  [● = obrigatório (GS/1000)]")

    print(f"\n{'═' * _W}")
    safe_input("\n  Pressione Enter para voltar...")


# ── Dashboard Financeiro ─────────────────────────────────────────────────────


def _dashboard_financeiro(jogador):
    """Exibe saldo, histórico de transações e breakdown por categoria."""
    clear_screen()
    _header("FINANCEIRO")
    print()

    dinheiro = getattr(jogador, "dinheiro", 0)
    print(f"  Saldo atual : $ {dinheiro:,.0f}")
    print()

    transacoes = getattr(jogador, "transacoes", [])

    if not transacoes:
        print_yellow("  Nenhuma transação registrada ainda.")
        print("  Os ganhos e gastos aparecem aqui conforme você joga torneios.")
        print(f"\n{'═' * _W}")
        safe_input("\n  Pressione Enter para voltar...")
        return

    # Breakdown por categoria
    por_categoria = {}
    for t in transacoes:
        cat = t.get("categoria", "outros")
        por_categoria[cat] = por_categoria.get(cat, 0) + t.get("valor", 0)

    print_magenta("  TOTAIS POR CATEGORIA")
    _sep()
    for cat, total in sorted(por_categoria.items(), key=lambda x: x[1], reverse=True):
        sinal = "+" if total >= 0 else ""
        if total >= 0:
            print_green(f"    {cat:<20}  {sinal}$ {total:,.0f}")
        else:
            print_red(f"    {cat:<20}  $ {total:,.0f}")

    # Últimas transações
    print()
    print_magenta("  ÚLTIMAS TRANSAÇÕES")
    _sep()
    ultimas = transacoes[-10:]
    for t in reversed(ultimas):
        sem = t.get("semana", "?")
        desc = t.get("descricao", "")[:28]
        valor = t.get("valor", 0)
        saldo_pos = t.get("saldo_pos")
        sinal = "+" if valor >= 0 else ""
        saldo_str = f"  → $ {saldo_pos:,.0f}" if saldo_pos is not None else ""
        linha_t = f"    S{sem:<3}  {desc:<28}  {sinal}$ {valor:,.0f}{saldo_str}"
        if valor >= 0:
            print_green(linha_t)
        else:
            print_red(linha_t)

    print(f"\n{'═' * _W}")
    safe_input("\n  Pressione Enter para voltar...")


# ── Gestão de Carreira ───────────────────────────────────────────────────────


def menu_gestao(jogador, nome_save):
    """Menu principal de gestão de carreira."""
    if jogador is None:
        print_red("❌ Jogador não carregado.")
        return
    _CATS_NOME = {
        "treinador": "Treinador",
        "psicologo": "Psicólogo",
        "preparador": "Prep. Físico",
        "fisioterapeuta": "Fisioterapeuta",
        "marketing": "Marketing",
    }
    while True:
        clear_screen()
        _header("GESTÃO DE CARREIRA")
        print()

        # Empresário
        emp = getattr(jogador, "empresario", None)
        max_eq = obter_max_equipe(jogador)
        if isinstance(emp, dict):
            emp_data = EMPRESARIOS_DISPONIVEIS.get(emp.get("id", ""), {})
            nome_emp = emp_data.get("nome", "?")
            nac_emp = emp_data.get("nacionalidade", "?")
            est_emp = estrelas_display(emp_data.get("estrelas", 1))
            sem_emp = emp.get("semanas_restantes", 0)
            sal_emp = emp.get("salario", emp_data.get("salario_semanal", 0))
            print_green(
                f"  Empresário: {nome_emp} [{nac_emp}] {est_emp}"
                f"  (${sal_emp}/sem · {sem_emp} sem. restantes)"
            )
        else:
            print_yellow("  Empresário: Nenhum  (máx. 2 profissionais)")
        print()

        # Equipe
        equipe = getattr(jogador, "equipe", [])
        print_magenta(f"  Equipe: {len(equipe)}/{max_eq} slots")
        if equipe:
            for contrato in equipe:
                pid = contrato.get("id") if isinstance(contrato, dict) else contrato
                prof = PROFISSIONAIS_DISPONIVEIS.get(pid, {})
                nome_p = prof.get("nome", pid)
                nac_p = prof.get("nacionalidade", "?")
                est_p = estrelas_display(prof.get("estrelas", 1))
                cat_p = _CATS_NOME.get(
                    prof.get("categoria", ""), prof.get("categoria", "")
                )
                salario_p = (
                    contrato.get("salario", 0)
                    if isinstance(contrato, dict)
                    else prof.get("salario_semanal", 0)
                )
                sem_p = (
                    contrato.get("semanas_restantes", 0)
                    if isinstance(contrato, dict)
                    else 0
                )
                print_green(
                    f"    {cat_p:<14} {nome_p} [{nac_p}] {est_p}"
                    f"  ${salario_p}/sem · {sem_p} sem. restantes"
                )
        else:
            print_yellow("    (equipe vazia)")
        print()

        # Patrocínios e seguidores
        patrocinios = migrar_patrocinios(getattr(jogador, "patrocinios", []))
        if patrocinios != getattr(jogador, "patrocinios", []):
            jogador.patrocinios = patrocinios
            salvar_jogo(nome_save, jogador)
        seguidores = getattr(jogador, "seguidores", 0)
        avisos = getattr(jogador, "avisos_patrocinio", {})
        n_avisos = sum(1 for pid in patrocinios if pid in avisos)
        masters = sum(
            1
            for pid in patrocinios
            if PATROCINADORES_DISPONIVEIS.get(pid, {}).get("tier") == "master"
        )
        menores = len(patrocinios) - masters
        pat_str = f"  Patrocínios: Master {masters}/1  ·  Menores {menores}/3"
        if n_avisos:
            pat_str += f"  ⚠ {n_avisos} aviso(s)"
        print(f"{pat_str}   Seguidores: {seguidores:,}")
        print(f"  Saldo: ${jogador.dinheiro:,}")

        caixa = getattr(jogador, "caixa_email", [])
        pendentes_email = sum(
            1
            for item in (caixa if isinstance(caixa, list) else [])
            if isinstance(item, dict) and item.get("status", "pendente") == "pendente"
        )

        resumo_fin = _resumo_financeiro_semanal(jogador)
        desp = resumo_fin["despesa_equipe"]
        rec = resumo_fin["receita_patrocinio"]
        liq = resumo_fin["saldo_liquido"]
        print()
        print_magenta("  CAIXA SEMANAL")
        _sep()
        print(f"    Receita líquida patrocínio : ${rec:,}/sem")
        print(f"    Folha da equipe            : ${desp:,}/sem")
        if liq >= 0:
            print_green(f"    Saldo líquido semanal      : +${liq:,}/sem")
        else:
            print_red(f"    Saldo líquido semanal      : -${abs(liq):,}/sem")
        if liq < 0:
            runway = (jogador.dinheiro // abs(liq)) if abs(liq) > 0 else 999
            print_yellow(f"    Runway estimado            : {runway} semana(s)")
        elif liq == 0:
            print_yellow("    Runway estimado            : Estável (saldo neutro)")
        else:
            print_green("    Runway estimado            : Infinito (saldo positivo)")
        print_yellow("    Regra: patrocinador MASTER é sempre material esportivo.")

        print()
        print(f"{'─' * _W}")
        print_green("  [1] Empresário")
        print_green("  [2] Mercado de Profissionais")
        print_green("  [3] Patrocínios")
        badge = f" ({pendentes_email} pendente(s))" if pendentes_email else ""
        print_green(f"  [4] Caixa de E-mail{badge}")
        print_yellow("  [0] 🔙 Voltar")
        print()

        escolha = safe_input("  Opção: ").strip().lower()
        if escolha == "0":
            break
        elif escolha in {"1", "e"}:
            _mercado_empresario(jogador, nome_save)
        elif escolha == "2":
            _mercado_profissionais(jogador, nome_save)
        elif escolha in {"3", "p"}:
            _gerenciar_patrocinios(jogador, nome_save)
        elif escolha == "4":
            _caixa_email_carreira(jogador, nome_save)
        else:
            print_red("  ❌ Opção inválida.")
            safe_input("\n  Pressione Enter para continuar...")


# ── Caixa de e-mail ──────────────────────────────────────────────────────────


def _caixa_email_carreira(jogador, nome_save):
    while True:
        clear_screen()
        _header("CAIXA DE ENTRADA")
        print()

        caixa = getattr(jogador, "caixa_email", [])
        if not isinstance(caixa, list):
            caixa = []
            jogador.caixa_email = caixa

        pendentes = [
            item
            for item in caixa
            if isinstance(item, dict) and item.get("status", "pendente") == "pendente"
        ]

        if not pendentes:
            print_yellow("  Nenhuma proposta pendente no momento.")
            print(f"\n{'═' * _W}")
            safe_input("\n  Pressione Enter para voltar...")
            return

        for i, item in enumerate(pendentes, 1):
            tipo = item.get("tipo", "geral").replace("_", " ").upper()
            titulo = item.get("titulo", "Sem título")
            print_green(f"  [{i}] {titulo}")
            print(f"      Tipo: {tipo}")
            print(f"      {item.get('mensagem', '')}")

            oferta = item.get("oferta", {})
            if item.get("tipo") == "patrocinio":
                print_cyan(
                    f"      OFERTA: ${oferta.get('pagamento_semanal', 0)}/sem"
                    f" · Bônus: ${oferta.get('bonus_assinatura', 0):,}"
                )
            elif item.get("tipo") == "empresario":
                print_cyan(
                    f"      OFERTA: ${oferta.get('salario_semanal', 0)}/sem"
                    f" · Duração: {oferta.get('duracao_semanas', 26)} sem"
                )
            elif item.get("tipo") in {"programa_tv", "comercial"}:
                print_cyan(
                    f"      RETORNO: +{oferta.get('ganho_seguidores', 0):,} seg."
                    f" · Cachê: ${oferta.get('cache', 0):,}"
                )
            print(f"  {'─' * (_W - 4)}")

        print()
        print_yellow("  [0] 🔙 Voltar")
        print()

        escolha = safe_input("  Número da proposta para responder: ").strip()
        if escolha == "0":
            return
        if not escolha.isdigit() or not (1 <= int(escolha) <= len(pendentes)):
            print_red("  ❌ Opção inválida.")
            safe_input("\n  Pressione Enter para continuar...")
            continue

        proposta = pendentes[int(escolha) - 1]
        print()
        print_magenta(f"  Ação para '{proposta.get('titulo', '?')}':")
        acao = (
            safe_input("  Aceitar [a]  ·  Recusar [r]  ·  Cancelar [c]: ")
            .strip()
            .lower()
        )
        if acao == "c":
            continue
        if acao not in {"a", "r"}:
            print_red("  ❌ Ação inválida.")
            safe_input("\n  Pressione Enter para continuar...")
            continue

        ranking = SistemaRanking(
            get_caminho_ranking_save(nome_save, genero=jogador.genero)
        )
        sucesso, msg = processar_acao_email_carreira(
            jogador,
            proposta,
            "aceitar" if acao == "a" else "recusar",
            ranking,
        )
        if sucesso:
            print_green(f"\n  ✅ {msg}")
        else:
            print_red(f"\n  ❌ {msg}")

        salvar_jogo(nome_save, jogador)
        safe_input("\n  Pressione Enter para continuar...")


# ── Proposta de contrato ─────────────────────────────────────────────────────


def _proposta_contrato(jogador, prof_id, nome_save, eh_empresario=False):
    """Fluxo de proposta de contrato com negociação de salário."""
    if eh_empresario:
        prof = EMPRESARIOS_DISPONIVEIS.get(prof_id, {})
    else:
        prof = PROFISSIONAIS_DISPONIVEIS.get(prof_id, {})
    if not prof:
        print_red("  Profissional não encontrado.")
        safe_input("\n  Pressione Enter para continuar...")
        return False

    clear_screen()
    _header("PROPOSTA DE CONTRATO")
    print()

    nome = prof.get("nome", "?")
    nac = prof.get("nacionalidade", "?")
    est = estrelas_display(prof.get("estrelas", 1))
    sal_base = prof.get("salario_semanal", 0)
    cat = prof.get("categoria", "")

    print(f"  Candidato     : {nome} [{nac}] {est}")
    print(f"  Especialidade : {prof.get('estilo', cat).title()}")
    print()

    desc = prof.get("descricao", "")
    print_magenta("  Descrição:")
    for line in textwrap.wrap(desc, _W - 6):
        print(f"    {line}")

    if not eh_empresario:
        print()
        print_magenta("  Efeito:")
        print(f"    {_descricao_efeito_profissional(prof)}")

    print()
    print(f"  Salário base  : ${sal_base:,}/semana")
    print(f"{'─' * _W}")

    print_magenta("\n  Duração do contrato:")
    print("    [1] 13 semanas  (curto prazo)")
    print("    [2] 26 semanas  (temporada)  — Recomendado")
    print("    [3] 52 semanas  (longo prazo)")
    print("    [0] Cancelar")

    escolha_dur = safe_input("\n  Opção: ").strip()
    duracoes = {"1": 13, "2": 26, "3": 52}
    if escolha_dur not in duracoes:
        return False
    duracao = duracoes[escolha_dur]

    # Negociar salário (±25%)
    sal_final = sal_base
    if (
        safe_input(f"\n  Negociar salário? (base: ${sal_base}) [s/n]: ").strip().lower()
        == "s"
    ):
        margem = int(sal_base * 0.25)
        sal_min = sal_base - margem
        sal_max = sal_base + margem
        print(f"\n  Faixa aceitável: ${sal_min} – ${sal_max}")
        proposta = safe_input("  Sua proposta ($): ").strip()
        if proposta.isdigit():
            p = int(proposta)
            if sal_min <= p <= sal_max:
                sal_final = p
                print_green(f"  ✅ Proposta de ${sal_final} aceita!")
            elif p < sal_min:
                print_yellow(f"  ⚠️ Oferta muito baixa. Aceitando o mínimo: ${sal_min}")
                sal_final = sal_min
            else:
                print_yellow(f"  ⚠️ Teto atingido. Aceitando o máximo: ${sal_max}")
                sal_final = sal_max

    custo_total = sal_final * duracao
    print()
    print(f"{'─' * _W}")
    print(f"  Pagamento : ${sal_final:,}/semana")
    print(f"  Duração   : {duracao} semanas")
    print(f"  Total     : ${custo_total:,}")
    print(f"{'─' * _W}")

    if safe_input("\n  Confirmar assinatura? [s/n]: ").strip().lower() != "s":
        print_yellow("\n  Proposta cancelada.")
        safe_input("\n  Pressione Enter para continuar...")
        return False

    contrato = {"id": prof_id, "semanas_restantes": duracao, "salario": sal_final}
    if eh_empresario:
        jogador.empresario = contrato
        print_green(f"\n  ✅ {nome} é agora seu empresário!")
    else:
        jogador.equipe.append(contrato)
        print_green(f"\n  ✅ {nome} entrou na sua equipe!")

    salvar_jogo(nome_save, jogador)
    safe_input("\n  Pressione Enter para continuar...")
    return True


# ── Mercado de Empresários ───────────────────────────────────────────────────


def _mercado_empresario(jogador, nome_save):
    """Gerencia o empresário (contrato separado da equipe)."""
    while True:
        clear_screen()
        _header("EMPRESÁRIO")
        print()

        emp = getattr(jogador, "empresario", None)
        if isinstance(emp, dict):
            emp_data = EMPRESARIOS_DISPONIVEIS.get(emp.get("id", ""), {})
            nome_e = emp_data.get("nome", "?")
            nac_e = emp_data.get("nacionalidade", "?")
            est_e = estrelas_display(emp_data.get("estrelas", 1))
            print_green(
                f"  Atual: {nome_e} [{nac_e}] {est_e}"
                f"  (${emp.get('salario', 0)}/sem"
                f" · {emp.get('semanas_restantes', 0)} sem. restantes)"
            )
            print(f"    Máx. profissionais: {emp_data.get('max_equipe', 2)}")
        else:
            print_yellow("  Sem empresário.  (máximo atual: 2 profissionais)")
        print()

        print_magenta("  Empresários disponíveis:")
        print()
        for i, (eid, emp_d) in enumerate(EMPRESARIOS_DISPONIVEIS.items(), 1):
            esta = isinstance(emp, dict) and emp.get("id") == eid
            est = estrelas_display(emp_d.get("estrelas", 1))
            status = "  [ATUAL]" if esta else ""
            print_green(
                f"  [{i}] {emp_d['nome']} [{emp_d['nacionalidade']}] {est}{status}"
            )
            print(
                f"       ${emp_d['salario_semanal']}/sem"
                f" · Máx. equipe: {emp_d['max_equipe']}"
                f" · +{int(emp_d.get('bonus_patrocinio', 0) * 100)}% patrocínio"
            )
            print(f"       {emp_d['descricao']}")
            print()

        print(f"{'─' * _W}")
        print_red("  [D] Dispensar empresário atual")
        print_yellow("  [0] 🔙 Voltar")
        print()

        escolha = (
            safe_input("  Número para contratar  ·  D dispensar  ·  0 voltar: ")
            .strip()
            .lower()
        )
        if escolha == "0":
            break
        elif escolha == "d":
            if not isinstance(emp, dict):
                print_yellow("  Nenhum empresário para dispensar.")
                safe_input("\n  Pressione Enter para continuar...")
            else:
                emp_data = EMPRESARIOS_DISPONIVEIS.get(emp.get("id", ""), {})
                sem_rest = emp.get("semanas_restantes", 0)
                sal = emp.get("salario", 0)
                compensacao = sem_rest * (sal // 2)
                print_yellow(
                    f"\n  Dispensar {emp_data.get('nome', '?')}?"
                    f" Compensação: ${compensacao:,}"
                    f" ({sem_rest} sem. × ${sal // 2})"
                )
                if safe_input("  Confirmar? [s/n]: ").strip().lower() == "s":
                    jogador.empresario = None
                    if compensacao > 0:
                        jogador.registrar_transacao(
                            -compensacao,
                            "Compensação empresário",
                            categoria="equipe",
                        )
                    salvar_jogo(nome_save, jogador)
                    print_green("  ✅ Empresário dispensado.")
                safe_input("\n  Pressione Enter para continuar...")
            break
        elif escolha.isdigit():
            idx = int(escolha) - 1
            keys = list(EMPRESARIOS_DISPONIVEIS.keys())
            if 0 <= idx < len(keys):
                eid = keys[idx]
                if isinstance(emp, dict) and emp.get("id") == eid:
                    print_yellow("  Você já tem este empresário.")
                    safe_input("\n  Pressione Enter para continuar...")
                    continue
                if isinstance(emp, dict):
                    print_yellow(
                        "  Você já tem um empresário."
                        " Dispense-o antes de contratar outro."
                    )
                    safe_input("\n  Pressione Enter para continuar...")
                    continue
                _proposta_contrato(jogador, eid, nome_save, eh_empresario=True)
                break
        else:
            print_red("  ❌ Opção inválida.")
            safe_input("\n  Pressione Enter para continuar...")


# ── Mercado de Profissionais ─────────────────────────────────────────────────


def _mercado_profissionais(jogador, nome_save):
    """Lista e gerencia os profissionais da equipe."""
    _CATS_ORDEM = [
        "treinador",
        "psicologo",
        "preparador",
        "fisioterapeuta",
        "marketing",
    ]
    _CATS_NOME = {
        "treinador": "Treinadores",
        "psicologo": "Psicólogos",
        "preparador": "Preparadores Físicos",
        "fisioterapeuta": "Fisioterapeutas",
        "marketing": "Gestores de Marketing",
    }

    while True:
        clear_screen()
        equipe = getattr(jogador, "equipe", [])
        max_eq = obter_max_equipe(jogador)
        ids_equipe = set()
        cats_ocupadas = set()
        for c in equipe:
            pid = c.get("id") if isinstance(c, dict) else c
            ids_equipe.add(pid)
            prof = PROFISSIONAIS_DISPONIVEIS.get(pid, {})
            cats_ocupadas.add(prof.get("categoria"))

        _header("MERCADO DE PROFISSIONAIS")
        print()
        print(
            f"  Equipe: {len(equipe)}/{max_eq} slots  ·  Saldo: ${jogador.dinheiro:,}"
        )
        print_yellow("  [EQUIPE]=já contratado · ⚠=salário acima do caixa")
        if obter_max_equipe(jogador) == 2 and not getattr(jogador, "empresario", None):
            print_yellow("  Dica: contrate um empresário para liberar mais slots!")
        print()

        idx_global = 1
        id_to_key = {}
        for cat in _CATS_ORDEM:
            profs_cat = [
                (pid, p)
                for pid, p in PROFISSIONAIS_DISPONIVEIS.items()
                if p.get("categoria") == cat
            ]
            if not profs_cat:
                continue
            print_magenta(f"  {_CATS_NOME[cat]}:")
            for pid, p in profs_cat:
                esta = pid in ids_equipe
                est = estrelas_display(p.get("estrelas", 1))
                sal = p.get("salario_semanal", 0)
                efeito = _descricao_efeito_profissional(p)
                status = " [EQUIPE]" if esta else ""
                label = f"[{idx_global}]"
                alerta = " ⚠" if sal > getattr(jogador, "dinheiro", 0) else ""
                if esta:
                    print_green(
                        f"    {label} {p['nome']} [{p.get('nacionalidade', '?')}]"
                        f" {est}{status}"
                    )
                else:
                    print(
                        f"    {label} {p['nome']} [{p.get('nacionalidade', '?')}] {est}"
                    )
                print(f"         ${sal}/sem{alerta}  ·  {efeito}")
                id_to_key[str(idx_global)] = pid
                idx_global += 1
            print()

        print(f"{'─' * _W}")
        print_green("  [C] Ver contratos ativos")
        print_red("  [D] Dispensar profissional")
        print_yellow("  [0] 🔙 Voltar")
        print()

        escolha = (
            safe_input(
                "  Número para contratar  ·  C contratos  ·  D dispensar  ·  0 voltar: "
            )
            .strip()
            .lower()
        )

        if escolha == "0":
            break
        elif escolha == "c":
            _ver_contratos_ativos(jogador)
        elif escolha == "d":
            _dispensar_profissional(jogador, nome_save)
        elif escolha in id_to_key:
            pid = id_to_key[escolha]
            prof = PROFISSIONAIS_DISPONIVEIS[pid]
            cat = prof.get("categoria")
            if pid in ids_equipe:
                print_yellow(f"  {prof['nome']} já está na sua equipe.")
                safe_input("\n  Pressione Enter para continuar...")
                continue
            if cat in cats_ocupadas:
                nome_cat = _CATS_NOME.get(cat, cat)
                print_yellow(
                    f"  Você já tem um(a) {nome_cat} na equipe." " Dispense-o primeiro."
                )
                safe_input("\n  Pressione Enter para continuar...")
                continue
            if len(equipe) >= max_eq:
                print_red(
                    f"  Equipe cheia ({max_eq} slots)."
                    " Dispense alguém ou contrate um empresário melhor."
                )
                safe_input("\n  Pressione Enter para continuar...")
                continue
            _proposta_contrato(jogador, pid, nome_save)
        else:
            print_red("  ❌ Opção inválida.")
            safe_input("\n  Pressione Enter para continuar...")


# ── Ver contratos ativos ─────────────────────────────────────────────────────


def _ver_contratos_ativos(jogador):
    clear_screen()
    _header("CONTRATOS ATIVOS")
    print()

    equipe = getattr(jogador, "equipe", [])
    if not equipe:
        print_yellow("  Nenhum profissional contratado.")
    else:
        for c in equipe:
            pid = c.get("id") if isinstance(c, dict) else c
            prof = PROFISSIONAIS_DISPONIVEIS.get(pid, {})
            nome = prof.get("nome", pid)
            nac = prof.get("nacionalidade", "?")
            sal = (
                c.get("salario", prof.get("salario_semanal", 0))
                if isinstance(c, dict)
                else prof.get("salario_semanal", 0)
            )
            sem = c.get("semanas_restantes", 0) if isinstance(c, dict) else 0
            total_restante = sal * sem
            est = estrelas_display(prof.get("estrelas", 1))
            print_green(f"  {nome} [{nac}] {est}")
            print(
                f"    ${sal}/sem  ·  {sem} sem. restantes"
                f"  ·  Total: ${total_restante:,}"
            )

    emp = getattr(jogador, "empresario", None)
    if isinstance(emp, dict):
        emp_data = EMPRESARIOS_DISPONIVEIS.get(emp.get("id", ""), {})
        nome_e = emp_data.get("nome", "?")
        sal_e = emp.get("salario", 0)
        sem_e = emp.get("semanas_restantes", 0)
        print()
        print_green(f"  Empresário: {nome_e}  ${sal_e}/sem  ·  {sem_e} sem. restantes")

    print(f"\n{'═' * _W}")
    safe_input("\n  Pressione Enter para voltar...")


# ── Dispensar profissional ───────────────────────────────────────────────────


def _dispensar_profissional(jogador, nome_save):
    equipe = getattr(jogador, "equipe", [])
    if not equipe:
        print_yellow("  Equipe vazia.")
        safe_input("\n  Pressione Enter para continuar...")
        return

    clear_screen()
    _header("DISPENSAR PROFISSIONAL")
    print()

    for i, c in enumerate(equipe, 1):
        pid = c.get("id") if isinstance(c, dict) else c
        prof = PROFISSIONAIS_DISPONIVEIS.get(pid, {})
        nome = prof.get("nome", pid)
        sal = (
            c.get("salario", prof.get("salario_semanal", 0))
            if isinstance(c, dict)
            else 0
        )
        sem = c.get("semanas_restantes", 0) if isinstance(c, dict) else 0
        compensacao = sem * (sal // 2)
        print(
            f"  [{i}] {nome}"
            f"  —  ${sal}/sem  ·  {sem} sem. rest."
            f"  ·  Compensação: ${compensacao:,}"
        )
    print("  [0] Cancelar")
    print()

    escolha = safe_input("  Quem dispensar? ").strip()
    if escolha == "0" or not escolha.isdigit():
        return
    idx = int(escolha) - 1
    if not (0 <= idx < len(equipe)):
        return

    c = equipe[idx]
    pid = c.get("id") if isinstance(c, dict) else c
    prof = PROFISSIONAIS_DISPONIVEIS.get(pid, {})
    nome = prof.get("nome", pid)
    sal = c.get("salario", 0) if isinstance(c, dict) else 0
    sem = c.get("semanas_restantes", 0) if isinstance(c, dict) else 0
    compensacao = sem * (sal // 2)

    print_yellow(f"\n  Dispensar {nome}? Compensação: ${compensacao:,}")
    if safe_input("  Confirmar? [s/n]: ").strip().lower() != "s":
        return

    equipe.pop(idx)
    if compensacao > 0:
        jogador.registrar_transacao(
            -compensacao, f"Compensação: {nome}", categoria="equipe"
        )
    salvar_jogo(nome_save, jogador)
    print_green(f"  ✅ {nome} dispensado.")
    safe_input("\n  Pressione Enter para continuar...")


# ── Patrocínios ──────────────────────────────────────────────────────────────


def _gerenciar_patrocinios(jogador, nome_save):
    # Dados que não mudam dentro deste menu
    ranking = SistemaRanking(get_caminho_ranking_save(nome_save, genero=jogador.genero))
    posicao = ranking.obter_posicao(jogador.nome)
    seguidores = getattr(jogador, "seguidores", 0)
    temporada = carregar_temporada(nome_save)

    # Migrar formato legado uma vez na entrada
    pat_antigos = list(getattr(jogador, "patrocinios", []))
    pat_normalizados = migrar_patrocinios(pat_antigos)
    if pat_normalizados != pat_antigos:
        jogador.patrocinios = pat_normalizados
        salvar_jogo(nome_save, jogador)

    while True:
        clear_screen()
        avisos = getattr(jogador, "avisos_patrocinio", {})
        masters_ativos = [
            p
            for p in jogador.patrocinios
            if PATROCINADORES_DISPONIVEIS.get(p, {}).get("tier") == "master"
        ]
        menores_ativos = [
            p
            for p in jogador.patrocinios
            if PATROCINADORES_DISPONIVEIS.get(p, {}).get("tier", "menor") != "master"
        ]

        _header("PATROCÍNIOS")
        print()
        print(
            f"  Ranking: #{posicao}"
            f"  ·  Seguidores: {seguidores:,}"
            f"  ·  Master: {len(masters_ativos)}/1"
            f"  ·  Menores: {len(menores_ativos)}/3"
        )
        print_yellow(
            "  Regra: patrocinador MASTER é exclusivo para material esportivo."
        )

        if jogador.patrocinios:
            print()
            print_magenta("  Ativos:")
            for pid in jogador.patrocinios:
                p = PATROCINADORES_DISPONIVEIS.get(pid, {"nome": str(pid), "tier": "?"})
                tier_label = "MASTER" if p.get("tier") == "master" else "MENOR"
                print_green(f"  ✓ {p.get('nome', pid)}  [{tier_label}]")

        # Lista de marcas
        patrocinadores_visiveis = sorted(
            [
                (key, p)
                for key, p in PATROCINADORES_DISPONIVEIS.items()
                if _patrocinio_visivel_no_momento(p, posicao, seguidores, temporada)
            ],
            key=lambda kv: (
                0 if kv[1].get("tier") == "master" else 1,
                kv[1].get("requisito_ranking", 9999),
                kv[1].get("req_seguidores", 0),
                kv[1].get("nome", ""),
            ),
        )

        print()
        print_magenta("  Marcas disponíveis:")
        print()
        for i, (key, p) in enumerate(patrocinadores_visiveis, 1):
            assinado = key in jogador.patrocinios
            tem_aviso = key in avisos
            semanas_aviso = int(avisos.get(key, 0) or 0)
            tier = p.get("tier", "menor")
            req_rank = p["requisito_ranking"]
            req_seg = p.get("req_seguidores", 0)
            cumpre = (posicao <= req_rank) and (seguidores >= req_seg)

            tier_label = " [MASTER]" if tier == "master" else ""
            req_str = f"#{req_rank}"
            if req_seg > 0:
                req_str += f" + {req_seg:,} seg."

            if tem_aviso and assinado:
                motivo = "ranking" if posicao > req_rank * 1.5 else "seguidores"
                prazo = max(0, 3 - semanas_aviso)
                print_yellow(
                    f"  [{i}] ⚠ {p['nome']}{tier_label}"
                    f"  [INSATISFEITO — {motivo.upper()} — prazo: {prazo} sem.]"
                )
            elif assinado:
                print_green(f"  [{i}] ✓ {p['nome']}{tier_label}  [ASSINADO]")
            elif cumpre:
                print_green(f"  [{i}] {p['nome']}{tier_label}")
            else:
                print_red(f"  [{i}] {p['nome']}{tier_label}  (bloqueado)")
            print(
                f"       Req: {req_str}"
                f"  ·  ${p['pagamento_semanal']}/sem"
                f"  ·  Bônus título: ${p['bonus_titulo']:,}"
            )
            print(f"       {p['descricao']}")
            print()

        print(f"{'─' * _W}")
        print_red("  [R] Encerrar um patrocínio")
        print_yellow("  [0] 🔙 Voltar")
        print()

        escolha = (
            safe_input("  Número para assinar  ·  R encerrar  ·  0 voltar: ")
            .strip()
            .lower()
        )

        if escolha == "0":
            break
        elif escolha == "r":
            if not jogador.patrocinios:
                print_red("\n  Você não tem patrocínios para encerrar.")
                safe_input("\n  Pressione Enter para continuar...")
                continue
            print()
            for i, p_id in enumerate(jogador.patrocinios, 1):
                p = PATROCINADORES_DISPONIVEIS.get(p_id, {"nome": p_id})
                print(f"    [{i}] {p['nome']}")
            print("    [0] Cancelar")
            idx_str = safe_input("\n  Qual encerrar? ").strip()
            if idx_str == "0" or not idx_str.isdigit():
                continue
            idx_p = int(idx_str) - 1
            if not (0 <= idx_p < len(jogador.patrocinios)):
                print_red("  ❌ Opção inválida.")
                safe_input("\n  Pressione Enter para continuar...")
                continue
            removido = jogador.patrocinios.pop(idx_p)
            pat = PATROCINADORES_DISPONIVEIS.get(removido, {"nome": removido})
            getattr(jogador, "avisos_patrocinio", {}).pop(removido, None)
            salvar_jogo(nome_save, jogador)
            print_yellow(f"\n  Contrato com {pat['nome']} encerrado.")
            safe_input("\n  Pressione Enter para continuar...")
        elif escolha.isdigit() and 1 <= int(escolha) <= len(patrocinadores_visiveis):
            p_id = [k for k, _ in patrocinadores_visiveis][int(escolha) - 1]
            pode, motivo = pode_assinar_patrocinio(jogador, p_id, posicao, seguidores)
            if not pode:
                print_red(f"\n  ❌ {motivo}")
                safe_input("\n  Pressione Enter para continuar...")
                continue
            p = PATROCINADORES_DISPONIVEIS[p_id]
            bonus = p.get("bonus_assinatura", 0)
            print()
            print_green(f"  {p['nome']} quer assinar!")
            print(f"  · Pagamento    : ${p['pagamento_semanal']}/sem")
            print(f"  · Bônus entrada: ${bonus:,}")
            print()
            if safe_input("  Confirmar assinatura? [s/n]: ").strip().lower() == "s":
                jogador.patrocinios.append(p_id)
                if bonus > 0:
                    jogador.registrar_transacao(
                        bonus,
                        f"Bônus Assinatura: {p['nome']}",
                        categoria="patrocinio",
                    )
                salvar_jogo(nome_save, jogador)
                print_green(f"\n  ✅ Contrato assinado! Bônus de ${bonus:,} recebido.")
            else:
                print_yellow("\n  Assinatura cancelada.")
            safe_input("\n  Pressione Enter para continuar...")
        else:
            print_red("  ❌ Opção inválida.")
            safe_input("\n  Pressione Enter para continuar...")
