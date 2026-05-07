import os
import random
from copy import deepcopy

from src.calendario_participacao import (
    ajustar_prob_participacao_por_contexto,
    prob_participacao,
)
from src.dados import (
    carregar_estado_torneio,
    get_caminho_torneio_save,
)
from src.jogador import normalizar_nome
from src.progressao import evoluir_npc_pos_torneio
from src.imprensa import disparar_entrevista
from src.gerador_nomes import gerar_jogador_fraco
from src.json_utils import salvar_json_seguro
from src.torneio_profile import (
    TOURNAMENT_PROFILES,
    ENTRY_DIRECT_SELECTORS,
    WILDCARD_POLICIES,
    WILDCARD_OVERRIDES,
)
from src.torneio_entry_config import ENTRY_DIRECT_CONFIGS
from src.torneio_constants import (
    RANKING_POSICAO_FALLBACK,
    RANKING_LIMITE_CHALLENGER,
    RANKING_LIMITE_ENTRADA_DIRETA,
    RANKING_LIMITE_ITF,
    SEEDS_ATP_1000,
)
from src.torneio_npc import simular_partida_npc_basica
from src.torneio_utils import (
    extrair_codigo_pais,
    mesmo_pais,
    deduplicar_jogadores,
    weighted_sample_sem_reposicao,
    garantir_dados_completos,
)
from src.torneio_logic import (
    obter_rank_entrada,
    selecionar_entrada_direta,
    selecionar_campo_finals,
)
from src.log_jogo import log_erro


