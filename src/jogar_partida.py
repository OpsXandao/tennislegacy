import random
from dataclasses import dataclass
from typing import Optional

from src.io_utils import safe_input
from src.simulacao_partida import (
    ModoSimulacao,
    TipoSaque,
    ContextoPonto,
    ContextoPartida,
    SimuladorPonto,
    EstatisticasPartida,
    EstrategiaAtaque,
    EstrategiaDefesa,
    normalizar_superficie,
)


@dataclass
class ConfigPartida:
    superficie: str = "dura"
    melhor_de: int = 3
    tiebreak_decisivo_pontos: int = 7
    nome_torneio: Optional[str] = None
    tipo_torneio: Optional[str] = None


def criar_config_partida(info_torneio: Optional[dict]) -> ConfigPartida:
    if not info_torneio:
        return ConfigPartida()
    tipo = info_torneio.get("tipo", "")
    superficie = info_torneio.get("quadra", "dura")
    melhor_de = 5 if tipo.strip().lower() == "grand slam" else 3
    tiebreak_decisivo = 10 if melhor_de == 5 else 7
    return ConfigPartida(
        superficie=superficie,
        melhor_de=melhor_de,
        tiebreak_decisivo_pontos=tiebreak_decisivo,
        nome_torneio=info_torneio.get("nome"),
        tipo_torneio=tipo,
    )


def escolher_modo_simulacao():
    """Permite ao usuário escolher o modo de simulação da partida."""
    print("\nEscolha o modo de simulacao:")
    print("1. Rapido (comportamento classico)")
    print("2. Detalhado (descricao ponto a ponto)")
    escolha = safe_input("Escolha (1 ou 2): ").strip()
    if escolha == "2":
        return ModoSimulacao.DETALHADO
    return ModoSimulacao.RAPIDO


def escolher_tipo_saque():
    """Permite ao usuário escolher o tipo de saque no modo detalhado."""
    print("\nTipo de saque:")
    print("1. Agressivo (mais aces, mais faltas)")
    print("2. Seguro (menos faltas, menos aces)")
    print("3. Variado (equilibrado)")
    escolha = safe_input("Escolha (1, 2 ou 3): ").strip()
    if escolha == "1":
        return TipoSaque.AGRESSIVO
    elif escolha == "2":
        return TipoSaque.SEGURO
    return TipoSaque.VARIADO


def escolher_estrategias():
    """
    Permite ao usuário escolher estratégias de ataque e defesa.

    Returns:
        dict com chaves 'ataque' e 'defesa' contendo os enums correspondentes
    """
    print("\n" + "="*45)
    print("       ESCOLHA SUA ESTRATEGIA")
    print("="*45)

    # Estratégia de ataque
    print("\n=== ESTRATEGIA DE ATAQUE ===")
    print("[1] Agressivo na rede - Subir a rede apos golpes fortes")
    print("[2] Fundo de quadra - Winners do baseline")
    print("[3] Variado - Alternar padroes")

    escolha_ataque = safe_input("Escolha (1, 2 ou 3): ").strip()
    if escolha_ataque == "1":
        ataque = EstrategiaAtaque.REDE
    elif escolha_ataque == "3":
        ataque = EstrategiaAtaque.VARIADO
    else:
        ataque = EstrategiaAtaque.FUNDO

    # Estratégia de defesa
    print("\n=== ESTRATEGIA DE DEFESA ===")
    print("[1] Contra-ataque - Virar com winners")
    print("[2] Consistencia - Bolas altas, esperar erro")
    print("[3] Neutralizar - Slice para resetar")

    escolha_defesa = safe_input("Escolha (1, 2 ou 3): ").strip()
    if escolha_defesa == "1":
        defesa = EstrategiaDefesa.CONTRA_ATAQUE
    elif escolha_defesa == "3":
        defesa = EstrategiaDefesa.NEUTRALIZAR
    else:
        defesa = EstrategiaDefesa.CONSISTENCIA

    # Converte para formato compatível com o código existente
    estilo_map = {
        EstrategiaAtaque.REDE: "atacar_na_rede",
        EstrategiaAtaque.FUNDO: "atacar_do_fundo",
        EstrategiaAtaque.VARIADO: "atacar_pelo_meio",
    }

    return {
        "ataque": ataque,
        "defesa": defesa,
        "estilo": estilo_map[ataque],  # Compatibilidade com código existente
    }


