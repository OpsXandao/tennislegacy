from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4
from fastapi import HTTPException

from src.match_state import ContextoPartida, ContextoPonto, EstatisticasPartida
from src.services.simulador_ponto import SimuladorPonto
from src.match_config import ConfigPartida, criar_config_partida
from src.constants.match_constants import EstrategiaSaque, IntencaoPonto, TipoSaque
from src.utils.tactics_utils import (
    estrategia_padrao_ui,
    normalizar_estrategia,
    serializar_estrategia,
    desserializar_estrategia,
)
from src.utils.match_runtime_utils import (
    valor_entidade,
    pontuacao_texto,
    resumo_textual_evento,
)
from src.jogador import obter_bonus_rivalidade


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
    estrategia_j: dict[str, Any] = field(default_factory=estrategia_padrao_ui)
    estrategia_a: dict[str, Any] = field(default_factory=dict)
    competidor_j: Any = field(init=False)
    competidor_a: dict[str, Any] = field(init=False)
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
    last_event_payload: dict[str, Any] = field(default_factory=dict)
    ajuste_tatico_j: str = "manter"
    ajuste_tatico_a: str = "manter"
    quimica_j: dict[str, Any] = field(default_factory=dict)
    quimica_a: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        from src.match_core import _definir_estrategia_auto

        if self.modo not in {"manual", "estrategista", "detalhado"}:
            self.estrategia_j = normalizar_estrategia(self.modo, self.estrategia_j)
        self.competidor_j = self.jogador
        self.competidor_a = self.adversario
        if self.modalidade == "duplas":
            from src.utils.match_doubles_utils import compor_dupla_efetiva

            self.competidor_j, self.competidor_a = compor_dupla_efetiva(
                self.save_name, self.jogador, self.adversario
            )
            self.adversario = self.competidor_a
            self.quimica_j = self.competidor_j.get("quimica", {})
            self.quimica_a = self.competidor_a.get("quimica", {})
        if not self.estrategia_a:
            self.estrategia_a = _definir_estrategia_auto(
                self.adversario, self.config.superficie
            )
        self.simulador = SimuladorPonto(self.competidor_j, self.competidor_a)
        self.contexto_partida = ContextoPartida(
            superficie=self.config.superficie,
            stamina_j=float(valor_entidade(self.competidor_j, "energia", 100) or 100),
            stamina_a=float(valor_entidade(self.competidor_a, "energia", 100) or 100),
            moral_j=float(valor_entidade(self.competidor_j, "moral", 70) or 70),
            moral_a=float(valor_entidade(self.competidor_a, "moral", 70) or 70),
            ritmo_j=float(valor_entidade(self.competidor_j, "ritmo_jogo", 50) or 50),
            ritmo_a=float(valor_entidade(self.competidor_a, "ritmo_jogo", 50) or 50),
            clima=self.config.clima,
            vento=self.config.vento,
            umidade=self.config.umidade,
            altitude_m=self.config.altitude_m,
            indoor=self.config.indoor,
        )
        self.energia_inicial = int(
            valor_entidade(self.competidor_j, "energia", 100) or 100
        )
        self.energia_inicial_a = int(
            valor_entidade(self.competidor_a, "energia", 100) or 100
        )
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
        from src.dados import carregar_jogador

        jogador = carregar_jogador(payload["save_name"])
        if jogador is None:
            raise HTTPException(
                status_code=404, detail="Jogador do save da partida nao encontrado."
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
            estrategia_j=desserializar_estrategia(payload.get("estrategia_j")),
            estrategia_a=desserializar_estrategia(payload.get("estrategia_a")),
        )
        runtime.stats_j = EstatisticasPartida(**payload.get("stats_j", {}))
        runtime.stats_a = EstatisticasPartida(**payload.get("stats_a", {}))
        contexto_raw = payload.get("contexto_partida", {}) or {}
        campos_contexto = ContextoPartida.__dataclass_fields__.keys()
        runtime.contexto_partida = ContextoPartida(
            **{k: v for k, v in contexto_raw.items() if k in campos_contexto}
        )
        for attr in [
            "sets",
            "games",
            "pontos",
            "log",
            "pausado",
            "total_pontos",
            "energia_inicial",
            "energia_inicial_a",
            "fadiga_inicial_j",
            "fadiga_inicial_a",
            "finalizado_torneio",
            "last_point_snapshot",
            "last_event_payload",
            "ajuste_tatico_j",
            "ajuste_tatico_a",
            "quimica_j",
            "quimica_a",
        ]:
            if attr in payload:
                setattr(runtime, attr, payload[attr])
        if "set_scores" in payload:
            runtime.set_scores = [tuple(item) for item in payload["set_scores"]]
        if "sacador" in payload:
            runtime.sacador = payload["sacador"]
        if "encerrado" in payload:
            runtime.encerrado = bool(payload["encerrado"])
        if "vencedor" in payload:
            runtime.vencedor = payload["vencedor"]
        return runtime

    def _fadiga_ao_vivo(self, lado: str) -> int:
        from src.fadiga import _aumento_fadiga_nao_linear

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
        estrategia = self.estrategia_j if self.sacador == "j" else self.estrategia_a
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
        padrao = str(stats_info.get("padrao", "") or "").strip()
        momento = stats_info.get("momento", "normal")
        if stats_info.get("ace"):
            return (
                "Seu saque entrou pesado e virou ace."
                if vencedor_ponto == "j"
                else "O rival abriu a quadra no saque e encaixou um ace."
            )
        if stats_info.get("dupla_falta"):
            return (
                "O rival cedeu sob pressão no segundo saque."
                if vencedor_ponto == "j"
                else "Seu segundo saque escapou no momento errado."
            )
        if stats_info.get("winner"):
            return (
                f"{padrao}."
                if padrao
                else (
                    "Você encontrou o golpe decisivo."
                    if vencedor_ponto == "j"
                    else "O rival achou o golpe decisivo."
                )
            )
        if stats_info.get("erro_nao_forcado"):
            return (
                "O rival vazou depois de perder o controle da troca."
                if vencedor_ponto == "j"
                else "Você entregou o ponto sem pressão suficiente."
            )
        if padrao:
            return f"{padrao}."
        if momento in {"match_point", "set_point", "break_point"}:
            return (
                "Você sobreviveu ao ponto grande."
                if vencedor_ponto == "j"
                else "O rival levou a melhor no ponto grande."
            )
        return "Troca equilibrada, ponto resolvido no detalhe."

    def _descricao_evento_json(
        self,
        vencedor_ponto: str,
        stats_info: dict[str, Any],
        descricoes: list[str] | None = None,
        event_type: str = "ponto",
    ) -> dict[str, Any]:
        texto = self._descricao_evento(vencedor_ponto, stats_info, descricoes).strip()
        momento = str(stats_info.get("momento", "normal") or "normal")
        tags = [
            t
            for t in ["ace", "dupla_falta", "winner", "erro_nao_forcado"]
            if stats_info.get(t)
        ]
        if self.modalidade == "duplas":
            tags.append("duplas")
        if momento != "normal":
            tags.append(momento)
        return {
            "kind": event_type,
            "headline": str(stats_info.get("padrao", "") or texto),
            "detail": texto,
            "winner": vencedor_ponto,
            "pressure": str(stats_info.get("pressao", "media") or "media"),
            "moment": momento,
            "mode": self.modo,
            "surface": self.config.superficie,
            "tags": tags,
            "insights": list(stats_info.get("insights", []) or []),
        }

    def _atualizar_pos_ponto(
        self, contexto: ContextoPonto, vencedor_ponto: str, stats_info: dict[str, Any]
    ) -> None:
        from src.match_core import atualizar_estatisticas
        from src.match_dynamics import (
            atualizar_momentum_contextual,
            aplicar_custo_stamina_contextual,
        )

        atualizar_estatisticas(
            self.stats_j, self.stats_a, vencedor_ponto, stats_info, contexto
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
        self.contexto_partida.stamina_j, self.contexto_partida.stamina_a = (
            aplicar_custo_stamina_contextual(
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
        )

    def _tem_fisioterapeuta(self, lado: str) -> bool:
        from src.management import obter_profissional_da_equipe

        if lado == "j":
            equipe = list(getattr(self.jogador, "equipe", []) or [])
        else:
            equipe = list(self.adversario.get("equipe", []) or [])
        return obter_profissional_da_equipe(equipe, "fisioterapeuta") is not None

    def _recuperar_stamina_intervalo(self, multiplicador: int = 1) -> None:
        from src.match_dynamics import calcular_stamina_pos_recuperacao

        fj = float(getattr(self.jogador, "atributos", {}).get("resistencia", 50) or 50)
        fa = float(self.adversario.get("atributos", {}).get("resistencia", 50) or 50)
        tipo = "set" if multiplicador >= 2 else "game"
        tem_fisio_j = self._tem_fisioterapeuta("j")
        tem_fisio_a = self._tem_fisioterapeuta("a")
        for _ in range(max(1, int(multiplicador))):
            self.contexto_partida.stamina_j = calcular_stamina_pos_recuperacao(
                self.contexto_partida.stamina_j,
                fisico=fj,
                indoor=self.contexto_partida.indoor,
                clima=self.contexto_partida.clima,
                umidade=self.contexto_partida.umidade,
                tipo=tipo,
                tem_fisioterapeuta=tem_fisio_j,
            )
            self.contexto_partida.stamina_a = calcular_stamina_pos_recuperacao(
                self.contexto_partida.stamina_a,
                fisico=fa,
                indoor=self.contexto_partida.indoor,
                clima=self.contexto_partida.clima,
                umidade=self.contexto_partida.umidade,
                tipo=tipo,
                tem_fisioterapeuta=tem_fisio_a,
            )

    def _atualizar_placar(self, vencedor_ponto: str) -> tuple[str, str]:
        idx = 0 if vencedor_ponto == "j" else 1
        self.pontos[idx] += 1
        if self._is_tiebreak():
            if (self.pontos[0] + self.pontos[1]) % 2 == 1:
                self.sacador = "a" if self.sacador == "j" else "j"
            if (
                max(self.pontos) >= self._tiebreak_alvo()
                and abs(self.pontos[0] - self.pontos[1]) >= 2
            ):
                sw = 0 if self.pontos[0] > self.pontos[1] else 1
                self.games[sw] += 1
                self._fechar_set(sw)
                return "set", f"Set decidido no tiebreak por {self._nome_lado(sw)}."
            return "ponto", "Ponto confirmado."
        if self.pontos[idx] >= 4 and abs(self.pontos[0] - self.pontos[1]) >= 2:
            self.games[idx] += 1
            self.pontos = [0, 0]
            self.sacador = "a" if self.sacador == "j" else "j"
            self._recuperar_stamina_intervalo()
            if not self.encerrado:
                self._ajustar_plano_adversario("game")
            if self._set_encerrado():
                self._fechar_set(idx)
                return "set", f"Set para {self._nome_lado(idx)}."
            return "game", f"Game para {self._nome_lado(idx)}."
        return "ponto", "Ponto confirmado."

    def _set_encerrado(self) -> bool:
        return (
            max(self.games) >= 6 and abs(self.games[0] - self.games[1]) >= 2
        ) or max(self.games) == 7

    def _fechar_set(self, vencedor_set: int) -> None:
        self.set_scores.append((self.games[0], self.games[1]))
        self.sets[vencedor_set] += 1
        cont = self.sets[vencedor_set] < self._sets_para_vencer()
        if cont:
            self._recuperar_stamina_intervalo(multiplicador=2)
            self.ajuste_tatico_a = (
                random.choice(["agressivo", "manter"])
                if vencedor_set == 0
                else random.choice(["seguro", "manter"])
            )
        self.games = [0, 0]
        self.pontos = [0, 0]
        if not self.encerrado:
            self._ajustar_plano_adversario("set")
        if not cont:
            self.encerrado = True
            self.vencedor = "jogador" if vencedor_set == 0 else "adversario"
        self.sacador = "a" if self.sacador == "j" else "j"

    def aplicar_ajuste_tatico(self, ajuste: str) -> None:
        if ajuste.lower() in {"agressivo", "seguro", "manter"}:
            self.ajuste_tatico_j = ajuste.lower()
            self._persistir()

    def _ajustar_plano_adversario(self, fase: str = "game") -> None:
        from src.match_core import _definir_estrategia_auto

        eb = _definir_estrategia_auto(self.adversario, self.config.superficie)

        def _pct(v, t):
            return (float(v) / float(t)) * 100.0 if t > 0 else 0.0

        st_a = float(getattr(self.contexto_partida, "stamina_a", 100) or 100)
        p1_a = _pct(self.stats_a.primeiro_saque_in, self.stats_a.primeiro_saque_total)
        pd_a = _pct(
            self.stats_a.pontos_ganhos_devolucao, self.stats_a.pontos_total_devolucao
        )
        w_d = self.stats_a.winners - self.stats_j.winners
        e_d = self.stats_a.erros_nao_forcados - self.stats_j.erros_nao_forcados
        est = dict(self.estrategia_a or eb or estrategia_padrao_ui())
        est.update({k: v for k, v in eb.items() if v is not None})
        if self.sets[1] - self.sets[0] < 0:
            est["intencao"] = IntencaoPonto.ARRISCAR
            est["saque"] = EstrategiaSaque.FORCAR
            if est.get("estilo") == "atacar_do_fundo":
                est["saque_tipo"] = TipoSaque.AGRESSIVO
        elif st_a < 45:
            est["intencao"] = IntencaoPonto.DEFENSIVO
            est["saque"] = EstrategiaSaque.SEGURO
            est["saque_tipo"] = TipoSaque.SEGURO
        if p1_a < 52:
            est["saque"] = EstrategiaSaque.SEGURO
            est["saque_tipo"] = TipoSaque.SEGURO
        elif p1_a > 66 and w_d <= 0:
            est["saque"] = EstrategiaSaque.FORCAR
            if est.get("estilo") != "atacar_na_rede":
                est["saque_tipo"] = TipoSaque.AGRESSIVO
        if pd_a < 26 and st_a >= 50:
            est["estilo"] = "atacar_do_fundo"
            est["intencao"] = IntencaoPonto.DEFENSIVO
        elif w_d <= -4 and e_d <= 0:
            est["estilo"] = "atacar_pelo_meio"
            est["intencao"] = IntencaoPonto.ARRISCAR
        elif (
            self.stats_a.rallies_longos > self.stats_a.rallies_curtos + 4 and st_a < 55
        ):
            est["estilo"] = "atacar_na_rede"
            est["intencao"] = IntencaoPonto.ARRISCAR
        if fase == "set" and st_a >= 58 and w_d < 0:
            est["intencao"] = IntencaoPonto.ARRISCAR
            if est.get("estilo") == "atacar_do_fundo":
                est["saque_tipo"] = TipoSaque.AGRESSIVO
        self.estrategia_a = est

    def _nome_lado(self, idx: int) -> str:
        return (
            getattr(self.jogador, "nome", "Jogador")
            if idx == 0
            else self.adversario.get("nome", "Adversario")
        )

    def _placar_final_texto(self) -> str:
        return f"{self._nome_lado(0 if self.vencedor == 'jogador' else 1)} {max(self.sets)} x {min(self.sets)} {self._nome_lado(1 if self.vencedor == 'jogador' else 0)}"

    def _serializar_stats_lado(self, s: EstatisticasPartida) -> dict:
        return {
            "aces": s.aces,
            "duplas_faltas": s.duplas_faltas,
            "primeiro_saque_pct": s.percentual_primeiro_saque(),
            "winners": s.winners,
            "erros_nao_forcados": s.erros_nao_forcados,
            "pontos_saque_pct": s.percentual_pontos_saque(),
            "pontos_devolucao_pct": s.percentual_pontos_devolucao(),
            "break_points": f"{s.break_points_convertidos}/{s.break_points_total}",
            "rallies_curtos": s.rallies_curtos,
            "rallies_medios": s.rallies_medios,
            "rallies_longos": s.rallies_longos,
        }

    def _registrar_historicos(self, instancia) -> None:
        from src.services.match_runtime_finalization import registrar_historicos

        registrar_historicos(self, instancia)

    def _finalizar_torneio(self) -> None:
        from src.services.match_runtime_finalization import finalizar_torneio

        finalizar_torneio(self)

    def to_snapshot(self) -> dict[str, Any]:
        d = {
            k: v
            for k, v in self.__dict__.items()
            if not k.startswith("_")
            and k
            not in [
                "jogador",
                "competidor_j",
                "competidor_a",
                "simulador",
                "contexto_partida",
                "config",
                "stats_j",
                "stats_a",
                "estrategia_j",
                "estrategia_a",
            ]
        }
        d.update(
            {
                "config": dict(self.config.__dict__),
                "estrategia_j": serializar_estrategia(self.estrategia_j),
                "estrategia_a": serializar_estrategia(self.estrategia_a),
                "stats_j": dict(self.stats_j.__dict__),
                "stats_a": dict(self.stats_a.__dict__),
                "contexto_partida": dict(self.contexto_partida.__dict__),
            }
        )
        return d

    def _persistir(self) -> None:
        from api.routes._match_store import save_snapshot, set_runtime_cache

        save_snapshot(self.save_name, self.partida_id, self.to_snapshot())
        set_runtime_cache(self.partida_id, self)

    def serializar(
        self, event_type: str = "ponto", descricao: str = ""
    ) -> dict[str, Any]:
        if self.encerrado:
            pts = ["-", "-"]
        elif self._is_tiebreak():
            pts = [str(self.pontos[0]), str(self.pontos[1])]
        else:
            pts = list(pontuacao_texto(self.pontos[0], self.pontos[1]))
        payload = {
            "tipo": event_type,
            "descricao": descricao,
            "descricao_json": dict(
                getattr(self, "last_event_payload", {})
                or {
                    "kind": event_type,
                    "headline": descricao or "Ponto confirmado.",
                    "detail": descricao or "Ponto confirmado.",
                    "winner": None,
                    "pressure": "baixa",
                    "moment": "normal",
                    "mode": getattr(self, "modo", "manual"),
                    "surface": getattr(self.config, "superficie", ""),
                    "tags": [event_type],
                    "insights": [],
                }
            ),
            "sets": [int(self.sets[0]), int(self.sets[1])],
            "games": [int(self.games[0]), int(self.games[1])],
            "pontos": pts,
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
            "estrategia_j": serializar_estrategia(self.estrategia_j),
            "estrategia_a": serializar_estrategia(self.estrategia_a),
            "ajuste_tatico_j": self.ajuste_tatico_j,
            "ajuste_tatico_a": self.ajuste_tatico_a,
            "quimica_j": getattr(self, "quimica_j", {}),
            "quimica_a": getattr(self, "quimica_a", {}),
        }
        if self.encerrado and self.vencedor:
            payload["vencedor"] = self.vencedor
            payload["placar_final"] = self._placar_final_texto()
            if self.modalidade == "duplas" and getattr(self, "quimica_j", {}):
                from src.duplas import gerar_comentario_parceiro

                payload["comentario_parceiro"] = gerar_comentario_parceiro(
                    getattr(self, "quimica_j", {}).get("label", "Profissional"),
                    venceu=(self.vencedor == "jogador"),
                )
        return payload

    def aplicar_estrategia(self, valor: str | None) -> None:
        self.estrategia_j = normalizar_estrategia(valor, self.estrategia_j)
        self._persistir()

    def definir_pausa(self, pausado: bool) -> None:
        self.pausado = bool(pausado)
        self._persistir()

    def jogar_ponto(self) -> dict[str, Any]:
        if self.encerrado:
            return self.serializar(event_type="fim", descricao="Partida encerrada.")

        def _get_psico_com_ajuste(lado: str):
            base = (
                self.simulador._get_psico_jogador()
                if lado == "j"
                else self.simulador._get_psico_adversario()
            )
            aj = self.ajuste_tatico_j if lado == "j" else self.ajuste_tatico_a
            res = dict(base)
            if aj == "agressivo":
                res["agressividade"] = min(100, res.get("agressividade", 50) + 10)
                res["clutch"] = max(0, res.get("clutch", 50) - 5)
            elif aj == "seguro":
                res["clutch"] = min(100, res.get("clutch", 50) + 10)
                res["agressividade"] = max(0, res.get("agressividade", 50) - 10)
            return res

        pj_t, pa_t = _get_psico_com_ajuste("j"), _get_psico_com_ajuste("a")
        oj, oa = self.simulador._get_psico_jogador, self.simulador._get_psico_adversario
        self.simulador._get_psico_jogador, self.simulador._get_psico_adversario = (
            lambda: pj_t,
            lambda: pa_t,
        )
        try:
            ctx = self._contexto_ponto()
            if self.modo == "detalhado":
                vencedor, desc, si = self.simulador.simular_ponto_detalhado(
                    self.estrategia_j,
                    ctx,
                    tipo_saque=self._tipo_saque_do_sacador(),
                    contexto_partida=self.contexto_partida,
                    estrategia_adversario=self.estrategia_a,
                )
            elif self.modo == "estrategista":
                vencedor, desc, si = self.simulador.simular_ponto_estrategista(
                    self.estrategia_j,
                    ctx,
                    tipo_saque=self._tipo_saque_do_sacador(),
                    contexto_partida=self.contexto_partida,
                    estrategia_adversario=self.estrategia_a,
                )
            else:
                vencedor, si = self.simulador.simular_ponto_rapido(
                    self.estrategia_j,
                    contexto=ctx,
                    contexto_partida=self.contexto_partida,
                    estrategia_adversario=self.estrategia_a,
                )
                desc = None
            sd = si.to_dict() if hasattr(si, "to_dict") else dict(si)
            sd["sequencia_j"], sd["sequencia_a"] = (
                self.contexto_partida.sequencia_j,
                self.contexto_partida.sequencia_a,
            )
            self.last_point_snapshot = sd
            self._atualizar_pos_ponto(ctx, vencedor, sd)
            et, bm = self._atualizar_placar(vencedor)
            dp = self._descricao_evento_json(vencedor, sd, desc, event_type=et)
            msg = f"{resumo_textual_evento(dp)} {bm}".strip()
            self.last_event_payload = dp
            self.log.append(msg)
            self.total_pontos += 1
        finally:
            self.simulador._get_psico_jogador, self.simulador._get_psico_adversario = (
                oj,
                oa,
            )
        if self.encerrado:
            self._finalizar_torneio()
            return self.serializar(event_type="fim", descricao=msg)
        self._persistir()
        return self.serializar(event_type=et, descricao=msg)

    def simular_set(self) -> dict[str, Any]:
        si = tuple(self.sets)
        res = self.serializar(event_type="set", descricao="Set ja concluido.")
        while not self.encerrado and tuple(self.sets) == si:
            res = self.jogar_ponto()
        return res

    def simular_partida(self) -> dict[str, Any]:
        res = self.serializar(event_type="fim", descricao="Partida ja concluida.")
        while not self.encerrado:
            res = self.jogar_ponto()
        return res


def criar_match_runtime(
    save_name: str,
    jogador: Any,
    adversario: dict[str, Any],
    torneio_info: dict[str, Any],
    modo: str,
    modalidade: str = "simples",
) -> MatchRuntime:
    from api.routes._match_store import invalidate_other_snapshots

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
    from api.routes._match_store import (
        get_runtime_cache,
        load_snapshot,
        set_runtime_cache,
    )
    from src.dados import SAVES_DIR
    from pathlib import Path

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
