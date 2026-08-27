"""
Copa Davis - Torneio de Tênis por Equipes Nacionais

A Copa Davis é a principal competição masculina de tênis por equipes.
Cada confronto (tie) consiste em:
- 2 partidas de simples
- 1 partida de duplas (simulada automaticamente)

O jogador participa representando seu país nas partidas de simples,
mas precisa ser convocado pela seleção nacional.
"""

import random
import logging

from src.constants.torneio_constants import START_YEAR
from src.dados import (
    get_caminho_ranking_save,
    get_caminho_torneio_save,
    carregar_estado_torneio,
    carregar_ranking_nacoes_davis,
)
from src.jogador import normalizar_nome
from src.ranking import SistemaRanking
from src.utils.gerador_nomes import gerar_nome_completo
from src.constants.constantes import DEFAULT_ATRIBUTOS, DEFAULT_ATRIBUTOS_PSICOLOGICOS
from src.save import salvar_jogo
from src.utils.json_utils import salvar_json_seguro
from src.utils.log_jogo import log_erro
from src.constants.davis_cup_constants import (
    PAISES_DAVIS_CUP,
    EQUIPES_QUALIFIERS_R1_2026,
    EQUIPES_QUALIFIERS_R2_2026,
    EQUIPES_FINAL8_2026,
    TIES_QUALIFIERS_R1_2026,
    TIES_QUALIFIERS_R2_2026,
    TIES_FINAL8_QUARTAS_2026,
    TIES_QUALIFIERS_R1_INFO_2026,
    TIES_QUALIFIERS_R2_INFO_2026,
    FINAL8_INFO_2026,
    _MAPA_PAIS_3_PARA_2,
)
from src.davis_selecao import SelecaoNacional, _codigo_pais_canonico
from src.davis_simulacao import (
    ties_por_seeding as _ties_por_seeding_fn,
    vitorias_para_vencer_tie as _vitorias_para_vencer_tie_fn,
    criar_agenda_tie as _criar_agenda_tie_fn,
    forca_simples as _forca_simples_fn,
    forca_duplas as _forca_duplas_fn,
    simular_confronto_npc as _simular_confronto_npc_fn,
    simular_restante_fase as _simular_restante_fase_fn,
    avancar_fase as _avancar_fase_fn,
)
from src.services.tournament_state_service import carregar_estado, salvar_estado

logger = logging.getLogger(__name__)


