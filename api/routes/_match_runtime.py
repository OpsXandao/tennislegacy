from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import random
from typing import Any
from uuid import uuid4

from fastapi import HTTPException

from api.routes._match_store import (
    get_runtime_cache,
    invalidate_other_snapshots,
    load_snapshot,
    save_snapshot,
    set_runtime_cache,
)
from src.dados import SAVES_DIR, carregar_jogador, carregar_temporada
from src.fadiga import (
    handle_fadiga_e_lesao,
    handle_fadiga_e_lesao_npc,
    _aumento_fadiga_nao_linear,
)
from src.jogar_partida import atualizar_estatisticas, _definir_estrategia_auto
from src.match_config import ConfigPartida, criar_config_partida
from src.match_constants import EstrategiaSaque, IntencaoPonto, TipoSaque
from src.match_history import MatchHistoryManager
from src.match_dynamics import (
    aplicar_custo_stamina_contextual,
    atualizar_momentum_contextual,
    calcular_stamina_pos_recuperacao,
)
from src.progressao import handle_xp_e_level_up
from src.save import salvar_jogo
from src.log_jogo import log_erro
from src.jogador import (
    atualizar_rivalidade,
    normalizar_nome,
    obter_bonus_rivalidade,
)
from src.simulacao_partida import (
    ContextoPartida,
    ContextoPonto,
    EstatisticasPartida,
    SimuladorPonto,
)
from src.torneio import avancar_fase
from api.routes._shared import carregar_torneio_api

SCORE_MAP = ("0", "15", "30", "40")


def _estrategia_padrao() -> dict[str, Any]:
    return {
        "estilo": "atacar_do_fundo",
        "saque": EstrategiaSaque.SEGURO,
        "saque_tipo": TipoSaque.VARIADO,
        "intencao": IntencaoPonto.PACIENTE,
    }


def _normalizar_pacote_tatico(valor: str | None) -> dict[str, str] | None:
    texto = str(valor or "").strip()
    if not texto:
        return None
    if texto.startswith("fm|"):
        partes = texto.split("|")
        if len(partes) >= 5:
            _, mentalidade, abordagem, instrucao, segundo_saque = partes[:5]
            return {
                "mentalidade": mentalidade.upper(),
                "abordagem": abordagem.upper(),
                "instrucao": instrucao.upper(),
                "segundo_saque": segundo_saque.upper(),
            }
    if "|" in texto:
        partes = texto.split("|")
        if len(partes) == 3:
            mentalidade, abordagem, instrucao = partes
            return {
                "mentalidade": mentalidade.upper(),
                "abordagem": abordagem.upper(),
                "instrucao": instrucao.upper(),
                "segundo_saque": "SEGURO",
            }
    return None


def _estrategia_do_pacote_tatico(
    mentalidade: str,
    abordagem: str,
    instrucao: str,
    segundo_saque: str,
    estrategia_atual: dict[str, Any] | None = None,
) -> dict[str, Any]:
    estrategia = dict(estrategia_atual or _estrategia_padrao())

    if abordagem == "SERVE_VOLLEY":
        estrategia["estilo"] = "atacar_na_rede"
        estrategia["saque_tipo"] = TipoSaque.AGRESSIVO
    elif abordagem == "COUNTER":
        estrategia["estilo"] = "atacar_pelo_meio"
        estrategia["saque_tipo"] = TipoSaque.SEGURO
    else:
        estrategia["estilo"] = "atacar_do_fundo"
        estrategia["saque_tipo"] = (
            TipoSaque.AGRESSIVO if mentalidade == "OFENSIVA" else TipoSaque.VARIADO
        )

    if mentalidade == "OFENSIVA":
        estrategia["intencao"] = IntencaoPonto.ARRISCAR
        if estrategia["saque_tipo"] != TipoSaque.SEGURO:
            estrategia["saque_tipo"] = TipoSaque.AGRESSIVO
    elif mentalidade == "DEFENSIVA":
        estrategia["intencao"] = IntencaoPonto.DEFENSIVO
        estrategia["saque_tipo"] = TipoSaque.SEGURO
    else:
        estrategia["intencao"] = IntencaoPonto.PACIENTE

    if instrucao == "ATACAR_SAQUE":
        estrategia["intencao"] = IntencaoPonto.ARRISCAR
    elif instrucao == "TROCAS_LONGAS":
        estrategia["estilo"] = "atacar_do_fundo"
        estrategia["intencao"] = IntencaoPonto.DEFENSIVO
    elif instrucao == "FORCAR_BACKHAND":
        estrategia["estilo"] = "atacar_pelo_meio"
        if mentalidade != "DEFENSIVA":
            estrategia["intencao"] = IntencaoPonto.ARRISCAR

    estrategia["saque"] = (
        EstrategiaSaque.FORCAR
        if str(segundo_saque).upper() == "FORCAR"
        else EstrategiaSaque.SEGURO
    )
    estrategia["mentalidade"] = mentalidade
    estrategia["abordagem"] = abordagem
    estrategia["instrucao"] = instrucao
    return estrategia


def _enum_value(valor: Any) -> Any:
    if isinstance(valor, Enum):
        return valor.value
    return valor


def _serializar_estrategia(estrategia: dict[str, Any]) -> dict[str, Any]:
    return {chave: _enum_value(valor) for chave, valor in (estrategia or {}).items()}


def _atualizar_historico_torneios(destino: Any, entrada: dict[str, Any]) -> None:
    historico = list(getattr(destino, "historico_torneios", []) or [])
    chave_entrada = (
        normalizar_nome(entrada.get("nome", "")),
        int(entrada.get("ano", 0) or 0),
        int(entrada.get("semana", 0) or 0),
        str(entrada.get("modalidade", "simples") or "simples"),
    )

    for idx, item in enumerate(historico):
        if not isinstance(item, dict):
            continue
        chave_item = (
            normalizar_nome(item.get("nome", item.get("torneio", ""))),
            int(item.get("ano", 0) or 0),
            int(item.get("semana", 0) or 0),
            str(item.get("modalidade", "simples") or "simples"),
        )
        if chave_item == chave_entrada:
            historico[idx] = {**item, **entrada}
            destino.historico_torneios = historico
            return

    historico.append(entrada)
    destino.historico_torneios = historico


