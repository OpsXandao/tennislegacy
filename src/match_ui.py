try:
    from colorama import Fore, Style
except ImportError:

    class _NoColor:
        def __getattr__(self, _name):
            return ""

    Fore = _NoColor()
    Style = _NoColor()

from src.io_utils import (
    safe_input,
    get_char_non_blocking,
    clear_screen,
    print_blue,
    print_green,
    print_magenta,
)
from src.match_constants import (
    ModoSimulacao,
    TipoSaque,
    EstrategiaAtaque,
    EstrategiaDefesa,
    EstrategiaSaque,
    IntencaoPonto,
)
from src.simulacao_partida import normalizar_superficie


def _nome_entidade(entidade, padrao="Jogador"):
    if isinstance(entidade, dict):
        return str(entidade.get("nome", padrao))
    return str(getattr(entidade, "nome", padrao))


def escolher_modo_simulacao():
    print("\n" + "=" * 54)
    print_blue(f"{'MODO DE SIMULAÇÃO':^54}")
    print("=" * 54)
    print_green("[1] Rápido       ")
    print("     Resultado imediato por game. Acompanhe o placar.")
    print_green("[2] Detalhado    ")
    print("     Narração ponto a ponto com descrição dos lances.")
    print_green("[3] Estrategista ")
    print("     Você decide a intenção em cada ponto.")
    print()
    print("     Dica: pressione qualquer tecla durante o jogo para pausar.")
    print("=" * 54)
    escolha = safe_input("Escolha (1, 2 ou 3): ").strip()
    if escolha == "2":
        return ModoSimulacao.DETALHADO
    if escolha == "3":
        return ModoSimulacao.ESTRATEGISTA
    return ModoSimulacao.RAPIDO


def escolher_tipo_saque():
    print("\nTipo de saque:")
    print("1. Agressivo (mais aces, mais faltas)")
    print("2. Seguro (menos faltas, menos aces)")
    print("3. Variado (equilibrado)")
    escolha = safe_input("Escolha (1, 2 ou 3): ").strip()
    if escolha == "1":
        return TipoSaque.AGRESSIVO
    if escolha == "2":
        return TipoSaque.SEGURO
    return TipoSaque.VARIADO


def escolher_estrategias():
    print("\n" + "=" * 54)
    print_blue(f"{'ESTRATÉGIA DE JOGO':^54}")
    print("=" * 54)

    print_magenta("\n[ATAQUE]")
    print("  [1] Na rede    — Subir após golpes fortes (voleio)")
    print("  [2] Do fundo   — Winners do baseline (forehand/backhand)")
    print("  [3] Variado    — Alternar padrões conforme o ponto")
    escolha_ataque = safe_input("  Escolha (1-3): ").strip()
    if escolha_ataque == "1":
        ataque = EstrategiaAtaque.REDE
    elif escolha_ataque == "3":
        ataque = EstrategiaAtaque.VARIADO
    else:
        ataque = EstrategiaAtaque.FUNDO

    print_magenta("\n[DEFESA]")
    print("  [1] Contra-ataque — Revidar com winners")
    print("  [2] Consistência  — Bolas altas, esperar o erro")
    print("  [3] Neutralizar   — Slice para resetar o rally")
    escolha_defesa = safe_input("  Escolha (1-3): ").strip()
    if escolha_defesa == "1":
        defesa = EstrategiaDefesa.CONTRA_ATAQUE
    elif escolha_defesa == "3":
        defesa = EstrategiaDefesa.NEUTRALIZAR
    else:
        defesa = EstrategiaDefesa.CONSISTENCIA

    print_magenta("\n[1º SAQUE]")
    print("  [1] Agressivo — Mais aces, mais faltas")
    print("  [2] Seguro    — Menos faltas, menos aces")
    print("  [3] Variado   — Equilibrado")
    escolha_saque_tipo = safe_input("  Escolha (1-3): ").strip()
    if escolha_saque_tipo == "1":
        saque_tipo = TipoSaque.AGRESSIVO
    elif escolha_saque_tipo == "2":
        saque_tipo = TipoSaque.SEGURO
    else:
        saque_tipo = TipoSaque.VARIADO

    print_magenta("\n[2º SAQUE]")
    print("  [1] Forçar  — Arriscar no segundo serviço")
    print("  [2] Seguro  — Priorizar colocar em jogo")
    escolha_saque = safe_input("  Escolha (1-2): ").strip()
    saque = EstrategiaSaque.FORCAR if escolha_saque == "1" else EstrategiaSaque.SEGURO

    estilo_map = {
        EstrategiaAtaque.REDE: "atacar_na_rede",
        EstrategiaAtaque.FUNDO: "atacar_do_fundo",
        EstrategiaAtaque.VARIADO: "atacar_pelo_meio",
    }
    return {
        "ataque": ataque,
        "defesa": defesa,
        "saque": saque,
        "saque_tipo": saque_tipo,
        "estilo": estilo_map[ataque],
    }


