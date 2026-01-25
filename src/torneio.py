import os
import json
import random

from src.dados import (
    carregar_estado_torneio,
    get_caminho_ranking_save,
    get_caminho_torneio_save,
)
from src.jogador import Jogador, normalizar_nome
from src.calendario import obter_torneio_por_nome
from src.jogar_partida import criar_config_partida, jogar_partida
from src.progressao import handle_xp_e_level_up, handle_fadiga_e_lesao, recuperar_energia_entre_rodadas
from src.save import salvar_jogo
from src.ranking import SistemaRanking
from src.gerador_nomes import gerar_jogador_fraco



class Torneio:
    def __init__(
        self, tournament_data, jogador_nome, jogador_nacionalidade, ranking, nome_save=None
    ):
        self.nome_save = nome_save
        self.tournament_data = tournament_data
        self.semana = int(tournament_data["semana"]) if "semana" in tournament_data else 1 # Extract semana from tournament_data
        self.nome_torneio_atual = tournament_data["nome"] # Extract nome from tournament_data
        self.jogador_nome = jogador_nome
        self.jogador_nacionalidade = jogador_nacionalidade
        self.ranking = ranking
        self.caminho_json = get_caminho_torneio_save(self.nome_save)

        # Define best_of_sets based on tournament type
        if self.tournament_data["tipo"] == "Grand Slam":
            self.best_of_sets = 5
        else:
            self.best_of_sets = 3

        # Define number of rounds based on tournament type
        if self.tournament_data["tipo"] == "Grand Slam":
            self.num_rounds = 7 # 128 players
        elif self.tournament_data["tipo"] == "Davis Cup":
            self.num_rounds = 0 # Special handling
        else: # ATP 250, 500, 1000
            self.num_rounds = 5 # 32 players

    def garantir_dados_completos(self, jogador):
        if isinstance(jogador, dict) and "atributos" in jogador:
            return jogador
        nome = jogador["nome"] if isinstance(jogador, dict) else str(jogador)
        obj = self.ranking.buscar_jogador_por_nome(nome)
        if obj:
            return obj
        return {"nome": nome, "nacionalidade": "??"}

    def _get_first_main_draw_phase(self):
        if self.tournament_data["tipo"] == "Grand Slam":
            return "r128"
        elif self.tournament_data["tipo"] == "Davis Cup":
            return "" # Not applicable, handled separately
        else: # ATP
            return "pre_oitavas"


    def _carregar_estado(self):
        estado = carregar_estado_torneio(self.nome_save)
        if estado is None:
            # Cria um estado vazio/padrão se o arquivo não existir
            estado = {
                "torneio": self.nome_torneio_atual,
                "semana": self.semana,
                "fase_atual": "qualy_1",
                "rodadas": {},
                "resultados": {},
                "jogador": self.jogador_nome,
                "jogador_vivo": True,
                "tournament_data": self.tournament_data, # Save tournament data
            }
            self._salvar_estado(estado)
        else:
            # If loaded state exists but doesn't have tournament_data (old save), add it
            if "tournament_data" not in estado:
                from src.calendario import obter_torneio_por_nome
                estado["tournament_data"] = obter_torneio_por_nome(estado["semana"], estado["torneio"])
                # Also ensure best_of_sets and num_rounds are set for old saves
                if estado["tournament_data"]["tipo"] == "Grand Slam":
                    self.best_of_sets = 5
                    self.num_rounds = 7
                elif estado["tournament_data"]["tipo"] == "Davis Cup":
                    self.best_of_sets = 3 # Placeholder
                    self.num_rounds = 0 # Placeholder
                else:
                    self.best_of_sets = 3
                    self.num_rounds = 5
                self._salvar_estado(estado) # Save updated state

        return estado

    def _salvar_estado(self, estado):
        with open(self.caminho_json, "w", encoding="utf-8") as f:
            json.dump(estado, f, indent=2, ensure_ascii=False)

    def escolher_participantes(self, todos_jogadores):
        nome_jogador = self.jogador_nome.strip()
        nome_jogador_lower = nome_jogador.lower()

        # Adiciona o jogador principal ao ranking se não estiver lá
        jogador_principal_obj = {
            "nome": nome_jogador,
            "nacionalidade": self.jogador_nacionalidade,
        }
        if self.ranking.obter_posicao(nome_jogador) is None:
            self.ranking.adicionar_jogador_novo(jogador_principal_obj)
            self.ranking.salvar_ranking()
            # Recarrega o ranking para incluir o jogador principal
            self.ranking.carregar_ranking()
            self.ranking.ordenar()

        # Determina o tamanho da chave principal e do qualifying
        if self.tournament_data["tipo"] == "Grand Slam":
            tamanho_chave_principal = 128
            vagas_qualy = 16 # 4 rodadas de qualy para 16 vagas
            num_jogadores_qualy = 128 # 128 jogadores no qualy para 16 vagas
            num_top_diretos = 112 # 128 - 16
        else: # ATP 250/500/1000
            tamanho_chave_principal = 32
            vagas_qualy = 4 # 2 rodadas de qualy para 4 vagas
            num_jogadores_qualy = 16 # 16 jogadores no qualy para 4 vagas
            num_top_diretos = 28 # 32 - 4

        # Separa os jogadores do ranking
        jogadores_ranking_ordenado = self.ranking.ranking
        
        # Garante que o jogador principal esteja na lista de todos os jogadores
        if nome_jogador_lower not in [j["nome"].lower() for j in jogadores_ranking_ordenado]:
            jogadores_ranking_ordenado.append(jogador_principal_obj)
            self.ranking.adicionar_jogador_novo(jogador_principal_obj) # Adiciona ao ranking da instancia
            self.ranking.salvar_ranking() # Salva no disco
            self.ranking.carregar_ranking() # Recarrega para ordenar novamente
            jogadores_ranking_ordenado = self.ranking.ranking # Atualiza a lista
            self.ranking.ordenar() # Garante que está ordenado

        # Seleciona os jogadores para a chave principal (entrada direta)
        chave_principal = []
        qualy_players = []

        # Tenta preencher a chave principal com os melhores do ranking
        for j in jogadores_ranking_ordenado:
            if len(chave_principal) < num_top_diretos and j["nome"].lower() != nome_jogador_lower:
                chave_principal.append(j)
            elif j["nome"].lower() != nome_jogador_lower: # Jogadores restantes vão para o qualy
                qualy_players.append(j)
            
            # Se o jogador principal está entre os top diretos, adiciona ele
            if j["nome"].lower() == nome_jogador_lower and len(chave_principal) < num_top_diretos:
                chave_principal.append(j)

        # Se o jogador principal não foi para a chave principal, coloca ele no qualy
        if nome_jogador_lower not in [j["nome"].lower() for j in chave_principal]:
            if nome_jogador_lower not in [j["nome"].lower() for j in qualy_players]:
                qualy_players.insert(0, jogador_principal_obj) # Prioriza o jogador no qualy
            else: # Se já está no qualy, garante que esteja no início
                qualy_players.remove(jogador_principal_obj)
                qualy_players.insert(0, jogador_principal_obj)
        
        # Shuffle players for qualifying (excluding the main player if already placed)
        outros_qualy = [j for j in qualy_players if j["nome"].lower() != nome_jogador_lower]
        random.shuffle(outros_qualy)
        
        if nome_jogador_lower in [j["nome"].lower() for j in qualy_players]:
            final_qualy_list = [jogador_principal_obj] + outros_qualy
        else:
            final_qualy_list = outros_qualy

        final_qualy_list = final_qualy_list[:num_jogadores_qualy]

        # Completa com bots se não houver jogadores suficientes para o qualy
        while len(final_qualy_list) < num_jogadores_qualy:
            bot = gerar_jogador_fraco(len(final_qualy_list) + 1, self.tournament_data["pais_sede"])
            final_qualy_list.append(bot)

        # Garante que a chave principal tenha o número correto de jogadores
        # Se faltar, completa com os próximos do ranking que não foram para o qualy
        if len(chave_principal) < num_top_diretos:
            jogadores_nao_selecionados = [j for j in jogadores_ranking_ordenado if j not in chave_principal and j not in final_qualy_list]
            for j in jogadores_nao_selecionados:
                if len(chave_principal) < num_top_diretos:
                    chave_principal.append(j)
                else:
                    break

        # Se ainda faltar na chave principal, adiciona bots
        while len(chave_principal) < num_top_diretos:
            bot = gerar_jogador_fraco(len(chave_principal) + 1, self.tournament_data["pais_sede"])
            chave_principal.append(bot)


        print(f"\n🟢 Entrada direta ({len(chave_principal)} jogadores):")
        for j in chave_principal:
            nome = j["nome"]
            pos = self.ranking.obter_posicao(nome) or "N/A"
            destaque = "⭐" if nome.lower() == nome_jogador_lower else ""
            print(f"• {nome} {destaque} — #{pos}")

        print(f"\n🟡 Qualifying ({len(final_qualy_list)} jogadores):")
        for j in final_qualy_list:
            nome = j["nome"]
            pos = self.ranking.obter_posicao(nome) or "N/A"
            destaque = "⭐" if nome.lower() == nome_jogador_lower else ""
            print(f"• {nome} {destaque} — #{pos}")

        return chave_principal, final_qualy_list



    def jogar_qualy(self, jogadores_qualy):
        # Determine qualifying phases based on tournament type
        if self.tournament_data["tipo"] == "Grand Slam":
            qualy_phases = ["qualy_r1", "qualy_r2", "qualy_r3"]
            main_draw_phases = ["r128", "r64", "r32", "r16", "quartas", "semifinal", "final"]
        else: # ATP
            qualy_phases = ["qualy_1", "qualy_2"]
            main_draw_phases = ["pre_oitavas", "oitavas", "quartas", "semifinal", "final"]

        if not jogadores_qualy:
            print("⚠️ Sem jogadores para a qualificação.")
            return

        # Ensure a power of 2 for initial qualifying round (current qualy_r1/qualy_1 assumes 16 or 128)
        # Find the smallest power of 2 greater than or equal to len(jogadores_qualy)
        num_players_qualy_round1 = 1
        while num_players_qualy_round1 < len(jogadores_qualy):
            num_players_qualy_round1 *= 2
        
        # Pad with bots if needed to reach num_players_qualy_round1
        while len(jogadores_qualy) < num_players_qualy_round1:
            jogadores_qualy.append(gerar_jogador_fraco(len(jogadores_qualy) + 1, self.tournament_data["pais_sede"]))

        random.shuffle(jogadores_qualy)
        confrontos_qualy_r1 = list(zip(jogadores_qualy[::2], jogadores_qualy[1::2]))

        # Ensure player is in a confrontation
        nomes_confrontos_normalized = [normalizar_nome(a["nome"]) for a, _ in confrontos_qualy_r1] + \
                                      [normalizar_nome(b["nome"]) for _, b in confrontos_qualy_r1]
        if normalizar_nome(self.jogador_nome) not in nomes_confrontos_normalized:
            jogador_dict = {
                "nome": self.jogador_nome,
                "nacionalidade": self.jogador_nacionalidade,
            }
            # Find an empty slot or replace a bot
            found_slot = False
            for i, (p1, p2) in enumerate(confrontos_qualy_r1):
                if p1["nome"].startswith("Bot") or p2["nome"].startswith("Bot"):
                    if p1["nome"].startswith("Bot"):
                        confrontos_qualy_r1[i] = (jogador_dict, p2)
                    else:
                        confrontos_qualy_r1[i] = (p1, jogador_dict)
                    found_slot = True
                    break
            if not found_slot: # Fallback: replace first player in first match
                confrontos_qualy_r1[0] = (jogador_dict, confrontos_qualy_r1[0][1])

        rodadas_dict = {qualy_phases[0]: confrontos_qualy_r1}
        resultados_dict = {qualy_phases[0]: []}
        
        # Initialize other qualifying and main draw phases as empty
        for phase in qualy_phases[1:] + main_draw_phases:
            rodadas_dict[phase] = []
            resultados_dict[phase] = []

        estado = {
            "semana": self.semana,
            "torneio": self.nome_torneio,
            "fase_atual": qualy_phases[0],
            "jogador": self.jogador_nome,
            "jogador_vivo": True,
            "rodadas": rodadas_dict,
            "resultados": resultados_dict,
            "tournament_data": self.tournament_data, # Ensure tournament_data is saved
        }

        caminho = get_caminho_torneio_save(self.nome_save)
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

        if self.tournament_data["tipo"] == "Grand Slam":
            ordem = [
                "qualy_r1", "qualy_r2", "qualy_r3", # Assuming 3 rounds of qualifying for a GS
                "r128", "r64", "r32", "r16", "quartas", "semifinal", "final",
            ]
        elif self.tournament_data["tipo"] == "Davis Cup":
            # Davis Cup has a different format, this function might not be used directly for phase progression
            # For now, we'll return, assuming its progression is handled elsewhere or is simpler.
            return
        else: # ATP 250/500/1000 and others
            ordem = [
                "qualy_1", "qualy_2", # Current ATP qualifying structure
                "pre_oitavas", "oitavas", "quartas", "semifinal", "final",
            ]

        try:
            idx = ordem.index(fase)
        except ValueError:
            print(f"❌ Fase desconhecida: {fase}")
            return

        if idx + 1 >= len(ordem):
            estado["fase_atual"] = "finalizado"
            return

        # Nova lógica: busca SEMPRE o dicionário completo no ranking (id ou nome)
        vencedores = []
        for i, r in enumerate(estado["resultados"][fase]):
            jogador_obj = None
            nome_vencedor = None
            try:
                if isinstance(r, dict):
                    vencedor = r.get("vencedor")
                    id_ranking = (
                        vencedor.get("id_ranking")
                        if isinstance(vencedor, dict)
                        else None
                    )
                    nome_vencedor = (
                        vencedor.get("nome")
                        if isinstance(vencedor, dict)
                        else str(vencedor)
                    )
                    # Busca pelo id no ranking
                    if id_ranking and 1 <= id_ranking <= len(self.ranking.ranking):
                        jogador_obj = self.ranking.ranking[id_ranking - 1]
                    if not jogador_obj:
                        jogador_obj = self.ranking.buscar_jogador_por_nome(
                            nome_vencedor
                        )
                    if not jogador_obj:
                        raise ValueError(
                            f"Jogador '{nome_vencedor}' não encontrado no ranking."
                        )
                elif isinstance(r, str):
                    nome_vencedor = extrair_nome_puro(r)
                    jogador_obj = self.ranking.buscar_jogador_por_nome(nome_vencedor)
                    if not jogador_obj:
                        print(
                            f"⚠️ Resultado NPC: não encontrei '{nome_vencedor}' no ranking (veio de '{r}'). Usando dict mínimo."
                        )
                        jogador_obj = {"nome": nome_vencedor, "nacionalidade": "??"}

                else:
                    raise TypeError(f"Tipo inesperado em resultado: {type(r)}")
            except Exception as e:
                print(f"❌ Erro ao processar vencedor da posição {i} em '{fase}': {e}")
                jogador_obj = {
                    "nome": nome_vencedor if nome_vencedor else str(r),
                    "nacionalidade": "??",
                }
            vencedores.append(jogador_obj)

        # Função utilitária para corrigir lista de vencedores
        def corrigir_lista(vencedores, esperado, nome_bot):
            if len(vencedores) < esperado:
                print(
                    f"⚠️ Corrigindo número de vencedores ({len(vencedores)}) para {esperado} adicionando bots."
                )
                while len(vencedores) < esperado:
                    vencedores.append(
                        gerar_jogador_fraco(len(vencedores)+1, self.tournament_data["pais_sede"])
                    )
            elif len(vencedores) > esperado:
                print(
                    f"⚠️ Mais vencedores ({len(vencedores)}) que o esperado ({esperado}). Cortando excesso."
                )
                vencedores[:] = vencedores[:esperado]
            return vencedores

        proxima_fase = ordem[idx + 1]
        
        # Calculate the target number of players for the *next* phase's draw
        target_draw_size = 0
        if proxima_fase == "final":
            target_draw_size = 2
        elif proxima_fase == "semifinal":
            target_draw_size = 4
        elif proxima_fase == "quartas":
            target_draw_size = 8
        elif proxima_fase == "r16" or proxima_fase == "oitavas":
            target_draw_size = 16
        elif proxima_fase == "r32" or proxima_fase == "pre_oitavas":
            target_draw_size = 32
        elif proxima_fase == "r64":
            target_draw_size = 64
        elif proxima_fase == "r128":
            target_draw_size = 128
        # For qualifying rounds, the number of participants is usually a power of 2.
        # The 'vencedores' list should already contain the correct number of winners to form the next round.
        # If not, 'corrigir_lista' will pad it with bots.
        # The `target_draw_size` for a qualifying round is the number of players that will participate in *that* round.
        elif proxima_fase.startswith("qualy_"):
            target_draw_size = len(vencedores) # All winners advance to next qualy round
        else: # Fallback for new phases, assume single elimination
            target_draw_size = len(vencedores)

        # Correct the winners list to have the correct number of players for the next draw
        vencedores_corrigidos = corrigir_lista(vencedores, target_draw_size, f"Bot_{proxima_fase}")


        # If it's a phase where qualifiers merge into the main draw, the draw is created elsewhere (e.g., iniciar_torneio)
        # So, this `_atualizar_fase_se_necessario` function just advances the phase.
        is_merge_phase_to_main_draw = False
        if (self.tournament_data["tipo"] == "Grand Slam" and fase == "qualy_r3" and proxima_fase == "r128"):
            is_merge_phase_to_main_draw = True
        elif (self.tournament_data["tipo"] != "Grand Slam" and fase == "qualy_2" and proxima_fase == "pre_oitavas"):
            is_merge_phase_to_main_draw = True
        
        if is_merge_phase_to_main_draw:
            direct_entries = estado.get("direct_entries", [])
            expected_main_draw_size = 128 if self.tournament_data["tipo"] == "Grand Slam" else 32
            expected_qualifiers = 16 if self.tournament_data["tipo"] == "Grand Slam" else 4
            qualifiers = corrigir_lista(list(vencedores), expected_qualifiers, "BotQualyMain")

            main_draw_players = direct_entries + qualifiers
            while len(main_draw_players) < expected_main_draw_size:
                main_draw_players.append({"nome": f"BotMD{len(main_draw_players) + 1}", "nacionalidade": "??"})

            random.shuffle(main_draw_players)
            estado["rodadas"][proxima_fase] = [
                (self.garantir_dados_completos(a), self.garantir_dados_completos(b))
                for a, b in zip(main_draw_players[::2], main_draw_players[1::2])
            ]
            estado["resultados"][proxima_fase] = []
            estado["fase_atual"] = proxima_fase
        else:
            random.shuffle(vencedores_corrigidos) # Shuffle winners for the next round
            estado["rodadas"][proxima_fase] = [
                (self.garantir_dados_completos(a), self.garantir_dados_completos(b))
                for a, b in zip(vencedores_corrigidos[::2], vencedores_corrigidos[1::2])
            ]
            estado["resultados"][proxima_fase] = []
            estado["fase_atual"] = proxima_fase



    def _simular_partida_npc(self, a, b):
        vencedor = random.choice([a, b])
        perdedor = b if vencedor == a else a
        
        # Determine sets based on best_of_sets
        if self.best_of_sets == 5:
            sets_v = 3
            sets_d = random.choice([0, 1, 2])
        else: # best_of_sets == 3
            sets_v = 2
            sets_d = random.choice([0, 1])

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
        estado = carregar_estado_torneio(self.nome_save)
        if not estado:
            print("⚠️ Arquivo de torneio não encontrado.")
            return


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
        
        if self.tournament_data["tipo"] == "Grand Slam":
            fases_ordem = [
                "qualy_r1", "qualy_r2", "qualy_r3",
                "r128", "r64", "r32", "r16", "quartas", "semifinal", "final",
            ]
        elif self.tournament_data["tipo"] == "Davis Cup":
            print("\n⚠️ Simulação de torneio restante para Davis Cup não implementada. Retornando.")
            return # Davis Cup has special phase handling
        else: # ATP 250/500/1000 and others
            fases_ordem = [
                "qualy_1", "qualy_2",
                "pre_oitavas", "oitavas", "quartas", "semifinal", "final",
            ]

        while True:
            fase = estado["fase_atual"]
            confrontos = estado["rodadas"].get(fase, [])

            # INOVAÇÃO: Se está na final e não há confrontos, tenta gerar a final
            if fase == "final" and not confrontos:
                semifinal_resultados = estado["resultados"].get("semifinal", [])
                if len(semifinal_resultados) == 1:
                    # Padrão: só teve um confronto na semi
                    jogador_a = semifinal_resultados[0]["vencedor"]
                    jogador_b = (
                        semifinal_resultados[0]["jogador_a"]
                        if semifinal_resultados[0]["vencedor"]["nome"]
                        != semifinal_resultados[0]["jogador_a"]["nome"]
                        else semifinal_resultados[0]["jogador_b"]
                    )
                    final_confronto = [jogador_a, jogador_b]
                    estado["rodadas"]["final"] = [final_confronto]
                    confrontos = [final_confronto]
                elif len(semifinal_resultados) == 2:
                    # Duas semis: pega os dois vencedores
                    jogador_a = semifinal_resultados[0]["vencedor"]
                    jogador_b = semifinal_resultados[1]["vencedor"]
                    final_confronto = [jogador_a, jogador_b]
                    estado["rodadas"]["final"] = [final_confronto]
                    confrontos = [final_confronto]
                else:
                    # Não tem semifinal suficiente para montar a final
                    break

            if not confrontos:
                break  # Não há mais confrontos, fim do torneio

            novos_resultados = []
            for a, b in confrontos:
                vencedor, perdedor, placar = self._simular_partida_npc(a, b)
                resultado_dict = {
                    "jogador_a": self.garantir_dados_completos(a),
                    "jogador_b": self.garantir_dados_completos(b),
                    "vencedor": self.garantir_dados_completos(vencedor),
                    "resultado": placar,
                }
                novos_resultados.append(resultado_dict)

            estado["resultados"][fase].extend(novos_resultados)

            # Se simulou a final, finaliza!
            if fase == "final":
                estado["fase_atual"] = "finalizado"
                self._salvar_estado(estado)
                break

            self._atualizar_fase_se_necessario(estado)
            self._salvar_estado(estado)
            estado = self._carregar_estado()  # Recarrega para pegar a próxima fase

            # Verifica se já terminou
            if estado["fase_atual"] == "finalizado":
                break

        # Impressão do campeão
        resultados_final = estado["resultados"].get("final", [])
        if resultados_final:
            resultado_final = resultados_final[0]
            if isinstance(resultado_final, dict):
                campeao = resultado_final.get("vencedor", {}).get(
                    "nome", "Desconhecido"
                )
            else:
                campeao = resultado_final.split()[0]
            print(f"\n🏁 Torneio finalizado. Campeão: {campeao}")
        else:
            print("\n⚠️ Não foi possível simular a final corretamente.")

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
                # Monta dicionário padronizado
                id_jogador_a = self.ranking.obter_posicao(jogador_a["nome"])
                id_jogador_b = self.ranking.obter_posicao(jogador_b["nome"])
                id_vencedor = self.ranking.obter_posicao(vencedor["nome"])
                resultado_dict = {
                    "jogador_a": {
                        **self.garantir_dados_completos(jogador_a),
                        "id_ranking": id_jogador_a,
                    },
                    "jogador_b": {
                        **self.garantir_dados_completos(jogador_b),
                        "id_ranking": id_jogador_b,
                    },
                    "vencedor": {
                        **self.garantir_dados_completos(vencedor),
                        "id_ranking": id_vencedor,
                    },
                    "resultado": resultado,
                }
                novos_resultados.append(resultado_dict)
            else:
                novos_confrontos.append((a, b))  # Mantém o confronto do jogador

        estado["rodadas"][fase] = novos_confrontos
        estado["resultados"][fase].extend(novos_resultados)
        self._atualizar_fase_se_necessario(estado)
        self._salvar_estado(estado)

    def simular_torneio_npc(self, todos_jogadores_ranking):
        """
        Simula um torneio completo para NPCs e retorna o campeão.
        Não salva o estado do torneio para o save_file principal.
        """
        # Criar um nome de save temporário para não sobrescrever o save do jogador
        temp_save_name = f"temp_npc_torneio_{self.nome_torneio_atual}_{self.semana}"
        temp_caminho_json = get_caminho_torneio_save(temp_save_name)

        # Ensure the directory for the temporary save exists
        os.makedirs(os.path.dirname(temp_caminho_json), exist_ok=True)

        # Need to create a dummy Torneio instance for the simulation
        # Use a dummy player name for this instance
        dummy_player_name = "NPC_Dummy_Player"
        dummy_player_nacionalidade = "??"

        temp_instance = Torneio(
            tournament_data=self.tournament_data,
            jogador_nome=dummy_player_name, # A dummy player name
            jogador_nacionalidade=dummy_player_nacionalidade,
            ranking=self.ranking, # Use the main ranking
            nome_save=temp_save_name,
        )
        
        # Initialize the tournament state for the NPC tournament
        estado_npc_torneio = {
            "torneio": self.nome_torneio_atual,
            "semana": self.semana,
            "fase_atual": "qualy_1" if temp_instance.tournament_data.get("qualificacao", False) else temp_instance._get_first_main_draw_phase(), # Start with qualy or first main draw phase
            "rodadas": {},
            "resultados": {},
            "jogador": dummy_player_name,
            "jogador_vivo": False, # NPC tournament, no user player
            "tournament_data": self.tournament_data,
        }

        # Initialize phases dynamically
        if self.tournament_data["tipo"] == "Grand Slam":
            qualy_phases = ["qualy_r1", "qualy_r2", "qualy_r3"]
            main_draw_phases = ["r128", "r64", "r32", "r16", "quartas", "semifinal", "final"]
        else: # ATP
            qualy_phases = ["qualy_1", "qualy_2"]
            main_draw_phases = ["pre_oitavas", "oitavas", "quartas", "semifinal", "final"]

        all_phases = qualy_phases + main_draw_phases
        for phase in all_phases:
            estado_npc_torneio["rodadas"][phase] = []
            estado_npc_torneio["resultados"][phase] = []
        
        # Save initial state of the NPC tournament
        with open(temp_caminho_json, "w", encoding="utf-8") as f:
            json.dump(estado_npc_torneio, f, indent=2, ensure_ascii=False)

        # Get participants
        # We need a list of players *not* including the actual user player
        filtered_todos_jogadores = [p for p in todos_jogadores_ranking if normalizar_nome(p["nome"]) != normalizar_nome(self.jogador_nome)]
        
        # Use escolher_participantes with the dummy instance. This will generate the draws.
        # But we need to ensure it's not trying to insert the *user's* player
        # The escolher_participantes method already handles inserting a player (if not found in ranking)
        # So, for NPC simulation, we might need a version of escolher_participantes that doesn't prioritize a specific player.
        # For simplicity for now, let's pass a very low-ranked dummy player name to escolher_participantes
        temp_instance.jogador_nome = "Lowest_Rank_Bot"
        temp_instance.jogador_nacionalidade = "??"
        
        direct_entries, qualifying_players = temp_instance.escolher_participantes(filtered_todos_jogadores)

        # Run qualifying (all NPC matches)
        if qualifying_players:
            temp_instance.jogar_qualy(qualifying_players)
            # Simulate all qualy matches
            temp_instance.simular_torneio_restante(filtered_todos_jogadores) # This will simulate all qualy matches and advance phases
            
            # Reload state after qualy simulation
            estado_npc_torneio = carregar_estado_torneio(temp_save_name)
            qualy_final_phase = ""
            num_expected_qualifiers = 0
            if temp_instance.tournament_data["tipo"] == "Grand Slam":
                qualy_final_phase = "qualy_r3"
                num_expected_qualifiers = 16
            else:
                qualy_final_phase = "qualy_2"
                num_expected_qualifiers = 4
            
            qualifiers = []
            if qualy_final_phase in estado_npc_torneio["resultados"] and estado_npc_torneio["resultados"][qualy_final_phase]:
                qualifiers = [r["vencedor"] for r in estado_npc_torneio["resultados"][qualy_final_phase]]
            
            while len(qualifiers) < num_expected_qualifiers:
                qualifiers.append(gerar_jogador_fraco(len(qualifiers)+1, self.tournament_data["pais_sede"]))
        else:
            qualifiers = []

        # Create main draw
        main_draw_players = direct_entries + qualifiers
        random.shuffle(main_draw_players)

        first_main_draw_phase = ""
        if temp_instance.tournament_data["tipo"] == "Grand Slam":
            first_main_draw_phase = "r128"
        else:
            first_main_draw_phase = "pre_oitavas"
        
        # Set the first main draw round in the temp_instance's state
        estado_npc_torneio["rodadas"][first_main_draw_phase] = [
            (temp_instance.garantir_dados_completos(a), temp_instance.garantir_dados_completos(b))
            for a, b in zip(main_draw_players[::2], main_draw_players[1::2])
        ]
        estado_npc_torneio["fase_atual"] = first_main_draw_phase
        estado_npc_torneio["resultados"][first_main_draw_phase] = []
        
        with open(temp_caminho_json, "w", encoding="utf-8") as f:
            json.dump(estado_npc_torneio, f, indent=2, ensure_ascii=False)

        # Simulate main draw
        temp_instance.simular_torneio_restante(filtered_todos_jogadores)
        
        # Get champion
        estado_npc_torneio = carregar_estado_torneio(temp_save_name) # Reload final state
        champion = None
        if "final" in estado_npc_torneio["resultados"] and estado_npc_torneio["resultados"]["final"]:
            champion = estado_npc_torneio["resultados"]["final"][0]["vencedor"]

        # Clean up temporary save file
        os.remove(temp_caminho_json)
        
        return champion

    def jogador_ainda_ativo(self):
        estado = self._carregar_estado()
        return estado.get("jogador_vivo", True)

    def exibir_resultados(self):
        estado = self._carregar_estado()
        
        if self.tournament_data["tipo"] == "Grand Slam":
            fases_ordenadas = [
                "qualy_r1", "qualy_r2", "qualy_r3",
                "r128", "r64", "r32", "r16", "quartas", "semifinal", "final",
            ]
        elif self.tournament_data["tipo"] == "Davis Cup":
            print("\n📊 Resultados da Davis Cup (formato de equipes, em breve).")
            return
        else: # ATP 250/500/1000 and others
            fases_ordenadas = [
                "qualy_1", "qualy_2",
                "pre_oitavas", "oitavas", "quartas", "semifinal", "final",
            ]

        ultima_fase = next(
            (f for f in reversed(fases_ordenadas) if estado["resultados"].get(f)), None
        )
        if ultima_fase:
            print(f"\n📊 Resultados da fase {ultima_fase}:")
            for r in estado["resultados"][ultima_fase]:
                if isinstance(r, dict):
                    nome_a = r["jogador_a"]["nome"]
                    nome_b = r["jogador_b"]["nome"]
                    nome_vencedor = (
                        r["vencedor"]["nome"]
                        if isinstance(r["vencedor"], dict)
                        else str(r["vencedor"])
                    )
                    placar = r["resultado"]
                    print(f"- {nome_a} vs {nome_b} | 🏆 {nome_vencedor} ({placar})")
                else:
                    print("-", r)
        else:
            print("\n📊 Nenhum resultado disponível ainda.")

    def exibir_confrontos_fase_atual(self):
        estado = self._carregar_estado()
        fase = estado["fase_atual"]
        print(f"\n🗓️ Confrontos da fase {fase}:")
        for idx, confronto in enumerate(estado["rodadas"].get(fase, []), 1):
            # Novo formato (dicionário de jogadores)
            if isinstance(confronto, dict):
                nome_a = confronto.get("jogador_a", {}).get("nome", "?")
                nome_b = confronto.get("jogador_b", {}).get("nome", "?")
            else:
                # Formato antigo: tupla/lista de dicts ou strings
                jogador_a = confronto[0]
                jogador_b = confronto[1]
                nome_a = (
                    jogador_a.get("nome")
                    if isinstance(jogador_a, dict)
                    else str(jogador_a)
                )
                nome_b = (
                    jogador_b.get("nome")
                    if isinstance(jogador_b, dict)
                    else str(jogador_b)
                )
            print(f"{idx}. {nome_a} vs {nome_b}")

    def iniciar_torneio(self, nome_torneio, todos_jogadores):
        try:
            estado = self._carregar_estado()
            estado["torneio"] = nome_torneio
            self._salvar_estado(estado)

            direct_entries, qualifying_players = self.escolher_participantes(todos_jogadores)
            jogador_direct = normalizar_nome(self.jogador_nome) in [
                normalizar_nome(j["nome"]) for j in direct_entries
            ]

            if self.tournament_data["tipo"] == "Davis Cup":
                print(f"\n📁 Torneio {nome_torneio} (Davis Cup) iniciado com sucesso e salvo. Formato de equipes.")
                # Davis Cup logic will be implemented separately.
                # For now, just initialize a dummy state or handle its unique structure.
                # Example: create groups, then playoffs.
                return
            elif self.tournament_data["tipo"] == "United Cup":
                print(f"\n📁 Torneio {nome_torneio} (United Cup) iniciado com sucesso e salvo. Formato de equipes mistas.")
                print("⚠️ A lógica para a United Cup ainda não foi implementada. O torneio será ignorado por enquanto.")
                return

            # --- Qualifying Tournament ---
            qualifiers = []
            if qualifying_players and self.tournament_data.get("qualificacao", True):
                self.jogar_qualy(qualifying_players)
                estado = self._carregar_estado()
                estado["direct_entries"] = direct_entries
                self._salvar_estado(estado)

                if jogador_direct:
                    while estado["fase_atual"].startswith("qualy"):
                        self.simular_npcs_na_fase_atual("__npc_only__")
                        estado = self._carregar_estado()

                    qualy_final_phase = "qualy_r3" if self.tournament_data["tipo"] == "Grand Slam" else "qualy_2"
                    if qualy_final_phase in estado["resultados"] and estado["resultados"][qualy_final_phase]:
                        qualifiers = [r["vencedor"] for r in estado["resultados"][qualy_final_phase]]
                        print(f"✅ Classificados do qualifying ({len(qualifiers)}): {[j['nome'] for j in qualifiers]}")
                    print(f"\n📁 Torneio {nome_torneio} iniciado com sucesso e salvo. Chave principal gerada.")
                    return
                else:
                    print("🟡 Qualifying iniciado. A chave principal será gerada após o qualifying.")
                    return
            else:
                print("⚠️ Sem qualifying para este torneio.")

            # --- Main Draw Creation ---
            main_draw_players = direct_entries + qualifiers

            # Ensure the total number of players for the main draw is correct
            expected_main_draw_size = 0
            if self.tournament_data["tipo"] == "Grand Slam":
                expected_main_draw_size = 128
            else: # ATP
                expected_main_draw_size = 32
            
            # Pad with bots if needed (shouldn't happen if escolher_participantes is correct)
            while len(main_draw_players) < expected_main_draw_size:
                 main_draw_players.append(gerar_jogador_fraco(len(main_draw_players) + 1, self.tournament_data["pais_sede"]))
            
            random.shuffle(main_draw_players) # Shuffle for draw

            # Create initial main draw matchups
            first_main_draw_phase = ""
            if self.tournament_data["tipo"] == "Grand Slam":
                first_main_draw_phase = "r128"
            else: # ATP
                first_main_draw_phase = "pre_oitavas"
            
            confrontos_main_draw = [(self.garantir_dados_completos(a), self.garantir_dados_completos(b))
                                    for a, b in zip(main_draw_players[::2], main_draw_players[1::2])]
            
            # Ensure the player is in the main draw (if they didn't get direct entry and didn't qualify, or if they are bot-replaced)
            player_in_main_draw = normalizar_nome(self.jogador_nome) in [normalizar_nome(p["nome"]) for p in main_draw_players]
            
            if not player_in_main_draw:
                # If player is not in main draw, put them in a random slot, replacing a bot or low-ranked player
                for i, (p1, p2) in enumerate(confrontos_main_draw):
                    if p1["nome"].startswith("Bot") or p2["nome"].startswith("Bot"):
                        if p1["nome"].startswith("Bot"):
                            confrontos_main_draw[i] = ({"nome": self.jogador_nome, "nacionalidade": self.jogador_nacionalidade}, p2)
                        else:
                            confrontos_main_draw[i] = (p1, {"nome": self.jogador_nome, "nacionalidade": self.jogador_nacionalidade})
                        break
                
            estado["rodadas"][first_main_draw_phase] = confrontos_main_draw
            estado["fase_atual"] = first_main_draw_phase # Set current phase to first main draw round
            estado["resultados"][first_main_draw_phase] = [] # Clear results for this phase

            self._salvar_estado(estado)

            print(f"\n📁 Torneio {nome_torneio} iniciado com sucesso e salvo. Chave principal gerada.")
        except Exception as e:
            print(f"❌ Erro ao iniciar torneio: {e}")

    def _obter_fase_index(self, fase):
        if self.tournament_data["tipo"] == "Grand Slam":
            fases_ordem = [
                "qualy_r1", "qualy_r2", "qualy_r3",
                "r128", "r64", "r32", "r16", "quartas", "semifinal", "final",
            ]
        elif self.tournament_data["tipo"] == "Davis Cup":
            return -1 # Davis Cup has special phase handling, this index is not directly applicable
        else: # ATP 250/500/1000 and others
            fases_ordem = [
                "qualy_1", "qualy_2",
                "pre_oitavas", "oitavas", "quartas", "semifinal", "final",
            ]
        return fases_ordem.index(fase) if fase in fases_ordem else -1

    def normalizar_confrontos(self, confrontos_raw):
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

        caminho = get_caminho_torneio_save(self.nome_save)
        estado = carregar_estado_torneio(self.nome_save)

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

    @property
    def nome_torneio(self):
        return self.nome_torneio_atual

    def jogar_partida_do_jogador(self, jogador, nome_save):
        estado = self._carregar_estado()
        fase = estado["fase_atual"]

        # Localiza o confronto do jogador
        confronto_jogador = None
        adversario = None  # Inicializa para evitar erro

        for a, b in estado["rodadas"].get(fase, []):
            nome_a = a["nome"] if isinstance(a, dict) else a
            nome_b = b["nome"] if isinstance(b, dict) else b
            if normalizar_nome(nome_a) == normalizar_nome(jogador.nome):
                adversario = b if nome_a == jogador.nome else a
                confronto_jogador = (a, b)
                break
            if normalizar_nome(nome_b) == normalizar_nome(jogador.nome):
                adversario = a if nome_b == jogador.nome else b
                confronto_jogador = (a, b)
                break

        if adversario is None:
            print("Você não tem confronto nesta fase ou já jogou sua partida.")
            return {
                "msg": "Nenhum confronto para o jogador nesta fase.",
                "fase_eliminacao": None,
                "eliminado": False,
            }

        # Agora sim, chama a partida!
        # Cria a configuração da partida baseada nos dados do torneio
        config_partida = criar_config_partida(self.tournament_data)
        vencedor_nome, placar_final, pontos_disputados = jogar_partida(
            jogador, adversario, self.nome_save, config=config_partida
        )
        vencedor = {"nome": vencedor_nome}

        # Atualiza o resultado do torneio
        self.processar_resultado_partida(jogador, adversario, vencedor, placar_final)
        
        # Simula as outras partidas da fase
        self.simular_npcs_na_fase_atual(jogador.nome)

        # Lida com o ganho de XP e possível level up
        vitoria = normalizar_nome(vencedor_nome) == normalizar_nome(jogador.nome)
        jogador = handle_xp_e_level_up(jogador, vitoria)

        # Lida com o aumento de fadiga e possível lesão
        jogador = handle_fadiga_e_lesao(jogador, pontos_disputados=pontos_disputados)

        # Salva o estado do jogador (com XP e fadiga atualizados)
        salvar_jogo(nome_save, jogador)

        # Checa se foi eliminado
        jogador_ativo = self.jogador_ainda_ativo()

        # Avança para a próxima fase (se todas as partidas acabaram)
        avancar_fase(self)

        # Recupera energia se o jogador avançou de fase
        estado_atualizado = self._carregar_estado()
        if jogador_ativo and estado_atualizado["fase_atual"] != fase:
            jogador = recuperar_energia_entre_rodadas(jogador)
            salvar_jogo(nome_save, jogador)

        return {
            "msg": "✅ Partida jogada e resultados atualizados!",
            "fase_eliminacao": fase if not jogador_ativo else None,
            "eliminado": not jogador_ativo,
            "jogador": jogador, # Retorna o objeto jogador atualizado
        }

    def buscar_jogador_completo(self, nome):
        """Busca um jogador completo pelo nome (ou ID, se quiser expandir depois)."""
        jogador = self.ranking.buscar_jogador_por_nome(nome)
        if jogador:
            return jogador
        # fallback: tenta buscar por partes do nome se necessário
        for j in self.ranking.ranking:
            if nome in j["nome"]:
                return j
        # fallback final
        print(
            f"⚠️ Jogador '{nome}' não encontrado no ranking, retornando dicionário mínimo."
        )
        return {"nome": nome, "nacionalidade": "??"}