def _fase_alcancada_apos_partida(
    instancia: Any, fase_atual: str, jogador_venceu: bool
) -> str:
    fase_norm = str(fase_atual or "").strip().lower()
    if not fase_norm:
        return ""
    if not jogador_venceu:
        return fase_norm
    if fase_norm == "final":
        return "campeao"

    try:
        fases = list(instancia._fases_ordem())
        idx = fases.index(fase_norm)
        if idx + 1 < len(fases):
            return str(fases[idx + 1]).lower()
    except Exception as e:
        log_erro(None, "_fase_alcancada_apos_partida", e)
    return fase_norm


def _desserializar_estrategia(estrategia: dict[str, Any] | None) -> dict[str, Any]:
    data = dict(estrategia or {})
    if data.get("saque") in {"seguro", "forcar"}:
        data["saque"] = (
            EstrategiaSaque.FORCAR
            if data["saque"] == "forcar"
            else EstrategiaSaque.SEGURO
        )
    if data.get("saque_tipo") in {"agressivo", "seguro", "variado"}:
        mapa_tipo = {
            "agressivo": TipoSaque.AGRESSIVO,
            "seguro": TipoSaque.SEGURO,
            "variado": TipoSaque.VARIADO,
        }
        data["saque_tipo"] = mapa_tipo[data["saque_tipo"]]
    if data.get("intencao") in {"arriscar", "paciente", "defensivo"}:
        mapa_intencao = {
            "arriscar": IntencaoPonto.ARRISCAR,
            "paciente": IntencaoPonto.PACIENTE,
            "defensivo": IntencaoPonto.DEFENSIVO,
        }
        data["intencao"] = mapa_intencao[data["intencao"]]
    return data


def _normalizar_estrategia(
    valor: str | None, estrategia_atual: dict[str, Any]
) -> dict[str, Any]:
    estrategia = dict(estrategia_atual or _estrategia_padrao())
    pacote = _normalizar_pacote_tatico(valor)
    if pacote:
        return _estrategia_do_pacote_tatico(
            pacote["mentalidade"],
            pacote["abordagem"],
            pacote["instrucao"],
            pacote["segundo_saque"],
            estrategia,
        )
    chave = str(valor or "").strip().lower()
    segundo_saque_override = None
    if "::" in chave:
        chave, segundo_saque_override = chave.split("::", 1)
        segundo_saque_override = segundo_saque_override.strip().lower()
    if chave in {"rede", "atacar_na_rede"}:
        estrategia["estilo"] = "atacar_na_rede"
    elif chave in {"variado", "atacar_pelo_meio"}:
        estrategia["estilo"] = "atacar_pelo_meio"
    elif chave in {"agressivo", "arriscar"}:
        estrategia["intencao"] = IntencaoPonto.ARRISCAR
        estrategia["saque"] = EstrategiaSaque.FORCAR
    elif chave in {"defensivo", "seguro"}:
        estrategia["intencao"] = IntencaoPonto.DEFENSIVO
        estrategia["saque"] = EstrategiaSaque.SEGURO
    else:
        estrategia["estilo"] = "atacar_do_fundo"
        estrategia["intencao"] = IntencaoPonto.PACIENTE

    if segundo_saque_override in {"seguro", "forcar"}:
        estrategia["saque"] = (
            EstrategiaSaque.FORCAR
            if segundo_saque_override == "forcar"
            else EstrategiaSaque.SEGURO
        )
    return estrategia


def _pontuacao_texto(pontos_a: int, pontos_b: int) -> tuple[str, str]:
    if pontos_a >= 3 and pontos_b >= 3:
        if pontos_a == pontos_b:
            return ("40", "40")
        if pontos_a > pontos_b:
            return ("AD", "40")
        return ("40", "AD")
    return (SCORE_MAP[min(pontos_a, 3)], SCORE_MAP[min(pontos_b, 3)])