def escolher_intencao_ponto():
    print("\nQual a sua intenção para o próximo ponto?")
    print("[1] Arriscar (tentar um winner)")
    print("[2] Paciente (construir o ponto)")
    print("[3] Defensivo (devolver a bola e esperar um erro)")
    while True:
        escolha = safe_input("Escolha (1, 2 ou 3): ").strip()
        if escolha == "1":
            return IntencaoPonto.ARRISCAR
        if escolha == "2":
            return IntencaoPonto.PACIENTE
        if escolha == "3":
            return IntencaoPonto.DEFENSIVO
        print("Opção inválida. Tente novamente.")


def verificar_abandono():
    confirmar = safe_input("Tem certeza que deseja abandonar? (s/n): ").strip().lower()
    return confirmar == "s"


def show_pause_menu(jogador, adversario, stats_j, stats_a, estrategias, modo_atual):
    def print_pause_menu():
        print("\n--- JOGO PAUSADO ---")
        print("[c] Continuar")
        print("[e] Ver Estatisticas")
        print("[t] Mudar Estrategia")
        print("[m] Alternar Modo (Rapido/Detalhado)")
        print("[q] Abandonar Partida")

    print_pause_menu()
    nome_j = _nome_entidade(jogador, "Jogador")
    nome_a = _nome_entidade(adversario, "Adversário")
    while True:
        escolha = get_char_non_blocking().lower()
        if not escolha:
            continue
        if escolha == "e":
            clear_screen()
            print(stats_j.exibir(nome_j, nome_a, stats_a))
            safe_input("\nPressione Enter para voltar ao menu de pausa...")
            clear_screen()
            print_pause_menu()
        elif escolha == "t":
            novas_estrategias = escolher_estrategias()
            return "continue", novas_estrategias, modo_atual
        elif escolha == "m":
            novo_modo = (
                ModoSimulacao.RAPIDO
                if modo_atual == ModoSimulacao.DETALHADO
                else ModoSimulacao.DETALHADO
            )
            print(f"\n✅ Modo alterado para {novo_modo.name}. Vale no proximo game.")
            return "continue", estrategias, novo_modo
        elif escolha == "q":
            return "abandon", estrategias, modo_atual
        elif escolha == "c":
            return "continue", estrategias, modo_atual