class DavisCup:
    """Classe que gerencia a Copa Davis."""

    def __init__(self, tournament_data, jogador, ranking, nome_save):
        self.tournament_data = tournament_data
        self.jogador = jogador
        self.ranking = ranking
        self.nome_save = nome_save
        self.genero = getattr(jogador, "genero", "masculino")
        self.caminho_json = get_caminho_torneio_save(nome_save, genero=self.genero)
        self.pais_jogador = jogador.nacionalidade
        self.selecao = None

    def _nome_competicao(self):
        tipo = self.tournament_data.get("tipo")
        if tipo in {"Davis Cup", "Billie Jean King Cup"}:
            return tipo
        return "Davis Cup" if self.genero == "masculino" else "Billie Jean King Cup"

    def _carregar_estado(self):
        """Carrega o estado atual do torneio."""
        estado = carregar_estado(self.nome_save, self.genero)
        # Verifica se o estado é do tipo correto (Davis Cup)
        tipos_validos = {"Davis Cup", "Billie Jean King Cup"}
        if estado is None or estado.get("tipo") not in tipos_validos:
            estado = self._criar_estado_inicial()
            self._salvar_estado(estado)
        elif "modo_competicao" not in estado:
            estado = self._criar_estado_inicial()
            self._salvar_estado(estado)
        return estado

    def _salvar_estado(self, estado):
        """Salva o estado do torneio."""
        salvar_estado(self.nome_save, self.genero, estado)

    def _persistir_convocacao_no_estado(self, estado=None):
        estado = estado or self._carregar_estado()
        if not self.selecao:
            return estado

        selecoes = estado.setdefault("selecoes", {})
        selecoes[self.selecao.pais] = {
            "capitao": self.selecao.capitao,
            "convocados": list(self.selecao.convocados),
        }
        return estado

    def verificar_convocacao(self):
        """
        Verifica se o jogador será convocado para a seleção.
        Retorna (convocado, posicao, mensagem).
        """
        self.selecao = SelecaoNacional(
            self.pais_jogador, self.ranking, genero=self.jogador.genero
        )
        estado = self._carregar_estado()
        if not estado.get("jogador_vivo", True):
            return (
                False,
                None,
                f"Sua seleção não está participante desta etapa da {self._nome_competicao()}.",
            )
        elegivel, posicao, msg = self.selecao.verificar_elegibilidade(self.jogador)

        if not elegivel:
            return False, None, msg

        # Critérios mais fiéis:
        # - Top 5 nacional: convocação praticamente garantida
        # - Top 6-8: alta chance (reserva/titular alternativo)
        # - Top 9-15: chance baixa (lesão/rotação)
        # - >15: exceção rara
        if posicao <= 5:
            return (
                True,
                posicao,
                f"Parabéns! Você foi convocado como #{posicao} do país!",
            )
        if posicao <= 8:
            if random.random() < 0.85:
                return True, posicao, f"Você foi convocado! (#{posicao} do país)"
            return (
                False,
                posicao,
                f"Você ficou fora por pouco nesta convocação. (#{posicao} do país)",
            )
        if posicao <= 15:
            if random.random() < 0.30:
                return (
                    True,
                    posicao,
                    f"Você foi convocado como opção tática! (#{posicao} do país)",
                )
            return (
                False,
                posicao,
                f"Não convocado desta vez. (#{posicao} do país)",
            )

        if random.random() < 0.08:
            return (
                True,
                posicao,
                f"Convocação surpresa! (#{posicao} do país)",
            )
        return (
            False,
            posicao,
            f"Você não foi convocado. Continue subindo no ranking! (#{posicao} do país)",
        )

    def processar_convocacao(self, interactive=True):
        """
        Processa toda a lógica de convocação do jogador.
        Retorna True se foi convocado E aceitou, False caso contrário.
        """
        self.selecao = SelecaoNacional(
            self.pais_jogador,
            self.ranking,
            genero=getattr(self.jogador, "genero", "masculino"),
        )

        if interactive:
            logger.debug("\n" + "=" * 60)
            logger.debug(
                f"           🏆 {self._nome_competicao().upper()} - CONVOCAÇÃO"
            )
            logger.debug("=" * 60)
            logger.debug(f"📍 Sua nacionalidade: {self.pais_jogador}")
            logger.debug(f"📍 Capitão da seleção: {self.selecao.capitao}")
            logger.debug("-" * 60)
            logger.debug("📊 JOGADORES DO SEU PAÍS NO RANKING:")
            logger.debug("-" * 60)

            for i, j in enumerate(self.selecao.jogadores[:10], 1):
                nome = j.get("nome", "??")
                pontos = j.get("pontos", 0)
                overall = j.get("overall", "??")
                destaque = (
                    " ⭐ (VOCÊ)"
                    if normalizar_nome(nome) == normalizar_nome(self.jogador.nome)
                    else ""
                )
                logger.debug(
                    f"  {i:2}. {nome:<25} | OVR: {overall:>3} | Pts: {pontos:>5}{destaque}"
                )
            logger.debug("-" * 60)

        # Verifica convocação
        convocado, posicao, mensagem = self.verificar_convocacao()

        if interactive:
            logger.debug("\n" + "=" * 60)
            logger.debug("           📋 LISTA DE CONVOCADOS")
            logger.debug("=" * 60)

        if convocado:
            if interactive:
                logger.debug(f"\n✅ {mensagem}")

            # Define posição do jogador na convocação
            if posicao == 1:
                pos_convocacao = 1  # Simples 1
            elif posicao == 2:
                pos_convocacao = 2  # Simples 2
            else:
                # Se não é top 2, pode jogar simples 1 ou 2
                pos_convocacao = random.choice([1, 2])

            self.selecao.convocar_jogador(self.jogador, pos_convocacao)
            self.selecao.completar_convocacao(5)

            if interactive:
                self.selecao.exibir_convocacao()
                logger.debug(
                    f"\n🎾 Você jugará as partidas de {('Simples 1' if pos_convocacao == 1 else 'Simples 2')}!"
                )
                logger.debug("   O capitão aguarda sua resposta sobre a convocação...")
                logger.debug(
                    f"\n🎉 Você aceitou representar {self.pais_jogador} na {self._nome_competicao()}!"
                )

            return True
        else:
            if interactive:
                logger.debug(f"\n❌ {mensagem}")
                self.selecao.completar_convocacao(5)
                logger.debug("\n📋 Convocados para representar o país:")
                self.selecao.exibir_convocacao()
                logger.debug(
                    "\n💪 Continue trabalhando duro para ser convocado na próxima!"
                )
            else:
                self.selecao.completar_convocacao(5)
            return False

    def recusar_convocacao(self, posicao, interactive=True):
        """Processa a recusa de convocação pelo jogador."""
        if interactive:
            logger.debug("\n" + "=" * 60)
            logger.debug("           ❌ CONVOCAÇÃO RECUSADA")
            logger.debug("=" * 60)
            logger.debug(
                f"\n📰 NOTÍCIA: {self.jogador.nome} recusa convocação para a {self._nome_competicao()}!"
            )

            if posicao == 1:
                logger.debug(f'   "{self.jogador.nome}, número 1 do país, decidiu não')
                logger.debug(
                    f"   defender as cores de {self.pais_jogador} na {self._nome_competicao()}."
                )
                logger.debug('   A decisão causou surpresa no mundo do tênis."')
            elif posicao <= 3:
                logger.debug(
                    f'   "{self.jogador.nome}, um dos principais jogadores do país,'
                )
                logger.debug(
                    f"   optou por não participar da {self._nome_competicao()}, priorizando"
                )
                logger.debug('   sua agenda no circuito individual."')
            else:
                logger.debug(
                    f'   "{self.jogador.nome} comunicou ao capitão {self.selecao.capitao}'
                )
                logger.debug(
                    f'   que não poderá atender à convocação para a {self._nome_competicao()}."'
                )

        impacto_moral = -10 if posicao == 1 else (-5 if posicao <= 3 else -3)

        if interactive:
            logger.debug(f"📊 Impacto: Moral {impacto_moral}")

        # Aplica penalidade de moral
        if hasattr(self.jogador, "moral"):
            self.jogador.moral = max(0, self.jogador.moral + impacto_moral)

        # Reconstrói a convocação sem o jogador
        self.selecao = SelecaoNacional(
            self.pais_jogador, self.ranking, genero=self.genero
        )
        self.selecao.completar_convocacao(4)

        if interactive:
            logger.debug("-" * 60)
            logger.debug("O capitão convocou um substituto:")
            logger.debug("-" * 60)
            self.selecao.exibir_convocacao()
            logger.debug(f"A {self._nome_competicao()} seguirá sem sua participação.")
            logger.debug("Você poderá focar em outros torneios do calendário.")

        return False

    def _modo_competicao(self):
        nome = (self.tournament_data.get("nome") or "").lower()
        if (
            "qualifiers - 1" in nome
            or "qualificatórias da copa davis, primeira rodada" in nome
        ):
            return "qualifiers_r1"
        if (
            "qualifiers - 2" in nome
            or "qualificatórias da copa davis, segunda rodada" in nome
        ):
            return "qualifiers_r2"
        if "qualifiers" in nome or "qualificat" in nome:
            if "2" in nome or "segunda" in nome or "2ª" in nome:
                return "qualifiers_r2"
            return "qualifiers_r1"
        if "finais - grupos" in nome or "finals - grupos" in nome:
            # Calendário legado usava fase de grupos; no formato 2026 isso representa
            # a 2ª rodada de qualifiers para definir o Final 8.
            return "qualifiers_r2"
        if "final 8" in nome or ("finals" in nome and "grupos" not in nome):
            return "final8"
        # Fallback para eventos Davis genéricos
        return "final8"

    def _ano_competicao(self):
        ano_torneio = self.tournament_data.get("ano_referencia")
        if ano_torneio is not None:
            try:
                return int(ano_torneio)
            except (TypeError, ValueError):
                pass
        try:
            from src.dados import carregar_temporada

            return int(carregar_temporada(self.nome_save).get("ano", START_YEAR))
        except Exception as e:
            log_erro(
                self.nome_save,
                "davis_cup_ano_competicao",
                e,
                {"ano_torneio_raw": ano_torneio},
            )
            return START_YEAR

    def _usar_modo_carreira(self):
        # 2026 usa a chave histórica oficial; anos seguintes usam modo carreira dinâmico.
        return self._ano_competicao() > START_YEAR

    def _codigo_pais(self, valor):
        if not valor:
            return ""
        texto = str(valor).strip()
        if texto.startswith("[") and "]" in texto:
            fechamento = texto.find("]")
            return texto[1:fechamento].upper()
        return texto.upper()

    def _ranking_nacoes_carreira(self):
        """
        Ranking de nações no modo carreira:
        usa base oficial da Davis + adiciona países faltantes com 0 pontos.
        """
        base = carregar_ranking_nacoes_davis().get("nations", [])
        ranking = []
        codigos_vistos = set()
        nome_por_codigo = {}

        for item in base:
            if not isinstance(item, dict):
                continue
            codigo = self._codigo_pais(item.get("code") or item.get("codigo"))
            if not codigo:
                continue
            nome = item.get("name") or item.get("nome") or codigo
            played = int(item.get("played", 0) or 0)
            pontos = float(item.get("points", 0) or 0)
            ranking.append((codigo, pontos, played, f"[{codigo}] {nome}"))
            codigos_vistos.add(codigo)
            nome_por_codigo[codigo] = nome

        # Países conhecidos no ecossistema do jogo que não estejam no ranking oficial
        paises_referencia = (
            list(PAISES_DAVIS_CUP)
            + list(EQUIPES_QUALIFIERS_R1_2026)
            + list(EQUIPES_QUALIFIERS_R2_2026)
            + list(EQUIPES_FINAL8_2026)
        )
        for p in paises_referencia:
            if isinstance(p, tuple):
                for x in p:
                    codigo = self._codigo_pais(x)
                    if codigo and codigo not in codigos_vistos:
                        nome = x.split("]", 1)[1].strip() if "]" in x else codigo
                        ranking.append((codigo, 0.0, 0, f"[{codigo}] {nome}"))
                        codigos_vistos.add(codigo)
                        nome_por_codigo[codigo] = nome

        # Países presentes no ranking de jogadores também entram com 0 se faltarem
        for j in self.ranking.ranking:
            if not isinstance(j, dict):
                continue
            codigo = self._codigo_pais(j.get("nacionalidade", ""))
            if codigo and codigo not in codigos_vistos:
                nome = nome_por_codigo.get(codigo, codigo)
                ranking.append((codigo, 0.0, 0, f"[{codigo}] {nome}"))
                codigos_vistos.add(codigo)

        ranking.sort(key=lambda x: (x[1], x[2], x[0]), reverse=True)
        return [(codigo, pontos, rotulo) for codigo, pontos, _played, rotulo in ranking]

    def _equipes_carreira(self, quantidade):
        ranking_nacoes = self._ranking_nacoes_carreira()
        equipes = [nac for _, _, nac in ranking_nacoes[:quantidade]]
        if len(equipes) < quantidade:
            base = list(PAISES_DAVIS_CUP)
            for pais in base:
                if len(equipes) >= quantidade:
                    break
                if not any(self._paises_iguais(pais, e) for e in equipes):
                    equipes.append(pais)
        return equipes

    def _ties_por_seeding(self, equipes_ordenadas):
        return _ties_por_seeding_fn(equipes_ordenadas)

    def _equipes_modo_competicao(self, modo):
        if self._usar_modo_carreira():
            if modo == "qualifiers_r1":
                return self._equipes_carreira(26)
            if modo == "qualifiers_r2":
                return self._equipes_carreira(14)
            if modo == "final8":
                return self._equipes_carreira(8)
        if modo == "qualifiers_r1":
            return list(EQUIPES_QUALIFIERS_R1_2026)
        if modo == "qualifiers_r2":
            return list(EQUIPES_QUALIFIERS_R2_2026)
        if modo == "final8":
            return list(EQUIPES_FINAL8_2026)
        return list(PAISES_DAVIS_CUP)

    def _vitorias_para_vencer_tie(self, estado):
        return _vitorias_para_vencer_tie_fn(estado)

    def _criar_estado_inicial(self):
        """Cria o estado inicial da Copa Davis conforme o formato real de 2026."""
        modo = self._modo_competicao()
        paises = self._equipes_modo_competicao(modo)
        pais_jogador_normalizado = self._normalizar_pais_para_lista(self.pais_jogador)

        if pais_jogador_normalizado and pais_jogador_normalizado not in paises:
            # Garante presença do país do jogador para não bloquear gameplay.
            paises[-1] = pais_jogador_normalizado

        pais_no_torneio = pais_jogador_normalizado or self.pais_jogador
        jogador_participa = any(self._paises_iguais(p, pais_no_torneio) for p in paises)

        selecoes = {}
        for pais in paises:
            sel = SelecaoNacional(pais, self.ranking, genero=self.genero)
            sel.completar_convocacao(5)
            selecoes[pais] = {"capitao": sel.capitao, "convocados": sel.convocados}

        estado_base = {
            "torneio": self.tournament_data["nome"],
            "tipo": self.tournament_data.get("tipo", "Davis Cup"),
            "semana": self.tournament_data.get("semana", 1),
            "modo_competicao": modo,
            "modo_davis": (
                "carreira" if self._usar_modo_carreira() else "historico_2026"
            ),
            "ano_competicao": self._ano_competicao(),
            "jogador": self.jogador.nome,
            "pais_jogador": pais_no_torneio,
            "jogador_vivo": bool(jogador_participa),
            "jogador_convocado": False,
            "posicao_convocacao": None,
            "selecoes": selecoes,
            "eliminatorias": {"quartas": [], "semifinal": [], "final": []},
            "resultados_confrontos": [],
            "confronto_atual": None,
            "partida_atual": 0,
            "tournament_data": self.tournament_data,
        }

        if modo in ("qualifiers_r1", "qualifiers_r2"):
            estado_base["fase_atual"] = "qualifiers"
            if self._usar_modo_carreira():
                ties = self._ties_por_seeding(paises)
            else:
                ties = (
                    TIES_QUALIFIERS_R1_2026
                    if modo == "qualifiers_r1"
                    else TIES_QUALIFIERS_R2_2026
                )
            confronto_jogador = None
            for equipe_a, equipe_b in ties:
                if self._paises_iguais(
                    equipe_a, pais_no_torneio
                ) or self._paises_iguais(equipe_b, pais_no_torneio):
                    confronto_jogador = {
                        "equipe_a": equipe_a,
                        "equipe_b": equipe_b,
                        "vencedor": None,
                    }
                    break
            estado_base["confronto_atual"] = confronto_jogador
            if not confronto_jogador:
                estado_base["jogador_vivo"] = False
        else:
            estado_base["fase_atual"] = "quartas"
            ties_qf = (
                self._ties_por_seeding(paises)
                if self._usar_modo_carreira()
                else TIES_FINAL8_QUARTAS_2026
            )
            for equipe_a, equipe_b in ties_qf:
                estado_base["eliminatorias"]["quartas"].append(
                    {"equipe_a": equipe_a, "equipe_b": equipe_b, "vencedor": None}
                )
            if jogador_participa:
                for confronto in estado_base["eliminatorias"]["quartas"]:
                    if self._paises_iguais(
                        pais_no_torneio, confronto["equipe_a"]
                    ) or self._paises_iguais(pais_no_torneio, confronto["equipe_b"]):
                        estado_base["confronto_atual"] = confronto
                        break
            else:
                estado_base["jogador_vivo"] = False

        return estado_base

    def _normalizar_pais_para_lista(self, pais):
        """Encontra o país correspondente na lista oficial."""
        if not pais:
            return None

        pais_upper = pais.upper()

        for p in PAISES_DAVIS_CUP:
            if p.upper() == pais_upper:
                return p
            # Compara código
            if pais.startswith("["):
                codigo = pais.split("]")[0] + "]"
                if p.startswith(codigo.upper()):
                    return p

        return None

    def _criar_selecoes_par(self, equipe_a, equipe_b, tamanho=5):
        sel_a = SelecaoNacional(equipe_a, self.ranking, genero=self.genero)
        sel_a.completar_convocacao(tamanho)
        sel_b = SelecaoNacional(equipe_b, self.ranking, genero=self.genero)
        sel_b.completar_convocacao(tamanho)
        return sel_a, sel_b

    def _criar_agenda_tie(self, total, s1_j, s2_j, s1_a, s2_a):
        return _criar_agenda_tie_fn(total, s1_j, s2_j, s1_a, s2_a)

    def _paises_iguais(self, pais1, pais2):
        """Verifica se dois países são o mesmo (comparação flexível)."""
        if not pais1 or not pais2:
            return False

        # Compara diretamente
        if pais1.upper() == pais2.upper():
            return True
        return _codigo_pais_canonico(pais1) == _codigo_pais_canonico(pais2)

    def _garantir_atributos_jogador(self, jogador_dict):
        if "atributos" not in jogador_dict or not isinstance(
            jogador_dict["atributos"], dict
        ):
            jogador_dict["atributos"] = DEFAULT_ATRIBUTOS.copy()
        if "atributos_psicologicos" not in jogador_dict or not isinstance(
            jogador_dict["atributos_psicologicos"], dict
        ):
            jogador_dict["atributos_psicologicos"] = (
                DEFAULT_ATRIBUTOS_PSICOLOGICOS.copy()
            )
        if "overall" not in jogador_dict:
            jogador_dict["overall"] = round(
                sum(jogador_dict["atributos"].values()) / len(jogador_dict["atributos"])
            )

        # HEAL: Se o nome for genérico (Jogador X), gera um real
        nome_atual = jogador_dict.get("nome", "")
        if "Jogador " in nome_atual and jogador_dict.get("e_ficticio"):
            novo_nome = gerar_nome_completo(
                jogador_dict.get("nacionalidade", "US"), self.genero
            )
            jogador_dict["nome"] = novo_nome

        return jogador_dict

    def _gerar_equipe_adversaria(self, pais):
        """Retorna a equipe adversária (jogadores convocados)."""
        estado = self._carregar_estado()
        selecao_dados = estado.get("selecoes", {}).get(pais)

        if selecao_dados and selecao_dados.get("convocados"):
            return selecao_dados["convocados"]

        # Fallback: gera jogadores
        sel = SelecaoNacional(pais, self.ranking, genero=self.genero)
        sel.completar_convocacao(5)
        return sel.convocados

    def _forca_simples(self, atleta):
        """Score para escalar simples (ranking atual + overall)."""
        return _forca_simples_fn(atleta)

    def _forca_duplas(self, atleta):
        """Score para escalar duplas (ranking de duplas + voleio + atributo duplas)."""
        return _forca_duplas_fn(atleta)

    def _info_local_confronto(self, modo_competicao, equipe_a, equipe_b):
        """Retorna dados de sede do tie conforme formato/ano."""
        cod_a = _codigo_pais_canonico(equipe_a)
        cod_b = _codigo_pais_canonico(equipe_b)
        chave = (cod_a, cod_b)

        if modo_competicao == "qualifiers_r1":
            return TIES_QUALIFIERS_R1_INFO_2026.get(chave)
        if modo_competicao == "qualifiers_r2":
            return TIES_QUALIFIERS_R2_INFO_2026.get(chave)
        if modo_competicao == "final8":
            return dict(FINAL8_INFO_2026)
        return None

    def obter_info_confronto_atual(self):
        """Informações do confronto atual (adversário, sede e superfície)."""
        estado = self._carregar_estado()
        confronto = estado.get("confronto_atual") or {}
        if not confronto:
            return None

        pais_jogador = estado.get("pais_jogador", self.pais_jogador)
        equipe_a = confronto.get("equipe_a")
        equipe_b = confronto.get("equipe_b")
        if not equipe_a or not equipe_b:
            return None
        adversario = (
            equipe_b if self._paises_iguais(pais_jogador, equipe_a) else equipe_a
        )
        local = (
            self._info_local_confronto(
                estado.get("modo_competicao"), equipe_a, equipe_b
            )
            or {}
        )
        return {
            "equipe_a": equipe_a,
            "equipe_b": equipe_b,
            "adversario": adversario,
            "cidade": local.get("cidade"),
            "pais_sede": local.get("pais"),
            "superficie": local.get("superficie"),
        }

    def obter_proximo_confronto(self):
        """Retorna informações sobre o próximo confronto do jogador."""
        estado = self._carregar_estado()

        if not estado.get("jogador_convocado"):
            return None

        fase = estado.get("fase_atual")
        confronto = estado.get("confronto_atual")
        if fase in ["qualifiers", "quartas", "semifinal", "final"] and confronto:
            pais_jogador = estado.get("pais_jogador")
            if self._paises_iguais(
                pais_jogador, confronto.get("equipe_a")
            ) or self._paises_iguais(pais_jogador, confronto.get("equipe_b")):
                adversario = (
                    confronto.get("equipe_b")
                    if self._paises_iguais(pais_jogador, confronto.get("equipe_a"))
                    else confronto.get("equipe_a")
                )
                return {"fase": fase, "adversario": adversario}

        return None

    def _atualizar_estado_apos_confronto(self, resultado):
        """Atualiza o estado do torneio após um confronto."""
        estado = self._carregar_estado()
        pais_jogador = estado["pais_jogador"]
        estado.setdefault("resultados_confrontos", []).append(resultado)
        fase = estado.get("fase_atual")
        modo = estado.get("modo_competicao")
        vencedor = resultado.get("vencedor")

        if fase == "qualifiers":
            estado["fase_atual"] = "finalizado"
            estado["confronto_atual"] = None
            estado["jogador_vivo"] = self._paises_iguais(vencedor, pais_jogador)
            if not estado["jogador_vivo"]:
                estado["fase_eliminacao"] = "eliminado_qualifiers"
            if modo == "qualifiers_r2" and estado["jogador_vivo"]:
                estado["classificado_final8"] = True
            self._salvar_estado(estado)
            return

        if fase in ("quartas", "semifinal", "final"):
            chave = estado.get("eliminatorias", {}).get(fase, [])
            for confronto in chave:
                if self._paises_iguais(
                    confronto.get("equipe_a"), resultado.get("equipe_a")
                ) and self._paises_iguais(
                    confronto.get("equipe_b"), resultado.get("equipe_b")
                ):
                    confronto["vencedor"] = vencedor
                    break
                if self._paises_iguais(
                    confronto.get("equipe_a"), resultado.get("equipe_b")
                ) and self._paises_iguais(
                    confronto.get("equipe_b"), resultado.get("equipe_a")
                ):
                    confronto["vencedor"] = vencedor
                    break

            self._simular_restante_fase_eliminatoria(estado, fase)
            self._avancar_fase_eliminatoria(estado, fase)

            if not estado.get("confronto_atual"):
                estado["jogador_vivo"] = False
            elif not (
                self._paises_iguais(
                    pais_jogador, estado["confronto_atual"].get("equipe_a")
                )
                or self._paises_iguais(
                    pais_jogador, estado["confronto_atual"].get("equipe_b")
                )
            ):
                estado["jogador_vivo"] = False

        self._salvar_estado(estado)

        # Fix 2: distribuir pontos quando o torneio termina (inclusive pela
        # partida do jogador humano — o serviço cobre apenas a rota NPC).
        if estado.get("fase_atual") == "finalizado":
            try:
                from src.pontuacao import distribuir_pontos_davis

                distribuir_pontos_davis(self.nome_save)
            except Exception as exc:
                log_erro(
                    self.nome_save,
                    "distribuir_pontos_davis_pos_confronto",
                    exc,
                    {},
                )

    def _simular_confronto_npc(self, equipe_a, equipe_b, alvo_vitorias=2):
        """Simula confronto NPC baseado no overall das equipes e vantagem de casa."""
        estado = self._carregar_estado()
        return _simular_confronto_npc_fn(
            equipe_a,
            equipe_b,
            alvo_vitorias,
            estado,
            self.ranking,
            self.genero,
            self._paises_iguais,
            self._info_local_confronto,
        )

    def _simular_restante_fase_eliminatoria(self, estado, fase):
        _simular_restante_fase_fn(estado, fase, self._simular_confronto_npc)

    def _avancar_fase_eliminatoria(self, estado, fase):
        pais_jogador = estado.get("pais_jogador")
        _avancar_fase_fn(estado, fase, pais_jogador, self._paises_iguais)

    def jogador_ainda_ativo(self):
        """Verifica se o jogador ainda está no torneio."""
        estado = self._carregar_estado()
        return estado.get("jogador_vivo", True) and estado.get(
            "jogador_convocado", False
        )

    def obter_fase_atual(self):
        """Retorna a fase atual do torneio."""
        estado = self._carregar_estado()
        return estado.get("fase_atual", "qualifiers")

    def obter_confronto_jogador(self, nome_jogador=None):
        """Retorna os dados do confronto atual do jogador humano."""
        estado = self._carregar_estado()
        if not estado.get("jogador_convocado"):
            return None

        confronto = estado.get("confronto_atual")
        if not confronto:
            return None

        # O "adversário" depende de qual partida do tie estamos
        idx_partida = estado.get("partida_atual", 0)
        # Se o tie já acabou ou passou do limite
        if idx_partida >= 5:
            return None

        # Determina a partida atual do tie
        # Formato simplificado para MatchRuntime: retorna o oponente direto
        # Precisamos saber se o jogador joga a partida atual
        pais_jogador = estado.get("pais_jogador")
        equipe_a = confronto.get("equipe_a")
        equipe_b = confronto.get("equipe_b")

        selecao_a, selecao_b = self._criar_selecoes_par(equipe_a, equipe_b)

        # Identifica quem é a seleção do jogador
        minha_sel = (
            selecao_a if self._paises_iguais(equipe_a, pais_jogador) else selecao_b
        )
        adv_sel = selecao_b if minha_sel == selecao_a else selecao_a

        # Desde 2019 todos os ties são melhor-de-3: agenda sempre com 3 partidas.
        fase = estado.get("fase_atual")
        total = 3

        if idx_partida >= total:
            return None

        s1_j, s2_j = minha_sel.convocados[0], minha_sel.convocados[1]
        s1_a, s2_a = adv_sel.convocados[0], adv_sel.convocados[1]
        agenda = self._criar_agenda_tie(total, s1_j, s2_j, s1_a, s2_a)

        tipo, p_j, p_a = agenda[idx_partida]

        # Verifica se é a vez do humano
        if tipo == "simples":
            if normalizar_nome(p_j.get("nome", "")) == normalizar_nome(
                self.jogador.nome
            ):
                return {
                    "jogador1": p_j.get("nome"),
                    "jogador2": p_a.get("nome"),
                    "jogador1_nacionalidade": minha_sel.pais,
                    "jogador2_nacionalidade": adv_sel.pais,
                    "superficie": (
                        (self.obter_info_confronto_atual() or {}).get("superficie")
                        or self.tournament_data.get("superficie", "Hard")
                    ),
                    "tipo": "simples",
                    "fase": fase,
                }

        return None

    def processar_resultado_partida(self, jogador, adversario, resultado, placar_texto):
        """Registra o resultado de uma partida individual no tie da Davis."""
        estado = self._carregar_estado()
        confronto = estado.get("confronto_atual")
        if not confronto:
            return

        idx = estado.get("partida_atual", 0)
        venc_nome = resultado.get("nome")

        # Registra a partida no log do confronto
        partida_log = {
            "tipo": "simples",
            "jogador_a": (
                jogador.nome if hasattr(jogador, "nome") else jogador.get("nome")
            ),
            "jogador_b": adversario.get("nome"),
            "vencedor": venc_nome,
            "placar": placar_texto,
        }

        if "partidas" not in confronto:
            confronto["partidas"] = []
        confronto["partidas"].append(partida_log)

        # Atualiza placar do tie
        if "placar_tie" not in confronto:
            confronto["placar_tie"] = [0, 0]

        # Quem é equipe A e B no tie?
        pais_j = estado.get("pais_jogador")
        if self._paises_iguais(confronto["equipe_a"], pais_j):
            idx_venc = (
                0
                if normalizar_nome(venc_nome)
                == normalizar_nome(
                    jogador.nome if hasattr(jogador, "nome") else jogador.get("nome")
                )
                else 1
            )
        else:
            idx_venc = (
                1
                if normalizar_nome(venc_nome)
                == normalizar_nome(
                    jogador.nome if hasattr(jogador, "nome") else jogador.get("nome")
                )
                else 0
            )

        confronto["placar_tie"][idx_venc] += 1
        estado["partida_atual"] = idx + 1

        # Fix 3: substituição por lesão após a partida do jogador humano.
        # Se o jogador ficou lesionado, troca-o pelo próximo convocado que
        # ainda não jogou. Apenas registra o evento no log — sem reprocessar
        # a partida já disputada.
        jogador_lesionado = isinstance(
            getattr(jogador, "status_lesao", None), dict
        ) and jogador.status_lesao.get("lesionado")
        if jogador_lesionado and self.selecao:
            nome_jogador_norm = normalizar_nome(
                jogador.nome if hasattr(jogador, "nome") else jogador.get("nome", "")
            )
            jogadores_que_jogaram = {
                normalizar_nome(p.get("jogador_a", ""))
                for p in confronto.get("partidas", [])
            } | {
                normalizar_nome(p.get("jogador_b", ""))
                for p in confronto.get("partidas", [])
            }
            substituto = None
            for conv in self.selecao.convocados:
                nome_conv = normalizar_nome(conv.get("nome", ""))
                if (
                    nome_conv != nome_jogador_norm
                    and nome_conv not in jogadores_que_jogaram
                ):
                    substituto = conv
                    break
            if substituto:
                log_erro(
                    self.nome_save,
                    "davis_substituicao_lesao",
                    Exception(
                        f"{jogador.nome} lesionado — substituído por "
                        f"{substituto.get('nome')} no tie."
                    ),
                    {
                        "jogador": jogador.nome,
                        "substituto": substituto.get("nome"),
                        "fase": estado.get("fase_atual"),
                    },
                )
                # Atualiza a convocação no estado para as próximas partidas.
                for i, conv in enumerate(self.selecao.convocados):
                    if normalizar_nome(conv.get("nome", "")) == nome_jogador_norm:
                        self.selecao.convocados[i] = substituto
                        break
                selecoes = estado.setdefault("selecoes", {})
                pais_j_key = estado.get("pais_jogador", self.pais_jogador)
                if pais_j_key in selecoes:
                    convs = selecoes[pais_j_key].get("convocados", [])
                    for i, conv in enumerate(convs):
                        if normalizar_nome(conv.get("nome", "")) == nome_jogador_norm:
                            convs[i] = substituto
                            break

        # Verifica se o tie acabou
        alvo = self._vitorias_para_vencer_tie(estado)
        if max(confronto["placar_tie"]) >= alvo:
            venc_tie = (
                confronto["equipe_a"]
                if confronto["placar_tie"][0] >= alvo
                else confronto["equipe_b"]
            )
            confronto["vencedor"] = venc_tie
            # Atualiza o estado geral com o vencedor do tie
            self._atualizar_estado_apos_confronto(confronto)
        else:
            self._salvar_estado(estado)

    def simular_npcs_na_fase_atual(self, nome_jogador=None):
        """Simula as outras partidas do tie (NPCs) até que seja a vez do jogador ou o tie acabe."""
        estado = self._carregar_estado()
        confronto = estado.get("confronto_atual")
        if not confronto or confronto.get("vencedor"):
            return

        pais_j = estado.get("pais_jogador")
        equipe_a = confronto.get("equipe_a")
        equipe_b = confronto.get("equipe_b")

        selecao_a, selecao_b = self._criar_selecoes_par(equipe_a, equipe_b)

        minha_sel = selecao_a if self._paises_iguais(equipe_a, pais_j) else selecao_b
        adv_sel = selecao_b if minha_sel == selecao_a else selecao_a

        fase = estado.get("fase_atual")
        # Desde 2019 todos os ties são melhor-de-3: agenda sempre com 3 partidas.
        total = 3
        alvo = self._vitorias_para_vencer_tie(estado)

        s1_j, s2_j = minha_sel.convocados[0], minha_sel.convocados[1]
        s1_a, s2_a = adv_sel.convocados[0], adv_sel.convocados[1]
        agenda = self._criar_agenda_tie(total, s1_j, s2_j, s1_a, s2_a)

        while estado["partida_atual"] < total and not confronto.get("vencedor"):
            idx = estado["partida_atual"]
            tipo, p_j, p_a = agenda[idx]

            # Se for a vez do humano, para a simulação
            if tipo == "simples" and normalizar_nome(
                p_j.get("nome", "")
            ) == normalizar_nome(self.jogador.nome):
                break

            # Simula partida NPC
            if tipo == "simples":
                # Lógica simplificada de vitória baseada em overall
                ovr_j = p_j.get("overall", 70)
                ovr_a = p_a.get("overall", 70)
                prob = 0.5 + (ovr_j - ovr_a) * 0.05
                venceu = random.random() < prob
                venc_nome = p_j["nome"] if venceu else p_a["nome"]
                placar = "2-0" if venceu else "0-2"

                partida_log = {
                    "tipo": "simples",
                    "jogador_a": p_j["nome"],
                    "jogador_b": p_a["nome"],
                    "vencedor": venc_nome,
                    "placar": placar,
                }
            else:
                # Duplas
                ovr_j = (
                    minha_sel.convocados[0]["overall"]
                    + minha_sel.convocados[2]["overall"]
                ) / 2
                ovr_a = (
                    adv_sel.convocados[0]["overall"] + adv_sel.convocados[2]["overall"]
                ) / 2
                prob = 0.5 + (ovr_j - ovr_a) * 0.05
                venceu = random.random() < prob
                venc_nome = minha_sel.pais if venceu else adv_sel.pais
                placar = "2-1" if venceu else "1-2"

                partida_log = {
                    "tipo": "duplas",
                    "equipe_a": minha_sel.pais,
                    "equipe_b": adv_sel.pais,
                    "vencedor": venc_nome,
                    "placar": placar,
                }

            if "partidas" not in confronto:
                confronto["partidas"] = []
            confronto["partidas"].append(partida_log)

            if "placar_tie" not in confronto:
                confronto["placar_tie"] = [0, 0]

            idx_venc = 0 if venceu == (minha_sel == selecao_a) else 1
            confronto["placar_tie"][idx_venc] += 1
            estado["partida_atual"] += 1

            if max(confronto["placar_tie"]) >= alvo:
                venc_tie = (
                    confronto["equipe_a"]
                    if confronto["placar_tie"][0] >= alvo
                    else confronto["equipe_b"]
                )
                confronto["vencedor"] = venc_tie
                self._atualizar_estado_apos_confronto(confronto)
                return

        self._salvar_estado(estado)

    def _montar_fatores_fadiga(self, config, adversario):
        """Retorna dicionário de fatores para cálculo de fadiga."""
        return {
            "superficie": config.superficie,
            "melhor_de": config.melhor_de,
            "ovr_adversario": adversario.get("overall", 70),
        }

    def to_api_state(self):
        """Retorna o estado serializável para a API."""
        estado = self._carregar_estado()
        confronto_tie = estado.get("confronto_atual") or {}

        # Cria um 'bracket' virtual com a partida atual para o MatchScreen encontrar o adversário
        bracket = []
        conf_humano = self.obter_confronto_jogador()
        if conf_humano:
            bracket.append(
                {
                    "jogador1": conf_humano["jogador1"],
                    "jogador2": conf_humano["jogador2"],
                    "jogador1_nacionalidade": conf_humano["jogador1_nacionalidade"],
                    "jogador2_nacionalidade": conf_humano["jogador2_nacionalidade"],
                    "fase": conf_humano["fase"],
                    "vencedor": None,
                    "placar": "",
                }
            )

        return {
            "nome": estado.get("torneio", "Davis Cup"),
            "tipo": estado.get("tipo", "Davis Cup"),
            "fase_atual": estado.get("fase_atual", "qualifiers"),
            "jogador_ativo": self.jogador_ainda_ativo(),
            "davis": True,
            "estado": estado,
            "confronto_atual": confronto_tie,
            "bracket": bracket,
            "superficie": (
                (self.obter_info_confronto_atual() or {}).get("superficie")
                or self.tournament_data.get("superficie", "Hard")
            ),
        }