@dataclass
class MatchRuntime:
    partida_id: str
    save_name: str
    modo: str
    jogador: Any
    adversario: dict[str, Any]
    torneio_info: dict[str, Any]
    config: ConfigPartida
    modalidade: str = "simples"
    estrategia_j: dict[str, Any] = field(default_factory=_estrategia_padrao)
    estrategia_a: dict[str, Any] = field(default_factory=dict)
    simulador: SimuladorPonto = field(init=False)
    contexto_partida: ContextoPartida = field(init=False)
    stats_j: EstatisticasPartida = field(default_factory=EstatisticasPartida)
    stats_a: EstatisticasPartida = field(default_factory=EstatisticasPartida)
    sets: list[int] = field(default_factory=lambda: [0, 0])
    games: list[int] = field(default_factory=lambda: [0, 0])
    pontos: list[int] = field(default_factory=lambda: [0, 0])
    set_scores: list[tuple[int, int]] = field(default_factory=list)
    sacador: str = "j"
    encerrado: bool = False
    vencedor: str | None = None
    log: list[str] = field(default_factory=list)
    pausado: bool = False
    total_pontos: int = 0
    energia_inicial: int = 100
    energia_inicial_a: int = 100
    fadiga_inicial_j: int = 0
    fadiga_inicial_a: int = 0
    finalizado_torneio: bool = False
    last_point_snapshot: dict[str, Any] = field(default_factory=dict)
    ajuste_tatico_j: str = "manter"
    ajuste_tatico_a: str = "manter"

    def __post_init__(self) -> None:
        self.estrategia_j = _normalizar_estrategia(self.modo, self.estrategia_j)
        self.estrategia_a = _definir_estrategia_auto(
            self.adversario, self.config.superficie
        )
        self.simulador = SimuladorPonto(self.jogador, self.adversario)
        self.contexto_partida = ContextoPartida(
            superficie=self.config.superficie,
            stamina_j=float(getattr(self.jogador, "energia", 100)),
            stamina_a=float(self.adversario.get("energia", 100) or 100),
            moral_j=float(getattr(self.jogador, "moral", 70)),
            moral_a=float(self.adversario.get("moral", 70) or 70),
            ritmo_j=float(getattr(self.jogador, "ritmo_jogo", 50)),
            ritmo_a=float(self.adversario.get("ritmo_jogo", 50) or 50),
            clima=self.config.clima,
            vento=self.config.vento,
            umidade=self.config.umidade,
            altitude_m=self.config.altitude_m,
            indoor=self.config.indoor,
        )
        self.energia_inicial = int(getattr(self.jogador, "energia", 100) or 100)
        self.energia_inicial_a = int(self.adversario.get("energia", 100) or 100)
        self.fadiga_inicial_j = int(getattr(self.jogador, "fadiga", 0) or 0)
        self.fadiga_inicial_a = int(self.adversario.get("fadiga", 0) or 0)
        bonus_rival = obter_bonus_rivalidade(
            self.jogador, self.adversario.get("nome", "Adversario")
        )
        if bonus_rival.get("ativa"):
            self.contexto_partida.moral_j = min(
                100.0, self.contexto_partida.moral_j + bonus_rival["bonus_mental"]
            )
            self.contexto_partida.momentum_j = min(
                6, self.contexto_partida.momentum_j + bonus_rival["bonus_momentum"]
            )
            self.log.append(
                f"Partida de rival contra {bonus_rival['nome']} (H2H {bonus_rival['vitorias']}-{bonus_rival['derrotas']})."
            )

    @classmethod
    def from_snapshot(cls, payload: dict[str, Any]) -> "MatchRuntime":
        jogador = carregar_jogador(payload["save_name"])
        if jogador is None:
            raise HTTPException(
                status_code=404,
                detail="Jogador do save da partida nao encontrado.",
            )

        runtime = cls(
            partida_id=payload["partida_id"],
            save_name=payload["save_name"],
            modo=payload["modo"],
            jogador=jogador,
            adversario=payload["adversario"],
            torneio_info=payload["torneio_info"],
            config=ConfigPartida(**payload["config"]),
            modalidade=payload.get("modalidade", "simples"),
            estrategia_j=_desserializar_estrategia(payload.get("estrategia_j")),
            estrategia_a=_desserializar_estrategia(payload.get("estrategia_a")),
        )
        runtime.estrategia_j = _desserializar_estrategia(payload.get("estrategia_j"))
        runtime.estrategia_a = _desserializar_estrategia(payload.get("estrategia_a"))
        runtime.stats_j = EstatisticasPartida(**payload.get("stats_j", {}))
        runtime.stats_a = EstatisticasPartida(**payload.get("stats_a", {}))
        contexto_raw = payload.get("contexto_partida", {}) or {}
        campos_contexto = ContextoPartida.__dataclass_fields__.keys()
        contexto_filtrado = {
            chave: valor
            for chave, valor in contexto_raw.items()
            if chave in campos_contexto
        }
        runtime.contexto_partida = ContextoPartida(**contexto_filtrado)
        runtime.sets = list(payload.get("sets", [0, 0]))
        runtime.games = list(payload.get("games", [0, 0]))
        runtime.pontos = list(payload.get("pontos", [0, 0]))
        runtime.set_scores = [tuple(item) for item in payload.get("set_scores", [])]
        runtime.sacador = payload.get("sacador", "j")
        runtime.encerrado = bool(payload.get("encerrado", False))
        runtime.vencedor = payload.get("vencedor")
        runtime.log = list(payload.get("log", []))
        runtime.pausado = bool(payload.get("pausado", False))
        runtime.total_pontos = int(payload.get("total_pontos", 0))
        runtime.energia_inicial = int(payload.get("energia_inicial", 100))
        runtime.energia_inicial_a = int(payload.get("energia_inicial_a", 100))
        runtime.fadiga_inicial_j = int(payload.get("fadiga_inicial_j", 0))
        runtime.fadiga_inicial_a = int(payload.get("fadiga_inicial_a", 0))
        runtime.finalizado_torneio = bool(payload.get("finalizado_torneio", False))
        runtime.last_point_snapshot = dict(payload.get("last_point_snapshot", {}) or {})
        runtime.ajuste_tatico_j = str(payload.get("ajuste_tatico_j", "manter"))
        runtime.ajuste_tatico_a = str(payload.get("ajuste_tatico_a", "manter"))
        return runtime

    def _fadiga_ao_vivo(self, lado: str) -> int:
        if lado == "j":
            fadiga_inicial = int(
                getattr(self, "fadiga_inicial_j", getattr(self.jogador, "fadiga", 0))
                or 0
            )
            energia_inicial = int(getattr(self, "energia_inicial", 100) or 100)
            stamina_atual = int(
                round(getattr(self.contexto_partida, "stamina_j", energia_inicial))
            )
        else:
            fadiga_inicial = int(
                getattr(self, "fadiga_inicial_a", self.adversario.get("fadiga", 0)) or 0
            )
            energia_inicial = int(
                getattr(self, "energia_inicial_a", self.adversario.get("energia", 100))
                or 100
            )
            stamina_atual = int(
                round(getattr(self.contexto_partida, "stamina_a", energia_inicial))
            )

        energia_perdida = max(0, energia_inicial - stamina_atual)
        aumento = _aumento_fadiga_nao_linear(
            fadiga_inicial,
            int(getattr(self, "total_pontos", 0) or 0),
            energia_perdida=energia_perdida,
        )
        return min(100, fadiga_inicial + aumento)

    def _sets_para_vencer(self) -> int:
        return self.config.melhor_de // 2 + 1

    def _is_tiebreak(self) -> bool:
        return self.games == [6, 6]

    def _tiebreak_alvo(self) -> int:
        if sum(self.sets) + 1 == self.config.melhor_de:
            return int(self.config.tiebreak_decisivo_pontos or 7)
        return 7

    def _contexto_ponto(self) -> ContextoPonto:
        return ContextoPonto(
            sacador=self.sacador,
            placar_game=(self.pontos[0], self.pontos[1]),
            placar_set=(self.games[0], self.games[1]),
            placar_partida=(self.sets[0], self.sets[1]),
            sets_para_vencer=self._sets_para_vencer(),
            is_tiebreak=self._is_tiebreak(),
            tiebreak_alvo=self._tiebreak_alvo(),
        )

    def _tipo_saque_do_sacador(self) -> TipoSaque:
        if self.sacador == "j":
            estrategia = self.estrategia_j
        else:
            estrategia = self.estrategia_a
        return estrategia.get("saque_tipo", TipoSaque.VARIADO)

    def _descricao_evento(
        self,
        vencedor_ponto: str,
        stats_info: dict[str, Any],
        descricoes: list[str] | None = None,
    ) -> str:
        if descricoes:
            return " ".join(
                str(item).strip() for item in descricoes if str(item).strip()
            )
        if stats_info.get("ace"):
            return "Ace do jogador." if vencedor_ponto == "j" else "Ace do adversario."
        if stats_info.get("dupla_falta"):
            return "Dupla falta."
        if stats_info.get("winner"):
            return (
                "Winner do jogador."
                if vencedor_ponto == "j"
                else "Winner do adversario."
            )
        if stats_info.get("erro_nao_forcado"):
            return "Erro nao forcado no rally."
        return "Ponto disputado."

    def _atualizar_pos_ponto(
        self, contexto: ContextoPonto, vencedor_ponto: str, stats_info: dict[str, Any]
    ) -> None:
        atualizar_estatisticas(
            self.stats_j,
            self.stats_a,
            vencedor_ponto,
            stats_info,
            contexto,
        )
        (
            self.contexto_partida.momentum_j,
            self.contexto_partida.momentum_a,
            self.contexto_partida.sequencia_j,
            self.contexto_partida.sequencia_a,
            self.contexto_partida.ultimo_vencedor,
        ) = atualizar_momentum_contextual(
            self.contexto_partida.momentum_j,
            self.contexto_partida.momentum_a,
            self.contexto_partida.sequencia_j,
            self.contexto_partida.sequencia_a,
            self.contexto_partida.ultimo_vencedor,
            vencedor=vencedor_ponto,
            is_match_point=contexto.is_match_point(),
            is_set_point=contexto.is_set_point(),
            is_break_point=contexto.is_break_point(),
            is_tiebreak=contexto.is_tiebreak,
            jogador_perdendo=contexto.jogador_perdendo(),
            adversario_perdendo=contexto.adversario_perdendo(),
            pj=contexto.placar_game[0],
            pa=contexto.placar_game[1],
        )
        (
            self.contexto_partida.stamina_j,
            self.contexto_partida.stamina_a,
        ) = aplicar_custo_stamina_contextual(
            self.contexto_partida.stamina_j,
            self.contexto_partida.stamina_a,
            stats_info=stats_info,
            superficie=self.contexto_partida.superficie,
            clima=self.contexto_partida.clima,
            umidade=self.contexto_partida.umidade,
            contexto_flags={
                "is_break_point": contexto.is_break_point(),
                "is_set_point": contexto.is_set_point(),
                "is_match_point": contexto.is_match_point(),
            },
            atributos_j=getattr(self.jogador, "atributos", {}),
            atributos_a=self.adversario.get("atributos", {}),
            psico_j=getattr(self.jogador, "atributos_psicologicos", {}),
            psico_a=self.adversario.get("atributos_psicologicos", {}),
            estrategia_j=self.estrategia_j,
            estrategia_a=self.estrategia_a,
        )

    def _recuperar_stamina_intervalo(self, multiplicador: int = 1) -> None:
        fisico_j = float(getattr(self.jogador, "atributos", {}).get("fisico", 50) or 50)
        fisico_a = float(self.adversario.get("atributos", {}).get("fisico", 50) or 50)
        repeticoes = max(1, int(multiplicador))
        for _ in range(repeticoes):
            self.contexto_partida.stamina_j = calcular_stamina_pos_recuperacao(
                self.contexto_partida.stamina_j,
                fisico=fisico_j,
                indoor=self.contexto_partida.indoor,
                clima=self.contexto_partida.clima,
                umidade=self.contexto_partida.umidade,
            )
            self.contexto_partida.stamina_a = calcular_stamina_pos_recuperacao(
                self.contexto_partida.stamina_a,
                fisico=fisico_a,
                indoor=self.contexto_partida.indoor,
                clima=self.contexto_partida.clima,
                umidade=self.contexto_partida.umidade,
            )

    def _atualizar_placar(self, vencedor_ponto: str) -> tuple[str, str]:
        idx = 0 if vencedor_ponto == "j" else 1
        self.pontos[idx] += 1
        event_type = "ponto"
        message = "Ponto confirmado."

        if self._is_tiebreak():
            total = self.pontos[0] + self.pontos[1]
            if total % 2 == 1:
                self.sacador = "a" if self.sacador == "j" else "j"
            alvo = self._tiebreak_alvo()
            if max(self.pontos) >= alvo and abs(self.pontos[0] - self.pontos[1]) >= 2:
                set_winner = 0 if self.pontos[0] > self.pontos[1] else 1
                self.games[set_winner] += 1
                event_type = "set"
                message = f"Set decidido no tiebreak por {self._nome_lado(set_winner)}."
                self._fechar_set(set_winner)
            return event_type, message

        if self.pontos[idx] >= 4 and abs(self.pontos[0] - self.pontos[1]) >= 2:
            self.games[idx] += 1
            self.pontos = [0, 0]
            self.sacador = "a" if self.sacador == "j" else "j"
            event_type = "game"
            message = f"Game para {self._nome_lado(idx)}."
            self._recuperar_stamina_intervalo()
            if not self.encerrado:
                self._ajustar_plano_adversario("game")
            if self._set_encerrado():
                event_type = "set"
                message = f"Set para {self._nome_lado(idx)}."
                self._fechar_set(idx)
        return event_type, message

    def _set_encerrado(self) -> bool:
        return (
            max(self.games) >= 6 and abs(self.games[0] - self.games[1]) >= 2
        ) or max(self.games) == 7

    def _fechar_set(self, vencedor_set: int) -> None:
        self.set_scores.append((self.games[0], self.games[1]))
        self.sets[vencedor_set] += 1
        partida_continua = self.sets[vencedor_set] < self._sets_para_vencer()

        if partida_continua:
            self._recuperar_stamina_intervalo(multiplicador=2)
            # Lógica de ajuste tático do NPC
            # Se o NPC perdeu o set, ele tende a arriscar mais
            if vencedor_set == 0:  # Jogador venceu o set
                self.ajuste_tatico_a = random.choice(["agressivo", "manter"])
            else:  # NPC venceu o set
                self.ajuste_tatico_a = random.choice(["seguro", "manter"])

        self.games = [0, 0]
        self.pontos = [0, 0]
        if not self.encerrado:
            self._ajustar_plano_adversario("set")
        if not partida_continua:
            self.encerrado = True
            self.vencedor = "jogador" if vencedor_set == 0 else "adversario"
        self.sacador = "a" if self.sacador == "j" else "j"

    def aplicar_ajuste_tatico(self, ajuste: str) -> None:
        """Aplica um ajuste tático temporário (para o próximo set)."""
        validos = {"agressivo", "seguro", "manter"}
        if ajuste.lower() in validos:
            self.ajuste_tatico_j = ajuste.lower()
            self._persistir()

    @staticmethod
    def _pct(valor: int, total: int) -> float:
        if total <= 0:
            return 0.0
        return (float(valor) / float(total)) * 100.0

    def _ajustar_plano_adversario(self, fase: str = "game") -> None:
        estrategia_base = _definir_estrategia_auto(
            self.adversario, self.config.superficie
        )
        vantagem_adversario = self.sets[1] - self.sets[0]
        stamina_a = float(getattr(self.contexto_partida, "stamina_a", 100) or 100)
        pct_primeiro_a = self._pct(
            self.stats_a.primeiro_saque_in, self.stats_a.primeiro_saque_total
        )
        pct_devolucao_a = self._pct(
            self.stats_a.pontos_ganhos_devolucao, self.stats_a.pontos_total_devolucao
        )
        winners_delta = self.stats_a.winners - self.stats_j.winners
        erros_delta = self.stats_a.erros_nao_forcados - self.stats_j.erros_nao_forcados
        rallies_longos = self.stats_a.rallies_longos
        rallies_curtos = self.stats_a.rallies_curtos

        estrategia = dict(self.estrategia_a or estrategia_base or _estrategia_padrao())
        estrategia.update({k: v for k, v in estrategia_base.items() if v is not None})

        if vantagem_adversario < 0:
            estrategia["intencao"] = IntencaoPonto.ARRISCAR
            estrategia["saque"] = EstrategiaSaque.FORCAR
            if estrategia.get("estilo") == "atacar_do_fundo":
                estrategia["saque_tipo"] = TipoSaque.AGRESSIVO
        elif stamina_a < 45:
            estrategia["intencao"] = IntencaoPonto.DEFENSIVO
            estrategia["saque"] = EstrategiaSaque.SEGURO
            estrategia["saque_tipo"] = TipoSaque.SEGURO
        elif vantagem_adversario > 0:
            estrategia["intencao"] = estrategia.get("intencao", IntencaoPonto.PACIENTE)
            estrategia["saque"] = estrategia.get("saque", EstrategiaSaque.SEGURO)

        if pct_primeiro_a < 52:
            estrategia["saque"] = EstrategiaSaque.SEGURO
            estrategia["saque_tipo"] = TipoSaque.SEGURO
        elif pct_primeiro_a > 66 and winners_delta <= 0:
            estrategia["saque"] = EstrategiaSaque.FORCAR
            if estrategia.get("estilo") != "atacar_na_rede":
                estrategia["saque_tipo"] = TipoSaque.AGRESSIVO

        if pct_devolucao_a < 26 and stamina_a >= 50:
            estrategia["estilo"] = "atacar_do_fundo"
            estrategia["intencao"] = IntencaoPonto.DEFENSIVO
        elif winners_delta <= -4 and erros_delta <= 0:
            estrategia["estilo"] = "atacar_pelo_meio"
            estrategia["intencao"] = IntencaoPonto.ARRISCAR
        elif rallies_longos > rallies_curtos + 4 and stamina_a < 55:
            estrategia["estilo"] = "atacar_na_rede"
            estrategia["intencao"] = IntencaoPonto.ARRISCAR

        if fase == "set" and stamina_a >= 58 and winners_delta < 0:
            estrategia["intencao"] = IntencaoPonto.ARRISCAR
            if estrategia.get("estilo") == "atacar_do_fundo":
                estrategia["saque_tipo"] = TipoSaque.AGRESSIVO

        self.estrategia_a = estrategia

    def _nome_lado(self, indice: int) -> str:
        return (
            getattr(self.jogador, "nome", "Jogador")
            if indice == 0
            else self.adversario.get("nome", "Adversario")
        )

    def _placar_final_texto(self) -> str:
        vencedor_nome = (
            getattr(self.jogador, "nome", "Jogador")
            if self.vencedor == "jogador"
            else self.adversario.get("nome", "Adversario")
        )
        perdedor_nome = (
            self.adversario.get("nome", "Adversario")
            if self.vencedor == "jogador"
            else getattr(self.jogador, "nome", "Jogador")
        )
        sets_vencedor = max(self.sets)
        sets_perdedor = min(self.sets)
        return f"{vencedor_nome} {sets_vencedor} x {sets_perdedor} {perdedor_nome}"

    def _serializar_stats_lado(
        self, stats: EstatisticasPartida
    ) -> dict[str, str | int]:
        return {
            "aces": stats.aces,
            "duplas_faltas": stats.duplas_faltas,
            "primeiro_saque_pct": stats.percentual_primeiro_saque(),
            "winners": stats.winners,
            "erros_nao_forcados": stats.erros_nao_forcados,
            "pontos_saque_pct": stats.percentual_pontos_saque(),
            "pontos_devolucao_pct": stats.percentual_pontos_devolucao(),
            "break_points": f"{stats.break_points_convertidos}/{stats.break_points_total}",
            "rallies_curtos": stats.rallies_curtos,
            "rallies_medios": stats.rallies_medios,
            "rallies_longos": stats.rallies_longos,
        }

    def _registrar_historicos(self, instancia) -> None:
        temporada = carregar_temporada(self.save_name)
        fase_label = str(
            self.torneio_info.get("fase_atual") or self.torneio_info.get("fase") or ""
        )
        if not fase_label:
            try:
                estado = instancia._carregar_estado()
                fase_label = str(estado.get("fase_atual") or "")
            except Exception as e:
                log_erro(self.save_name, "_registrar_historicos:fase_label", e)
                fase_label = ""

        adversario_nome = self.adversario.get("nome", "Adversario")
        placar_final = self._placar_final_texto()
        jogador_venceu = self.vencedor == "jogador"
        fase_alcancada = _fase_alcancada_apos_partida(
            instancia, fase_label, jogador_venceu
        )

        historico_jogador = {
            "ano": temporada.get("ano"),
            "semana": temporada.get("semana"),
            "torneio": self.torneio_info.get("nome", "Torneio Desconhecido"),
            "fase": fase_label,
            "adversario": adversario_nome,
            "placar": placar_final,
            "resultado": "V" if jogador_venceu else "D",
        }
        historico_partidas = list(getattr(self.jogador, "historico_partidas", []) or [])
        historico_partidas.append(historico_jogador)
        self.jogador.historico_partidas = historico_partidas[-30:]
        atualizar_rivalidade(
            self.jogador,
            adversario_nome,
            jogador_venceu,
            semana=temporada.get("semana"),
        )
        _atualizar_historico_torneios(
            self.jogador,
            {
                "nome": self.torneio_info.get("nome", "Torneio Desconhecido"),
                "torneio": self.torneio_info.get("nome", "Torneio Desconhecido"),
                "tipo": self.torneio_info.get("tipo", ""),
                "semana": temporada.get("semana"),
                "ano": temporada.get("ano"),
                "fase": fase_alcancada or fase_label,
                "fase_alcancada": fase_alcancada or fase_label,
                "pontos": 0,
                "premio": 0,
                "modalidade": self.modalidade,
                "expirado": False,
            },
        )

        ranking = getattr(instancia, "ranking", None)
        if ranking and adversario_nome:
            rival = ranking.buscar_jogador_por_nome(adversario_nome)
            if isinstance(rival, dict):
                rival_historico = list(rival.get("historico_partidas", []) or [])
                rival_historico.append(
                    {
                        "ano": temporada.get("ano"),
                        "semana": temporada.get("semana"),
                        "torneio": self.torneio_info.get(
                            "nome", "Torneio Desconhecido"
                        ),
                        "fase": fase_label,
                        "adversario": getattr(self.jogador, "nome", "Jogador"),
                        "placar": placar_final,
                        "resultado": "D" if jogador_venceu else "V",
                    }
                )
                rival["historico_partidas"] = rival_historico[-30:]
                rival["energia"] = int(round(self.contexto_partida.stamina_a))
                rival["fadiga"] = self._fadiga_ao_vivo("a")
                if "overall" not in rival or not rival.get("overall"):
                    from api.routes.ranking import _calcular_overall

                    rival["overall"] = _calcular_overall(rival)
                rival["ranking_pos"] = ranking.obter_posicao(
                    adversario_nome
                ) or rival.get("ranking_pos", 0)
                self.adversario.update(
                    {
                        "historico_partidas": rival["historico_partidas"],
                        "overall": rival.get("overall"),
                        "ranking_pos": rival.get("ranking_pos"),
                        "nacionalidade": rival.get(
                            "nacionalidade", self.adversario.get("nacionalidade")
                        ),
                    }
                )
                ranking.salvar_ranking()

        try:
            MatchHistoryManager(self.save_name).adicionar_partida(
                torneio=self.torneio_info.get("nome", "Torneio Desconhecido"),
                semana=temporada.get("semana", 1),
                ano=temporada.get("ano", 2026),
                modalidade="simples",
                jogadores=[getattr(self.jogador, "nome", "Jogador"), adversario_nome],
                resultado=placar_final,
                vencedor=(
                    getattr(self.jogador, "nome", "Jogador")
                    if jogador_venceu
                    else adversario_nome
                ),
                fase=fase_label,
            )
        except Exception as e:
            log_erro(self.save_name, "MatchHistoryManager.adicionar_partida", e)

    def _finalizar_torneio(self) -> None:
        if self.finalizado_torneio:
            return

        instancia = carregar_torneio_api(self.save_name)
        if not instancia:
            self.finalizado_torneio = True
            return

        vitoria = self.vencedor == "jogador"
        vencedor_nome = (
            getattr(self.jogador, "nome", "Jogador")
            if vitoria
            else self.adversario.get("nome", "Adversario")
        )

        instancia.processar_resultado_partida(
            self.jogador,
            self.adversario,
            {"nome": vencedor_nome},
            self._placar_final_texto(),
        )

        try:
            instancia.simular_npcs_na_fase_atual(instancia.jogador_nome)
            avancar_fase(instancia)
        except Exception as e:
            log_erro(self.save_name, "_finalizar_torneio:avancar_fase", e)

        self._registrar_historicos(instancia)

        self.jogador.energia = int(round(self.contexto_partida.stamina_j))
        self.jogador = handle_xp_e_level_up(self.jogador, vitoria)

        # Progressão natural baseada no desempenho da partida
        from src.progressao import handle_progressao_natural

        handle_progressao_natural(
            self.jogador,
            self.stats_j,
            self.estrategia_j,
            self.total_pontos,
            modalidade=self.modalidade,
        )

        self.jogador = handle_fadiga_e_lesao(
            self.jogador,
            pontos_disputados=self.total_pontos,
            fatores_partida=instancia._montar_fatores_fadiga(
                self.config, self.adversario
            ),
            energia_perdida=max(
                0, self.energia_inicial - int(round(self.contexto_partida.stamina_j))
            ),
            ranking=instancia.ranking,
        )
        self.adversario = (
            handle_fadiga_e_lesao_npc(
                self.adversario,
                pontos_disputados=self.total_pontos,
                fatores_partida=instancia._montar_fatores_fadiga(
                    self.config, self.adversario
                ),
                energia_perdida=max(
                    0,
                    self.energia_inicial_a
                    - int(round(self.contexto_partida.stamina_a)),
                ),
                rank_atual=self.adversario.get("ranking_pos"),
            )
            or self.adversario
        )
        salvar_jogo(self.save_name, self.jogador)
        estado_final = instancia._carregar_estado()
        if estado_final.get("fase_atual") == "finalizado" or not estado_final.get(
            "jogador_vivo", True
        ):
            from src.pontuacao import distribuir_pontos_torneio

            distribuir_pontos_torneio(
                self.save_name, genero=getattr(self.jogador, "genero", "masculino")
            )
        self.finalizado_torneio = True
        self._persistir()

    def to_snapshot(self) -> dict[str, Any]:
        return {
            "partida_id": self.partida_id,
            "save_name": self.save_name,
            "modo": self.modo,
            "modalidade": self.modalidade,
            "adversario": self.adversario,
            "torneio_info": self.torneio_info,
            "config": dict(self.config.__dict__),
            "estrategia_j": _serializar_estrategia(self.estrategia_j),
            "estrategia_a": _serializar_estrategia(self.estrategia_a),
            "stats_j": dict(self.stats_j.__dict__),
            "stats_a": dict(self.stats_a.__dict__),
            "contexto_partida": dict(self.contexto_partida.__dict__),
            "sets": list(self.sets),
            "games": list(self.games),
            "pontos": list(self.pontos),
            "set_scores": [list(item) for item in self.set_scores],
            "sacador": self.sacador,
            "encerrado": self.encerrado,
            "vencedor": self.vencedor,
            "log": list(self.log[-100:]),
            "pausado": self.pausado,
            "total_pontos": self.total_pontos,
            "energia_inicial": self.energia_inicial,
            "energia_inicial_a": self.energia_inicial_a,
            "fadiga_inicial_j": self.fadiga_inicial_j,
            "fadiga_inicial_a": self.fadiga_inicial_a,
            "finalizado_torneio": self.finalizado_torneio,
            "last_point_snapshot": dict(self.last_point_snapshot),
            "ajuste_tatico_j": self.ajuste_tatico_j,
            "ajuste_tatico_a": self.ajuste_tatico_a,
        }

    def _persistir(self) -> None:
        save_snapshot(self.save_name, self.partida_id, self.to_snapshot())
        set_runtime_cache(self.partida_id, self)

    def serializar(
        self, event_type: str = "ponto", descricao: str = ""
    ) -> dict[str, Any]:
        if self.encerrado:
            pontos = ["-", "-"]
        elif self._is_tiebreak():
            pontos = [str(self.pontos[0]), str(self.pontos[1])]
        else:
            pontos = list(_pontuacao_texto(self.pontos[0], self.pontos[1]))

        payload: dict[str, Any] = {
            "tipo": event_type,
            "descricao": descricao,
            "sets": [int(self.sets[0]), int(self.sets[1])],
            "games": [int(self.games[0]), int(self.games[1])],
            "pontos": pontos,
            "servindo": "jogador" if self.sacador == "j" else "adversario",
            "log": self.log[-25:],
            "encerrado": self.encerrado,
            "stats_j": self._serializar_stats_lado(self.stats_j),
            "stats_a": self._serializar_stats_lado(self.stats_a),
            "last_point_stats": self.last_point_snapshot,
            "energia_j": int(round(self.contexto_partida.stamina_j)),
            "energia_a": int(round(self.contexto_partida.stamina_a)),
            "fadiga_j": self._fadiga_ao_vivo("j"),
            "fadiga_a": self._fadiga_ao_vivo("a"),
            "estrategia_j": _serializar_estrategia(self.estrategia_j),
            "estrategia_a": _serializar_estrategia(self.estrategia_a),
            "ajuste_tatico_j": self.ajuste_tatico_j,
            "ajuste_tatico_a": self.ajuste_tatico_a,
        }
        if self.encerrado and self.vencedor:
            payload["vencedor"] = self.vencedor
            payload["placar_final"] = self._placar_final_texto()
        return payload

    def aplicar_estrategia(self, valor: str | None) -> None:
        self.estrategia_j = _normalizar_estrategia(valor, self.estrategia_j)
        self._persistir()

    def definir_pausa(self, pausado: bool) -> None:
        self.pausado = bool(pausado)
        self._persistir()

    def jogar_ponto(self) -> dict[str, Any]:
        if self.encerrado:
            return self.serializar(event_type="fim", descricao="Partida encerrada.")

        # X-5: Aplicar bônus táticos temporários antes de simular o ponto
        def _get_psico_com_ajuste(lado: str):
            if lado == "j":
                base = self.simulador._get_psico_jogador()
                ajuste = self.ajuste_tatico_j
            else:
                base = self.simulador._get_psico_adversario()
                ajuste = self.ajuste_tatico_a

            result = dict(base)
            if ajuste == "agressivo":
                result["agressividade"] = min(100, result.get("agressividade", 50) + 10)
                result["concentracao"] = max(0, result.get("concentracao", 50) - 5)
            elif ajuste == "seguro":
                result["concentracao"] = min(100, result.get("concentracao", 50) + 10)
                result["agressividade"] = max(0, result.get("agressividade", 50) - 10)
            return result

        psico_j_temp = _get_psico_com_ajuste("j")
        psico_a_temp = _get_psico_com_ajuste("a")

        # Monkey-patch temporário nos métodos de obter psico do simulador para este ponto
        # (Design pattern: Strategy/Decorator em runtime)
        old_get_j = self.simulador._get_psico_jogador
        old_get_a = self.simulador._get_psico_adversario
        self.simulador._get_psico_jogador = lambda: psico_j_temp
        self.simulador._get_psico_adversario = lambda: psico_a_temp

        try:
            contexto = self._contexto_ponto()
            if self.modo == "detalhado":
                vencedor, descricoes, stats_info = self.simulador.simular_ponto_detalhado(
                    self.estrategia_j,
                    contexto,
                    tipo_saque=self._tipo_saque_do_sacador(),
                    contexto_partida=self.contexto_partida,
                    estrategia_adversario=self.estrategia_a,
                )
            elif self.modo == "estrategista":
                vencedor, descricoes, stats_info = (
                    self.simulador.simular_ponto_estrategista(
                        self.estrategia_j,
                        contexto,
                        tipo_saque=self._tipo_saque_do_sacador(),
                        contexto_partida=self.contexto_partida,
                        estrategia_adversario=self.estrategia_a,
                    )
                )
            else:
                vencedor, stats_info = self.simulador.simular_ponto_rapido(
                    self.estrategia_j,
                    contexto=contexto,
                    contexto_partida=self.contexto_partida,
                    estrategia_adversario=self.estrategia_a,
                )
                descricoes = None

            stats_dict = (
                stats_info.to_dict()
                if hasattr(stats_info, "to_dict")
                else dict(stats_info)
            )
            self.last_point_snapshot = stats_dict
            self._atualizar_pos_ponto(contexto, vencedor, stats_dict)
            event_type, base_message = self._atualizar_placar(vencedor)
            descricao = self._descricao_evento(vencedor, stats_dict, descricoes)
            mensagem = f"{descricao} {base_message}".strip()
            self.log.append(mensagem)
            self.total_pontos += 1
        finally:
            self.simulador._get_psico_jogador = old_get_j
            self.simulador._get_psico_adversario = old_get_a

        if self.encerrado:
            self._finalizar_torneio()
            return self.serializar(event_type="fim", descricao=mensagem)
        self._persistir()
        return self.serializar(event_type=event_type, descricao=mensagem)

    def simular_set(self) -> dict[str, Any]:
        sets_iniciais = tuple(self.sets)
        ultimo_estado = self.serializar(event_type="set", descricao="Set ja concluido.")

        while not self.encerrado and tuple(self.sets) == sets_iniciais:
            ultimo_estado = self.jogar_ponto()

        return ultimo_estado

    def simular_partida(self) -> dict[str, Any]:
        ultimo_estado = self.serializar(
            event_type="fim", descricao="Partida ja concluida."
        )

        while not self.encerrado:
            ultimo_estado = self.jogar_ponto()

        return ultimo_estado


