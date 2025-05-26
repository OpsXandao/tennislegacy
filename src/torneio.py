import random

class TorneioATP250:
    def __init__(self, semana, jogador_nome, jogador_nacionalidade, ranking):
        self.semana = semana
        self.jogador_nome = jogador_nome
        self.jogador_nacionalidade = jogador_nacionalidade
        self.ranking = ranking

    def _buscar_instancia_jogador(self):
        import builtins
        return builtins.jogador  # para acessar o jogador global criado em main.py
    
    def preparar_jogadores_para_qualy(self, todos_jogadores):
        # Remove top 30
        jogadores_31_80 = [j for j in todos_jogadores if 31 <= self.ranking.obter_posicao(j["nome"]) <= 80]
        jogadores_81_plus = [j for j in todos_jogadores if self.ranking.obter_posicao(j["nome"]) > 80]

        # Sorteia 28 da faixa 31-80 para chave principal
        random.shuffle(jogadores_31_80)
        direto_na_chave = jogadores_31_80[:28]

        # Restantes da faixa + 81+ vão para o quali
        restantes_para_qualy = jogadores_31_80[28:] + jogadores_81_plus
        random.shuffle(restantes_para_qualy)
        quali_convidados = restantes_para_qualy[:15]  # 15 vagas

        # ➕ Adiciona o jogador principal aqui!
        jogador_principal = {"nome": self.jogador_nome, "nacionalidade": self.jogador_nacionalidade}
        quali_convidados.append(jogador_principal)

        # 📋 Mostrar chave direta
        print("\n🟢 Jogadores na chave principal (entrada direta):")
        for j in direto_na_chave:
            pos = self.ranking.obter_posicao(j["nome"]) or "N/A"
            destaque = "⭐" if j["nome"] == self.jogador_nome else ""
            print(f"• {j['nome']} {destaque} — {j['nacionalidade']} — #{pos}")


        # 📋 Mostrar quali (inclui o jogador agora!)
        print("\n🟡 Jogadores convidados para o qualifying:")
        for j in quali_convidados:
            pos = self.ranking.obter_posicao(j["nome"])
            destaque = "⭐" if j["nome"] == self.jogador_nome else ""
            print(f"• {j['nome']} {destaque} — {j['nacionalidade']} — #{pos}")


        return direto_na_chave, quali_convidados


    def simular_torneio(self, todos_jogadores):
        chave_principal, jogadores_qualy = self.preparar_jogadores_para_qualy(todos_jogadores)

        # Adiciona o jogador principal no quali
        random.shuffle(jogadores_qualy)

        jogador_vivo = True
        entrou_como_lucky = False
        ultimos_perdedores = []

        def simular_rodada(lista_jogadores, texto_rodada):
            nonlocal jogador_vivo
            print(f"\n🎾 {texto_rodada}")
            print("\n🧾 Confrontos da rodada:")
            for a, b in zip(lista_jogadores[::2], lista_jogadores[1::2]):
                sigla_a = a["nacionalidade"].split()[0].strip("[]")
                sigla_b = b["nacionalidade"].split()[0].strip("[]")
                print(f"• {a['nome']} [{sigla_a}] vs {b['nome']} [{sigla_b}]")

 
            vencedores, perdedores, resultados = [], [], []

            for a, b in zip(lista_jogadores[::2], lista_jogadores[1::2]):
                nomes = (a["nome"], b["nome"])
                jogador_env = self.jogador_nome in nomes

                if jogador_env and jogador_vivo:
                    adversario = b if nomes[0] == self.jogador_nome else a
                    jogador_inst = self._buscar_instancia_jogador()
                    sets_j, sets_adv = jogador_inst.jogar_partida(nome_adversario=adversario["nome"])
                    venceu = sets_j > sets_adv

                    resultado = (
                        f"{self.jogador_nome} {sets_j} x {sets_adv} {adversario['nome']}"
                        if nomes[0] == self.jogador_nome
                        else f"{adversario['nome']} {sets_adv} x {sets_j} {self.jogador_nome}"
                    )
                    resultado += " ✅" if venceu else " ❌"
                    resultados.append(resultado)

                    if venceu:
                        vencedores.append({"nome": self.jogador_nome, "nacionalidade": self.jogador_nacionalidade})
                        perdedores.append(adversario)
                    else:
                        jogador_vivo = False
                        perdedores.append({"nome": self.jogador_nome, "nacionalidade": self.jogador_nacionalidade})
                        vencedores.append(adversario)
                        ultimos_perdedores.append({"nome": self.jogador_nome, "nacionalidade": self.jogador_nacionalidade})
                        print("\n😔 Você foi eliminado do qualifying.")
                        if input("📋 Deseja simular o restante do torneio? (s/n): ").strip().lower() != "s":
                            return [], [], [], False
                else:
                    vencedor = random.choice([a, b])
                    perdedor = b if vencedor == a else a
                    sets_v, sets_d = 2, random.choice([0, 1])
                    resultado = (
                        f"{a['nome']} {sets_v} x {sets_d} {b['nome']}"
                        if vencedor == a
                        else f"{b['nome']} {sets_v} x {sets_d} {a['nome']}"
                    )
                    resultados.append(resultado)
                    vencedores.append(vencedor)
                    perdedores.append(perdedor)

            print("\n🏁 Resultados:")
            for r in resultados:
                print("-", r)

            return vencedores, perdedores, resultados, jogador_vivo

        # Rodada 1: 16 ➜ 8
        rodada1, _, _, jogador_vivo = simular_rodada(jogadores_qualy, "Rodada 1 do qualifying...")

        # Rodada 2: 8 ➜ 4
        if jogador_vivo:
            classificados, ultimos_perdedores, _, jogador_vivo = simular_rodada(rodada1, "Rodada 2 (final) do qualifying...")
        else:
            classificados = []

        # Lucky loser
        lucky_loser = None
        if ultimos_perdedores and random.choice([True, False]):
            lucky_loser = min(
                ultimos_perdedores,
                key=lambda p: self.ranking.obter_posicao(p["nome"]) or 9999
            )
            classificados.append(lucky_loser)
            entrou_como_lucky = lucky_loser["nome"] == self.jogador_nome

        return classificados, entrou_como_lucky