def verificar_abandono():
    """Verifica se o jogador quer abandonar a partida."""
    confirmar = safe_input("Tem certeza que deseja abandonar? (s/n): ").strip().lower()
    return confirmar == "s"


def atualizar_estatisticas(stats_j: EstatisticasPartida, stats_a: EstatisticasPartida,
                          vencedor: str, stats_info: dict, contexto: ContextoPonto):
    """Atualiza estatísticas baseado no resultado do ponto."""
    sacador = stats_info.get("sacador", contexto.sacador)

    # Estatísticas do sacador
    if sacador == "j":
        stats_sacador = stats_j
        stats_receptor = stats_a
    else:
        stats_sacador = stats_a
        stats_receptor = stats_j

    # Primeiro saque
    stats_sacador.primeiro_saque_total += 1
    if stats_info.get("primeiro_saque_in"):
        stats_sacador.primeiro_saque_in += 1

    # Aces e duplas faltas
    if stats_info.get("ace"):
        stats_sacador.aces += 1
    if stats_info.get("dupla_falta"):
        stats_sacador.duplas_faltas += 1

    # Winners e erros não forçados
    if vencedor == "j":
        if stats_info.get("winner"):
            stats_j.winners += 1
        if stats_info.get("erro_nao_forcado"):
            stats_a.erros_nao_forcados += 1
    else:
        if stats_info.get("winner"):
            stats_a.winners += 1
        if stats_info.get("erro_nao_forcado"):
            stats_j.erros_nao_forcados += 1

    # Pontos no saque/devolução
    if sacador == "j":
        stats_j.pontos_total_saque += 1
        stats_a.pontos_total_devolucao += 1
        if vencedor == "j":
            stats_j.pontos_ganhos_saque += 1
        else:
            stats_a.pontos_ganhos_devolucao += 1
    else:
        stats_a.pontos_total_saque += 1
        stats_j.pontos_total_devolucao += 1
        if vencedor == "a":
            stats_a.pontos_ganhos_saque += 1
        else:
            stats_j.pontos_ganhos_devolucao += 1

    # Break points
    if contexto.is_break_point():
        if sacador == "j":
            # Adversário tem break point contra jogador
            stats_a.break_points_total += 1
            stats_j.break_points_enfrentados += 1
            if vencedor == "a":
                stats_a.break_points_convertidos += 1
            else:
                stats_j.break_points_salvos += 1
        else:
            # Jogador tem break point contra adversário
            stats_j.break_points_total += 1
            stats_a.break_points_enfrentados += 1
            if vencedor == "j":
                stats_j.break_points_convertidos += 1
            else:
                stats_a.break_points_salvos += 1


def menu_entre_games(jogador, adversario, placar_set, placar_partida,
                     stats_j: EstatisticasPartida, stats_a: EstatisticasPartida,
                     estrategias: dict, contexto_partida: ContextoPartida):
    """
    Menu exibido após cada game no modo detalhado.

    Returns:
        - estrategias: se continuar normalmente
        - dict novo: se mudou estratégia
        - "SIMULAR_SET": se escolheu simular resto do set
        - "ABANDONAR": se escolheu abandonar
    """
    print(f"\n{'='*45}")
    print(f"  Set: {placar_set[0]}-{placar_set[1]} | Partida: {placar_partida[0]}-{placar_partida[1]}")
    print(f"  Stamina: {contexto_partida.stamina_j:.0f}% vs {contexto_partida.stamina_a:.0f}% | Momento: {contexto_partida.momentum_j}-{contexto_partida.momentum_a}")
    print(f"{'='*45}")
    print("[Enter] Continuar")
    print("[e] Ver Estatisticas")
    print("[t] Mudar Estrategia")
    print("[s] Simular resto do set")
    print("[q] Abandonar")

    escolha = safe_input("> ").strip().lower()

    if escolha == "e":
        stats_j.exibir(jogador.nome, adversario['nome'], stats_a)
        safe_input("\nPressione Enter para continuar...")
        return estrategias
    elif escolha == "t":
        return escolher_estrategias()
    elif escolha == "s":
        return "SIMULAR_SET"
    elif escolha == "q":
        if verificar_abandono():
            return "ABANDONAR"

    return estrategias