def exibir_estatisticas_set(
    jogador,
    adversario,
    games_j,
    games_a,
    stats_j,
    stats_a,
    num_set: int,
    stamina_fim_j: float = None,
    stamina_fim_a: float = None,
    stamina_pos_j: float = None,
    stamina_pos_a: float = None,
):
    """Tela de fim de set com estatísticas e painel de condição física."""
    clear_screen()
    nome_j = _nome_entidade(jogador, "Jogador")
    nome_a = _nome_entidade(adversario, "Adversário")
    vencedor_set = nome_j if games_j > games_a else nome_a
    linha = "=" * 54
    print(f"\n{linha}")
    print_blue(f"  FIM DO {num_set}º SET")
    print(f"  {nome_j} {games_j} — {games_a} {nome_a}")
    print(f"  Vencedor do set: {vencedor_set}")
    print(f"{linha}")
    print(stats_j.exibir(nome_j, nome_a, stats_a))

    # Painel de condição física (estilo Football Manager)
    if stamina_fim_j is not None and stamina_fim_a is not None:
        print(f"\n{'─' * 54}")
        print_blue("  ☕  CONDIÇÃO FÍSICA — Pausa entre Sets")
        print(f"{'─' * 54}")
        print(f"  {nome_j[:22]}")
        print(f"    Fim do set   {barra_stamina(stamina_fim_j)}")
        if stamina_pos_j is not None:
            rec_j = stamina_pos_j - stamina_fim_j
            print(
                f"    Após pausa   {barra_stamina(stamina_pos_j)}"
                f"   {Fore.GREEN}(+{rec_j:.0f}){Style.RESET_ALL}"
            )
        print()
        print(f"  {nome_a[:22]}")
        print(f"    Fim do set   {barra_stamina(stamina_fim_a)}")
        if stamina_pos_a is not None:
            rec_a = stamina_pos_a - stamina_fim_a
            print(
                f"    Após pausa   {barra_stamina(stamina_pos_a)}"
                f"   {Fore.GREEN}(+{rec_a:.0f}){Style.RESET_ALL}"
            )
        print(f"{'─' * 54}")

    safe_input("\n  Pressione Enter para o próximo set...")


def placar_pontos_txt(ponto):
    return {0: "0", 1: "15", 2: "30", 3: "40", 4: "AD"}.get(ponto, "40")


def _cor_stamina(valor: float) -> str:
    """Cor ANSI por nível de stamina (estilo FIFA/Football Manager)."""
    if valor >= 80:
        return Fore.GREEN
    if valor >= 65:
        return Fore.CYAN
    if valor >= 50:
        return Fore.YELLOW
    if valor >= 35:
        return Fore.YELLOW
    return Fore.RED


def _label_stamina(valor: float) -> str:
    """Rótulo de condição física (estilo Football Manager)."""
    if valor >= 80:
        return "Fresco"
    if valor >= 65:
        return "Bem"
    if valor >= 50:
        return "Cansado"
    if valor >= 35:
        return "Exausto"
    return "Crítico"


def barra_stamina(valor: float, largura: int = 12, delta: float = None) -> str:
    """Barra de stamina colorida com rótulo e delta opcional (↑ recuperou / ↓ cansou)."""
    valor = max(0.0, min(100.0, valor))
    preenchido = round(valor / 100 * largura)
    barra = "█" * preenchido + "░" * (largura - preenchido)
    cor = _cor_stamina(valor)
    label = _label_stamina(valor)
    delta_str = ""
    if delta is not None:
        if delta > 0.5:
            delta_str = f"  {Fore.GREEN}▲{delta:.0f}{Style.RESET_ALL}"
        elif delta < -0.5:
            delta_str = f"  {Fore.RED}▼{abs(delta):.0f}{Style.RESET_ALL}"
    return (
        f"{cor}[{barra}]{Style.RESET_ALL} {valor:>3.0f}%"
        f"  {cor}{label:<7}{Style.RESET_ALL}{delta_str}"
    )


