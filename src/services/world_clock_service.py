from __future__ import annotations

from typing import Any

from src.dados import SAVES_DIR, carregar_json, validar_nome_save
from src.repositories.season_repository import load_season
from src.services.tournament_state_service import carregar_estado
from src.utils.json_utils import salvar_json_seguro
from src.jogador import normalizar_nome

SLOTS_DIA = ["11:00", "13:00", "15:00", "17:00", "19:00", "21:00"]


def get_caminho_agenda(nome_save: str) -> str:
    nome_save = validar_nome_save(nome_save)
    return f"{SAVES_DIR}/{nome_save}/world_schedule.json"


def _agenda_vazia() -> dict[str, Any]:
    return {"clock": {"ano": 2026, "semana": 1, "dia": 1, "hora": "09:00"}, "events": []}


def carregar_agenda(nome_save: str) -> dict[str, Any]:
    agenda = carregar_json(get_caminho_agenda(nome_save), padrao=None)
    if not isinstance(agenda, dict):
        return _agenda_vazia()
    if not isinstance(agenda.get("events"), list):
        agenda["events"] = []
    if not isinstance(agenda.get("clock"), dict):
        agenda["clock"] = _agenda_vazia()["clock"]
    return agenda


def salvar_agenda(nome_save: str, agenda: dict[str, Any]) -> None:
    salvar_json_seguro(get_caminho_agenda(nome_save), agenda)


def _nome_entidade(entidade: Any) -> str:
    if isinstance(entidade, dict):
        return str(entidade.get("nome") or entidade.get("name") or "").strip()
    return str(entidade or "").strip()


def _nomes_confronto(confronto: Any) -> tuple[str, str] | None:
    if not isinstance(confronto, (list, tuple)) or len(confronto) < 2:
        return None
    nome_a = _nome_entidade(confronto[0])
    nome_b = _nome_entidade(confronto[1])
    if not nome_a or not nome_b:
        return None
    return nome_a, nome_b


def _fase_ordem(fase: str) -> int:
    ordem = {
        "qualy_1": 0,
        "qualy_2": 1,
        "qualy_r1": 0,
        "qualy_r2": 1,
        "qualy_r3": 2,
        "r128": 3,
        "r96": 4,
        "r64": 5,
        "r32": 6,
        "r16": 7,
        "oitavas": 7,
        "quartas": 8,
        "semifinal": 9,
        "final": 10,
    }
    return ordem.get(str(fase).lower(), 99)



def _tipo_torneio(estado_torneio: dict[str, Any]) -> str:
    td = estado_torneio.get("tournament_data")
    if not isinstance(td, dict):
        td = estado_torneio.get("estado", {}).get("tournament_data", {}) if isinstance(estado_torneio.get("estado"), dict) else {}
    return str(td.get("tipo") or estado_torneio.get("tipo") or "ATP 250")


def _superficie_torneio(estado_torneio: dict[str, Any]) -> str:
    td = estado_torneio.get("tournament_data")
    if not isinstance(td, dict):
        td = estado_torneio.get("estado", {}).get("tournament_data", {}) if isinstance(estado_torneio.get("estado"), dict) else {}
    return str(td.get("quadra") or estado_torneio.get("superficie") or "dura")


def _melhor_de_sets(tipo: str, genero: str, fase: str) -> int:
    if genero == "feminino":
        return 3
    if tipo == "Grand Slam" and not str(fase).lower().startswith("qualy"):
        return 5
    return 3


def _dia_base_fase(fase: str, tipo: str) -> int:
    fase_norm = str(fase or "").lower()
    if fase_norm.startswith("qualy"):
        return 0 + _fase_ordem(fase_norm)
    if tipo == "Grand Slam":
        mapa = {"r128": 3, "r64": 5, "r32": 7, "r16": 9, "quartas": 11, "semifinal": 13, "final": 15}
    elif "1000" in tipo:
        mapa = {"r96": 2, "r64": 3, "r32": 5, "r16": 6, "quartas": 7, "semifinal": 8, "final": 9}
    else:
        mapa = {"r48": 2, "r32": 2, "pre_oitavas": 2, "oitavas": 3, "r16": 3, "quartas": 4, "semifinal": 5, "final": 6}
    return mapa.get(fase_norm, 1 + _fase_ordem(fase_norm))


def _quadra_evento(idx: int, partida_jogador: bool, fase: str) -> str:
    fase_norm = str(fase or "").lower()
    if partida_jogador or fase_norm in {"semifinal", "final"}:
        return "Central"
    quadras = ["Quadra 1", "Quadra 2", "Quadra 3", "Quadra 4"]
    return quadras[idx % len(quadras)]


def _risco_atraso_clima(superficie: str, dia: int, indoor: bool = False) -> float:
    if indoor:
        return 0.0
    superficie_norm = str(superficie or "").lower()
    base = 0.06
    if "grama" in superficie_norm or "grass" in superficie_norm:
        base += 0.08
    elif "saibro" in superficie_norm or "clay" in superficie_norm:
        base += 0.04
    if dia in {0, 1, 2}:
        base += 0.02
    return round(min(0.22, base), 2)


def _ordenar_evento(evento: dict[str, Any]) -> tuple:
    return (
        int(evento.get("ano", 0) or 0),
        int(evento.get("semana", 0) or 0),
        int(evento.get("dia", 0) or 0),
        str(evento.get("hora", "")),
        int(evento.get("prioridade", 99) or 99),
    )


