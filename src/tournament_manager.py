import os
import json
import random
from src.dados import SAVES_DIR, carregar_ranking, get_caminho_ranking_global
from src.json_utils import salvar_json_seguro
from src.ranking import SistemaRanking
from src.jogador import normalizar_nome


def fases_por_tipo_torneio(tipo: str):
    """Retorna (lista_de_fases, draw_size) para o tipo de torneio."""
    tipo = str(tipo or "")
    if tipo == "Grand Slam":
        return ["r64", "r32", "r16", "quartas", "semifinal", "final"], 64
    if "1000" in tipo:
        return ["r32", "r16", "quartas", "semifinal", "final"], 32
    if "Finals" in tipo:
        return ["semifinal", "final"], 4
    if tipo == "Challenger 125":
        return ["r32", "r16", "quartas", "semifinal", "final"], 32
    if tipo in {"ITF 100", "ITF 25"}:
        return ["r32", "r16", "quartas", "semifinal", "final"], 32
    return ["r32", "r16", "quartas", "semifinal", "final"], 32


# Alias privado para uso interno
_fases_por_tipo = fases_por_tipo_torneio


def gerar_placar_fake() -> str:
    """Gera um placar fictício aleatório para partidas NPC."""
    opcoes = ["6-3 6-4", "7-5 6-4", "6-4 3-6 6-3", "6-2 6-2", "7-6 6-4"]
    return random.choice(opcoes)


# Alias privado para uso interno
_placar_fake = gerar_placar_fake


def _fases_duplas_por_draw(draw_size: int):
    """Retorna fases padrão para chaves de duplas."""
    if draw_size >= 64:
        return ["r64", "r32", "r16", "quartas", "semifinal", "final"]
    if draw_size >= 32:
        return ["r32", "r16", "quartas", "semifinal", "final"]
    if draw_size >= 16:
        return ["r16", "quartas", "semifinal", "final"]
    if draw_size >= 8:
        return ["quartas", "semifinal", "final"]
    return ["semifinal", "final"]


def _draw_duplas_por_tipo(tipo: str):
    """Define tamanho de draw de duplas por categoria."""
    tipo = str(tipo or "")
    if tipo == "Grand Slam":
        return 64
    if "1000" in tipo:
        return 32
    if "Finals" in tipo:
        return 8
    return 16