def exibir_estatisticas_set(jogador, adversario, games_j, games_a,
                            stats_j: EstatisticasPartida, stats_a: EstatisticasPartida,
                            num_set: int):
    """Exibe estatísticas completas ao final de cada set."""
    print(f"\n{'='*55}")
    print(f"       FIM DO {num_set}o SET: {jogador.nome} {games_j} x {games_a} {adversario['nome']}")
    print(f"{'='*55}")

    stats_j.exibir(jogador.nome, adversario['nome'], stats_a)

    safe_input("\nPressione Enter para continuar...")


STAMINA_CUSTO_BASE = {
    "curto": 0.35,
    "medio": 0.65,
    "longo": 0.95,
}

SUPERFICIE_FADIGA = {
    "dura": 1.0,
    "saibro": 1.12,
    "grama": 0.9,
}


def _placar_pontos_txt(ponto):
    return {0: "0", 1: "15", 2: "30", 3: "40", 4: "AD"}.get(ponto, "40")


def _atualizar_momentum(contexto_partida: ContextoPartida, vencedor: str):
    if vencedor == "j":
        contexto_partida.momentum_j = min(3, contexto_partida.momentum_j + 1)
        contexto_partida.momentum_a = max(0, contexto_partida.momentum_a - 1)
    else:
        contexto_partida.momentum_a = min(3, contexto_partida.momentum_a + 1)
        contexto_partida.momentum_j = max(0, contexto_partida.momentum_j - 1)


def _aplicar_custo_stamina(contexto_partida: ContextoPartida, stats_info: dict):
    intensidade = stats_info.get("intensidade", "medio")
    base = STAMINA_CUSTO_BASE.get(intensidade, STAMINA_CUSTO_BASE["medio"])
    superficie = normalizar_superficie(contexto_partida.superficie)
    fator = SUPERFICIE_FADIGA.get(superficie, 1.0)
    custo = base * fator
    contexto_partida.stamina_j = max(0.0, contexto_partida.stamina_j - custo)
    contexto_partida.stamina_a = max(0.0, contexto_partida.stamina_a - custo)


def _exibir_cabecalho_game(jogador, adversario, games, sets, sacador_atual, config, contexto_partida):
    superficie = normalizar_superficie(config.superficie)
    nome_sacador = jogador.nome if sacador_atual == "j" else adversario["nome"]
    titulo_torneio = ""
    if config.nome_torneio:
        tipo = f" | {config.tipo_torneio}" if config.tipo_torneio else ""
        titulo_torneio = f"{config.nome_torneio}{tipo}"
    print(f"\n{'='*52}")
    if titulo_torneio:
        print(f"{titulo_torneio:^52}")
    print(f"Superficie: {superficie.capitalize()} | Saque: {nome_sacador}")
    print(f"Set: {jogador.nome} {games['j']} x {games['a']} {adversario['nome']}")
    print(f"Partida: {sets['j']} - {sets['a']} | Stamina: {contexto_partida.stamina_j:.0f}% vs {contexto_partida.stamina_a:.0f}%")
    print(f"{'='*52}")


def _alvo_tiebreak(sets: dict, sets_para_vencer: int, config: ConfigPartida) -> int:
    if sets["j"] == sets_para_vencer - 1 and sets["a"] == sets_para_vencer - 1:
        return config.tiebreak_decisivo_pontos
    return 7


