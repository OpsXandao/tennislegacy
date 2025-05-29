import random, os, json
from jogador import normalizar_nome  # no topo do arquivo


class TorneioATP250:
    def __init__(
        self, semana, jogador_nome, jogador_nacionalidade, ranking, nome_save=None
    ):
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
        return (
            vencedor,
            perdedor,
            f"{vencedor['nome']} {sets_v} x {sets_d} {perdedor['nome']}",
        )

    def escolher_participantes(self, todos_jogadores):
        try:
            self.ranking.ordenar()

            nome_jogador = self.jogador_nome.strip()
            nome_jogador_lower = nome_jogador.lower()
            jogadores_31_80 = [
                j
                for j in todos_jogadores
                if 31 <= self.ranking.obter_posicao(j["nome"]) <= 80
            ]
            jogadores_81_plus = [
                j for j in todos_jogadores if self.ranking.obter_posicao(j["nome"]) > 80
            ]

            random.shuffle(jogadores_31_80)
            chave_principal = jogadores_31_80[:28]
            nomes_chave = {j["nome"] for j in chave_principal}

            restantes_para_qualy = jogadores_31_80[28:] + jogadores_81_plus
            restantes_para_qualy = [
                j for j in restantes_para_qualy if j["nome"] not in nomes_chave
            ]

            jogador_principal = {
                "nome": nome_jogador,
                "nacionalidade": self.jogador_nacionalidade,
            }
            if self.ranking.obter_posicao(nome_jogador) is None:
                self.ranking.adicionar_jogador_novo(jogador_principal)
                self.ranking.salvar_ranking()

            # Garante que o jogador principal esteja incluído no qualifying
            if nome_jogador not in [j["nome"].lower() for j in restantes_para_qualy]:
                restantes_para_qualy.append(jogador_principal)

            # 🔁 Garante prioridade para o jogador
            restantes_para_qualy = [
                j for j in restantes_para_qualy if j["nome"].lower() != nome_jogador
            ]
            restantes_para_qualy.insert(0, jogador_principal)

            # Completa até 16 jogadores
            while len(restantes_para_qualy) < 16:
                bot = {
                    "nome": f"BotQualy{len(restantes_para_qualy)+1}",
                    "nacionalidade": "??",
                }
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

    def jogar_qualy(self, jogadores_qualy):
        if len(jogadores_qualy) < 16:
            raise ValueError("❌ A qualificação precisa de pelo menos 16 jogadores.")
        if len(jogadores_qualy) > 16:
            jogadores_qualy = jogadores_qualy[:16]

        random.shuffle(jogadores_qualy)
        confrontos = list(zip(jogadores_qualy[::2], jogadores_qualy[1::2]))

        # Garante que o jogador esteja em um confronto
        nomes_confrontos = [a["nome"] for a, _ in confrontos] + [
            b["nome"] for _, b in confrontos
        ]
        if self.jogador_nome not in nomes_confrontos:
            jogador_dict = {
                "nome": self.jogador_nome,
                "nacionalidade": self.jogador_nacionalidade,
            }
            confronto_a, confronto_b = confrontos[0]
            confrontos[0] = (jogador_dict, confronto_b)

        estado = {
            "semana": self.semana,
            "torneio": self.nome_torneio,
            "fase_atual": "qualy_1",
            "jogador": self.jogador_nome,
            "jogador_vivo": True,
            "rodadas": {
                "qualy_1": confrontos,
                "qualy_2": [],
                "pre_oitavas": [],
                "oitavas": [],
                "quartas": [],
                "semifinal": [],
                "final": [],
            },
            "resultados": {
                "qualy_1": [],
                "qualy_2": [],
                "pre_oitavas": [],
                "oitavas": [],
                "quartas": [],
                "semifinal": [],
                "final": [],
            },
        }

        caminho = os.path.join("saves", self.nome_save, "torneio_atp.json")
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(estado, f, indent=2, ensure_ascii=False)

    def obter_proximo_adversario(self, nome_jogador):
        estado = self._carregar_estado()
        fase = estado["fase_atual"]
        nome_normalizado = normalizar_nome(nome_jogador)

        for a, b in estado["rodadas"].get(fase, []):
            if nome_normalizado in [normalizar_nome(a), normalizar_nome(b)]:
                adversario = b if normalizar_nome(a) == nome_normalizado else a
                return (
                    adversario if isinstance(adversario, dict) else {"nome": adversario}
                )
        return None

    def _atualizar_fase_se_necessario(self, estado):
        fase = estado["fase_atual"]
        total_confrontos = len(estado["rodadas"].get(fase, []))
        total_resultados = len(estado["resultados"].get(fase, []))

        if total_resultados < total_confrontos:
            return  # Ainda faltam partidas para essa fase

        ordem = [
            "qualy_1",
            "qualy_2",
            "pre_oitavas",
            "oitavas",
            "quartas",
            "semifinal",
            "final",
        ]
        idx = ordem.index(fase)
        if idx + 1 >= len(ordem):
            estado["fase_atual"] = "finalizado"
            return

        # Nova lógica: sempre busca o dicionário atualizado pelo id_ranking
        vencedores = []
        for r in estado["resultados"][fase]:
            if isinstance(r, dict):
                # Usa id_ranking se estiver disponível (mais seguro)
                id_vencedor = r["vencedor"].get("id_ranking")
                if id_vencedor is not None:
                    # Cuidado: id_ranking começa em 1, listas Python em 0
                    jogador_obj = (
                        self.ranking.ranking[id_vencedor - 1]
                        if id_vencedor - 1 < len(self.ranking.ranking)
                        else r["vencedor"]
                    )
                else:
                    # fallback caso id_ranking falhe
                    jogador_obj = self.ranking.buscar_jogador_por_nome(
                        r["vencedor"]["nome"]
                    )
                vencedores.append(jogador_obj)
            else:
                # Fallback para resultados antigos em string
                vencedor_nome = extrair_nome_puro(r)
                jogador_obj = self.ranking.buscar_jogador_por_nome(vencedor_nome)
                vencedores.append(jogador_obj)

        # 🚩 qualy_1: 8 vencedores para qualy_2
        if fase == "qualy_1":
            if len(vencedores) != 8:
                raise ValueError(
                    "❌ Esperado exatamente 8 vencedores para montar a 'qualy_2'."
                )
            random.shuffle(vencedores)
            estado["rodadas"]["qualy_2"] = list(zip(vencedores[::2], vencedores[1::2]))
            estado["resultados"]["qualy_2"] = []
            estado["fase_atual"] = "qualy_2"

        # 🚩 qualy_2: 4 vencedores para pre_oitavas + 12 do ranking
        elif fase == "qualy_2":
            if len(vencedores) != 4:
                raise ValueError(
                    "❌ Esperado exatamente 4 vencedores para montar a 'pre_oitavas'."
                )
            jogadores_chave = self.ranking.ranking[:12] + vencedores  # 12 + 4 = 16
            random.shuffle(jogadores_chave)
            estado["rodadas"]["pre_oitavas"] = list(
                zip(jogadores_chave[::2], jogadores_chave[1::2])
            )
            estado["resultados"]["pre_oitavas"] = []
            estado["fase_atual"] = "pre_oitavas"

        else:
            # Demais fases seguem normalmente
            proxima = ordem[idx + 1]
            if len(vencedores) != len(estado["rodadas"].get(fase, [])):
                print("⚠️ Número de vencedores diferente do esperado para próxima fase.")
            estado["rodadas"][proxima] = list(zip(vencedores[::2], vencedores[1::2]))
            estado["resultados"][proxima] = []
            estado["fase_atual"] = proxima

    def jogar_chave_principal(self, classificados):
        if len(classificados) != 4:
            raise ValueError(
                "❌ Esperado exatamente 4 vencedores do qualifying para montar a chave principal."
            )

        jogadores_top = self.ranking.ranking[:12]
        jogadores_chave = jogadores_top + classificados
        random.shuffle(jogadores_chave)

        confrontos = list(zip(jogadores_chave[::2], jogadores_chave[1::2]))

        nomes_confrontos = [a["nome"] for a, _ in confrontos] + [
            b["nome"] for _, b in confrontos
        ]
        if self.jogador_nome not in nomes_confrontos:
            jogador_dict = {
                "nome": self.jogador_nome,
                "nacionalidade": self.jogador_nacionalidade,
            }
            confronto_a, confronto_b = confrontos[0]
            confrontos[0] = (jogador_dict, confronto_b)

        caminho = os.path.join("saves", self.nome_save, "torneio_atp.json")
        with open(caminho, "r", encoding="utf-8") as f:
            estado = json.load(f)

        estado["fase_atual"] = "pre_oitavas"
        estado["rodadas"]["pre_oitavas"] = confrontos
        estado["resultados"]["pre_oitavas"] = []

        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(estado, f, indent=2, ensure_ascii=False)

    def _simular_partida_npc(self, a, b):
        vencedor = random.choice([a, b])
        perdedor = b if vencedor == a else a
        sets_v, sets_d = 2, random.choice([0, 1])

        # 🔧 Remover números residuais no nome (caso alguém já esteja com " 2")
        def limpar_nome(nome):
            return nome.strip().rstrip("0123456789").strip()

        nome_vencedor = limpar_nome(vencedor["nome"])
        nome_perdedor = limpar_nome(perdedor["nome"])

        return (
            vencedor,
            perdedor,
            f"{nome_vencedor} {sets_v} x {sets_d} {nome_perdedor}",
        )

    def remover_confronto_do_jogador(self, fase, nome_jogador):
        if not os.path.exists(self.caminho_json):
            print("⚠️ Arquivo de torneio não encontrado.")
            return

        with open(self.caminho_json, "r", encoding="utf-8") as f:
            estado = json.load(f)

        confrontos_originais = estado.get("rodadas", {}).get(fase, [])
        confrontos_filtrados = []
        removidos = 0

        nome_normalizado = normalizar_nome(nome_jogador)

        for a, b in confrontos_originais:
            a_nome = a["nome"] if isinstance(a, dict) else a
            b_nome = b["nome"] if isinstance(b, dict) else b

            if nome_normalizado in [normalizar_nome(a_nome), normalizar_nome(b_nome)]:
                print(f"🧹 Removendo confronto: {a_nome} vs {b_nome}")
                removidos += 1
                continue

            confrontos_filtrados.append((a, b))

        estado["rodadas"][fase] = confrontos_filtrados

        with open(self.caminho_json, "w", encoding="utf-8") as f:
            json.dump(estado, f, indent=2, ensure_ascii=False)

        print(f"✅ Confrontos removidos: {removidos} na fase '{fase}'")

    def simular_torneio_restante(self, todos_jogadores):
        estado = self._carregar_estado()
        fases = [
            "qualy_1",
            "qualy_2",
            "pre_oitavas",
            "oitavas",
            "quartas",
            "semifinal",
            "final",
        ]
        idx = fases.index(estado["fase_atual"])

        while idx < len(fases):
            fase = fases[idx]
            confrontos = estado["rodadas"].get(fase, [])
            if not confrontos:
                break

            novos_resultados = []
            for a, b in confrontos:
                # Compatibilidade com formato antigo e novo
                if isinstance(a, str):
                    j1 = next(
                        (j for j in todos_jogadores if j["nome"] == a), {"nome": a}
                    )
                else:
                    j1 = a

                if isinstance(b, str):
                    j2 = next(
                        (j for j in todos_jogadores if j["nome"] == b), {"nome": b}
                    )
                else:
                    j2 = b

                vencedor, perdedor, placar = self._simular_partida_npc(j1, j2)
                novos_resultados.append(placar)

            estado["resultados"][fase].extend(novos_resultados)
            self._atualizar_fase_se_necessario(estado)
            idx += 1

        self._salvar_estado(estado)
        resultado_final = estado["resultados"]["final"][0]
        if isinstance(resultado_final, dict):
            campeao = resultado_final.get("vencedor", {}).get("nome", "Desconhecido")
        else:
            campeao = resultado_final.split()[0]

        print(f"\n🏁 Torneio finalizado. Campeão: {campeao}")

    def simular_npcs_na_fase_atual(self, nome_jogador):
        estado = self._carregar_estado()
        fase = estado["fase_atual"]
        novos_resultados = []
        novos_confrontos = []

        nome_normalizado = normalizar_nome(nome_jogador)

        for a, b in estado["rodadas"].get(fase, []):
            nome_a = a["nome"] if isinstance(a, dict) else a
            nome_b = b["nome"] if isinstance(b, dict) else b

            nomes_confronto = [normalizar_nome(nome_a), normalizar_nome(nome_b)]

            if nome_normalizado not in nomes_confronto:
                jogador_a = a if isinstance(a, dict) else {"nome": nome_a}
                jogador_b = b if isinstance(b, dict) else {"nome": nome_b}
                vencedor, perdedor, resultado = self._simular_partida_npc(
                    jogador_a, jogador_b
                )
                novos_resultados.append(resultado)
            else:
                novos_confrontos.append((a, b))  # Mantém o confronto do jogador

        estado["rodadas"][fase] = novos_confrontos
        estado["resultados"][fase].extend(novos_resultados)
        self._atualizar_fase_se_necessario(estado)
        self._salvar_estado(estado)

    def jogador_ainda_ativo(self):
        estado = self._carregar_estado()
        return estado.get("jogador_vivo", True)

    def exibir_resultados(self):
        estado = self._carregar_estado()
        fases_ordenadas = [
            "qualy_1",
            "qualy_2",
            "pre_oitavas",
            "oitavas",
            "quartas",
            "semifinal",
            "final",
        ]

        ultima_fase = next(
            (f for f in reversed(fases_ordenadas) if estado["resultados"].get(f)), None
        )

        if ultima_fase:
            print(f"\n📊 Resultados da fase {ultima_fase}:")
            for r in estado["resultados"].get(ultima_fase, []):
                if isinstance(r, dict):  # novo formato
                    nome_vencedor = (
                        r["vencedor"]["nome"]
                        if isinstance(r["vencedor"], dict)
                        else str(r["vencedor"])
                    )
                    nome_a = r["jogador_a"]["nome"]
                    nome_b = r["jogador_b"]["nome"]
                    placar = r["resultado"]
                    print(f"- {nome_a} vs {nome_b} | 🏆 {nome_vencedor} ({placar})")
                else:
                    print("-", r)  # compatibilidade com formato antigo
        else:
            print("\n📊 Nenhum resultado disponível ainda.")

    def exibir_confrontos_restantes(self):
        estado = self._carregar_estado()
        fase = estado["fase_atual"]
        jogador_normalizado = normalizar_nome(self.jogador_nome)

        print(f"\n🗓️ Confrontos restantes da fase {fase}:")
        for a, b in estado["rodadas"].get(fase, []):
            nome_a = a["nome"] if isinstance(a, dict) else a
            nome_b = b["nome"] if isinstance(b, dict) else b

            estrela_a = "⭐" if normalizar_nome(nome_a) == jogador_normalizado else ""
            estrela_b = "⭐" if normalizar_nome(nome_b) == jogador_normalizado else ""

            print(f"• {nome_a}{estrela_a} vs {nome_b}{estrela_b}")

    def _atualizar_fase_se_necessario(self, estado):
        fase = estado["fase_atual"]
        total_confrontos = len(estado["rodadas"].get(fase, []))
        total_resultados = len(estado["resultados"].get(fase, []))

        if total_resultados < total_confrontos:
            return  # Ainda faltam partidas para essa fase

        ordem = [
            "qualy_1",
            "qualy_2",
            "pre_oitavas",
            "oitavas",
            "quartas",
            "semifinal",
            "final",
        ]
        idx = ordem.index(fase)
        if idx + 1 >= len(ordem):
            estado["fase_atual"] = "finalizado"
            return

        vencedores = []
        for r in estado["resultados"][fase]:
            jogador_obj = None
            if isinstance(r, dict) and isinstance(r.get("vencedor"), dict):
                # Se já existe id_ranking, usa ele
                id_rank = r["vencedor"].get("id_ranking")
                if id_rank and 1 <= id_rank <= len(self.ranking.ranking):
                    jogador_obj = self.ranking.ranking[
                        id_rank - 1
                    ]  # Ranking começa em 1
            if not jogador_obj:
                # fallback para nome limpo
                if isinstance(r, dict):
                    vencedor_nome = (
                        r["vencedor"]["nome"]
                        if isinstance(r["vencedor"], dict)
                        else str(r["vencedor"])
                    )
                else:
                    vencedor_nome = extrair_nome_puro(r)
                jogador_obj = self.ranking.buscar_jogador_por_nome(vencedor_nome)
            if jogador_obj:
                vencedores.append(jogador_obj)
            else:
                vencedores.append({"nome": vencedor_nome, "nacionalidade": "??"})

        # 🚩 qualy_1: 8 vencedores para qualy_2
        if fase == "qualy_1":
            if len(vencedores) != 8:
                raise ValueError(
                    "❌ Esperado exatamente 8 vencedores para montar a 'qualy_2'."
                )
            random.shuffle(vencedores)
            estado["rodadas"]["qualy_2"] = list(zip(vencedores[::2], vencedores[1::2]))
            estado["resultados"]["qualy_2"] = []
            estado["fase_atual"] = "qualy_2"
        # 🚩 qualy_2: 4 vencedores + 12 do ranking = 16
        elif fase == "qualy_2":
            if len(vencedores) != 4:
                raise ValueError(
                    "❌ Esperado exatamente 4 vencedores para montar a 'pre_oitavas'."
                )
            jogadores_chave = self.ranking.ranking[:12] + vencedores
            random.shuffle(jogadores_chave)
            estado["rodadas"]["pre_oitavas"] = list(
                zip(jogadores_chave[::2], jogadores_chave[1::2])
            )
            estado["resultados"]["pre_oitavas"] = []
            estado["fase_atual"] = "pre_oitavas"
        else:
            # Demais fases normais
            proxima = ordem[idx + 1]
            if len(vencedores) != len(estado["rodadas"].get(fase, [])):
                print("⚠️ Número de vencedores diferente do esperado para próxima fase.")
            estado["rodadas"][proxima] = list(zip(vencedores[::2], vencedores[1::2]))
            estado["resultados"][proxima] = []
            estado["fase_atual"] = proxima

    def iniciar_torneio(self, nome_torneio, todos_jogadores):
        try:
            self.nome_torneio = nome_torneio  # ✅ Define o atributo aqui

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

    def _obter_fase_index(self, fase):
        fases = [
            "qualy_1",
            "qualy_2",
            "pre_oitavas",
            "oitavas",
            "quartas",
            "semifinal",
            "final",
        ]
        return fases.index(fase) if fase in fases else -1

    def normalizar_confrontos(self, confrontos_raw):
        from jogador import Jogador  # evita import circular

        confrontos_obj = []
        for a, b in confrontos_raw:
            a_nome = a["nome"] if isinstance(a, dict) else a
            a_nac = a.get("nacionalidade", "??") if isinstance(a, dict) else "??"
            b_nome = b["nome"] if isinstance(b, dict) else b
            b_nac = b.get("nacionalidade", "??") if isinstance(b, dict) else "??"

            jogador_a = Jogador(a_nome, 25, a_nac, self.nome_save)
            jogador_b = Jogador(b_nome, 25, b_nac, self.nome_save)
            confrontos_obj.append((jogador_a, jogador_b))
        return confrontos_obj

    def processar_resultado_partida(self, jogador, adversario, vencedor, resultado_str):
        def garantir_dict_jogador(j):
            if isinstance(j, dict):
                return j
            elif hasattr(j, "to_dict"):
                return j.to_dict()
            elif isinstance(j, str):
                return {"nome": j, "nacionalidade": "??"}
            else:
                return {"nome": str(j), "nacionalidade": "??"}

        caminho = os.path.join("saves", self.nome_save, "torneio_atp.json")
        with open(caminho, "r", encoding="utf-8") as f:
            estado = json.load(f)

        fase = estado["fase_atual"]
        confrontos = estado["rodadas"].get(fase, [])

        jogador_dict = garantir_dict_jogador(jogador)
        adversario_dict = garantir_dict_jogador(adversario)
        vencedor_dict = garantir_dict_jogador(vencedor)

        jogador_norm = normalizar_nome(jogador_dict["nome"])
        adversario_norm = normalizar_nome(adversario_dict["nome"])
        vencedor_norm = normalizar_nome(vencedor_dict["nome"])

        # Busca a posição no ranking para cada jogador
        id_jogador = self.ranking.obter_posicao(jogador_dict["nome"])
        id_adversario = self.ranking.obter_posicao(adversario_dict["nome"])
        id_vencedor = self.ranking.obter_posicao(vencedor_dict["nome"])

        # Remove o confronto atual
        confrontos_restantes = [
            (a, b)
            for a, b in confrontos
            if set(
                [normalizar_nome(a.get("nome", a)), normalizar_nome(b.get("nome", b))]
            )
            != set([jogador_norm, adversario_norm])
        ]
        estado["rodadas"][fase] = confrontos_restantes

        # Adiciona resultado como dicionário padronizado, com id do ranking
        resultado_dict = {
            "jogador_a": {**jogador_dict, "id_ranking": id_jogador},
            "jogador_b": {**adversario_dict, "id_ranking": id_adversario},
            "vencedor": {**vencedor_dict, "id_ranking": id_vencedor},
            "resultado": (
                resultado_str.split(":")[1].strip()
                if ":" in resultado_str
                else resultado_str
            ),
        }
        estado["resultados"].setdefault(fase, []).append(resultado_dict)

        estado["jogador_vivo"] = vencedor_norm == jogador_norm

        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(estado, f, ensure_ascii=False, indent=2)
            
