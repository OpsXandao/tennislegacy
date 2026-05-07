import random

from src.dados import carregar_ranking, get_caminho_ranking_save
from src.duplas import fundir_dupla
from src.jogar_partida import jogar_partida, criar_config_partida
from src.log_jogo import log_erro
from src.io_utils import (
    safe_input,
    clear_screen,
    print_blue,
    print_yellow,
    print_green,
    print_red,
    print_magenta,
)


def evento_convite_duplas(jogador_inst, nome_save):
    """Gera um evento aleatório onde o jogador é convidado para um torneio exibição de duplas."""
    chance = 0.05 + (getattr(jogador_inst, "reputacao_imprensa", 50) / 1000)
    if random.random() > chance:
        return False

    clear_screen()
    print_magenta("\n--- 📩 MENSAGEM RECEBIDA ---")

    mista = random.random() > 0.5
    genero_alvo = (
        "feminino"
        if mista and jogador_inst.genero == "masculino"
        else jogador_inst.genero
    )
    if mista and jogador_inst.genero == "feminino":
        genero_alvo = "masculino"

    caminho_rk = get_caminho_ranking_save(nome_save, genero=genero_alvo)
    try:
        ranking_parceiros = carregar_ranking(caminho_rk)
        parceiro = random.choice(ranking_parceiros[:50])
    except Exception as e:
        log_erro(
            nome_save,
            "evento_convite_duplas_carregar_ranking",
            e,
            {"caminho_rk": caminho_rk, "genero_alvo": genero_alvo},
        )
        return False

    tipo_dupla = "Duplas Mistas" if mista else "Duplas"
    print_blue(f"\n📱 {parceiro['nome']} te enviou uma mensagem:")
    print(
        f'"E aí, {jogador_inst.nome}! Vai rolar um torneio exibição de {tipo_dupla} neste fim de semana.'
    )
    print(' Estou precisando de uma dupla que cubra bem a rede. Topa jogar comigo?"')
    print()
    print_yellow(
        f"Parceiro(a): {parceiro['nome']} ({parceiro['nacionalidade']}) | Overall: {parceiro.get('overall', '?')}"
    )
    print("Prêmio: Experiência e grana extra.")
    print()

    if safe_input("Aceitar convite? (s/n): ").lower() == "s":
        _jogar_exibicao_duplas(
            jogador_inst, parceiro, ranking_parceiros, tipo_dupla, nome_save
        )
        return True

    print("Você recusou o convite.")
    safe_input("Pressione Enter para continuar...")
    return False


def _jogar_exibicao_duplas(jogador, parceiro, ranking_bots, tipo_dupla, nome_save):
    clear_screen()
    print_green(f"\n🎉 Você formou dupla com {parceiro['nome']}!")

    equipe_jogador = fundir_dupla(jogador, parceiro)

    print_blue("\n--- 🎾 Atributos da sua Dupla ---")
    print(f"Sinergia de Voleio: {equipe_jogador['atributos']['voleio']}")
    print(f"Sinergia de Saque: {equipe_jogador['atributos']['saque']}")
    print(f"Sinergia Geral (Overall): {equipe_jogador['overall']}")
    safe_input("\nPressione Enter para ir à quadra...")

    pool_adversarios = ranking_bots[30:] if len(ranking_bots) > 32 else ranking_bots
    bots = random.sample(pool_adversarios, min(2, len(pool_adversarios)))
    if len(bots) < 2:
        if len(ranking_bots) < 2:
            print("Não há jogadores suficientes para o jogo de exibição.")
            return
        bots = random.sample(ranking_bots, 2)
    equipe_adversaria = fundir_dupla(bots[0], bots[1])

    print_yellow(f"\n🔥 PARTIDA DE EXIBIÇÃO: {tipo_dupla.upper()} 🔥")
    print(f"{equipe_jogador['nome']} VS {equipe_adversaria['nome']}")
    safe_input("Pressione Enter para começar a partida...")

    info_exibicao = {
        "nome": f"Exibição de {tipo_dupla}",
        "tipo": "ATP 250",
        "quadra": "dura",
    }
    config = criar_config_partida(info_exibicao)
    vencedor, perdedor, placar = jogar_partida(
        equipe_jogador, equipe_adversaria, nome_save, config=config
    )

    clear_screen()
    print_magenta("\n--- 🏁 FIM DA EXIBIÇÃO ---")
    print(f"Placar: {placar}")

    if vencedor["nome"] == equipe_jogador["nome"]:
        premio = random.randint(1500, 5000)
        xp = 75
        print_green(f"\n🏆 INCRÍVEL! Vocês venceram o desafio de {tipo_dupla}!")
        print_green(f"💰 Prêmio: ${premio}")
        print_green(f"✨ XP: {xp}")
        jogador.xp += xp
        if hasattr(jogador, "registrar_transacao"):
            jogador.registrar_transacao(
                premio, f"Campeão Exibição de {tipo_dupla}", "premiacao"
            )
        else:
            jogador.dinheiro += premio
        if hasattr(jogador, "reputacao_imprensa"):
            jogador.reputacao_imprensa = min(100, jogador.reputacao_imprensa + 5)
    else:
        print_red("\n❌ Vocês perderam. A falta de entrosamento pesou.")
        print("Mas foi um bom treino (+25 XP).")
        jogador.xp += 25

    safe_input("\nPressione Enter para voltar ao calendário...")