def _definir_estrategia_auto(jogador, superficie: str) -> dict:
    atributos = jogador.atributos if hasattr(jogador, "atributos") else jogador.get("atributos", {})
    saque = atributos.get("saque", 50)
    voleio = atributos.get("voleio", 50)
    slice_ = atributos.get("slice", 50)
    forehand = atributos.get("forehand", 50)
    backhand = atributos.get("backhand", 50)
    topspin = atributos.get("topspin", 50)
    movimento = atributos.get("movimento", 50)
    winner = atributos.get("winner", 50)

    superficie = normalizar_superficie(superficie)
    rede_score = saque * 0.4 + voleio * 0.4 + slice_ * 0.2
    fundo_score = forehand * 0.35 + backhand * 0.35 + topspin * 0.3
    variado_score = movimento * 0.4 + winner * 0.3 + saque * 0.3

    if superficie == "grama":
        rede_score *= 1.1
    elif superficie == "saibro":
        fundo_score *= 1.1

    if rede_score >= fundo_score and rede_score >= variado_score:
        estilo = "atacar_na_rede"
    elif fundo_score >= variado_score:
        estilo = "atacar_do_fundo"
    else:
        estilo = "atacar_pelo_meio"

    return {"estilo": estilo}


def simular_game_rapido(jogador, adversario, estrategia, sacador, placar_set, placar_partida,
                        simulador: SimuladorPonto, contexto_partida: ContextoPartida,
                        estrategia_adversario: dict,
                        stats_j: EstatisticasPartida = None, stats_a: EstatisticasPartida = None,
                        silencioso: bool = False, sets_para_vencer: int = 2):
    """Simula um game completo no modo rápido."""
    pontos = {"j": 0, "a": 0}
    vantagem = None
    historico = []

    while True:
        contexto = ContextoPonto(
            sacador=sacador,
            placar_game=(pontos["j"], pontos["a"]),
            placar_set=placar_set,
            placar_partida=placar_partida,
            sets_para_vencer=sets_para_vencer,
        )

        vencedor, stats_info = simulador.simular_ponto_rapido(
            estrategia, contexto, contexto_partida, estrategia_adversario
        )
        historico.append(vencedor)
        _aplicar_custo_stamina(contexto_partida, stats_info)
        _atualizar_momentum(contexto_partida, vencedor)

        # Atualiza estatísticas se fornecidas
        if stats_j is not None and stats_a is not None:
            atualizar_estatisticas(stats_j, stats_a, vencedor, stats_info, contexto)

        if pontos["j"] >= 3 and pontos["a"] >= 3:
            if vantagem is None:
                if pontos["j"] == pontos["a"]:
                    if not silencioso:
                        print("Deuce!")
                    vantagem = vencedor
                    if not silencioso:
                        print(f"Advantage {jogador.nome if vencedor == 'j' else adversario['nome']}")
                else:
                    vantagem = vencedor
                    if not silencioso:
                        print(f"Advantage {jogador.nome if vencedor == 'j' else adversario['nome']}")
            else:
                if vencedor == vantagem:
                    return vencedor, historico, False
                else:
                    vantagem = None
                    if not silencioso:
                        print("Deuce!")
        else:
            pontos[vencedor] += 1
            if pontos[vencedor] >= 4 and abs(pontos["j"] - pontos["a"]) >= 2:
                return vencedor, historico, False
            if not silencioso:
                print(f"Placar: {jogador.nome} {_placar_pontos_txt(pontos['j'])} x {_placar_pontos_txt(pontos['a'])} {adversario['nome']}")


