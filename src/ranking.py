import os
from src.dados import (
    SAVES_DIR,
    carregar_npc_detalhado,
    carregar_ranking,
    get_caminho_ranking_global,
)
from src.utils.nome_utils import normalizar_nome
from src.utils.json_utils import salvar_json_seguro
from src.constants.constantes import DEFAULT_ATRIBUTOS, DEFAULT_ATRIBUTOS_PSICOLOGICOS
from src.player_ratings import ajustar_atributo_duplas, calcular_overall_contextual


class SistemaRanking:
    def __init__(
        self,
        caminho_arquivo: str,
        modalidade: str = "simples",
        persistir_reparos_na_carga: bool = False,
    ) -> None:
        self.caminho_arquivo: str = caminho_arquivo
        self.modalidade: str = modalidade  # 'simples' ou 'duplas'
        self.persistir_reparos_na_carga: bool = persistir_reparos_na_carga
        self._sorted_mode: str = modalidade
        self._pos_cache: dict[str, list | None] = {"simples": None, "duplas": None}
        self._nome_cache: dict[str, int] | None = None
        self._calculated_modes: set[str] = set()
        self._mudou_na_carga: bool = False
        self._duplas_corrompidas_por_pais3: bool = False

        ranking_bruto = self.carregar_ranking()
        self._preparar_sinais_de_correcao(ranking_bruto)
        self.ranking, mudou = self._normalizar_ranking(ranking_bruto)

        # --- Verificação de Saúde do Ranking ---
        if len(self.ranking) < 300:
            genero = (
                "feminino" if "wta" in self.caminho_arquivo.lower() else "masculino"
            )

            from src.dados import get_caminho_ranking_global_duplas

            if self.modalidade == "duplas":
                path_global = get_caminho_ranking_global_duplas(genero)
            else:
                path_global = get_caminho_ranking_global(genero)

            ranking_global = carregar_ranking(path_global)

            if ranking_global and len(ranking_global) > len(self.ranking):
                nova_lista, _ = self._normalizar_ranking(ranking_global)

                # Se ainda estivermos carregando do global de SIMPLES para um ranking de DUPLAS
                # (caso o global de duplas também esteja vazio/ausente), limpamos os pontos.
                if self.modalidade == "duplas" and "duplas" not in path_global.lower():
                    for j in nova_lista:
                        j["pontos_detalhados"] = []
                        j["pontos_ranking"] = 0
                        j["pontos"] = 0
                        j["pontos_detalhados_duplas"] = []
                        j["pontos_ranking_duplas"] = 0
                        j["pontos_duplas"] = 0

                self.ranking = nova_lista
                mudou = True

            # Se ainda for curto (ex: base global corrompida), gera Newgens reais
            if len(self.ranking) < 300:
                from src.utils.gerador_nomes import gerar_jogador_fraco

                while len(self.ranking) < 300:
                    novo = gerar_jogador_fraco(len(self.ranking) + 1, genero=genero)
                    novo["is_bot"] = False  # Trata como NPC permanente
                    self.ranking.append(novo)
                mudou = True

        self._mudou_na_carga = bool(mudou)
        if mudou and self.persistir_reparos_na_carga:
            self.salvar_ranking()

    @property
    def tem_reparos_pendentes(self) -> bool:
        return self._mudou_na_carga

    def carregar_ranking(self):
        from src.dados import (
            carregar_ranking,
            get_caminho_ranking_duplas,
        )

        # Se o caminho fornecido for o genérico, tenta ajustar para a modalidade
        if "duplas" in self.caminho_arquivo:
            return carregar_ranking(self.caminho_arquivo)

        # Se for inicializado com modalidade 'duplas' mas caminho de simples, corrige
        if self.modalidade == "duplas" and "duplas" not in self.caminho_arquivo:
            genero = (
                "feminino" if "wta" in self.caminho_arquivo.lower() else "masculino"
            )
            # Tenta extrair o nome do save do path
            partes = self.caminho_arquivo.split(os.sep)
            if "saves" in partes:
                idx = partes.index("saves")
                if idx + 1 < len(partes):
                    nome_save = partes[idx + 1]
                    self.caminho_arquivo = get_caminho_ranking_duplas(
                        nome_save, genero=genero
                    )

        return carregar_ranking(self.caminho_arquivo)

    def _invalidate_caches(self):
        self._pos_cache = {"simples": None, "duplas": None}
        self._nome_cache = None
        self._sorted_mode = None
        self._calculated_modes = set()

    def _get_nome_cache(self):
        if self._nome_cache is None:
            self._nome_cache = {normalizar_nome(j): j for j in self.ranking}
        return self._nome_cache

    @staticmethod
    def _is_entrada_bot_invalida(jogador):
        if not isinstance(jogador, dict):
            return False
        nome_norm = normalizar_nome(jogador)
        if jogador.get("is_bot") or jogador.get("e_ficticio"):
            return True
        if nome_norm.startswith("bot ") or nome_norm.startswith("bot externo"):
            return True
        return jogador.get("nome", "") == "Lowest_Rank_Bot"

    def _normalizar_ranking(self, ranking):
        if not isinstance(ranking, list):
            return [], True
        antes = len(ranking)
        ranking = [j for j in ranking if not self._is_entrada_bot_invalida(j)]
        ranking_unicos, mudou_dups = self._remover_duplicados(ranking)

        mudou_norm = False
        normalizado = []
        for j in ranking_unicos:
            j_norm, alt = self._normalizar_jogador(j)
            normalizado.append(j_norm)
            mudou_norm = mudou_norm or alt

        return normalizado, (len(normalizado) != antes) or mudou_dups or mudou_norm

    def _preparar_sinais_de_correcao(self, ranking):
        self._duplas_corrompidas_por_pais3 = False

        if self.modalidade == "duplas" and isinstance(ranking, list):
            paises = [
                str(j.get("pais3") or "").strip().upper()
                for j in ranking
                if isinstance(j, dict) and j.get("pais3")
            ]
            paises_unicos = {p for p in paises if p}
            # Se todo o ranking veio com o mesmo pais3, o feed está corrompido.
            if len(paises) >= 20 and len(paises_unicos) == 1:
                self._duplas_corrompidas_por_pais3 = True

    def _inferir_contexto_ranking(self):
        genero = "feminino" if "wta" in self.caminho_arquivo.lower() else "masculino"
        nome_save = None
        partes = self.caminho_arquivo.split(os.sep)
        if "saves" in partes:
            idx = partes.index("saves")
            if idx + 1 < len(partes):
                nome_save = partes[idx + 1]
        return nome_save, genero

    def _resolver_nacionalidade_por_base_local(self, nome_jogador):
        nome_save, genero = self._inferir_contexto_ranking()
        dados = carregar_npc_detalhado(nome_save, nome_jogador, genero=genero)
        if not isinstance(dados, dict):
            return None
        nacionalidade = str(dados.get("nacionalidade") or "").strip()
        return nacionalidade or None

    def _normalizar_jogador(self, j):
        mudou = False
        if not isinstance(j, dict):
            j = {"nome": str(j)}
            mudou = True

        pontos_simples = int(j.get("pontos_ranking", j.get("pontos", 0)) or 0)
        pontos_duplas = int(j.get("pontos_duplas", 0) or 0)
        pontos_ranking_duplas = int(j.get("pontos_ranking_duplas", 0) or 0)
        historico_simples = j.get("pontos_detalhados") or []

        # Alguns índices lean vieram com pontos de duplas gravados no campo de simples.
        # Quando isso acontece, migramos os pontos para o eixo correto sem bloquear
        # jogadores que pontuam nas duas modalidades.
        if (
            self.modalidade == "simples"
            and pontos_simples > 0
            and pontos_duplas > 0
            and pontos_simples == pontos_duplas
            and pontos_ranking_duplas == 0
            and not historico_simples
        ):
            j["pontos_ranking_duplas"] = pontos_duplas
            j["pontos_ranking"] = 0
            j["pontos"] = 0
            mudou = True

        # Suporte para o novo ranking de duplas que usa 'pais3' em vez de 'nacionalidade'
        if "pais3" in j and ("nacionalidade" not in j or j["nacionalidade"] == "??"):
            pais = str(j["pais3"]).upper()
            if self._duplas_corrompidas_por_pais3:
                j["nacionalidade"] = (
                    self._resolver_nacionalidade_por_base_local(j.get("nome")) or "[??]"
                )
            else:
                j["nacionalidade"] = f"[{pais}]" if not pais.startswith("[") else pais
            mudou = True

        campos_obrigatorios = [
            ("nacionalidade", "??"),
            ("pontos_detalhados", []),
            ("trofeus", []),
            ("historico_torneios", []),
            ("pontos_ytd", 0),
            ("dinheiro", 0),
            ("pontos_duplas", 0),
            ("pontos_detalhados_duplas", []),
            ("pontos_ranking", j.get("pontos_ranking") or j.get("pontos", 0)),
            ("pontos_ranking_duplas", 0),
            ("moral", 70),
            ("fadiga", 0),
            ("energia", 100),
            ("superficie_preferida", "dura"),
            ("protected_ranking", None),
            ("protected_ranking_semanas", 0),
            ("is_bot", False),
            ("e_jogador_principal", False),
            ("e_ficticio", False),
        ]

        for campo, padrao in campos_obrigatorios:
            if campo not in j:
                j[campo] = padrao
                mudou = True

        # Se não tem atributos técnicos, marca como 'is_lean' para carregar do DB depois
        if "atributos" not in j and not j.get("is_lean"):
            j["is_lean"] = True
            mudou = True

        # Se 'pontos' existia mas 'pontos_ranking' não (migração manual)
        if (
            "pontos" in j
            and "pontos_ranking" in j
            and j["pontos_ranking"] == 0
            and j["pontos"] > 0
        ):
            j["pontos_ranking"] = j["pontos"]
            mudou = True

        if j.get("is_lean"):
            return j, mudou

        if not j.get("atributos"):
            j["atributos"] = DEFAULT_ATRIBUTOS.copy()
            mudou = True

        if ajustar_atributo_duplas(j):
            mudou = True

        if not j.get("atributos_psicologicos"):
            j["atributos_psicologicos"] = DEFAULT_ATRIBUTOS_PSICOLOGICOS.copy()
            mudou = True

        overall_novo = calcular_overall_contextual(j)
        if int(j.get("overall", 0) or 0) != overall_novo:
            j["overall"] = overall_novo
            mudou = True

        return j, mudou

    def _remover_duplicados(self, ranking):
        unicos = {}
        mudou = False
        for j in ranking:
            chave = (normalizar_nome(j), j.get("nacionalidade", "??"))
            if chave not in unicos:
                unicos[chave] = j
            else:
                mudou = True
                if j.get("pontos_ranking", 0) > unicos[chave].get("pontos_ranking", 0):
                    unicos[chave] = j
        return list(unicos.values()), mudou

    def salvar_ranking(self, save_details=True):
        """
        Salva o ranking.
        Se save_details=True, também salva/atualiza os arquivos individuais dos jogadores.
        O arquivo principal de ranking fica 'lean' (apenas índice).
        """
        if not self.ranking:
            return

        # Extrai nome do save do path para saber onde salvar os detalhes
        partes = self.caminho_arquivo.split(os.sep)
        nome_save = None
        if "saves" in partes:
            idx = partes.index("saves")
            if idx + 1 < len(partes):
                nome_save = partes[idx + 1]

        ranking_lean = []
        for j in self.ranking:
            # Salva o arquivo detalhado do jogador se estivermos em um save E tivermos os dados completos
            if save_details and nome_save and not j.get("is_lean"):
                subfolder = (
                    "atp" if "wta" not in self.caminho_arquivo.lower() else "wta"
                )
                safe_name = (
                    j["nome"]
                    .lower()
                    .replace(" ", "_")
                    .replace("'", "")
                    .replace(".", "")
                )
                caminho_npc = os.path.join(
                    SAVES_DIR, nome_save, "jogadores", subfolder, f"{safe_name}.json"
                )
                os.makedirs(os.path.dirname(caminho_npc), exist_ok=True)
                salvar_json_seguro(caminho_npc, j)

            # Cria a versão lean para o arquivo principal (ÍNDICE PURO)
            # energia/fadiga/moral são incluídos para preservar estado físico
            # entre rodadas do mesmo torneio sem precisar salvar o shard completo
            lean_entry = {
                "nome": j.get("nome"),
                "nacionalidade": j.get("nacionalidade"),
                "pontos": j.get("pontos", 0),
                "pontos_duplas": j.get("pontos_duplas", 0),
                "pontos_ranking": j.get("pontos_ranking", 0),
                "pontos_ranking_duplas": j.get("pontos_ranking_duplas", 0),
                "pontos_ytd": j.get("pontos_ytd", 0),
                "is_lean": True,
                "energia": j.get("energia", 100),
                "fadiga": j.get("fadiga", 0),
                "moral": j.get("moral", 70),
            }
            ranking_lean.append(lean_entry)

        salvar_json_seguro(self.caminho_arquivo, ranking_lean)

    def ordenar(self, modalidade=None, recalculate=False):
        modalidade = modalidade or self.modalidade
        # Força recalculação se o modo nunca foi calculado nesta instância
        should_recalc = recalculate or (modalidade not in self._calculated_modes)

        if self._sorted_mode == modalidade and not should_recalc:
            return

        # Define os campos com base na modalidade desejada, garantindo separação total
        is_s = modalidade == "simples"
        c_pts = "pontos_detalhados" if is_s else "pontos_detalhados_duplas"
        c_rk = "pontos_ranking" if is_s else "pontos_ranking_duplas"
        c_tot = "pontos" if is_s else "pontos_duplas"

        if should_recalc:
            if is_s:
                _, genero = self._inferir_contexto_ranking()
                top_n = 16 if genero == "feminino" else 19
            for j in self.ranking:
                det = j.get(c_pts, [])
                if det:
                    pts_ord = sorted((p.get("pontos", 0) for p in det), reverse=True)
                    # Simples: top 16 (WTA) ou top 19 (ATP) resultados. Duplas: todos (ATP real)
                    j[c_rk] = sum(pts_ord[:top_n]) if is_s else sum(pts_ord)
                    j[c_tot] = sum(pts_ord)
                else:
                    # Se não tem detalhes, pontos_ranking é o total
                    j[c_rk] = j.get(c_tot, 0)
            self._calculated_modes.add(modalidade)

        self.ranking.sort(key=lambda x: x.get(c_rk, 0), reverse=True)
        self._sorted_mode = modalidade
        self._rebuild_pos_cache(modalidade)

    def _rebuild_pos_cache(self, modalidade):
        cache = {}
        for idx, j in enumerate(self.ranking, 1):
            cache[normalizar_nome(j)] = idx
        self._pos_cache[modalidade] = cache

    def adicionar_dinheiro(self, nome, valor):
        if valor <= 0:
            return
        j = self.buscar_jogador_por_nome(nome)
        if j:
            atual = j.get("dinheiro", 0) or 0
            j["dinheiro"] = atual + valor
            return j
        return None

    def adicionar_pontos(
        self,
        nome,
        pontos,
        sem_exp,
        modalidade="simples",
        ano_exp=None,
        metadados=None,
        ano_expiracao=None,
    ):
        nome_norm = normalizar_nome(nome)
        j_enc = self.buscar_jogador_por_nome(nome_norm)

        if not j_enc:
            j_enc, _ = self._normalizar_jogador({"nome": nome})
            self.ranking.append(j_enc)
            self._invalidate_caches()

        # Independente de ser um ranking sharded de duplas ou não,
        # respeitamos a modalidade do ponto para salvar no campo correto do jogador.
        c_pts = (
            "pontos_detalhados"
            if modalidade == "simples"
            else "pontos_detalhados_duplas"
        )

        bloco = {"pontos": pontos, "semana_expiracao": sem_exp}
        ano_ref = ano_exp if ano_exp is not None else ano_expiracao
        if ano_ref is not None:
            bloco["ano_expiracao"] = int(ano_ref)
        if isinstance(metadados, dict):
            for k in [
                "torneio",
                "tipo",
                "semana_origem",
                "ano_origem",
                "fase",
                "modalidade",
            ]:
                if k in metadados:
                    bloco[k] = metadados[k]

        j_enc.setdefault(c_pts, []).append(bloco)
        # Invalida calculo do modo pois os pontos mudaram
        if modalidade in self._calculated_modes:
            self._calculated_modes.remove(modalidade)

        self.ordenar(modalidade, recalculate=True)

    def adicionar_jogador_novo(self, jogador_dict, atualizar_global=False):
        """
        Adiciona jogador se ainda não existir no ranking atual.
        Não atualiza a base global por padrão; saves novos devem partir apenas
        dos JSONs originais em `db/`.
        """
        if not isinstance(jogador_dict, dict):
            jogador_dict = {"nome": str(jogador_dict)}
        if jogador_dict.get("is_bot") or jogador_dict.get("e_ficticio"):
            return None
        nome = jogador_dict.get("nome", "")
        if not nome:
            return None

        existente = self.buscar_jogador_por_nome(nome)
        if existente:
            return existente

        jogador_norm, _ = self._normalizar_jogador(dict(jogador_dict))
        self.ranking.append(jogador_norm)
        self._invalidate_caches()
        if atualizar_global:
            self._atualizar_ranking_global(jogador_dict)
        return jogador_norm

    def obter_posicao(self, nome, modalidade=None):
        target_mod = modalidade or self._sorted_mode or "simples"
        self.ordenar(modalidade=target_mod, recalculate=False)
        return (self._pos_cache.get(target_mod) or {}).get(normalizar_nome(nome))

    def top_n(self, n=10):
        self.ordenar(recalculate=False)
        return self.ranking[:n]

    def ranking_race(self, n=20):
        return sorted(
            self.ranking, key=lambda x: int(x.get("pontos_ytd", 0) or 0), reverse=True
        )[:n]

    def buscar_jogador_por_nome(self, nome):
        j = self._get_nome_cache().get(normalizar_nome(nome))
        if j and j.get("is_lean"):
            # Carrega detalhes se for uma entrada 'lean'
            partes = self.caminho_arquivo.split(os.sep)
            nome_save = None
            if "saves" in partes:
                idx = partes.index("saves")
                if idx + 1 < len(partes):
                    nome_save = partes[idx + 1]

            from src.dados import carregar_npc_detalhado

            genero = (
                "feminino" if "wta" in self.caminho_arquivo.lower() else "masculino"
            )

            # Se não estamos em um save, carregar_npc_detalhado usará o Master DB se passarmos nome_save=None
            detalhes = carregar_npc_detalhado(nome_save, j["nome"], genero=genero)
            if detalhes:
                # Preserva valores transientes do torneio (não sobrescrever com dados
                # do shard que refletem estado base, não o estado atual em torneio)
                _energia_atual = j.get("energia")
                _fadiga_atual = j.get("fadiga")
                _moral_atual = j.get("moral")
                # Atualiza o objeto no cache (e na lista self.ranking)
                j.update(detalhes)
                j["is_lean"] = False
                # Restaura valores transientes se estavam presentes no lean entry
                if _energia_atual is not None:
                    j["energia"] = _energia_atual
                if _fadiga_atual is not None:
                    j["fadiga"] = _fadiga_atual
                if _moral_atual is not None:
                    j["moral"] = _moral_atual
        return j

    def _atualizar_ranking_global(self, jogador_dict):
        """Garante que o jogador também está no ranking global (ATP ou WTA)."""
        if (
            not isinstance(jogador_dict, dict)
            or jogador_dict.get("is_bot")
            or jogador_dict.get("e_ficticio")
            or normalizar_nome(jogador_dict).startswith("bot ")
            or normalizar_nome(jogador_dict).startswith("bot externo")
        ):
            return
        genero = "feminino" if "wta" in self.caminho_arquivo else "masculino"
        caminho_global = get_caminho_ranking_global(genero=genero)
        if not os.path.exists(caminho_global):
            return

        dados = carregar_ranking(caminho_global)
        nomes_globais = {normalizar_nome(j) for j in dados}

        nome_norm = normalizar_nome(jogador_dict)
        if nome_norm in nomes_globais:
            return

        jogador_completo, _ = self._normalizar_jogador(jogador_dict.copy())
        dados.append(jogador_completo)
        salvar_json_seguro(caminho_global, dados)