def gerar_ordem_de_jogo(
    estado_torneio: dict[str, Any], temporada: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    if not isinstance(estado_torneio, dict):
        return []

    fase = str(estado_torneio.get("fase_atual") or "")
    if not fase or fase == "finalizado":
        return []

    estado = estado_torneio.get("estado", {}) if isinstance(estado_torneio.get("estado"), dict) else estado_torneio
    rodadas = estado.get("rodadas", {}) if isinstance(estado.get("rodadas"), dict) else {}
    confrontos = rodadas.get(fase, [])
    if not isinstance(confrontos, list):
        return []

    jogador_nome = str(estado.get("jogador") or estado_torneio.get("jogador") or "")
    jogador_norm = normalizar_nome(jogador_nome) if jogador_nome else ""
    torneio_nome = str(estado_torneio.get("nome") or estado_torneio.get("torneio") or estado.get("torneio") or "Torneio")
    semana = int((temporada or {}).get("semana", estado_torneio.get("semana", estado.get("semana", 1))) or 1)
    ano = int((temporada or {}).get("ano", estado_torneio.get("ano", 2026)) or 2026)
    tipo = _tipo_torneio(estado_torneio)
    genero = str(estado_torneio.get("genero") or estado.get("genero") or "masculino")
    superficie = _superficie_torneio(estado_torneio)
    td_estado = estado.get("tournament_data") if isinstance(estado.get("tournament_data"), dict) else {}
    indoor = bool(td_estado.get("indoor", False))
    dia_base = _dia_base_fase(fase, tipo)
    melhor_de = _melhor_de_sets(tipo, genero, fase)

    eventos: list[dict[str, Any]] = []
    for idx, confronto in enumerate(confrontos):
        nomes = _nomes_confronto(confronto)
        if not nomes:
            continue
        nome_a, nome_b = nomes
        partida_jogador = jogador_norm in {normalizar_nome(nome_a), normalizar_nome(nome_b)}
        slot = SLOTS_DIA[idx % len(SLOTS_DIA)]
        dia = dia_base + (idx // len(SLOTS_DIA))
        categoria = "matchday" if partida_jogador else "world_sim"
        eventos.append(
            {
                "id": f"{torneio_nome}:{fase}:{idx + 1}",
                "tipo": "player_match" if partida_jogador else "npc_match",
                "categoria": categoria,
                "ano": ano,
                "semana": semana,
                "dia": dia,
                "hora": slot,
                "torneio": torneio_nome,
                "tipo_torneio": tipo,
                "fase": fase,
                "jogador1": nome_a,
                "jogador2": nome_b,
                "quadra": _quadra_evento(idx, partida_jogador, fase),
                "superficie": superficie,
                "melhor_de": melhor_de,
                "risco_atraso_clima": _risco_atraso_clima(superficie, dia, indoor=indoor),
                "janela_recuperacao_horas": 20 if idx >= len(SLOTS_DIA) else 36,
                "prioridade": 0 if partida_jogador else 5,
                "status": "scheduled",
                "stop_for_player": partida_jogador,
                "presentation": "ea_matchday" if partida_jogador else "fm_result_tick",
            }
        )

    return sorted(eventos, key=_ordenar_evento)

def sincronizar_agenda_torneio(
    nome_save: str,
    estado_torneio: dict[str, Any] | None,
    temporada: dict[str, Any] | None = None,
) -> dict[str, Any]:
    agenda = carregar_agenda(nome_save)
    if not isinstance(estado_torneio, dict):
        return agenda

    eventos_novos = gerar_ordem_de_jogo(estado_torneio, temporada=temporada)
    torneio_nome = str(estado_torneio.get("nome") or estado_torneio.get("torneio") or "Torneio")
    agenda["events"] = [
        evento
        for evento in agenda.get("events", [])
        if evento.get("torneio") != torneio_nome or evento.get("status") != "scheduled"
    ] + eventos_novos

    if temporada:
        agenda["clock"].update(
            {
                "ano": int(temporada.get("ano", agenda["clock"].get("ano", 2026)) or 2026),
                "semana": int(temporada.get("semana", agenda["clock"].get("semana", 1)) or 1),
            }
        )
    salvar_agenda(nome_save, agenda)
    return agenda


def proximo_evento_jogavel(agenda: dict[str, Any]) -> dict[str, Any] | None:
    eventos = [
        evento
        for evento in agenda.get("events", [])
        if evento.get("status") == "scheduled" and evento.get("stop_for_player")
    ]
    if not eventos:
        return None
    return sorted(eventos, key=_ordenar_evento)[0]


def obter_agenda_torneio(nome_save: str, genero: str = "masculino") -> dict[str, Any]:
    temporada = load_season(nome_save) or {"semana": 1, "ano": 2026}
    estado = carregar_estado(nome_save, genero=genero)
    agenda = sincronizar_agenda_torneio(nome_save, estado, temporada=temporada)
    return {
        "clock": agenda["clock"],
        "events": agenda.get("events", []),
        "proximo_jogavel": proximo_evento_jogavel(agenda),
    }


def avancar_ate_proximo_momento(nome_save: str) -> dict[str, Any]:
    agenda = carregar_agenda(nome_save)
    proximo = proximo_evento_jogavel(agenda)
    if not proximo:
        return {"ok": False, "mensagem": "Nenhum momento jogavel agendado.", "clock": agenda["clock"]}
    agenda["clock"].update(
        {"ano": proximo["ano"], "semana": proximo["semana"], "dia": proximo["dia"], "hora": proximo["hora"]}
    )
    salvar_agenda(nome_save, agenda)
    return {"ok": True, "clock": agenda["clock"], "evento": proximo}