def simular_game_detalhado(jogador, adversario, estrategia, sacador, placar_set, placar_partida,
                           simulador: SimuladorPonto, contexto_partida: ContextoPartida,
                           estrategia_adversario: dict,
                           stats_j: EstatisticasPartida = None, stats_a: EstatisticasPartida = None,
                           sets_para_vencer: int = 2):
    """Simula um game completo no modo detalhado com descrições."""
    pontos = {"j": 0, "a": 0}
    vantagem = None
    historico = []

    # Escolhe tipo de saque se jogador está sacando
    tipo_saque = None
    if sacador == "j":
        tipo_saque = escolher_tipo_saque()

    while True:
        contexto = ContextoPonto(
            sacador=sacador,
            placar_game=(pontos["j"], pontos["a"]),
            placar_set=placar_set,
            placar_partida=placar_partida,
            sets_para_vencer=sets_para_vencer,
        )

        # Mostra indicadores de momento importante
        if contexto.is_match_point():
            print("\n*** MATCH POINT! ***")
        elif contexto.is_set_point():
            print("\n*** SET POINT! ***")
        elif contexto.is_break_point():
            print("\n*** BREAK POINT! ***")

        # Simula o ponto
        vencedor, descricoes, stats_info = simulador.simular_ponto_detalhado(
            estrategia, contexto, tipo_saque, contexto_partida, estrategia_adversario
        )
        historico.append(vencedor)
        _aplicar_custo_stamina(contexto_partida, stats_info)
        _atualizar_momentum(contexto_partida, vencedor)

        # Atualiza estatísticas se fornecidas
        if stats_j is not None and stats_a is not None:
            atualizar_estatisticas(stats_j, stats_a, vencedor, stats_info, contexto)

        # Mostra descrições
        for desc in descricoes:
            print(desc)

        if pontos["j"] >= 3 and pontos["a"] >= 3:
            if vantagem is None:
                if pontos["j"] == pontos["a"]:
                    print("Deuce!")
                    vantagem = vencedor
                    nome_vantagem = jogador.nome if vencedor == 'j' else adversario['nome']
                    print(f"Advantage {nome_vantagem}")
                else:
                    vantagem = vencedor
                    nome_vantagem = jogador.nome if vencedor == 'j' else adversario['nome']
                    print(f"Advantage {nome_vantagem}")
            else:
                if vencedor == vantagem:
                    nome_vencedor = jogador.nome if vencedor == 'j' else adversario['nome']
                    print(f"Game para {nome_vencedor}!")
                    return vencedor, historico, False
                else:
                    vantagem = None
                    print("Deuce!")
        else:
            pontos[vencedor] += 1
            print(f"Placar: {jogador.nome} {_placar_pontos_txt(pontos['j'])} x {_placar_pontos_txt(pontos['a'])} {adversario['nome']}")

            if pontos[vencedor] >= 4 and abs(pontos["j"] - pontos["a"]) >= 2:
                nome_vencedor = jogador.nome if vencedor == 'j' else adversario['nome']
                print(f"Game para {nome_vencedor}!")
                return vencedor, historico, False

        # Opção de abandonar ou continuar
        print()
        entrada = safe_input("[Enter] Continuar | [q] Abandonar: ").strip().lower()
        if entrada == "q":
            if verificar_abandono():
                return "abandono", historico, True


def simular_resto_do_set(jogador, adversario, games: dict, sacador_atual: str,
                         estrategias: dict, stats_j: EstatisticasPartida,
                         stats_a: EstatisticasPartida, placar_partida: tuple,
                         simulador: SimuladorPonto, contexto_partida: ContextoPartida,
                         config: ConfigPartida, sets_para_vencer: int,
                         estrategia_adversario: dict):
    """
    Simula todos os games restantes do set atual no modo rápido.

    Returns:
        (games, sacador_atual, stats_j, stats_a)
    """
    print("\nSimulando resto do set...")

    while True:
        placar_set = (games["j"], games["a"])

        # Simula game no modo rápido (silencioso)
        vencedor, historico, _ = simular_game_rapido(
            jogador, adversario, estrategias, sacador_atual,
            placar_set, placar_partida, simulador, contexto_partida, estrategia_adversario,
            stats_j, stats_a, silencioso=True
        )

        games[vencedor] += 1
        sacador_atual = "a" if sacador_atual == "j" else "j"

        # Mostra progresso
        print(f"  {jogador.nome} {games['j']} x {games['a']} {adversario['nome']}")

        # Verifica fim do set
        if (games["j"] >= 6 or games["a"] >= 6) and abs(games["j"] - games["a"]) >= 2:
            break

        # Tiebreak
        if games["j"] == 6 and games["a"] == 6:
            print("  Tiebreak!")
            sets_dict = {"j": placar_partida[0], "a": placar_partida[1]}
            alvo = _alvo_tiebreak(sets_dict, sets_para_vencer, config)
            vencedor_tb, _, _ = simular_tiebreak(
                jogador, adversario, estrategias, sacador_atual,
                placar_partida, simulador, contexto_partida,
                stats_j, stats_a, alvo, silencioso=True, sets_para_vencer=sets_para_vencer,
                estrategia_adversario=estrategia_adversario
            )
            games[vencedor_tb] += 1
            sacador_atual = "a" if sacador_atual == "j" else "j"
            print(f"  Tiebreak: {jogador.nome} {games['j']} x {games['a']} {adversario['nome']}")
            break

    print("Simulacao do set concluida!")
    return games, sacador_atual, stats_j, stats_a


