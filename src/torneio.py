import random, os, json

import jogador

class TorneioATP250:
    def __init__(self, semana, jogador_nome, jogador_nacionalidade, ranking, nome_save=None):
        self.nome_save = nome_save
        self.semana = semana
        self.jogador_nome = jogador_nome
        self.jogador_nacionalidade = jogador_nacionalidade
        self.ranking = ranking
        self.caminho_json = os.path.join("saves", self.nome_save, "torneio_atp.json")

    def _carregar_estado(self):
        with open(self.caminho_json, "r", encoding="utf-8") as f:
            return json.load(f)

    def _salvar_estado(self, estado):
        with open(self.caminho_json, "w", encoding="utf-8") as f:
            json.dump(estado, f, indent=2, ensure_ascii=False)

    def _simular_partida_npc(self, a, b):
        vencedor = random.choice([a, b])
        perdedor = b if vencedor == a else a
        sets_v, sets_d = 2, random.choice([0, 1])
        return vencedor, perdedor, f"{vencedor['nome']} {sets_v} x {sets_d} {perdedor['nome']}"

    def escolher_participantes(self, todos_jogadores):
        try:
            self.ranking.ordenar()

            nome_jogador = self.jogador_nome.strip()
            nome_jogador_lower = nome_jogador.lower()
            jogadores_31_80 = [j for j in todos_jogadores if 31 <= self.ranking.obter_posicao(j["nome"]) <= 80]
            jogadores_81_plus = [j for j in todos_jogadores if self.ranking.obter_posicao(j["nome"]) > 80]

            random.shuffle(jogadores_31_80)
            chave_principal = jogadores_31_80[:28]
            nomes_chave = {j["nome"] for j in chave_principal}

            restantes_para_qualy = jogadores_31_80[28:] + jogadores_81_plus
            restantes_para_qualy = [j for j in restantes_para_qualy if j["nome"] not in nomes_chave]

            jogador_principal = {"nome": nome_jogador, "nacionalidade": self.jogador_nacionalidade}
            if self.ranking.obter_posicao(nome_jogador) is None:
                self.ranking.adicionar_jogador_novo(jogador_principal)
                self.ranking.salvar_ranking()

            # Garante que o jogador principal esteja incluído no qualifying
            if nome_jogador not in [j["nome"].lower() for j in restantes_para_qualy]:
                restantes_para_qualy.append(jogador_principal)

            # 🔁 Garante prioridade para o jogador
            restantes_para_qualy = [
                j for j in restantes_para_qualy
                if j["nome"].lower() != nome_jogador
            ]
            restantes_para_qualy.insert(0, jogador_principal)

            # Completa até 16 jogadores
            while len(restantes_para_qualy) < 16:
                bot = {"nome": f"BotQualy{len(restantes_para_qualy)+1}", "nacionalidade": "??"}
                restantes_para_qualy.append(bot)

            qualifying = restantes_para_qualy[:16]

            print(f"\n🟢 Entrada direta ({len(chave_principal)} jogadores):")
            for j in chave_principal:
                nome = j["nome"]
                pos = self.ranking.obter_posicao(nome) or "N/A"
                destaque = "⭐" if nome.lower() == nome_jogador.lower() else ""
                print(f"• {nome} {destaque} — #{pos}")

            print(f"\n🟡 Qualifying ({len(qualifying)} jogadores):")
            for j in qualifying:
                nome = j["nome"]
                pos = self.ranking.obter_posicao(nome) or "N/A"
                destaque = "⭐" if nome.lower() == nome_jogador.lower() else ""
                print(f"• {nome} {destaque} — #{pos}")

            return chave_principal, qualifying

        except Exception as e:
            print(f"❌ Erro ao escolher participantes: {e}")
            return [], []

    def _criar_caminho_torneio(self):
        return os.path.join("saves", self.nome_save, "torneio_atp.json")

    def jogar_qualy(self, qualifying):
        try:
            if len(qualifying) < 16:
                raise ValueError("❌ A qualificação precisa de pelo menos 16 jogadores.")
            if len(qualifying) > 16:
                qualifying = qualifying[:16]

            random.shuffle(qualifying)
            confrontos_qualy_1 = list(zip(qualifying[::2], qualifying[1::2]))

            nomes_confrontos = [a["nome"] for a, _ in confrontos_qualy_1] + [b["nome"] for _, b in confrontos_qualy_1]
            if self.jogador_nome not in nomes_confrontos:
                jogador_principal = {"nome": self.jogador_nome, "nacionalidade": self.jogador_nacionalidade}
                # Certifique-se de que o jogador está em um confronto
                for i, (a, b) in enumerate(confrontos_qualy_1):
                    if self.jogador_nome not in [a["nome"], b["nome"]]:
                        confronto_antigo = confrontos_qualy_1[i]
                        confrontos_qualy_1[i] = (jogador_principal, confronto_antigo[1])
                        break

            estado = {
                "semana": self.semana,
                "torneio": None,
                "fase_atual": "qualy_1",
                "jogador": self.jogador_nome,
                "jogador_vivo": True,
                "rodadas": {
                    "qualy_1": [(a["nome"], b["nome"]) for a, b in confrontos_qualy_1],
                    "qualy_2": [],
                    "pre_oitavas": [],
                    "oitavas": [],
                    "quartas": [],
                    "semifinal": [],
                    "final": []
                },
                "resultados": {
                    "qualy_1": [],
                    "qualy_2": [],
                    "pre_oitavas": [],
                    "oitavas": [],
                    "quartas": [],
                    "semifinal": [],
                    "final": []
                }
            }

            self._salvar_estado(estado)
            print("✅ Fase de Qualifying iniciada e salva com sucesso.")
        except Exception as e:
            print(f"❌ Erro ao iniciar fase de qualifying: {e}")


    def obter_proximo_adversario(self, nome_jogador):
        estado = self._carregar_estado()
        fase = estado["fase_atual"]
        for a, b in estado["rodadas"].get(fase, []):
            if nome_jogador.strip().lower() in [a.strip().lower(), b.strip().lower()]:
                return {"nome": b} if a.strip().lower() == nome_jogador.strip().lower() else {"nome": a}
        return None

    def processar_resultado_partida(self, jogador, adversario, vencedor, resultado_str):
        caminho = os.path.join("saves", self.nome_save, "torneio_atp.json")
        with open(caminho, "r", encoding="utf-8") as f:
            estado = json.load(f)

        fase = estado["fase_atual"]

        # Remove o confronto atual da lista de rodadas
        estado["rodadas"][fase] = [
            (a, b) for a, b in estado["rodadas"].get(fase, [])
            if jogador.nome.strip().lower() not in [a.strip().lower(), b.strip().lower()]
        ]

        # ✅ Adiciona o resultado na lista da fase atual
        estado["resultados"].setdefault(fase, []).append(resultado_str)

        # Atualiza jogador_vivo
        estado["jogador_vivo"] = (vencedor == jogador.nome)

        self._atualizar_fase_se_necessario(estado)

        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(estado, f, indent=2, ensure_ascii=False)

    def jogar_chave_principal(self, entrada_direta):
        try:
            estado = self._carregar_estado()

            # Garante que os vencedores da qualy_2 existam
            resultados_qualy2 = estado["resultados"].get("qualy_2", [])
            if len(resultados_qualy2) != 4:
                raise ValueError("❌ Esperado exatamente 4 vencedores do qualifying para montar a chave principal.")

            # Extrai os nomes dos vencedores da qualy_2
            vencedores_qualy = [r.split(" x ")[0].rsplit(" ", 1)[0] for r in resultados_qualy2]

            # Monta a lista de todos os jogadores da chave principal
            random.shuffle(entrada_direta)
            jogadores_chave = entrada_direta + [{"nome": nome, "nacionalidade": "??"} for nome in vencedores_qualy]

            # Gera os confrontos da primeira fase da chave principal
            confrontos_pre_oitavas = list(zip(jogadores_chave[::2], jogadores_chave[1::2]))

            estado["rodadas"]["pre_oitavas"] = [(a["nome"], b["nome"]) for a, b in confrontos_pre_oitavas]
            estado["resultados"]["pre_oitavas"] = []

            print(f"✅ Chave principal organizada com {len(jogadores_chave)} jogadores.")
            self._salvar_estado(estado)
        except Exception as e:
            print(f"❌ Erro ao iniciar chave principal: {e}")




    def simular_npcs_na_fase_atual(self, nome_jogador):
        estado = self._carregar_estado()
        fase = estado["fase_atual"]
        novos_resultados = []

        for a, b in estado["rodadas"].get(fase, []):
            if nome_jogador.strip().lower() not in [a.strip().lower(), b.strip().lower()]:
                vencedor, perdedor, resultado = self._simular_partida_npc({"nome": a}, {"nome": b})
                novos_resultados.append(resultado)

        estado["resultados"][fase].extend(novos_resultados)
        self._atualizar_fase_se_necessario(estado)
        self._salvar_estado(estado)

    def simular_torneio_restante(self, todos_jogadores):
        estado = self._carregar_estado()
        fases = ["qualy_1", "qualy_2", "pre_oitavas", "oitavas", "quartas", "semifinal", "final"]
        idx = fases.index(estado["fase_atual"])

        while idx < len(fases):
            fase = fases[idx]
            confrontos = estado["rodadas"].get(fase, [])
            if not confrontos:
                break

            for a, b in confrontos:
                j1 = next((j for j in todos_jogadores if j["nome"] == a), {"nome": a})
                j2 = next((j for j in todos_jogadores if j["nome"] == b), {"nome": b})
                vencedor, perdedor, placar = self._simular_partida_npc(j1, j2)
                estado["resultados"][fase].append(placar)

            self._atualizar_fase_se_necessario(estado)
            idx += 1

        self._salvar_estado(estado)
        print(f"\n🏁 Torneio finalizado. Campeão: {estado['resultados']['final'][0].split()[0]}")

    def jogador_ainda_ativo(self):
        estado = self._carregar_estado()
        return estado.get("jogador_vivo", True)

    def exibir_resultados(self):
        estado = self._carregar_estado()
        fases_ordenadas = ["qualy_1", "qualy_2", "pre_oitavas", "oitavas", "quartas", "semifinal", "final"]
        
        # Encontra a última fase com resultado não vazio
        ultima_fase = next((f for f in reversed(fases_ordenadas) if estado["resultados"].get(f)), None)
        
        if ultima_fase:
            print(f"\n📊 Resultados da fase {ultima_fase}:")
            for r in estado["resultados"].get(ultima_fase, []):
                print("-", r)
        else:
            print("\n📊 Nenhum resultado disponível ainda.")

    def exibir_confrontos_restantes(self):
        estado = self._carregar_estado()
        fase = estado["fase_atual"]
        print(f"\n🗓️ Confrontos restantes da fase {fase}:")
        for a, b in estado["rodadas"].get(fase, []):
            print(f"• {a} vs {b}")

    def _atualizar_fase_se_necessario(self, estado):
        fase = estado["fase_atual"]

        total_confrontos = len(estado["rodadas"].get(fase, []))
        total_resultados = len(estado["resultados"].get(fase, []))

        if total_resultados < total_confrontos:
            return  # Ainda faltam partidas para essa fase

        ordem = ["qualy_1", "qualy_2", "pre_oitavas", "oitavas", "quartas", "semifinal", "final"]
        idx = ordem.index(fase)
        if idx + 1 >= len(ordem):
            estado["fase_atual"] = "finalizado"
            return

        proxima = ordem[idx + 1]
        vencedores = [r.split(" x ")[0].rsplit(" ", 1)[0] for r in estado["resultados"][fase]]

        if proxima == "qualy_2":
            if len(vencedores) != 8:
                raise ValueError("❌ 'qualy_2' precisa de 8 jogadores")
            estado["rodadas"]["qualy_2"] = list(zip(vencedores[::2], vencedores[1::2]))
            estado["resultados"]["qualy_2"] = []
            estado["fase_atual"] = "qualy_2"
            return

        if fase == "qualy_2":
            if len(vencedores) != 4:
                raise ValueError("❌ 'qualy_2' deve terminar com exatamente 4 vencedores.")
            # Aqui não avançamos automaticamente — é a lógica que depois chamará jogar_chave_principal()
            estado["fase_atual"] = "pre_oitavas"
            return

        # Para as demais fases
        estado["rodadas"][proxima] = list(zip(vencedores[::2], vencedores[1::2]))
        estado["resultados"][proxima] = []
        estado["fase_atual"] = proxima



    def iniciar_torneio(self, nome_torneio, todos_jogadores):
        try:
            # Seleciona quem vai direto pra chave principal e quem vai pro qualifying
            entrada_direta, qualifying = self.escolher_participantes(todos_jogadores)

            # Inicia o qualifying
            self.jogar_qualy(qualifying)

            # Atualiza nome do torneio no estado salvo
            estado = self._carregar_estado()
            estado["torneio"] = nome_torneio
            self._salvar_estado(estado)

            print(f"\n📁 Torneio {nome_torneio} iniciado com sucesso e salvo.")
        except Exception as e:
            print(f"❌ Erro ao iniciar torneio: {e}")