def criar_torneio_davis(torneio_data, jogador, nome_save, semana, interactive=True):
    """Cria e inicializa um torneio de Copa Davis."""
    ranking_path = get_caminho_ranking_save(
        nome_save, genero=getattr(jogador, "genero", "masculino")
    )
    ranking = SistemaRanking(ranking_path)

    torneio_data = dict(torneio_data or {})
    torneio_data["semana"] = semana
    try:
        from src.dados import carregar_temporada

        torneio_data["ano_referencia"] = int(
            carregar_temporada(nome_save).get("ano", START_YEAR)
        )
    except Exception as e:
        log_erro(
            nome_save,
            "criar_torneio_davis_ano_referencia",
            e,
            {"semana": semana, "torneio": torneio_data.get("nome")},
        )
        torneio_data["ano_referencia"] = START_YEAR

    davis = DavisCup(
        tournament_data=torneio_data,
        jogador=jogador,
        ranking=ranking,
        nome_save=nome_save,
    )

    # Processa a convocação
    try:
        convocado = davis.processar_convocacao(interactive=interactive)
    except TypeError:
        # Compatibilidade com stubs/test doubles antigos que não aceitam o novo parâmetro.
        convocado = davis.processar_convocacao()

    if not convocado:
        # Jogador não foi convocado ou recusou - salva moral atualizada
        salvar_jogo(nome_save, jogador)
        return None

    # Atualiza estado com a convocação
    estado = davis._carregar_estado()
    estado["jogador_convocado"] = True
    estado = davis._persistir_convocacao_no_estado(estado)

    # Encontra a posição do jogador na convocação
    if davis.selecao:
        for i, c in enumerate(davis.selecao.convocados):
            if c.get("e_jogador_principal"):
                estado["posicao_convocacao"] = i + 1
                break

    davis._salvar_estado(estado)

    if interactive:
        nome_competicao = estado.get("tipo", "Davis Cup")
        logger.debug(f"\n🏆 {nome_competicao} iniciada!")
        if estado.get("fase_atual") == "qualifiers":
            confronto = estado.get("confronto_atual") or {}
            logger.debug(
                f"📍 Tie classificatório: {confronto.get('equipe_a', '??')} vs {confronto.get('equipe_b', '??')}"
            )
            local = (
                davis._info_local_confronto(
                    estado.get("modo_competicao"),
                    confronto.get("equipe_a"),
                    confronto.get("equipe_b"),
                )
                or {}
            )
            if local:
                logger.debug(
                    f"📌 Sede: {local.get('cidade', '??')}, {local.get('pais', '??')} | {local.get('superficie', 'Hard')}"
                )
        else:
            logger.debug("📍 Formato Final 8 em mata-mata.")

    return davis


def carregar_davis_cup(nome_save, jogador):
    """Carrega um torneio de Copa Davis existente."""
    genero = getattr(jogador, "genero", "masculino")
    estado = carregar_estado_torneio(nome_save, genero=genero)
    tipos_validos = {"Davis Cup", "Billie Jean King Cup"}
    if not estado or estado.get("tipo") not in tipos_validos:
        return None

    ranking_path = get_caminho_ranking_save(nome_save, genero=genero)
    ranking = SistemaRanking(ranking_path)

    return DavisCup(
        tournament_data=estado.get("tournament_data", {}),
        jogador=jogador,
        ranking=ranking,
        nome_save=nome_save,
    )