def _sacador_tiebreak(sacador_inicial: str, indice_ponto: int) -> str:
    if indice_ponto == 0:
        return sacador_inicial
    bloco = (indice_ponto - 1) // 2
    if bloco % 2 == 0:
        return "a" if sacador_inicial == "j" else "j"
    return sacador_inicial


def simular_tiebreak(jogador, adversario, estrategia, sacador_inicial: str,
                     placar_partida: tuple, simulador: SimuladorPonto,
                     contexto_partida: ContextoPartida,
                     stats_j: EstatisticasPartida, stats_a: EstatisticasPartida,
                     alvo_pontos: int, silencioso: bool = False,
                     detalhado: bool = False, sets_para_vencer: int = 2,
                     estrategia_adversario: dict = None):
    pontos = {"j": 0, "a": 0}
    historico = []

    while True:
        idx = pontos["j"] + pontos["a"]
        sacador = _sacador_tiebreak(sacador_inicial, idx)
        contexto = ContextoPonto(
            sacador=sacador,
            placar_game=(pontos["j"], pontos["a"]),
            placar_set=(6, 6),
            placar_partida=placar_partida,
            sets_para_vencer=sets_para_vencer,
            is_tiebreak=True,
        )

        if detalhado:
            vencedor, descricoes, stats_info = simulador.simular_ponto_detalhado(
                estrategia, contexto, None, contexto_partida, estrategia_adversario
            )
            for desc in descricoes:
                if not silencioso:
                    print(desc)
        else:
            vencedor, stats_info = simulador.simular_ponto_rapido(
                estrategia, contexto, contexto_partida, estrategia_adversario
            )

        historico.append(vencedor)
        _aplicar_custo_stamina(contexto_partida, stats_info)
        _atualizar_momentum(contexto_partida, vencedor)

        if stats_j is not None and stats_a is not None:
            atualizar_estatisticas(stats_j, stats_a, vencedor, stats_info, contexto)

        pontos[vencedor] += 1
        if not silencioso:
            print(f"Tiebreak: {jogador.nome} {pontos['j']} x {pontos['a']} {adversario['nome']}")

        if (pontos["j"] >= alvo_pontos or pontos["a"] >= alvo_pontos) and abs(pontos["j"] - pontos["a"]) >= 2:
            return ("j" if pontos["j"] > pontos["a"] else "a"), historico, False