def exibir_tela_pre_partida(jogador, adversario, config):
    clear_screen()
    nome_j = _nome_entidade(jogador, "Jogador")
    nome_a = _nome_entidade(adversario, "Adversário")
    atrs_j = getattr(jogador, "atributos", {})
    overall_j = round(sum(atrs_j.values()) / len(atrs_j)) if atrs_j else 60
    overall_a = adversario.get("overall", 60)
    sup_labels = {
        "dura": "Dura (Hard)",
        "saibro": "Saibro (Clay)",
        "grama": "Grama (Grass)",
    }
    sup_nome = sup_labels.get(
        normalizar_superficie(config.superficie), config.superficie.capitalize()
    )
    linha = "=" * 54
    print(f"\n{linha}")
    print_blue(f"{'TÊNIS LEGACY':^54}")
    if config.nome_torneio:
        titulo = config.nome_torneio
        if config.tipo_torneio:
            titulo += f"  •  {config.tipo_torneio}"
        print_blue(f"{titulo:^54}")
    print(f"{linha}")
    print()
    print(f"  {nome_j:<24}  VS  {nome_a:>22}")
    print(f"  {'OVR ' + str(overall_j):<24}       {'OVR ' + str(overall_a):>22}")
    print()
    print(f"  Superfície : {sup_nome}")
    print(f"  Formato    : Melhor de {config.melhor_de} sets")
    ambiente = "Indoor" if config.indoor else "Outdoor"
    print(f"  Ambiente   : {ambiente} | Clima: {config.clima.capitalize()}")
    print(
        f"  Condições  : Vento {config.vento} km/h | Umidade {config.umidade}% | Altitude {config.altitude_m}m"
    )
    if config.melhor_de == 5:
        print("  Tiebreak   : Super-tiebreak no 5º set (10 pts)")
    print()
    print(f"{linha}")
    print()
    safe_input("  Pressione Enter para iniciar...")


def exibir_cabecalho_game(
    jogador,
    adversario,
    games,
    sets,
    sacador_atual,
    config,
    contexto_partida,
    modo_atual,
    resultado_sets=None,
    stamina_ref_j: float = None,
    stamina_ref_a: float = None,
):
    clear_screen()
    superficie = normalizar_superficie(config.superficie)
    sacando_j = sacador_atual == "j"

    # Suporte flexível para objeto ou dicionário
    nome_j = (
        jogador.nome
        if hasattr(jogador, "nome")
        else (jogador.get("nome") if isinstance(jogador, dict) else str(jogador))
    )
    nome_a = (
        adversario.get("nome")
        if isinstance(adversario, dict)
        else (adversario.nome if hasattr(adversario, "nome") else str(adversario))
    )

    linha = "=" * 54
    print(f"\n{linha}")
    if config.nome_torneio:
        tipo = f"  •  {config.tipo_torneio}" if config.tipo_torneio else ""
        print_blue(f"{config.nome_torneio + tipo:^54}")
    print(
        f"  Superfície: {superficie.capitalize():<12} Modo: {modo_atual.name.capitalize()}"
    )
    print(f"{linha}")
    if resultado_sets:
        sets_str = "  ".join(f"{sj}-{sa}" for sj, sa in resultado_sets)
        print(f"  Sets anteriores: {sets_str}")
    sj_str = f"{'* ' if sacando_j else '  '}{nome_j}"
    sa_str = f"{'* ' if not sacando_j else '  '}{nome_a}"
    print(f"  {sj_str:<35} {games['j']}")
    print(f"  {sa_str:<35} {games['a']}")
    print()
    delta_j = (
        contexto_partida.stamina_j - stamina_ref_j
        if stamina_ref_j is not None
        else None
    )
    delta_a = (
        contexto_partida.stamina_a - stamina_ref_a
        if stamina_ref_a is not None
        else None
    )
    print(f"  {nome_j:<25} {barra_stamina(contexto_partida.stamina_j, delta=delta_j)}")
    print(f"  {nome_a:<25} {barra_stamina(contexto_partida.stamina_a, delta=delta_a)}")
    # Alerta crítico quando stamina < 35% (estilo FIFA)
    criticos = []
    if contexto_partida.stamina_j < 35:
        criticos.append(nome_j)
    if contexto_partida.stamina_a < 35:
        criticos.append(nome_a)
    if criticos:
        alerta = " e ".join(c[:18] for c in criticos)
        print(f"  {Fore.RED}⚠  {alerta}: no limite físico!{Style.RESET_ALL}")
    print(f"{linha}")