class Torneio:
    def __init__(
        self,
        tournament_data,
        jogador_nome,
        jogador_nacionalidade,
        ranking,
        nome_save=None,
        genero="masculino",
    ):
        self.nome_save = nome_save
        self.tournament_data = tournament_data
        self.semana = (
            int(tournament_data["semana"]) if "semana" in tournament_data else 1
        )
        self.nome_torneio_atual = tournament_data["nome"]
        self.jogador_nome = jogador_nome
        self.jogador_nacionalidade = jogador_nacionalidade
        self.ranking = ranking
        self.genero = genero
        self.caminho_json = get_caminho_torneio_save(self.nome_save, self.genero)
        self._estado_cache = None
        self._estado_cache_mtime = None
        self._ultima_entry_info = {}
        self._perfil = self._resolver_perfil_torneio()

        # Define best_of_sets based on tournament profile and gender.
        if self.genero == "feminino":
            self.best_of_sets = self._perfil["best_of_sets_feminino"]
        else:
            self.best_of_sets = self._perfil["best_of_sets_masculino"]

        # Define number of rounds based on tournament profile.
        self.num_rounds = 0 if self._is_davis_cup() else self._perfil["num_rounds"]

    def _tipo_torneio(self):
        tournament_data = getattr(self, "tournament_data", None) or {}
        if isinstance(tournament_data, dict):
            return tournament_data.get("tipo", "")
        return ""

    def _is_grand_slam(self):
        return self._tipo_torneio() == "Grand Slam"

    def _is_atp_1000(self):
        return "1000" in self._tipo_torneio()

    def _is_finals(self):
        tipo = self._tipo_torneio()
        return (
            tipo == "ATP Finals"
            or tipo == "WTA Finals"
            or tipo == "Next Gen ATP Finals"
        )

    def _is_davis_cup(self):
        return self._tipo_torneio() in {"Davis Cup", "Billie Jean King Cup"}

    def _is_united_cup(self):
        return self._tipo_torneio() == "United Cup"

    def _nome_competicao_equipes(self):
        tipo = self._tipo_torneio()
        if tipo in {"Davis Cup", "Billie Jean King Cup", "United Cup"}:
            return tipo
        return "Davis Cup"

    def _usa_entrada_direta_ranqueados(self):
        return bool(self._perfil.get("usa_entrada_direta_ranqueados", False))

    def _resolver_perfil_torneio(self):
        tipo = self._tipo_torneio()
        tipo_lower = str(tipo or "").lower()
        if tipo == "Grand Slam":
            return TOURNAMENT_PROFILES["grand_slam"]
        if "1000" in tipo:
            return TOURNAMENT_PROFILES["atp_1000"]
        if "Finals" in tipo:
            return TOURNAMENT_PROFILES["atp_finals"]
        if "challenger" in tipo_lower:
            return TOURNAMENT_PROFILES["challenger_125"]
        if "itf" in tipo_lower:
            return TOURNAMENT_PROFILES["itf_padrao"]
        return TOURNAMENT_PROFILES["atp_padrao"]

    def _fases_qualy(self):
        return list(self._perfil["qualy_phases"])

    def _fases_main_draw(self):
        return list(self._perfil["main_draw_phases"])

    def _fases_ordem(self):
        return self._fases_qualy() + self._fases_main_draw()

    def _is_merge_phase_to_main_draw(self, fase, proxima_fase):
        return (fase, proxima_fase) in self._perfil["merge_transitions"]

    def _selector_entrada_direta(self):
        selector_name = ENTRY_DIRECT_SELECTORS.get(self._tipo_torneio())
        return selector_name

    def _politica_wildcard(self):
        return WILDCARD_POLICIES.get(self._tipo_torneio(), WILDCARD_POLICIES["default"])

    def _num_wildcards(self):
        return WILDCARD_OVERRIDES.get(self._tipo_torneio(), self._perfil["wildcards"])

    def garantir_dados_completos(self, jogador):
        return garantir_dados_completos(jogador, self.ranking)

    def _deduplicar_jogadores(self, jogadores):
        return deduplicar_jogadores(jogadores)

    def _weighted_sample_sem_reposicao(self, itens, pesos, k):
        return weighted_sample_sem_reposicao(itens, pesos, k)

    def _obter_rank_entrada(self, jogador):
        return obter_rank_entrada(jogador, self.ranking)

    def _selecionar_entrada_direta(
        self,
        jogadores_ranking_ordenado,
        num_top_diretos,
        nome_jogador_lower,
        priorizar_jogador,
        cfg,
    ):
        return selecionar_entrada_direta(
            self.ranking,
            jogadores_ranking_ordenado,
            num_top_diretos,
            self.jogador_nome,
            self.jogador_nacionalidade,
            priorizar_jogador,
            cfg,
        )

    def _selecionar_entrada_direta_atp250(
        self,
        jogadores_ranking_ordenado,
        num_top_diretos,
        nome_jogador_lower,
        priorizar_jogador,
    ):
        return self._selecionar_entrada_direta(
            jogadores_ranking_ordenado,
            num_top_diretos,
            nome_jogador_lower,
            priorizar_jogador,
            ENTRY_DIRECT_CONFIGS["ATP 250"],
        )

    def _selecionar_entrada_direta_atp500(
        self,
        jogadores_ranking_ordenado,
        num_top_diretos,
        nome_jogador_lower,
        priorizar_jogador,
    ):
        return self._selecionar_entrada_direta(
            jogadores_ranking_ordenado,
            num_top_diretos,
            nome_jogador_lower,
            priorizar_jogador,
            ENTRY_DIRECT_CONFIGS["ATP 500"],
        )

    def _selecionar_entrada_direta_challenger(
        self,
        jogadores_ranking_ordenado,
        num_top_diretos,
        nome_jogador_lower,
        priorizar_jogador,
    ):
        return self._selecionar_entrada_direta(
            jogadores_ranking_ordenado,
            num_top_diretos,
            nome_jogador_lower,
            priorizar_jogador,
            ENTRY_DIRECT_CONFIGS["Challenger 125"],
        )

    def _selecionar_entrada_direta_itf100(
        self,
        jogadores_ranking_ordenado,
        num_top_diretos,
        nome_jogador_lower,
        priorizar_jogador,
    ):
        return self._selecionar_entrada_direta(
            jogadores_ranking_ordenado,
            num_top_diretos,
            nome_jogador_lower,
            priorizar_jogador,
            ENTRY_DIRECT_CONFIGS["ITF 100"],
        )

    def _selecionar_entrada_direta_itf25(
        self,
        jogadores_ranking_ordenado,
        num_top_diretos,
        nome_jogador_lower,
        priorizar_jogador,
    ):
        return self._selecionar_entrada_direta(
            jogadores_ranking_ordenado,
            num_top_diretos,
            nome_jogador_lower,
            priorizar_jogador,
            ENTRY_DIRECT_CONFIGS["ITF 25"],
        )

    def _selecionar_campo_finals(
        self,
        jogadores_ranking_ordenado,
        num_top_diretos,
        nome_jogador_lower,
        priorizar_jogador,
    ):
        return selecionar_campo_finals(jogadores_ranking_ordenado, num_top_diretos)

    def _get_bot_pool(self, tamanho):
        ranking_atual = self.ranking.ranking
        bots = [
            j for j in ranking_atual if j.get("is_bot") and j.get("origem") == "gs_pool"
        ]
        if len(bots) < tamanho:
            faltam = tamanho - len(bots)
            for i in range(faltam):
                bots.append(gerar_jogador_fraco(f"newgen_{i}", genero=self.genero))
        random.shuffle(bots)
        return bots[:tamanho]

    def _gerar_npc_suporte(self, id_newgen, pais_sede=None):
        npc = gerar_jogador_fraco(id_newgen, pais_sede, genero=self.genero)
        npc["is_bot"] = False  # Trata como NPC real do tour
        npc["e_ficticio"] = True
        npc.setdefault("origem", "torneio_suporte")
        return npc

    def _extrair_codigo_pais(self, valor):
        return extrair_codigo_pais(valor)

    def _mesmo_pais(self, a, b):
        return mesmo_pais(a, b)

    def _promover_protected_ranking(self, chave_principal, qualy_players):
        """Move jogadores com PR de volta para a chave principal se necessário."""
        promovidos = []
        for j in qualy_players[:]:
            if int(j.get("protected_ranking_semanas", 0) or 0) > 0:
                pr = int(j.get("protected_ranking", 9999))
                if pr <= RANKING_LIMITE_ENTRADA_DIRETA:
                    promovidos.append(j)
                    qualy_players.remove(j)
        return chave_principal + promovidos

    def _numero_seeds_main_draw(self, draw_size):
        if draw_size >= 128:
            return 32
        if draw_size >= 64:
            return 16
        if draw_size >= 32:
            return 8
        if draw_size >= 16:
            return 4
        return 2

    def _seed_positions(self, draw_size, num_seeds):
        from src.torneio_draw import seed_positions

        return seed_positions(draw_size, num_seeds)

    def _montar_chave_principal(self, jogadores, draw_size):
        from src.torneio_draw import montar_chave_principal

        return montar_chave_principal(
            jogadores, draw_size, self.ranking, self.garantir_dados_completos
        )

    def _main_draw_tem_vagas_invalidas(self, confrontos):
        for confronto in confrontos:
            if not isinstance(confronto, (list, tuple)) or len(confronto) != 2:
                return True
            if confronto[0] is None or confronto[1] is None:
                return True
        return False

    def _completar_participantes_main_draw(
        self, estado, jogadores_main_draw, draw_size
    ):
        jogadores_completos = self._deduplicar_jogadores(
            [self.garantir_dados_completos(jogador) for jogador in jogadores_main_draw]
        )
        faltantes = max(0, draw_size - len(jogadores_completos))
        if faltantes == 0:
            return jogadores_completos

        alternates = [
            self.garantir_dados_completos(jogador)
            for jogador in estado.get("alternates", [])
        ]
        nomes_existentes = {
            normalizar_nome(j.get("nome", "")) for j in jogadores_completos
        }
        for alternate in alternates:
            nome_alt = normalizar_nome(alternate.get("nome", ""))
            if nome_alt in nomes_existentes:
                continue
            jogadores_completos.append(alternate)
            nomes_existentes.add(nome_alt)
            faltantes -= 1
            if faltantes == 0:
                return jogadores_completos

        if faltantes > 0:
            for bot in self._get_bot_pool(faltantes):
                bot_completo = self.garantir_dados_completos(bot)
                nome_bot = normalizar_nome(bot_completo.get("nome", ""))
                if nome_bot in nomes_existentes:
                    continue
                jogadores_completos.append(bot_completo)
                nomes_existentes.add(nome_bot)
                faltantes -= 1
                if faltantes == 0:
                    break

        return jogadores_completos

    def _montar_rodada_inicial_main_draw(self, estado, jogadores_main_draw):
        fase_inicial = self._get_first_main_draw_phase()
        draw_size = self._perfil["draw_size_main"]
        jogadores_serializados = self._completar_participantes_main_draw(
            estado, jogadores_main_draw, draw_size
        )
        if fase_inicial == "r96" and self._is_atp_1000():
            seeds, confrontos = self._montar_draw_r96_atp1000(jogadores_serializados)
            estado["seed_entries"] = seeds
            estado["rodadas"][fase_inicial] = confrontos
            return

        estado["rodadas"][fase_inicial] = self._montar_chave_principal(
            jogadores_serializados, draw_size
        )

    def _reparar_main_draw_se_necessario(self, estado):
        fase_inicial = self._get_first_main_draw_phase()
        if not fase_inicial:
            return False

        confrontos = estado.get("rodadas", {}).get(fase_inicial, [])
        if not confrontos or not self._main_draw_tem_vagas_invalidas(confrontos):
            return False

        classificados = []
        fases_qualy = self._fases_qualy()
        if fases_qualy:
            ultima_fase_qualy = fases_qualy[-1]
            for resultado in estado.get("resultados", {}).get(ultima_fase_qualy, []):
                vencedor = resultado.get("vencedor")
                if vencedor:
                    classificados.append(vencedor)

        direct_entries = estado.get("direct_entries", [])
        jogadores_main_draw = self._deduplicar_jogadores(
            list(direct_entries) + list(classificados)
        )
        self._montar_rodada_inicial_main_draw(estado, jogadores_main_draw)
        return True

    def _configurar_fase_inicial_com_qualy(self, estado, qualy_players):
        fases_qualy = self._fases_qualy()
        if not fases_qualy or not qualy_players:
            return False

        fase_inicial = fases_qualy[0]
        estado["fase_atual"] = fase_inicial
        estado["rodadas"][fase_inicial] = self._montar_qualifying(
            deepcopy(qualy_players),
            self._perfil["vagas_qualy"],
            fases_qualy,
        )
        return bool(estado["rodadas"][fase_inicial])

    def _montar_main_draw_a_partir_do_qualy(self, estado, classificados):
        direct_entries = estado.get("direct_entries", [])
        jogadores_main_draw = self._deduplicar_jogadores(
            list(direct_entries) + list(classificados)
        )
        self._montar_rodada_inicial_main_draw(estado, jogadores_main_draw)

    def _get_first_main_draw_phase(self):
        if self._is_davis_cup():
            return ""
        return self._perfil.get("main_draw_first_phase", "")

    def _aplicar_entry_info_estado(self, estado, entry_info):
        estado["entry_status"] = entry_info.get("status_entry", {})
        estado["cutoff_rank"] = entry_info.get("cutoff_rank")
        estado["alternates"] = entry_info.get("alternates", [])
        return estado

    def _expected_main_draw_size(self):
        return self._perfil["draw_size_first_main_phase"]

    def _montar_rodada_r96(self, main_draw_players, incluir_jogador_principal=False):
        """Lógica especializada para ATP 1000 com Bye pros Seeds (R96)."""
        jogadores_ordenados = sorted(
            main_draw_players,
            key=lambda j: self.ranking.obter_posicao(j.get("nome", ""))
            or RANKING_POSICAO_FALLBACK,
        )
        seeds = jogadores_ordenados[:SEEDS_ATP_1000]
        nao_seeds = jogadores_ordenados[SEEDS_ATP_1000:]

        if incluir_jogador_principal and normalizar_nome(self.jogador_nome) not in [
            normalizar_nome(p["nome"]) for p in jogadores_ordenados
        ]:
            jogador_humano_dict = {
                "nome": self.jogador_nome,
                "nacionalidade": self.jogador_nacionalidade,
            }
            if nao_seeds:
                nao_seeds[-1] = jogador_humano_dict
            else:
                nao_seeds.append(jogador_humano_dict)

        random.shuffle(nao_seeds)
        confrontos_r96 = []
        for i in range(0, len(nao_seeds), 2):
            if i + 1 < len(nao_seeds):
                confrontos_r96.append(
                    (
                        self.garantir_dados_completos(nao_seeds[i]),
                        self.garantir_dados_completos(nao_seeds[i + 1]),
                    )
                )

        return seeds, confrontos_r96

    def _montar_draw_r96_atp1000(self, main_draw_players):
        incluir_jogador = (
            self._obter_rank_entrada({"nome": self.jogador_nome})
            <= RANKING_LIMITE_ENTRADA_DIRETA
        )
        return self._montar_rodada_r96(
            main_draw_players, incluir_jogador_principal=incluir_jogador
        )

    def _jogador_em_seed_entries(self, estado, nome_jogador):
        seeds = estado.get("seed_entries", [])
        nome_norm = normalizar_nome(nome_jogador)
        for s in seeds:
            if normalizar_nome(s.get("nome", "")) == nome_norm:
                return True
        return False

    def _jogador_tem_bye_r96(self, estado, fase, nome_jogador):
        if fase == "r96" and self._is_atp_1000():
            return self._jogador_em_seed_entries(estado, nome_jogador)
        return False

    def _oferecer_entrevista(self, jogador, contexto_exibicao, contexto_id, **kwargs):
        disparar_entrevista(self.nome_save, jogador, contexto_id, **kwargs)

    def _indice_fase_no_estado(self, estado):
        fase = estado.get("fase_atual")
        fases = self._fases_ordem()
        try:
            return fases.index(fase)
        except ValueError:
            return 0

    def _normalizar_agenda_dia(self, estado):
        if "agenda_dia" not in estado or not isinstance(estado["agenda_dia"], dict):
            estado["agenda_dia"] = {"dia_atual": 1, "jogos_realizados": []}
        return estado["agenda_dia"]

    def _registrar_jogo_no_dia(self, estado, modalidade):
        agenda = self._normalizar_agenda_dia(estado)
        agenda.setdefault("jogos_realizados", []).append(modalidade)

    def _virar_dia_torneio(self, estado):
        agenda = self._normalizar_agenda_dia(estado)
        agenda["dia_atual"] += 1
        agenda["jogos_realizados"] = []

    def _multiplicador_desgaste_segundo_jogo(self):
        if self._is_grand_slam():
            return 1.4
        if self._is_atp_1000():
            return 1.25
        return 1.15

    def _multiplicador_recuperacao_mesmo_dia(self):
        if self._is_grand_slam():
            return 0.7
        if self._is_atp_1000():
            return 0.85
        return 1.0

    def _estimar_pressao_adversario(self, entidade):
        try:
            rank = self.ranking.obter_posicao(entidade.get("nome", "")) or 500
            if rank <= 10:
                return 0.9
            if rank <= 50:
                return 0.7
            return 0.4
        except Exception:
            return 0.5

    def _montar_fatores_fadiga(self, config_partida, adversario):
        return {
            "superficie": config_partida.superficie,
            "melhor_de": config_partida.melhor_de,
            "pressao_adversario": self._estimar_pressao_adversario(adversario),
        }

    def _carregar_estado(self, pular_leitura_arquivo=False):
        if not pular_leitura_arquivo and getattr(self, "nome_save", None):
            deve_recarregar = getattr(self, "_estado_cache", None) is None
            if getattr(self, "caminho_json", None) and os.path.exists(
                self.caminho_json
            ):
                mtime = os.path.getmtime(self.caminho_json)
                deve_recarregar = deve_recarregar or mtime > (
                    getattr(self, "_estado_cache_mtime", 0) or 0
                )
                if deve_recarregar:
                    self._estado_cache_mtime = mtime
            if deve_recarregar:
                estado = carregar_estado_torneio(self.nome_save, genero=self.genero)
                if estado:
                    self._estado_cache = estado

        if getattr(self, "_estado_cache", None):
            estado = self._estado_cache
        else:
            fase_inicial = "qualy_1"
            if hasattr(self, "_get_first_main_draw_phase"):
                try:
                    fase_inicial = self._get_first_main_draw_phase()
                except Exception:
                    fase_inicial = "qualy_1"
            estado = {
                "torneio": getattr(
                    self,
                    "nome_torneio_atual",
                    getattr(self, "tournament_data", {}).get("nome", "Torneio"),
                ),
                "semana": getattr(self, "semana", 1),
                "fase_atual": fase_inicial,
                "rodadas": {},
                "resultados": {},
                "jogador": getattr(self, "jogador_nome", None),
                "jogador_vivo": True,
                "tournament_data": getattr(self, "tournament_data", {}),
                "genero": getattr(self, "genero", "masculino"),
            }

        # Sanitização
        estado.setdefault("semana", getattr(self, "semana", 1))
        estado.setdefault("jogador", getattr(self, "jogador_nome", None))
        estado.setdefault("jogador_vivo", True)
        estado.setdefault("tournament_data", getattr(self, "tournament_data", {}))
        estado.setdefault("genero", getattr(self, "genero", "masculino"))
        fase_inicial = "qualy_1"
        if hasattr(self, "_get_first_main_draw_phase"):
            try:
                fase_inicial = self._get_first_main_draw_phase()
            except Exception:
                fase_inicial = "qualy_1"
        estado.setdefault(
            "fase_atual",
            fase_inicial,
        )
        estado.setdefault("rodadas", {})
        estado.setdefault("resultados", {})
        estado.setdefault("rodadas_duplas", {})
        estado.setdefault("resultados_duplas", {})
        estado.setdefault("agenda_dia", {})
        estado.setdefault("entry_status", {})
        self._reparar_main_draw_se_necessario(estado)

        return estado

    def _salvar_estado(self, estado):
        salvar_json_seguro(self.caminho_json, estado)
        self._estado_cache = deepcopy(estado)
        if os.path.exists(self.caminho_json):
            self._estado_cache_mtime = os.path.getmtime(self.caminho_json)

    def _parametros_participacao(self):
        tipo = self._tipo_torneio()
        if tipo == "Grand Slam":
            return {"draw_main": 104, "draw_qualy": 128, "vagas_qualy": 16}
        if "1000" in tipo:
            draw_main = (
                78 if "96" in str(self._perfil.get("draw_size_main", "")) else 44
            )
            return {"draw_main": draw_main, "draw_qualy": 48, "vagas_qualy": 12}
        if "500" in tipo:
            return {"draw_main": 25, "draw_qualy": 16, "vagas_qualy": 4}
        return {"draw_main": 24, "draw_qualy": 16, "vagas_qualy": 4}

    def _ranking_limite_torneio(self):
        tipo = str(self._tipo_torneio() or "").lower()
        if "challenger" in tipo:
            return RANKING_LIMITE_CHALLENGER
        if "itf" in tipo:
            return RANKING_LIMITE_ITF
        return None

    def _eh_elegivel_por_ranking_torneio(self, jogador):
        limite = self._ranking_limite_torneio()
        if limite is None:
            return True
        return self._obter_rank_entrada(jogador) > limite

    def _selecionar_wildcards(self, qualy_players, nome_jogador_lower, num_wildcards):
        """Seleciona jogadores para receber Wildcard (prioriza o player humano se estiver no qualy)."""
        wcs = []
        for j in qualy_players[:]:
            if normalizar_nome(j.get("nome", "")) == nome_jogador_lower:
                wcs.append(j)
                qualy_players.remove(j)
                break
        while len(wcs) < num_wildcards and qualy_players:
            wcs.append(qualy_players.pop(random.randint(0, len(qualy_players) - 1)))
        return wcs

    def _aplicar_wildcards(
        self,
        chave_principal,
        qualy_players,
        nome_jogador_lower,
        priorizar_jogador,
        num_wildcards,
    ):
        wcs = self._selecionar_wildcards(
            qualy_players, nome_jogador_lower, num_wildcards
        )
        return chave_principal + wcs

    def _montar_qualifying(
        self,
        qualy_players,
        vagas_qualy,
        fases_qualy,
        incluir_jogador_principal=False,
    ):
        """Gera as rodadas iniciais do Qualifying."""
        if not qualy_players:
            return []

        if incluir_jogador_principal:
            if normalizar_nome(self.jogador_nome) not in [
                normalizar_nome(p.get("nome", "")) for p in qualy_players
            ]:
                qualy_players.append(
                    {
                        "nome": self.jogador_nome,
                        "nacionalidade": self.jogador_nacionalidade,
                    }
                )

        num_jogadores_qualy = vagas_qualy * (2 ** len(fases_qualy))
        if len(qualy_players) < num_jogadores_qualy:
            qualy_players += self._get_bot_pool(
                num_jogadores_qualy - len(qualy_players)
            )
        else:
            qualy_players = qualy_players[:num_jogadores_qualy]

        random.shuffle(qualy_players)
        confrontos = []
        for i in range(0, len(qualy_players), 2):
            if i + 1 >= len(qualy_players):
                break
            confrontos.append(
                (
                    self.garantir_dados_completos(qualy_players[i]),
                    self.garantir_dados_completos(qualy_players[i + 1]),
                )
            )
        return confrontos

    def _completar_com_alternates(
        self, qualy_players, num_vagas_restantes, alternates_pool
    ):
        """Preenche o qualifying com Alternates se necessário."""
        while len(qualy_players) < num_vagas_restantes and alternates_pool:
            qualy_players.append(alternates_pool.pop(0))
        return qualy_players

    def _adicionar_bots_se_necessario(self, qualy_players, num_vagas_restantes):
        if len(qualy_players) < num_vagas_restantes:
            qualy_players += self._get_bot_pool(
                num_vagas_restantes - len(qualy_players)
            )
        return qualy_players

    def _score_pool_torneio(self, jogador):
        rank = self._obter_rank_entrada(jogador)
        torneio_pais = self._extrair_codigo_pais(
            self.tournament_data.get("pais_sede", "")
        )
        jogador_pais = self._extrair_codigo_pais(jogador.get("nacionalidade", ""))
        is_home = bool(torneio_pais and torneio_pais == jogador_pais)
        superficie_torneio = str(
            self.tournament_data.get("quadra", "dura") or "dura"
        ).lower()
        superficie_pref = str(jogador.get("superficie_preferida", "") or "").lower()
        superficie_match = bool(
            superficie_pref and superficie_pref in superficie_torneio
        )
        prob = prob_participacao(
            self._tipo_torneio(),
            rank,
            is_home=is_home,
            superficie_match=superficie_match,
        )
        prob = ajustar_prob_participacao_por_contexto(
            prob,
            jogador,
            tipo=self._tipo_torneio(),
            rank=rank,
            nome_torneio=self.tournament_data.get("nome", ""),
            semana_atual=self.tournament_data.get("semana", getattr(self, "semana", 1)),
            ano_atual=self.tournament_data.get("ano"),
        )
        bonus_home = 0.18 if is_home else 0.0
        bonus_surface = 0.08 if superficie_match else 0.0
        bonus_pr = (
            0.12 if int(jogador.get("protected_ranking_semanas", 0) or 0) > 0 else 0.0
        )
        noise = random.uniform(0.0, 0.08)
        score = prob + bonus_home + bonus_surface + bonus_pr + noise
        return min(1.0, score)

    def _selecionar_pool_torneio_realista(
        self, jogadores_aptos, total_necessario, priorizar_jogador=True
    ):
        jogadores_reais = [j for j in jogadores_aptos if not j.get("is_bot")]
        ordenados = sorted(jogadores_reais, key=self._obter_rank_entrada)
        candidatos = [
            (self._score_pool_torneio(jogador), jogador) for jogador in ordenados
        ]
        candidatos.sort(key=lambda item: (-item[0], self._obter_rank_entrada(item[1])))

        pool = [jogador for _score, jogador in candidatos[:total_necessario]]
        nomes_pool = {normalizar_nome(j.get("nome", "")) for j in pool}

        if priorizar_jogador and normalizar_nome(self.jogador_nome) not in nomes_pool:
            jogador_humano = next(
                (
                    jogador
                    for jogador in jogadores_aptos
                    if normalizar_nome(jogador.get("nome", ""))
                    == normalizar_nome(self.jogador_nome)
                ),
                {
                    "nome": self.jogador_nome,
                    "nacionalidade": self.jogador_nacionalidade,
                    "is_bot": False,
                },
            )
            if len(pool) >= total_necessario and pool:
                pool.pop()
            pool.append(jogador_humano)

        return sorted(self._deduplicar_jogadores(pool), key=self._obter_rank_entrada)

    def _selecionar_wildcards_realistas(
        self, remaining_pool, nome_jogador_lower, num_wildcards
    ):
        if num_wildcards <= 0:
            return [], remaining_pool

        pais_sede = self._extrair_codigo_pais(self.tournament_data.get("pais_sede", ""))
        elegiveis = list(remaining_pool)

        def wildcard_score(jogador):
            rank = self._obter_rank_entrada(jogador)
            jogador_pais = self._extrair_codigo_pais(jogador.get("nacionalidade", ""))
            same_country = pais_sede and jogador_pais == pais_sede
            local_bonus = 1000 if same_country else 0
            humana_bonus = (
                500
                if normalizar_nome(jogador.get("nome", "")) == nome_jogador_lower
                else 0
            )
            proximity_bonus = max(0, 200 - min(rank, 200))
            anti_star_penalty = -400 if rank <= 20 else (-180 if rank <= 50 else 0)
            return local_bonus + humana_bonus + proximity_bonus + anti_star_penalty

        elegiveis.sort(
            key=lambda jogador: (
                -wildcard_score(jogador),
                self._obter_rank_entrada(jogador),
            )
        )
        wildcards = elegiveis[:num_wildcards]
        nomes_wc = {normalizar_nome(j.get("nome", "")) for j in wildcards}
        restantes = [
            jogador
            for jogador in remaining_pool
            if normalizar_nome(jogador.get("nome", "")) not in nomes_wc
        ]
        return wildcards, restantes

    def escolher_participantes(self, todos_jogadores, priorizar_jogador=True):
        """Distribui jogadores entre Chave Principal, Qualy e Alternates."""
        params = self._parametros_participacao()
        nome_jogador_lower = normalizar_nome(self.jogador_nome)

        jogadores_aptos = [
            j
            for j in todos_jogadores
            if self._obter_rank_entrada(j) < 9999
            and normalizar_nome(j.get("nome", "")) != nome_jogador_lower
            and self._eh_elegivel_por_ranking_torneio(j)
        ]
        # Adiciona o jogador humano na lista de aptos para processamento uniforme
        jogador_humano_data = {
            "nome": self.jogador_nome,
            "nacionalidade": self.jogador_nacionalidade,
            "is_bot": False,
        }
        if self._eh_elegivel_por_ranking_torneio(jogador_humano_data):
            jogadores_aptos.append(jogador_humano_data)

        total_pool = (
            params["draw_main"]
            + params["draw_qualy"]
            + self._num_wildcards()
            + max(6, int(getattr(self, "_perfil", {}).get("vagas_qualy", 4)))
        )
        jogadores_aptos = self._selecionar_pool_torneio_realista(
            jogadores_aptos, total_pool, priorizar_jogador=priorizar_jogador
        )

        # 1. Entrada Direta (Main Draw)
        selector = self._selector_entrada_direta()
        if selector == "atp_finals":
            chave_principal = self._selecionar_campo_finals(
                jogadores_aptos, 8, nome_jogador_lower, priorizar_jogador
            )
            qualy_players = []
            alternates = []
        else:
            num_diretos = params["draw_main"]
            if selector and hasattr(self, selector):
                chave_principal = getattr(self, selector)(
                    jogadores_aptos,
                    num_diretos,
                    nome_jogador_lower,
                    priorizar_jogador,
                )
            else:
                chave_principal = jogadores_aptos[:num_diretos]

            nomes_main = {
                normalizar_nome(j.get("nome", ""))
                for j in chave_principal
                if isinstance(j, dict)
            }
            restantes = [
                j
                for j in jogadores_aptos
                if normalizar_nome(j.get("nome", "")) not in nomes_main
            ]

            num_wildcards = self._num_wildcards()
            wildcards, restantes = self._selecionar_wildcards_realistas(
                restantes,
                nome_jogador_lower,
                num_wildcards,
            )
            chave_principal = self._deduplicar_jogadores(chave_principal + wildcards)

            num_qualy = params["draw_qualy"]
            pior_rank_main = max(
                (self._obter_rank_entrada(j) for j in chave_principal),
                default=RANKING_POSICAO_FALLBACK,
            )
            qualy_pool = [
                j for j in restantes if self._obter_rank_entrada(j) > pior_rank_main
            ]
            if len(qualy_pool) < num_qualy:
                faltantes = [j for j in restantes if j not in qualy_pool]
                qualy_pool.extend(faltantes[: num_qualy - len(qualy_pool)])

            qualy_players = qualy_pool[:num_qualy]
            alternates = qualy_pool[num_qualy:]

            if priorizar_jogador and not any(
                normalizar_nome(j["nome"]) == nome_jogador_lower
                for j in chave_principal
            ):
                jogador_idx_qualy = next(
                    (
                        idx
                        for idx, jogador in enumerate(qualy_players)
                        if normalizar_nome(jogador.get("nome", ""))
                        == nome_jogador_lower
                    ),
                    None,
                )
                if jogador_idx_qualy is None:
                    jogador_idx_alt = next(
                        (
                            idx
                            for idx, jogador in enumerate(alternates)
                            if normalizar_nome(jogador.get("nome", ""))
                            == nome_jogador_lower
                        ),
                        None,
                    )
                    if jogador_idx_alt is not None:
                        jogador_humano = alternates.pop(jogador_idx_alt)
                        if len(qualy_players) >= num_qualy and qualy_players:
                            alternates.insert(0, qualy_players.pop())
                        qualy_players.append(jogador_humano)

        # Identifica o status de entrada do jogador humano
        status_entry = "Alternates"
        if any(
            normalizar_nome(j["nome"]) == nome_jogador_lower for j in chave_principal
        ):
            status_entry = "Main Draw"
        elif any(
            normalizar_nome(j["nome"]) == nome_jogador_lower for j in qualy_players
        ):
            status_entry = "Qualifying"

        self._ultima_entry_info = {
            "status_entry": {self.jogador_nome: status_entry},
            "chave_principal": chave_principal,
            "qualy_players": qualy_players,
            "alternates": alternates,
        }
        return chave_principal, qualy_players

    def jogar_qualy(self, jogadores_qualy):
        """Executa a simulação de todo o qualifying."""
        if self._is_finals() or self._is_davis_cup():
            return []

        fases_qualy = self._fases_qualy()
        if not fases_qualy:
            return []

        vagas_qualy = self._perfil["vagas_qualy"]
        confrontos = self._montar_qualifying(
            jogadores_qualy, vagas_qualy, fases_qualy, incluir_jogador_principal=True
        )

        # Simula rodadas do qualy
        vencedores = []
        for a, b in confrontos:
            vencedor, _perdedor, _placar, _sets_v, _sets_d = simular_partida_npc_basica(
                a,
                b,
                self.best_of_sets,
                superficie=self.tournament_data.get("quadra"),
            )
            vencedores.append(vencedor)
        for _ in range(len(fases_qualy) - 1):
            random.shuffle(vencedores)
            vencedores_rodada = []
            for i in range(0, len(vencedores), 2):
                if i + 1 >= len(vencedores):
                    break
                vencedor, _perdedor, _placar, _sets_v, _sets_d = (
                    simular_partida_npc_basica(
                        vencedores[i],
                        vencedores[i + 1],
                        self.best_of_sets,
                        superficie=self.tournament_data.get("quadra"),
                    )
                )
                vencedores_rodada.append(vencedor)
            vencedores = vencedores_rodada

        return vencedores[:vagas_qualy]

    def obter_proximo_adversario(self, nome_jogador):
        estado = self._carregar_estado()
        fase = estado["fase_atual"]
        nome_normalizado = normalizar_nome(nome_jogador)

        for a, b in estado["rodadas"].get(fase, []):
            nome_a = normalizar_nome(a["nome"] if isinstance(a, dict) else a)
            nome_b = normalizar_nome(b["nome"] if isinstance(b, dict) else b)
            if nome_normalizado in [nome_a, nome_b]:
                adversario = b if nome_a == nome_normalizado else a
                return (
                    adversario if isinstance(adversario, dict) else {"nome": adversario}
                )
        return None

    def _atualizar_fase_se_necessario(self, estado):
        def validar_qtd_vencedores(vencedores_lista, esperado, contexto):
            obtido = len(vencedores_lista)
            if obtido != esperado:
                msg = (
                    f"ERRO CRITICO: Qtd de vencedores inconsistente para {contexto}. "
                    f"Esperado={esperado} Obtido={obtido}."
                )
                log_erro(self.nome_save, "validar_qtd_vencedores", RuntimeError(msg))
                return False
            return True

        fase = estado["fase_atual"]
        if fase == "finalizado":
            return

        confrontos_fase = estado["rodadas"].get(fase, [])
        resultados_fase = estado["resultados"].get(fase, [])

        if not confrontos_fase and resultados_fase:
            # Fase concluída, avançar
            ordem = self._fases_ordem()
            try:
                idx = ordem.index(fase)
                if idx + 1 < len(ordem):
                    proxima_fase = ordem[idx + 1]
                    vencedores = [r["vencedor"] for r in resultados_fase]
                    # Evoluir perdedores
                    for r in resultados_fase:
                        perdedor = (
                            r["jogador_b"]
                            if r["vencedor"]["nome"] == r["jogador_a"]["nome"]
                            else r["jogador_a"]
                        )
                        if normalizar_nome(perdedor["nome"]) != normalizar_nome(
                            self.jogador_nome
                        ):
                            evoluir_npc_pos_torneio(perdedor, fase)

                    if self._is_merge_phase_to_main_draw(fase, proxima_fase):
                        if validar_qtd_vencedores(
                            vencedores,
                            self._perfil["vagas_qualy"],
                            f"{fase}->{proxima_fase}",
                        ):
                            self._montar_main_draw_a_partir_do_qualy(estado, vencedores)
                            estado["fase_atual"] = proxima_fase
                    elif len(vencedores) >= 2:
                        estado["rodadas"][proxima_fase] = [
                            (vencedores[i], vencedores[i + 1])
                            for i in range(0, len(vencedores), 2)
                        ]
                        estado["fase_atual"] = proxima_fase
                    else:
                        estado["fase_atual"] = "finalizado"
                        if vencedores:
                            estado["campeao_simples"] = vencedores[0]["nome"]
                            evoluir_npc_pos_torneio(vencedores[0], "campeao")
                else:
                    estado["fase_atual"] = "finalizado"
                    if resultados_fase:
                        estado["campeao_simples"] = resultados_fase[0]["vencedor"][
                            "nome"
                        ]
            except (ValueError, IndexError):
                estado["fase_atual"] = "finalizado"

    def _simular_partida_npc(self, a, b, modalidade="simples"):
        from src.torneio_sim import simular_partida_npc

        return simular_partida_npc(self, a, b, modalidade)

    def _processar_simulacao_rodada(
        self, confrontos, modalidade="simples", verbose=False
    ):
        from src.torneio_sim import processar_simulacao_rodada

        return processar_simulacao_rodada(self, confrontos, modalidade)

    def simular_npcs_na_fase_atual(self, nome_jogador):
        estado = self._carregar_estado()
        fase = estado.get("fase_atual")
        if not fase or fase == "finalizado":
            return
        confrontos = estado["rodadas"].get(fase, [])
        if not confrontos:
            return

        nome_norm = normalizar_nome(nome_jogador)
        confrontos_npc = []
        chaves_confrontos_npc = set()
        for a, b in confrontos:
            n_a = normalizar_nome(a["nome"] if isinstance(a, dict) else a)
            n_b = normalizar_nome(b["nome"] if isinstance(b, dict) else b)
            if n_a != nome_norm and n_b != nome_norm:
                confrontos_npc.append((a, b))
                chaves_confrontos_npc.add(frozenset((n_a, n_b)))

        if confrontos_npc:
            resultados = self._processar_simulacao_rodada(confrontos_npc)
            estado["resultados"].setdefault(fase, []).extend(resultados)
            # Remove os confrontos simulados
            estado["rodadas"][fase] = [
                c
                for c in confrontos
                if frozenset(
                    (
                        normalizar_nome(
                            c[0]["nome"] if isinstance(c[0], dict) else c[0]
                        ),
                        normalizar_nome(
                            c[1]["nome"] if isinstance(c[1], dict) else c[1]
                        ),
                    )
                )
                not in chaves_confrontos_npc
            ]
            self._salvar_estado(estado)

    def _aplicar_fadiga_npc_por_nome(self, nome, pontos, fatores_fadiga=None):
        jogador = self.ranking.buscar_jogador_por_nome(nome)
        if jogador:
            from src.fadiga import handle_fadiga_e_lesao_npc

            handle_fadiga_e_lesao_npc(
                jogador, pontos_disputados=pontos, fatores_partida=fatores_fadiga
            )
            return True
        return False

    def _aplicar_energia_npc_por_nome(self, nome, games_total):
        jogador = self.ranking.buscar_jogador_por_nome(nome)
        if jogador:
            perda = games_total * 0.8
            jogador["energia"] = max(5, int(jogador.get("energia", 100) - perda))
            return True
        return False

    def _set_energia_npc_por_nome(self, nome, energia):
        jogador = self.ranking.buscar_jogador_por_nome(nome)
        if jogador:
            jogador["energia"] = energia
            return True
        return False

    def _aplicar_moral_npc_partida(self, vencedor_nome, perdedor_nome):
        venc = self.ranking.buscar_jogador_por_nome(vencedor_nome)
        if venc:
            venc["moral"] = min(100, venc.get("moral", 70) + 5)
        perd = self.ranking.buscar_jogador_por_nome(perdedor_nome)
        if perd:
            perd["moral"] = max(0, perd.get("moral", 70) - 5)

    def _nomes_da_entidade(self, ent):
        if isinstance(ent, dict):
            if "jogadores" in ent:
                return [j["nome"] for j in ent["jogadores"]]
            return [ent["nome"]]
        return [str(ent)]

    def to_api_state(self):
        from src.torneio_api_adapter import to_api_state

        return to_api_state(self)

    def processar_resultado_partida(self, jogador, adversario, vencedor, resultado_str):
        estado = self._carregar_estado()
        fase = estado["fase_atual"]
        nome_jogador = (
            jogador.nome if hasattr(jogador, "nome") else jogador.get("nome", "")
        )
        nome_adversario = (
            adversario.get("nome", "")
            if isinstance(adversario, dict)
            else getattr(adversario, "nome", str(adversario))
        )
        if getattr(self, "nome_save", None):
            self.caminho_json = get_caminho_torneio_save(
                self.nome_save,
                genero=getattr(self, "genero", "masculino"),
            )
        res = {
            "jogador_a": self.garantir_dados_completos(jogador),
            "jogador_b": self.garantir_dados_completos(adversario),
            "vencedor": self.garantir_dados_completos(vencedor),
            "resultado": resultado_str,
        }
        estado["resultados"].setdefault(fase, []).append(res)

        estado["rodadas"][fase] = [
            c
            for c in estado["rodadas"].get(fase, [])
            if not (
                {
                    normalizar_nome(c[0]["nome"] if isinstance(c[0], dict) else c[0]),
                    normalizar_nome(c[1]["nome"] if isinstance(c[1], dict) else c[1]),
                }
                == {
                    normalizar_nome(nome_jogador),
                    normalizar_nome(nome_adversario),
                }
            )
        ]

        vencedor_nome = (
            vencedor.get("nome", "")
            if isinstance(vencedor, dict)
            else getattr(vencedor, "nome", str(vencedor))
        )
        jogador_venceu = normalizar_nome(vencedor_nome) == normalizar_nome(nome_jogador)
        estado["jogador_vivo"] = jogador_venceu
        self._atualizar_fase_se_necessario(estado)
        self._salvar_estado(estado)

    def jogador_ainda_ativo(self):
        estado = self._carregar_estado()
        return estado.get("jogador_vivo", False)

    def jogador_ainda_ativo_duplas(self):
        estado = self._carregar_estado()
        return estado.get("jogador_vivo_duplas", False)

    def iniciar_torneio(self, nome_torneio, todos_jogadores):
        chave_principal, qualy_players = self.escolher_participantes(todos_jogadores)
        estado = self._carregar_estado()
        entry_info = getattr(self, "_ultima_entry_info", {}) or {}
        estado["rodadas"] = {}
        estado["resultados"] = {}
        estado["direct_entries"] = [
            self.garantir_dados_completos(jogador) for jogador in chave_principal
        ]
        self._aplicar_entry_info_estado(estado, entry_info)

        qualy_habilitado = bool(self.tournament_data.get("qualificacao", True))
        iniciou_no_qualy = False
        if qualy_habilitado:
            iniciou_no_qualy = self._configurar_fase_inicial_com_qualy(
                estado, qualy_players
            )

        if not iniciou_no_qualy:
            first_phase = self._get_first_main_draw_phase()
            estado["fase_atual"] = first_phase
            self._montar_rodada_inicial_main_draw(estado, chave_principal)

        self._salvar_estado(estado)

    def remover_confronto_do_jogador(self, fase, nome_jogador):
        estado = self._carregar_estado()
        confrontos = estado.get("rodadas", {}).get(fase, [])
        estado.setdefault("rodadas", {})[fase] = [
            confronto
            for confronto in confrontos
            if not any(
                normalizar_nome(
                    item.get("nome", str(item)) if isinstance(item, dict) else str(item)
                )
                == normalizar_nome(nome_jogador)
                for item in confronto
            )
        ]
        self._salvar_estado(estado)

    def _marcar_eliminacao_em_item(self, item, nome_jogador, fase_saida):
        if isinstance(item, dict) and "nome" in item:
            if normalizar_nome(item.get("nome", "")) == normalizar_nome(nome_jogador):
                item["vivo"] = False
                item["fase_saida"] = fase_saida
            for valor in item.values():
                self._marcar_eliminacao_em_item(valor, nome_jogador, fase_saida)
            return
        if isinstance(item, list):
            for valor in item:
                self._marcar_eliminacao_em_item(valor, nome_jogador, fase_saida)
        elif isinstance(item, tuple):
            for valor in item:
                self._marcar_eliminacao_em_item(valor, nome_jogador, fase_saida)

    def _resolver_walkovers_pendentes(self, estado, nome_jogador):
        fase_atual = estado.get("fase_atual")
        if not fase_atual or fase_atual == "finalizado":
            return estado

        nome_norm = normalizar_nome(nome_jogador)
        confrontos = list(estado.get("rodadas", {}).get(fase_atual, []) or [])
        confrontos_restantes = []
        houve_walkover = False

        for confronto in confrontos:
            if not isinstance(confronto, (list, tuple)) or len(confronto) != 2:
                confrontos_restantes.append(confronto)
                continue

            jogador_a, jogador_b = confronto
            nomes_a = [
                normalizar_nome(nome) for nome in self._nomes_da_entidade(jogador_a)
            ]
            nomes_b = [
                normalizar_nome(nome) for nome in self._nomes_da_entidade(jogador_b)
            ]
            jogador_no_lado_a = nome_norm in nomes_a
            jogador_no_lado_b = nome_norm in nomes_b

            if not jogador_no_lado_a and not jogador_no_lado_b:
                confrontos_restantes.append(confronto)
                continue

            adversario = jogador_b if jogador_no_lado_a else jogador_a
            estado.setdefault("resultados", {}).setdefault(fase_atual, []).append(
                {
                    "jogador_a": self.garantir_dados_completos(jogador_a),
                    "jogador_b": self.garantir_dados_completos(jogador_b),
                    "vencedor": self.garantir_dados_completos(adversario),
                    "resultado": "W.O.",
                    "walkover": True,
                    "desistencia_jogador": True,
                    "fase_saida": fase_atual,
                }
            )
            houve_walkover = True

        if houve_walkover:
            estado.setdefault("rodadas", {})[fase_atual] = confrontos_restantes
            estado["jogador_vivo"] = False
            estado["desistencia_jogador"] = True
            estado["jogador_fase_saida"] = fase_atual
            self._marcar_eliminacao_em_item(estado, nome_jogador, fase_atual)
        return estado

    def desistir_do_torneio(self):
        estado = self._carregar_estado()
        if estado.get("fase_atual") == "finalizado":
            return False

        estado["jogador_vivo"] = False
        estado["desistencia_jogador"] = True
        estado["jogador_fase_saida"] = estado.get("fase_atual")
        self._marcar_eliminacao_em_item(
            estado, self.jogador_nome, estado.get("fase_atual")
        )
        for entrada in estado.get("direct_entries", []) or []:
            if isinstance(entrada, dict) and normalizar_nome(
                entrada.get("nome", "")
            ) == normalizar_nome(self.jogador_nome):
                entrada["vivo"] = False
                entrada["fase_saida"] = estado.get("fase_atual")
        estado = self._resolver_walkovers_pendentes(estado, self.jogador_nome)
        self._salvar_estado(estado)
        return True

    def simular_torneio_restante(self, todos_jogadores=None):
        estado = self._carregar_estado()
        estado = self._resolver_walkovers_pendentes(estado, self.jogador_nome)
        self._salvar_estado(estado)

        while True:
            estado = self._carregar_estado()
            if estado.get("fase_atual") == "finalizado":
                break
            self.simular_npcs_na_fase_atual(self.jogador_nome)
            estado = self._carregar_estado()
            self._atualizar_fase_se_necessario(estado)
            self._salvar_estado(estado)
        estado_final = self._carregar_estado()
        return estado_final.get("campeao_simples")

    def _distribuir_pontos_duplas(self, estado, nome_save):
        from src.dados import carregar_temporada, get_caminho_ranking_duplas
        from src.ranking import SistemaRanking

        if estado.get("pontos_duplas_distribuidos"):
            return

        temporada = carregar_temporada(nome_save) or {"semana": 1, "ano": 2026}
        ranking = SistemaRanking(
            get_caminho_ranking_duplas(
                nome_save, genero=getattr(self, "genero", "masculino")
            ),
            modalidade="duplas",
        )

        for fase, resultados in (estado.get("resultados_duplas") or {}).items():
            for resultado in resultados:
                vencedor = resultado.get("vencedor", {})
                nome_vencedor = (
                    vencedor.get("nome", "")
                    if isinstance(vencedor, dict)
                    else str(vencedor)
                )
                if not nome_vencedor:
                    continue
                ranking.adicionar_pontos(
                    nome_vencedor,
                    10,
                    temporada.get("semana", 1) + 52,
                    modalidade="duplas",
                    ano_exp=temporada.get("ano", 2026),
                    metadados={"torneio": getattr(self, "nome_torneio_atual", "")},
                )
        ranking.salvar_ranking()
        estado["pontos_duplas_distribuidos"] = True