def jogar_partida(jogador, adversario, nome_save, config: Optional[ConfigPartida] = None):
    config = config or ConfigPartida()
    config.superficie = normalizar_superficie(config.superficie)
    sets_para_vencer = config.melhor_de // 2 + 1

    print(f"\nIniciando partida entre {jogador.nome} e {adversario['nome']}")
    if config.nome_torneio:
        tipo_str = f" | {config.tipo_torneio}" if config.tipo_torneio else ""
        print(f"Torneio: {config.nome_torneio}{tipo_str}")
    print(f"Formato: Melhor de {config.melhor_de} | Superficie: {config.superficie}")

    modo = escolher_modo_simulacao()
    estrategias = escolher_estrategias()
    estrategia_adversario = _definir_estrategia_auto(adversario, config.superficie)

    sets = {"j": 0, "a": 0}
    resultado = []

    stats_total_j = EstatisticasPartida()
    stats_total_a = EstatisticasPartida()

    sacador_inicial = random.choice(["j", "a"])
    sacador_atual = sacador_inicial

    stamina_inicial = getattr(jogador, "energia", 100)
    contexto_partida = ContextoPartida(
        superficie=config.superficie,
        stamina_j=float(stamina_inicial),
        stamina_a=100.0,
    )
    simulador = SimuladorPonto(jogador, adversario)

    while sets["j"] < sets_para_vencer and sets["a"] < sets_para_vencer:
        games = {"j": 0, "a": 0}

        stats_set_j = EstatisticasPartida()
        stats_set_a = EstatisticasPartida()

        while True:
            _exibir_cabecalho_game(jogador, adversario, games, sets, sacador_atual, config, contexto_partida)

            placar_set = (games["j"], games["a"])
            placar_partida = (sets["j"], sets["a"])

            if modo == ModoSimulacao.DETALHADO:
                vencedor, historico, abandonou = simular_game_detalhado(
                    jogador, adversario, estrategias, sacador_atual,
                    placar_set, placar_partida, simulador, contexto_partida,
                    estrategia_adversario,
                    stats_set_j, stats_set_a, sets_para_vencer=sets_para_vencer
                )
            else:
                vencedor, historico, abandonou = simular_game_rapido(
                    jogador, adversario, estrategias, sacador_atual,
                    placar_set, placar_partida, simulador, contexto_partida,
                    estrategia_adversario,
                    stats_set_j, stats_set_a, sets_para_vencer=sets_para_vencer
                )

            if abandonou:
                print(f"\n{jogador.nome} abandonou a partida!")
                print(f"Vitoria por W.O. para {adversario['nome']}")
                return adversario['nome'], f"{adversario['nome']} venceu por W.O."

            games[vencedor] += 1
            sacador_atual = "a" if sacador_atual == "j" else "j"

            if modo == ModoSimulacao.DETALHADO:
                resultado_menu = menu_entre_games(
                    jogador, adversario,
                    (games["j"], games["a"]),
                    (sets["j"], sets["a"]),
                    stats_set_j, stats_set_a, estrategias, contexto_partida
                )

                if resultado_menu == "ABANDONAR":
                    print(f"\n{jogador.nome} abandonou a partida!")
                    print(f"Vitoria por W.O. para {adversario['nome']}")
                    return adversario['nome'], f"{adversario['nome']} venceu por W.O."
                elif resultado_menu == "SIMULAR_SET":
                    games, sacador_atual, stats_set_j, stats_set_a = simular_resto_do_set(
                        jogador, adversario, games, sacador_atual, estrategias,
                        stats_set_j, stats_set_a, (sets["j"], sets["a"]),
                        simulador, contexto_partida, config, sets_para_vencer,
                        estrategia_adversario
                    )
                    break
                elif isinstance(resultado_menu, dict):
                    estrategias = resultado_menu
            else:
                if vencedor == "a":
                    print("Voce perdeu este game.")
                    escolha = safe_input("Deseja mudar a estrategia? (s/n): ").strip().lower()
                    if escolha == "s":
                        estrategias = escolher_estrategias()

            if (games["j"] >= 6 or games["a"] >= 6) and abs(games["j"] - games["a"]) >= 2:
                break

            if games["j"] == 6 and games["a"] == 6:
                alvo_tb = _alvo_tiebreak(sets, sets_para_vencer, config)
                print(f"\nTIEBREAK (ate {alvo_tb})!")
                vencedor_tb, _, abandonou = simular_tiebreak(
                    jogador, adversario, estrategias, sacador_atual,
                    (sets["j"], sets["a"]), simulador, contexto_partida,
                    stats_set_j, stats_set_a, alvo_tb,
                    silencioso=False, detalhado=(modo == ModoSimulacao.DETALHADO),
                    sets_para_vencer=sets_para_vencer, estrategia_adversario=estrategia_adversario
                )

                if abandonou:
                    print(f"\n{jogador.nome} abandonou a partida!")
                    print(f"Vitoria por W.O. para {adversario['nome']}")
                    return adversario['nome'], f"{adversario['nome']} venceu por W.O."

                games[vencedor_tb] += 1
                sacador_atual = "a" if sacador_atual == "j" else "j"
                break

        winner = "j" if games["j"] > games["a"] else "a"
        sets[winner] += 1
        resultado.append((games["j"], games["a"]))

        exibir_estatisticas_set(jogador, adversario, games["j"], games["a"],
                               stats_set_j, stats_set_a, len(resultado))

        stats_total_j.merge(stats_set_j)
        stats_total_a.merge(stats_set_a)

    print("\n" + "="*55)
    print("       PARTIDA FINALIZADA!")
    print("="*55)
    print("\nResultado por sets:")
    for idx, (sj, sa) in enumerate(resultado, 1):
        print(f"Set {idx}: {jogador.nome} {sj} x {sa} {adversario['nome']}")

    vencedor_final = jogador.nome if sets["j"] > sets["a"] else adversario["nome"]
    perdedor_final = adversario["nome"] if vencedor_final == jogador.nome else jogador.nome
    placar_final = f"{vencedor_final} {max(sets['j'], sets['a'])} x {min(sets['j'], sets['a'])} {perdedor_final}"

    print(f"\nVencedor da partida: {vencedor_final}")
    print("\n" + "="*55)
    print("       ESTATISTICAS FINAIS DA PARTIDA")
    print("="*55)
    stats_total_j.exibir(jogador.nome, adversario['nome'], stats_total_a)

    if hasattr(jogador, "energia"):
        jogador.energia = max(0, min(100, int(contexto_partida.stamina_j)))

    pontos_disputados = stats_total_j.pontos_total_saque + stats_total_j.pontos_total_devolucao
    return vencedor_final, placar_final, pontos_disputados