def criar_torneio(torneio_escolhido, jogador, nome_save, semana):
    # Cria instância do ranking para ser usada pelo torneio
    from src.ranking import SistemaRanking

    ranking_path = os.path.join("saves", nome_save, "ranking_atp.json")
    ranking = SistemaRanking(ranking_path)

    instancia = TorneioATP250(
        semana=semana,
        jogador_nome=jogador["nome"],
        jogador_nacionalidade=jogador["nacionalidade"],
        ranking=ranking,
        nome_save=nome_save,
    )

    # Cria a estrutura do torneio no disco
    instancia.iniciar_torneio(torneio_escolhido["nome"], ranking.ranking)
    return instancia

def salvar_torneio(instancia):
    """
    Salva o estado atual do torneio associado à instância no arquivo correto do save.
    """
    caminho_json = os.path.join("saves", instancia.nome_save, "torneio_atp.json")
    estado = instancia._carregar_estado()
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(estado, f, indent=2, ensure_ascii=False)


def carregar_torneio(nome_save):
    from src.ranking import SistemaRanking

    ranking_path = os.path.join("saves", nome_save, "ranking_atp.json")
    ranking = SistemaRanking(ranking_path)
    caminho_json = os.path.join("saves", nome_save, "torneio_atp.json")

    with open(caminho_json, "r", encoding="utf-8") as f:
        estado = json.load(f)

    jogador_nome = estado["jogador"]
    # Busca nacionalidade no ranking pelo nome do jogador:
    jogador_obj = next((j for j in ranking.ranking if j["nome"] == jogador_nome), None)
    jogador_nacionalidade = jogador_obj["nacionalidade"] if jogador_obj else "??"

    instancia = TorneioATP250(
        semana=estado["semana"],
        jogador_nome=jogador_nome,
        jogador_nacionalidade=jogador_nacionalidade,
        ranking=ranking,
        nome_save=nome_save,
    )
    return instancia

def simular_partidas_npc(instancia, nome_jogador=None):
    """
    Simula as partidas entre NPCs na fase atual do torneio.
    Se nome_jogador for fornecido, preserva o confronto do player.
    """
    if nome_jogador is None:
        nome_jogador = instancia.jogador_nome
    instancia.simular_npcs_na_fase_atual(nome_jogador)

def avancar_fase(instancia):
    """
    Avança a fase do torneio conforme o estado atual e salva.
    """
    estado = instancia._carregar_estado()
    instancia._atualizar_fase_se_necessario(estado)
    instancia._salvar_estado(estado)


def extrair_nome_puro(resultado):
    if isinstance(resultado, dict):
        vencedor = resultado.get("vencedor", {})
        if isinstance(vencedor, dict):
            return vencedor.get("nome", "Desconhecido")
        return str(vencedor)
    elif isinstance(resultado, str):
        partes = resultado.split()
        if len(partes) >= 3 and partes[-2] == "x":
            return " ".join(partes[:-2])
        return resultado.strip()
    else:
        return "Desconhecido"