def criar_match_runtime(
    save_name: str,
    jogador: Any,
    adversario: dict[str, Any],
    torneio_info: dict[str, Any],
    modo: str,
    modalidade: str = "simples",
) -> MatchRuntime:
    partida_id = uuid4().hex
    invalidate_other_snapshots(save_name, partida_id)
    runtime = MatchRuntime(
        partida_id=partida_id,
        save_name=save_name,
        modo=modo,
        jogador=jogador,
        adversario=adversario,
        torneio_info=torneio_info,
        config=criar_config_partida(torneio_info),
        modalidade=modalidade,
    )
    runtime._persistir()
    return runtime


def obter_match_runtime(partida_id: str, save_name: str | None = None) -> MatchRuntime:
    runtime = get_runtime_cache(partida_id)
    if runtime:
        if save_name and getattr(runtime, "save_name", None) != save_name:
            raise HTTPException(status_code=404, detail="Partida ativa nao encontrada.")
        return runtime

    if save_name:
        payload = load_snapshot(save_name, partida_id)
        if payload:
            runtime = MatchRuntime.from_snapshot(payload)
            set_runtime_cache(partida_id, runtime)
            return runtime
    else:
        saves_root = Path(SAVES_DIR)
        if saves_root.exists():
            for save_dir in saves_root.iterdir():
                if not save_dir.is_dir():
                    continue
                payload = load_snapshot(save_dir.name, partida_id)
                if payload:
                    runtime = MatchRuntime.from_snapshot(payload)
                    set_runtime_cache(partida_id, runtime)
                    return runtime

    raise HTTPException(status_code=404, detail="Partida ativa nao encontrada.")
