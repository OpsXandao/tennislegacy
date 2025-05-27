import random, os, json, builtins
from save import carregar_estado_torneio
from src.ranking import SistemaRanking
from interface.menu_rodada import menu_rodadas
from src.calendario import distribuir_premio

class TorneioATP250:
    def __init__(self, semana, jogador_nome, jogador_nacionalidade, ranking, nome_save=None):
        self.nome_save = nome_save
        self.semana = semana
        self.jogador_nome = jogador_nome
        self.jogador_nacionalidade = jogador_nacionalidade
        self.ranking = ranking

    def _simular_partida_npc(self, a, b):
        vencedor = random.choice([a, b])
        perdedor = b if vencedor == a else a
        sets_v, sets_d = 2, random.choice([0, 1])
        resultado = f"{vencedor['nome']} {sets_v} x {sets_d} {perdedor['nome']}"
        return vencedor, perdedor, resultado

    def _buscar_instancia_jogador(self):
        try:
            return builtins.jogador
        except AttributeError:
            raise ValueError("Jogador não definido no contexto global.")

    def preparar_jogadores_para_qualy(self, todos_jogadores):
        try:
            self.ranking.ordenar()
            # Excluir jogadores top 30
            jogadores_31_80 = [j for j in todos_jogadores if 31 <= self.ranking.obter_posicao(j["nome"]) <= 80]
            jogadores_81_plus = [j for j in todos_jogadores if self.ranking.obter_posicao(j["nome"]) > 80]

            random.shuffle(jogadores_31_80)
            direto_na_chave = jogadores_31_80[:28]
            nomes_chave_principal = {j["nome"] for j in direto_na_chave}

            restantes_para_qualy = jogadores_31_80[28:] + jogadores_81_plus
            restantes_para_qualy = [j for j in restantes_para_qualy if j["nome"] not in nomes_chave_principal]
            random.shuffle(restantes_para_qualy)
            quali_convidados = restantes_para_qualy[:15]

            jogador_principal = {"nome": self.jogador_nome, "nacionalidade": self.jogador_nacionalidade}
            if self.ranking.obter_posicao(jogador_principal["nome"]) is None:
                self.ranking.adicionar_jogador_novo(jogador_principal)
                self.ranking.salvar_ranking()
            if self.jogador_nome not in {j["nome"] for j in quali_convidados}:
                quali_convidados.append(jogador_principal)

            print("\n🟢 Jogadores na chave principal (entrada direta):")
            for j in direto_na_chave:
                pos = self.ranking.obter_posicao(j["nome"]) or "N/A"
                destaque = "⭐" if j["nome"] == self.jogador_nome else ""
                print(f"• {j['nome']} {destaque} — {j['nacionalidade']} — #{pos}")

            print("\n🟡 Jogadores convidados para o qualifying:")
            for j in quali_convidados:
                pos = self.ranking.obter_posicao(j["nome"])
                destaque = "⭐" if j["nome"] == self.jogador_nome else ""
                print(f"• {j['nome']} {destaque} — {j['nacionalidade']} — #{pos}")

            return direto_na_chave, quali_convidados
        except Exception as e:
            print(f"❌ Erro ao preparar jogadores para o qualifying: {e}")
            return [], []

    def simular_torneio(self, todos_jogadores):
        try:
            caminho = os.path.join("saves", self.nome_save, "torneio_atp.json")
            if not os.path.exists(caminho):
                print("❌ Arquivo de estado do torneio não encontrado.")
                return [], False

            with open(caminho, "r", encoding="utf-8") as f:
                estado = json.load(f)

            jogador_ativo = self._buscar_instancia_jogador()
            fases = ["qualy_1", "qualy_2", "pre_oitavas", "oitavas", "quartas", "semifinal", "final"]
            resultados = estado["resultados"]

            fase_atual = estado["fase_atual"]
            index_fase = fases.index(fase_atual)

            while index_fase < len(fases):
                fase = fases[index_fase]
                confrontos = estado["rodadas"][fase]
                if not confrontos:
                    print(f"⚠️ Nenhum confronto para a fase {fase}.")
                    break

                # Recupera objetos dos jogadores
                confrontos_com_obj = [
                    (
                        next((j for j in todos_jogadores if j["nome"] == a), {"nome": a, "nacionalidade": "??"}),
                        next((j for j in todos_jogadores if j["nome"] == b), {"nome": b, "nacionalidade": "??"})
                    )
                    for a, b in confrontos
                ]

                print(f"\n🎾 Fase: {fase.replace('_', ' ').title()}")
                menu_rodadas(resultados[fase], confrontos_com_obj, jogador_ativo, self.nome_save, self)

                # Define vencedores dessa rodada para próxima fase
                vencedores = [r.split()[0] for r in resultados[fase]]

                if fase != "final":
                    proxima_fase = fases[index_fase + 1]
                    pares_proximos = list(zip(vencedores[::2], vencedores[1::2]))
                    estado["rodadas"][proxima_fase] = pares_proximos
                    estado["fase_atual"] = proxima_fase

                # Atualiza e salva o JSON a cada fase
                with open(caminho, "w", encoding="utf-8") as f:
                    json.dump(estado, f, indent=2, ensure_ascii=False)

                index_fase += 1

            print("\n🥇 Campeão do torneio:", vencedores[0])
            return vencedores, False

        except Exception as e:
            print(f"❌ Erro ao simular torneio: {e}")
            return [], False


    def salvar_estado(self, fase_atual, confrontos, resultados):
        from save import salvar_estado_torneio
        caminho = os.path.join("saves", self.nome_save, "torneio_atp.json")
        salvar_estado_torneio(caminho, fase_atual, confrontos, resultados)

    def retomar_torneio(self, caminho_torneio, jogador, jogadores_disponiveis):
        estado_salvo = carregar_estado_torneio(caminho_torneio)
        if not estado_salvo:
            return None
        print(f"\\n📂 Retomando o torneio salvo da {estado_salvo['fase_atual']}...")
        jogador_normalizado = jogador.nome.strip().lower()
        ativo = any(
            jogador_normalizado in (a.strip().lower(), b.strip().lower())
            for a, b in estado_salvo["confrontos"]
        )
        if not ativo:
            print("⚠️ Você já foi eliminado deste torneio.")
            os.remove(caminho_torneio)
            return jogador
        confrontos = [
            (
                next((j for j in jogadores_disponiveis if j["nome"] == a), {"nome": a, "nacionalidade": "??"}),
                next((j for j in jogadores_disponiveis if j["nome"] == b), {"nome": b, "nacionalidade": "??"})
            )
            for a, b in estado_salvo["confrontos"]
        ]
        menu_rodadas(estado_salvo["resultados"], confrontos, jogador, self.nome_save, self)
        return jogador

    def iniciar_torneio_json(self, nome_torneio, todos_jogadores):
        caminho_json = os.path.join("saves", self.nome_save, "torneio_atp.json")

        if os.path.exists(caminho_json):
            os.remove(caminho_json)

        # 🧠 Reutiliza a lógica centralizada de qualificação
        entrada_direta, qualifying = self.preparar_jogadores_para_qualy(todos_jogadores)

        # 🧩 Confrontos da Qualy 1
        random.shuffle(qualifying)
        confrontos_qualy_1 = list(zip(qualifying[::2], qualifying[1::2]))

        # 🎾 Chave principal: 28 + 4 espaços dos qualifiers
        random.shuffle(entrada_direta)
        jogadores_chave = entrada_direta + [{"nome": f"Qualy {i+1}", "nacionalidade": "??"} for i in range(4)]
        confrontos_pre_oitavas = list(zip(jogadores_chave[::2], jogadores_chave[1::2]))

        dados = {
            "semana": self.semana,
            "torneio": nome_torneio,
            "fase_atual": "qualy_1",
            "jogador": self.jogador_nome,
            "entrada_direta": entrada_direta,
            "qualifying": qualifying,
            "rodadas": {
                "qualy_1": [(a["nome"], b["nome"]) for a, b in confrontos_qualy_1],
                "qualy_2": [],
                "pre_oitavas": [(a["nome"], b["nome"]) for a, b in confrontos_pre_oitavas],
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

        os.makedirs(os.path.dirname(caminho_json), exist_ok=True)
        with open(caminho_json, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

        print(f"📁 Torneio inicializado e salvo em {caminho_json}")