def simular_partida_npc(jogador_a: dict, jogador_b: dict, config: Optional[ConfigPartida] = None):
    config = config or ConfigPartida()
    config.superficie = normalizar_superficie(config.superficie)
    sets_para_vencer = config.melhor_de // 2 + 1

    estrategia_a = _definir_estrategia_auto(jogador_a, config.superficie)
    estrategia_b = _definir_estrategia_auto(jogador_b, config.superficie)

    simulador = SimuladorPonto(jogador_a, jogador_b)
    contexto_partida = ContextoPartida(superficie=config.superficie, stamina_j=100.0, stamina_a=100.0)

    sets = {"j": 0, "a": 0}
    sacador_atual = random.choice(["j", "a"])

    while sets["j"] < sets_para_vencer and sets["a"] < sets_para_vencer:
        games = {"j": 0, "a": 0}
        stats_set_j = EstatisticasPartida()
        stats_set_a = EstatisticasPartida()

        while True:
            vencedor, _, _ = simular_game_rapido(
                jogador_a, jogador_b, estrategia_a, sacador_atual,
                (games["j"], games["a"]), (sets["j"], sets["a"]),
                simulador, contexto_partida, estrategia_b,
                stats_set_j, stats_set_a, silencioso=True, sets_para_vencer=sets_para_vencer
            )
            games[vencedor] += 1
            sacador_atual = "a" if sacador_atual == "j" else "j"

            if (games["j"] >= 6 or games["a"] >= 6) and abs(games["j"] - games["a"]) >= 2:
                break

            if games["j"] == 6 and games["a"] == 6:
                alvo_tb = _alvo_tiebreak(sets, sets_para_vencer, config)
                vencedor_tb, _, _ = simular_tiebreak(
                    jogador_a, jogador_b, estrategia_a, sacador_atual,
                    (sets["j"], sets["a"]), simulador, contexto_partida,
                    stats_set_j, stats_set_a, alvo_tb,
                    silencioso=True, detalhado=False, sets_para_vencer=sets_para_vencer,
                    estrategia_adversario=estrategia_b
                )
                games[vencedor_tb] += 1
                sacador_atual = "a" if sacador_atual == "j" else "j"
                break

        winner = "j" if games["j"] > games["a"] else "a"
        sets[winner] += 1

    vencedor_final = jogador_a if sets["j"] > sets["a"] else jogador_b
    perdedor_final = jogador_b if vencedor_final is jogador_a else jogador_a

    def limpar_nome(nome):
        return nome.strip().rstrip("0123456789").strip()

    nome_vencedor = limpar_nome(vencedor_final["nome"])
    nome_perdedor = limpar_nome(perdedor_final["nome"])
    placar_final = f"{nome_vencedor} {max(sets['j'], sets['a'])} x {min(sets['j'], sets['a'])} {nome_perdedor}"

    return vencedor_final, perdedor_final, placar_final