def criar_torneio(torneio_escolhido, jogador, nome_save, semana):
    # Cria instância do ranking para ser usada pelo torneio
    ranking_path = get_caminho_ranking_save(nome_save)
    ranking = SistemaRanking(ranking_path)

    # Add semana to torneio_escolhido for the Torneio class
    torneio_escolhido["semana"] = semana

    instancia = Torneio(
        tournament_data=torneio_escolhido,
        jogador_nome=jogador.nome,
        jogador_nacionalidade=jogador.nacionalidade,
        ranking=ranking,
        nome_save=nome_save,
    )

    # Cria a estrutura do torneio no disco
    instancia.iniciar_torneio(instancia.nome_torneio, ranking.ranking)
    return instancia


def salvar_torneio(instancia):
    """
    Salva o estado atual do torneio associado à instância no arquivo correto do save.
    """
    caminho_json = get_caminho_torneio_save(instancia.nome_save)
    estado = instancia._carregar_estado()
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(estado, f, indent=2, ensure_ascii=False)


def carregar_torneio(nome_save):
    ranking_path = get_caminho_ranking_save(nome_save)
    ranking = SistemaRanking(ranking_path)

    estado = carregar_estado_torneio(nome_save)
    if not estado:
        return None  # Ou levantar um erro

    jogador_nome = estado["jogador"]
    # Busca nacionalidade no ranking pelo nome do jogador:
    jogador_obj = next((j for j in ranking.ranking if j["nome"] == jogador_nome), None)
    jogador_nacionalidade = jogador_obj["nacionalidade"] if jogador_obj else "??"

    # Retrieve tournament_data from the saved state
    tournament_data = estado.get("tournament_data")
    if not tournament_data:
        # Fallback for old saves that don't have tournament_data directly
        from src.calendario import obter_torneio_por_nome
        tournament_data = obter_torneio_por_nome(estado["semana"], estado["torneio"])
        if not tournament_data:
            print(f"⚠️ Não foi possível carregar os dados do torneio {estado['torneio']} da semana {estado['semana']}.")
            return None # Or raise an error

    instancia = Torneio(
        tournament_data=tournament_data,
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
        # Considera que o nome está ANTES do placar " x "
        partes = resultado.split(" x ")
        if len(partes) > 1:
            nome = " x ".join(partes[:-1]).strip()
            # Se tiver sets "Fulano 2", remove o número do final
            nome = nome.rstrip("0123456789").strip()
            return nome
        else:
            return resultado.strip()
    else:
        return "Desconhecido"
