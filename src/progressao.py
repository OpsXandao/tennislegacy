import random

# --- Constantes de Progressão e Fadiga ---
XP_VITORIA = 50
XP_DERROTA = 20
FADIGA_POR_PONTO = 0.1
CHANCE_LESAO_THRESHOLD = 80  # Acima desta fadiga, há risco de lesão
CHANCE_LESAO_PROB = 0.2     # 20% de chance de lesão se acima do threshold
ENERGIA_RECUP_BASE = 10
ENERGIA_RECUP_POR_FISICO = 0.4

def handle_xp_e_level_up(jogador, vitoria):
    """
    Adiciona XP ao jogador com base no resultado da partida e verifica se ele subiu de nível.
    """
    xp_ganho = XP_VITORIA if vitoria else XP_DERROTA
    jogador.xp += xp_ganho
    print(f"\n✨ Você ganhou {xp_ganho} de XP!")

    # Verifica se o jogador subiu de nível
    while jogador.xp >= jogador.xp_para_proximo_nivel:
        jogador.nivel += 1
        jogador.pontos_de_skill += 1
        
        # Aumenta o XP necessário para o próximo nível
        xp_excedente = jogador.xp - jogador.xp_para_proximo_nivel
        jogador.xp_para_proximo_nivel = int(jogador.xp_para_proximo_nivel * 1.5)
        jogador.xp = xp_excedente

        print(f"🎉 LEVEL UP! Você alcançou o Nível {jogador.nivel}.")
        print(f"Você ganhou 1 Ponto de Skill! Você tem {jogador.pontos_de_skill} ponto(s) para usar.")
        
    return jogador

def handle_fadiga_e_lesao(jogador, pontos_disputados=None):
    """
    Aumenta a fadiga do jogador após uma partida e verifica a ocorrência de lesões.
    """
    if pontos_disputados is None:
        pontos_disputados = 0
    aumento = int(round(pontos_disputados * FADIGA_POR_PONTO))
    jogador.fadiga = min(100, jogador.fadiga + aumento)
    print(f"🥵 Sua fadiga aumentou para {jogador.fadiga}%.")

    # Verifica se há risco de lesão
    if jogador.fadiga > CHANCE_LESAO_THRESHOLD:
        print(f"⚠️ Sua fadiga está muito alta ({jogador.fadiga}%)! Há risco de lesão...")
        if random.random() < CHANCE_LESAO_PROB:
            semanas_lesionado = random.randint(2, 5)
            jogador.status_lesao["lesionado"] = True
            jogador.status_lesao["semanas_restantes"] = semanas_lesionado
            print(f"🚨 LESÃO! Você se lesionou e ficará fora por {semanas_lesionado} semanas.")
    
    return jogador

def recuperar_energia_entre_rodadas(jogador):
    fisico = jogador.atributos.get("fisico", 50)
    recuperacao = int(round(ENERGIA_RECUP_BASE + fisico * ENERGIA_RECUP_POR_FISICO))
    energia_antes = jogador.energia
    jogador.energia = min(100, jogador.energia + recuperacao)
    print(f"😌 Energia recuperada para a próxima rodada: {energia_antes}% -> {jogador.energia}%.")
    return jogador