class WeekTournamentManager:
    """
    Gerencia todos os torneios ativos em uma semana específica.
    Permite simulação síncrona e visualização de chaves de múltiplos torneios.
    """

    def __init__(self, nome_save, semana, genero="masculino"):
        self.nome_save = nome_save
        self.semana = semana
        self.genero = genero
        from src.dados import get_caminho_calendario_save

        self.caminho_base = get_caminho_calendario_save(nome_save, genero=genero)
        os.makedirs(self.caminho_base, exist_ok=True)

        ranking_path = os.path.join(
            SAVES_DIR,
            nome_save,
            f"ranking_{'atp' if genero == 'masculino' else 'wta'}.json",
        )
        self.ranking = SistemaRanking(ranking_path)
        # Fallback: se o ranking do save estiver vazio, usa o ranking global.
        # Ocorre em saves criados antes de copiar ambos os rankings.
        if not self.ranking.ranking:
            from src.dados import get_caminho_ranking_global

            global_path = get_caminho_ranking_global(genero)
            try:
                with open(global_path, "r", encoding="utf-8") as f:
                    self.ranking.ranking = json.load(f)
            except Exception:
                pass
        self.torneios = self._carregar_torneios()

    def _carregar_torneios(self):
        """Lê todos os JSONs da pasta sharded correspondentes à semana atual."""
        torneios = {}
        if not os.path.exists(self.caminho_base):
            return {}

        for filename in os.listdir(self.caminho_base):
            if not filename.endswith(".json"):
                continue
            caminho = os.path.join(self.caminho_base, filename)
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Só carrega se for da semana atual (para evitar carregar o ano todo)
                    if int(data.get("semana", 0)) == int(self.semana):
                        torneios[data["torneio"]] = data
            except Exception:
                continue
        return torneios

    def salvar(self):
        """Salva cada torneio em seu respectivo arquivo individual."""
        from src.dados import get_caminho_calendario_save

        for nome_t, data in self.torneios.items():
            caminho = get_caminho_calendario_save(
                self.nome_save, genero=self.genero, nome_torneio=nome_t
            )
            salvar_json_seguro(caminho, data)

    def obter_torneio(self, nome_torneio):
        return self.torneios.get(nome_torneio)

    def inicializar_torneios(self, lista_torneios_info, jogador_nome=None):
        """
        Cria os draws iniciais para todos os torneios da semana que ainda não existem.
        Usa a mesma lógica de seleção de participantes do torneio do jogador.
        """
        from src.calendario import _selecionar_participantes_para_torneio

        ranking_local = sorted(
            self.ranking.ranking,
            key=lambda j: int(j.get("pontos_ranking", j.get("pontos", 0)) or 0),
            reverse=True,
        )
        ranking_global = sorted(
            carregar_ranking(get_caminho_ranking_global(genero=self.genero)),
            key=lambda j: int(j.get("pontos_ranking", j.get("pontos", 0)) or 0),
            reverse=True,
        )

        # Merge local + global para maximizar uso de jogadores reais.
        ranking_ord = []
        nomes_vistos = set()
        for jogador in ranking_local + ranking_global:
            nome = jogador.get("nome", "")
            nome_norm = normalizar_nome(nome)
            if not nome_norm or nome_norm in nomes_vistos:
                continue
            ranking_ord.append(jogador)
            nomes_vistos.add(nome_norm)

        # Pool compartilhado entre torneios do mesmo gênero (evita duplicatas)
        disponiveis = {
            normalizar_nome(j.get("nome", "")) for j in ranking_ord if j.get("nome")
        }

        for info in lista_torneios_info:
            nome_t = info["nome"]
            semana_t = int(info.get("semana", self.semana) or self.semana)

            # Pula se já inicializado para esta semana
            existente = self.torneios.get(nome_t)
            if existente and int(existente.get("semana", 0) or 0) == semana_t:
                # Remove jogadores já usados do pool para manter coerência
                for rodada in existente.get("rodadas", {}).values():
                    for c in rodada:
                        for lado in c:
                            if isinstance(lado, dict):
                                disponiveis.discard(
                                    normalizar_nome(lado.get("nome", ""))
                                )
                continue

            tipo = info.get("tipo", "")
            if tipo in ("Davis Cup", "Billie Jean King Cup", "United Cup"):
                continue

            fases, draw_size = _fases_por_tipo(tipo)
            draw_duplas = _draw_duplas_por_tipo(tipo)

            selecionados = _selecionar_participantes_para_torneio(
                info, ranking_ord, disponiveis, max_jogadores=draw_size
            )
            jogadores = [
                {
                    "nome": j.get("nome", ""),
                    "overall": int(j.get("overall", 50) or 50),
                }
                for j in selecionados[:draw_size]
            ]

            # Fallback: reaproveita quaisquer jogadores reais ainda não usados no draw.
            nomes_no_draw = {normalizar_nome(j.get("nome", "")) for j in jogadores}
            for j in ranking_ord:
                if len(jogadores) >= max(2, draw_size):
                    break
                nome = j.get("nome", "")
                nome_norm = normalizar_nome(nome)
                if (
                    not nome_norm
                    or nome_norm in nomes_no_draw
                    or str(nome).startswith("Bot")
                    or bool(j.get("is_bot"))
                ):
                    continue
                jogadores.append(
                    {"nome": nome, "overall": int(j.get("overall", 50) or 50)}
                )
                nomes_no_draw.add(nome_norm)

            # Último recurso: gera NPCs com nomes reais (nunca "Bot Externo").
            if len(jogadores) < max(2, draw_size):
                from src.gerador_nomes import gerar_jogador_fraco

                while len(jogadores) < max(2, draw_size):
                    bot = gerar_jogador_fraco(
                        len(jogadores) + 1,
                        pais_sede=info.get("pais_sede"),
                        genero=self.genero,
                    )
                    jogadores.append({"nome": bot["nome"], "overall": bot["overall"]})

            random.shuffle(jogadores)
            confrontos = []
            for i in range(0, len(jogadores) - 1, 2):
                confrontos.append([jogadores[i], jogadores[i + 1]])

            # Duplas NPC: prioriza ranking de duplas, com fallback para ranking geral.
            ranking_duplas = sorted(
                ranking_ord,
                key=lambda j: (
                    int(j.get("pontos_ranking_duplas", j.get("pontos_duplas", 0)) or 0),
                    int(j.get("pontos_ranking", j.get("pontos", 0)) or 0),
                ),
                reverse=True,
            )
            needed_players = max(4, draw_duplas * 2)
            candidatos_duplas = []
            nomes_duplas = set()
            for j in ranking_duplas:
                nome = j.get("nome", "")
                nome_norm = normalizar_nome(nome)
                if not nome_norm or nome_norm in nomes_duplas:
                    continue
                if str(nome).startswith("Bot") or bool(j.get("is_bot")):
                    continue
                candidatos_duplas.append(j)
                nomes_duplas.add(nome_norm)
                if len(candidatos_duplas) >= needed_players:
                    break
            if len(candidatos_duplas) < 4:
                candidatos_duplas = ranking_ord[: min(len(ranking_ord), needed_players)]

            random.shuffle(candidatos_duplas)
            pares_duplas = []
            for i in range(0, len(candidatos_duplas) - 1, 2):
                a = candidatos_duplas[i]
                b = candidatos_duplas[i + 1]
                oa = int(a.get("overall", 50) or 50)
                ob = int(b.get("overall", 50) or 50)
                pares_duplas.append(
                    {
                        "nome": f"{a.get('nome', '??')} / {b.get('nome', '??')}",
                        "overall": max(1, int(round((oa + ob) / 2))),
                    }
                )
                if len(pares_duplas) >= draw_duplas:
                    break

            fases_duplas = _fases_duplas_por_draw(len(pares_duplas))
            confrontos_duplas = []
            for i in range(0, len(pares_duplas) - 1, 2):
                confrontos_duplas.append([pares_duplas[i], pares_duplas[i + 1]])

            self.torneios[nome_t] = {
                "torneio": nome_t,
                "semana": semana_t,
                "fase_atual": fases[0] if fases else "r32",
                "fases": fases,
                "rodadas": {fases[0]: confrontos} if fases else {},
                "resultados": {},
                "jogador": jogador_nome or "NPC",
                "jogador_vivo": False,
                "tournament_data": info,
                "genero": self.genero,
                "campeao_simples": None,
                "fases_duplas": fases_duplas,
                "fase_atual_duplas": (
                    fases_duplas[0]
                    if (fases_duplas and confrontos_duplas)
                    else "finalizado"
                ),
                "rodadas_duplas": (
                    {fases_duplas[0]: confrontos_duplas}
                    if (fases_duplas and confrontos_duplas)
                    else {}
                ),
                "resultados_duplas": {},
                "campeao_duplas": None,
            }

        self.salvar()

    def simular_rodada_para_todos(self, fase_alvo, jogador_nome=None):
        """
        Avança todos os torneios simulando as partidas NPC rodada a rodada.
        Se for o torneio do jogador, sincroniza o estado do save individual.
        """
        from src.dados import carregar_estado_torneio

        # Tenta carregar o torneio ativo do jogador para sincronização.
        estado_jogador = carregar_estado_torneio(self.nome_save, genero=self.genero)
        nome_t_jogador = (
            estado_jogador.get("torneio") if isinstance(estado_jogador, dict) else None
        )
        semana_t_jogador = (
            int(estado_jogador.get("semana", 0))
            if isinstance(estado_jogador, dict)
            else 0
        )

        for nome_t, estado in self.torneios.items():
            semana_t = int(estado.get("semana", self.semana) or self.semana)
            if semana_t != int(self.semana):
                continue

            # Se este for o torneio do jogador, sincroniza o estado e pula simulação manual.
            if nome_t == nome_t_jogador and semana_t == semana_t_jogador:
                # Copia campos críticos para manter a consistência no resumo mundial.
                for campo in [
                    "fase_atual",
                    "resultados",
                    "campeao_simples",
                    "fase_atual_duplas",
                    "resultados_duplas",
                    "campeao_duplas",
                    "rodadas",
                    "rodadas_duplas",
                ]:
                    if campo in estado_jogador:
                        estado[campo] = estado_jogador[campo]
                self.torneios[nome_t] = estado
                continue

            simples_finalizado = estado.get("fase_atual") == "finalizado"
            duplas_finalizado = estado.get("fase_atual_duplas") in (None, "finalizado")
            if simples_finalizado and duplas_finalizado:
                continue
            if estado.get("fase_atual") == fase_alvo and duplas_finalizado:
                continue

            self._simular_rodada_estado(nome_t, estado, jogador_nome)
            self._simular_rodada_duplas_estado(nome_t, estado, jogador_nome)

        self.salvar()

    def _simular_rodada_estado(self, nome_t, estado, jogador_nome=None):
        """Simula uma rodada de um torneio diretamente no dict de estado."""
        fases = estado.get("fases", [])
        fase_atual = estado.get("fase_atual")

        if fase_atual == "finalizado" or not fases:
            return

        try:
            idx = fases.index(fase_atual)
        except ValueError:
            estado["fase_atual"] = "finalizado"
            self.torneios[nome_t] = estado
            return

        confrontos = estado.get("rodadas", {}).get(fase_atual, [])
        if not confrontos:
            # Fase vazia: avança para finalizado
            estado["fase_atual"] = "finalizado"
            self.torneios[nome_t] = estado
            return

        jogador_norm = normalizar_nome(jogador_nome) if jogador_nome else None
        resultados = []
        vencedores = []

        for confronto in confrontos:
            a = (
                confronto[0]
                if isinstance(confronto[0], dict)
                else {"nome": str(confronto[0]), "overall": 50}
            )
            b = (
                confronto[1]
                if isinstance(confronto[1], dict)
                else {"nome": str(confronto[1]), "overall": 50}
            )

            # Partida do jogador humano: não simula, mantém o confronto em aberto
            nome_a = normalizar_nome(a.get("nome", ""))
            nome_b = normalizar_nome(b.get("nome", ""))
            if jogador_norm and jogador_norm in (nome_a, nome_b):
                vencedores.append(a)  # placeholder: será atualizado quando jogar
                continue

            oa = max(1, int(a.get("overall", 50) or 50))
            ob = max(1, int(b.get("overall", 50) or 50))
            # Fadiga acumulada: cada partida reduz efetividade em 4% (mín 82%)
            fator_a = max(0.82, 1.0 - a.get("_partidas", 0) * 0.04)
            fator_b = max(0.82, 1.0 - b.get("_partidas", 0) * 0.04)
            oa = max(1, int(oa * fator_a))
            ob = max(1, int(ob * fator_b))
            vencedor = random.choices([a, b], weights=[oa, ob], k=1)[0]
            resultados.append(
                {
                    "jogador_a": a.get("nome", "??"),
                    "jogador_b": b.get("nome", "??"),
                    "vencedor": vencedor.get("nome", "??"),
                    "placar": _placar_fake(),
                }
            )
            # Incrementa contador de partidas do vencedor para rastrear desgaste
            vencedor = dict(vencedor)
            vencedor["_partidas"] = vencedor.get("_partidas", 0) + 1
            vencedores.append(vencedor)

        estado.setdefault("resultados", {})[fase_atual] = resultados

        prox_idx = idx + 1
        if prox_idx >= len(fases) or len(vencedores) <= 1:
            estado["fase_atual"] = "finalizado"
            if vencedores:
                v = vencedores[0]
                estado["campeao_simples"] = (
                    v.get("nome") if isinstance(v, dict) else str(v)
                )
        else:
            prox_fase = fases[prox_idx]
            estado["fase_atual"] = prox_fase
            random.shuffle(vencedores)
            prox_confrontos = []
            for i in range(0, len(vencedores) - 1, 2):
                prox_confrontos.append([vencedores[i], vencedores[i + 1]])
            estado.setdefault("rodadas", {})[prox_fase] = prox_confrontos

        self.torneios[nome_t] = estado

    def _simular_rodada_duplas_estado(self, nome_t, estado, jogador_nome=None):
        """Simula uma rodada da chave de duplas NPC."""
        fases = estado.get("fases_duplas", [])
        fase_atual = estado.get("fase_atual_duplas")

        if fase_atual in (None, "finalizado") or not fases:
            return

        try:
            idx = fases.index(fase_atual)
        except ValueError:
            estado["fase_atual_duplas"] = "finalizado"
            self.torneios[nome_t] = estado
            return

        confrontos = estado.get("rodadas_duplas", {}).get(fase_atual, [])
        if not confrontos:
            estado["fase_atual_duplas"] = "finalizado"
            self.torneios[nome_t] = estado
            return

        jogador_norm = normalizar_nome(jogador_nome) if jogador_nome else None
        resultados = []
        vencedores = []

        for confronto in confrontos:
            a = (
                confronto[0]
                if isinstance(confronto[0], dict)
                else {"nome": str(confronto[0]), "overall": 50}
            )
            b = (
                confronto[1]
                if isinstance(confronto[1], dict)
                else {"nome": str(confronto[1]), "overall": 50}
            )

            nome_a = normalizar_nome(a.get("nome", ""))
            nome_b = normalizar_nome(b.get("nome", ""))
            partes_a = [normalizar_nome(p.strip()) for p in nome_a.split("/")]
            partes_b = [normalizar_nome(p.strip()) for p in nome_b.split("/")]
            if jogador_norm and (jogador_norm in partes_a or jogador_norm in partes_b):
                vencedores.append(a)
                continue

            oa = max(1, int(a.get("overall", 50) or 50))
            ob = max(1, int(b.get("overall", 50) or 50))
            vencedor = random.choices([a, b], weights=[oa, ob], k=1)[0]
            resultados.append(
                {
                    "dupla_a": a.get("nome", "??"),
                    "dupla_b": b.get("nome", "??"),
                    "vencedor": vencedor.get("nome", "??"),
                    "placar": _placar_fake(),
                }
            )
            vencedores.append(vencedor)

        estado.setdefault("resultados_duplas", {})[fase_atual] = resultados

        prox_idx = idx + 1
        if prox_idx >= len(fases) or len(vencedores) <= 1:
            estado["fase_atual_duplas"] = "finalizado"
            if vencedores:
                v = vencedores[0]
                estado["campeao_duplas"] = (
                    v.get("nome") if isinstance(v, dict) else str(v)
                )
        else:
            prox_fase = fases[prox_idx]
            estado["fase_atual_duplas"] = prox_fase
            random.shuffle(vencedores)
            prox_confrontos = []
            for i in range(0, len(vencedores) - 1, 2):
                prox_confrontos.append([vencedores[i], vencedores[i + 1]])
            estado.setdefault("rodadas_duplas", {})[prox_fase] = prox_confrontos

        self.torneios[nome_t] = estado

    def obter_resumo_semanal(self):
        from src.dados import obter_torneios_da_semana, carregar_estado_torneio

        def _normalizar_campeao(valor):
            if isinstance(valor, dict):
                return valor.get("nome")
            if isinstance(valor, str):
                nome = valor.strip()
                nome_low = nome.lower()
                if (
                    not nome
                    or nome in {"---", "TBD", "None", "null"}
                    or nome_low in {"n/a", "na", "cancelado"}
                    or nome_low.startswith("n/a ")
                    or nome_low.startswith("cancelado")
                ):
                    return None
                return nome
            return None

        # Tenta carregar o torneio ativo do jogador para sincronizar campeões reais.
        nome_save = getattr(self, "nome_save", None)
        genero = getattr(self, "genero", "masculino")

        estado_jogador = None
        if nome_save:
            estado_jogador = carregar_estado_torneio(nome_save, genero=genero)

        nome_t_jogador = (
            estado_jogador.get("torneio") if isinstance(estado_jogador, dict) else None
        )
        semana_t_jogador = (
            int(estado_jogador.get("semana", 0))
            if isinstance(estado_jogador, dict)
            else 0
        )

        oficiais = {}
        for info in obter_torneios_da_semana(self.semana, genero=genero):
            if not isinstance(info, dict):
                continue
            oficiais[info.get("nome")] = {
                "simples": _normalizar_campeao(info.get("ultimo_campeao")),
                "duplas": _normalizar_campeao(info.get("ultimo_campeao_duplas")),
            }

        resumo = []
        for nome_t, estado in self.torneios.items():
            semana_t = int(estado.get("semana", self.semana) or self.semana)
            if semana_t != int(self.semana):
                continue

            # Se este for o torneio do jogador, prioriza o estado do arquivo de save dele.
            if nome_t == nome_t_jogador and semana_t == semana_t_jogador:
                estado = estado_jogador

            campeao = None
            campeao_duplas = None
            if estado.get("fase_atual") == "finalizado":
                campeao = _normalizar_campeao(estado.get("campeao_simples"))
                if campeao is None:
                    finais = estado.get("resultados", {}).get("final", [])
                    if finais:
                        ultima_final = finais[-1]
                        campeao = _normalizar_campeao(ultima_final.get("vencedor"))
            if estado.get("fase_atual_duplas") == "finalizado":
                campeao_duplas = _normalizar_campeao(estado.get("campeao_duplas"))
                if campeao_duplas is None:
                    finais_duplas = estado.get("resultados_duplas", {}).get("final", [])
                    if finais_duplas:
                        ultima_final_duplas = finais_duplas[-1]
                        campeao_duplas = _normalizar_campeao(
                            ultima_final_duplas.get("vencedor")
                        )

            # Fallback para calendário oficial somente quando o estado simulado não trouxer campeão.
            if nome_t in oficiais:
                oficial = oficiais.get(nome_t, {})
                if campeao is None:
                    campeao = oficial.get("simples")
                if campeao_duplas is None:
                    campeao_duplas = oficial.get("duplas")

            resumo.append(
                {
                    "nome": nome_t,
                    "tipo": estado.get("tournament_data", {}).get("tipo", ""),
                    "fase": estado.get("fase_atual", "???"),
                    "campeao": campeao,
                    "campeao_duplas": campeao_duplas,
                }
            )
        return resumo
