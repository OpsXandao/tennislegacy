RANK_BRACKETS = (
    (5, "top5"),
    (20, "top20"),
    (50, "top50"),
    (100, "top100"),
    (10**9, "resto"),
)

PARTICIPACAO_BASE = {
    "Grand Slam": {
        "home": {"top50": 0.99, "top100": 0.92, "resto": 0.75},
        "away": {"top50": 0.98, "top100": 0.90, "resto": 0.70},
    },
    "1000": {
        "home": {"top50": 0.90, "top100": 0.70, "resto": 0.50},
        "away": {"top50": 0.85, "top100": 0.65, "resto": 0.40},
    },
    "500": {
        "home": {
            "top5": 0.90,
            "top20": 0.80,
            "top50": 0.70,
            "top100": 0.60,
            "resto": 0.50,
        },
        "away": {"top20": 0.65, "top50": 0.55, "top100": 0.50, "resto": 0.35},
    },
    "250": {
        "home": {"top20": 0.35, "top50": 0.45, "top100": 0.60, "resto": 0.80},
        "away": {
            "top5": 0.05,
            "top20": 0.12,
            "top50": 0.25,
            "top100": 0.45,
            "resto": 0.60,
        },
    },
    "Challenger 125": {
        "home": {"top100": 0.30, "resto": 0.78},
        "away": {"top100": 0.22, "resto": 0.68},
    },
    "ITF 100": {
        "home": {"top100": 0.12, "resto": 0.82},
        "away": {"top100": 0.08, "resto": 0.72},
    },
    "ITF 25": {
        "home": {"top100": 0.05, "resto": 0.88},
        "away": {"top100": 0.03, "resto": 0.78},
    },
}


def _faixa_rank(rank: int) -> str:
    for limite, label in RANK_BRACKETS:
        if rank <= limite:
            return label
    return "resto"


def prob_participacao(
    tipo: str, rank: int, is_home: bool = False, superficie_match: bool = False
) -> float:
    base = 0.4
    # Normaliza o tipo (remove prefixo ATP/WTA) para usar a mesma tabela
    tipo_normalizado = str(tipo).replace("ATP ", "").replace("WTA ", "")

    tabela_tipo = PARTICIPACAO_BASE.get(tipo_normalizado, {})
    # Caso não encontre com o tipo normalizado, tenta o original (fallback para Grand Slam etc)
    if not tabela_tipo:
        tabela_tipo = PARTICIPACAO_BASE.get(tipo, {})

    contexto = "home" if is_home else "away"
    tabela_contexto = tabela_tipo.get(contexto, {})
    base = tabela_contexto.get(_faixa_rank(int(rank or 10**9)), base)
    if superficie_match:
        base = min(0.99, base * 1.15)
    return base


def _clamp_prob(valor: float) -> float:
    return max(0.01, min(0.99, float(valor)))


def _normalizar_tipo(tipo: str) -> str:
    return str(tipo or "").replace("ATP ", "").replace("WTA ", "")


def _normalizar_nome_torneio(nome: str) -> str:
    texto = str(nome or "").strip().lower()
    return " ".join(texto.split())


def _semanas_desde_evento(
    semana_atual: int | None,
    ano_atual: int | None,
    semana_evento: int | None,
    ano_evento: int | None,
) -> int | None:
    if semana_atual is None or semana_evento is None:
        return None

    semana_atual = int(semana_atual)
    semana_evento = int(semana_evento)

    if ano_atual is None or ano_evento is None:
        delta = semana_atual - semana_evento
        return delta if delta >= 0 else None

    return (int(ano_atual) - int(ano_evento)) * 52 + (semana_atual - semana_evento)


def _extrair_carga_recente(
    historico_torneios: list | None, semana_atual: int | None, ano_atual: int | None
) -> tuple[int, int]:
    if not isinstance(historico_torneios, list) or semana_atual is None:
        return 0, 0

    semanas_jogadas: set[tuple[int | None, int]] = set()
    for item in historico_torneios:
        if not isinstance(item, dict):
            continue
        semana_evento = item.get("semana")
        if semana_evento is None:
            continue
        ano_evento = item.get("ano", ano_atual)
        delta = _semanas_desde_evento(
            semana_atual, ano_atual, semana_evento, ano_evento
        )
        if delta is None or delta < 0:
            continue
        semanas_jogadas.add(
            (
                int(ano_evento) if ano_evento is not None else None,
                int(semana_evento),
            )
        )

    if not semanas_jogadas:
        return 0, 0

    def _jogou_ha(delta_desejado: int) -> bool:
        for ano_evento, semana_evento in semanas_jogadas:
            delta = _semanas_desde_evento(
                semana_atual, ano_atual, semana_evento, ano_evento
            )
            if delta == delta_desejado:
                return True
        return False

    consecutivas = 0
    while _jogou_ha(consecutivas):
        consecutivas += 1

    recentes = 0
    for ano_evento, semana_evento in semanas_jogadas:
        delta = _semanas_desde_evento(
            semana_atual, ano_atual, semana_evento, ano_evento
        )
        if delta is not None and 0 <= delta <= 5:
            recentes += 1

    return consecutivas, recentes


def _perfil_agenda_npc(rank: int, jogador: dict) -> str:
    attrs = (
        jogador.get("atributos", {})
        if isinstance(jogador.get("atributos"), dict)
        else {}
    )
    fisico = int((attrs.get("fisico", jogador.get("fisico", 50)) or 50))
    mental = int(jogador.get("moral", 70) or 70)

    if rank <= 12:
        return "elite_seletiva"
    if rank <= 35 and fisico <= 52:
        return "veterano_seletivo"
    if rank >= 90 and fisico >= 65 and mental >= 65:
        return "grinder"
    if rank <= 80 and fisico >= 60:
        return "regular"
    return "equilibrado"


def _multiplicador_perfil(
    perfil: str, tipo_normalizado: str, consecutivas: int, recentes: int
) -> float:
    if perfil == "elite_seletiva":
        if tipo_normalizado == "250":
            return 0.50
        if tipo_normalizado in {"Challenger 125", "ITF 100", "ITF 25"}:
            return 0.18
        if tipo_normalizado == "500":
            return 0.88 if consecutivas <= 1 else 0.76
        return 1.04
    if perfil == "veterano_seletivo":
        if tipo_normalizado == "250":
            return 0.78
        if tipo_normalizado in {"Challenger 125", "ITF 100", "ITF 25"}:
            return 0.42
        if consecutivas >= 2:
            return 0.82
        return 0.96
    if perfil == "grinder":
        if tipo_normalizado == "250":
            return 1.14
        if tipo_normalizado in {"Challenger 125", "ITF 100", "ITF 25"}:
            return 1.22
        if tipo_normalizado == "500":
            return 1.06
        return 0.95 if recentes >= 4 else 1.0
    if perfil == "regular":
        if consecutivas >= 3:
            return 0.90
        if tipo_normalizado in {"Challenger 125", "ITF 100", "ITF 25"}:
            return 1.08
        return 1.02 if tipo_normalizado in {"250", "500"} else 1.0
    return 1.0


def _afinidade_torneio_historico(
    jogador: dict, nome_torneio: str, semana_atual: int | None, ano_atual: int | None
) -> float:
    historico = jogador.get("historico_torneios", [])
    if not isinstance(historico, list):
        return 1.0

    nome_ref = _normalizar_nome_torneio(nome_torneio)
    if not nome_ref:
        return 1.0

    melhor_fase = -1
    jogou_ultimo_ano = False
    titulo_recente = False
    pesos_fase = {
        "qualy_1": 0,
        "qualy_2": 1,
        "r128": 2,
        "r96": 2,
        "r64": 3,
        "r32": 4,
        "r16": 5,
        "oitavas": 5,
        "quartas": 6,
        "semifinal": 7,
        "final": 8,
        "campeao": 9,
    }

    for item in historico:
        if not isinstance(item, dict):
            continue
        if _normalizar_nome_torneio(item.get("torneio", "")) != nome_ref:
            continue
        fase = str(item.get("fase_alcancada", "r128") or "r128").lower()
        melhor_fase = max(melhor_fase, pesos_fase.get(fase, 0))
        delta = _semanas_desde_evento(
            semana_atual,
            ano_atual,
            item.get("semana"),
            item.get("ano", ano_atual),
        )
        if delta is not None and 0 <= delta <= 52:
            jogou_ultimo_ano = True
        if fase == "campeao" and delta is not None and 0 <= delta <= 104:
            titulo_recente = True

    multiplicador = 1.0
    if melhor_fase >= 9:
        multiplicador *= 1.30
    elif melhor_fase >= 8:
        multiplicador *= 1.20
    elif melhor_fase >= 7:
        multiplicador *= 1.12
    elif melhor_fase >= 6:
        multiplicador *= 1.06

    if jogou_ultimo_ano:
        multiplicador *= 1.05
    if titulo_recente:
        multiplicador *= 1.08

    return multiplicador


def ajustar_prob_participacao_por_contexto(
    prob_base: float,
    jogador: dict | None = None,
    *,
    tipo: str = "",
    rank: int | None = None,
    nome_torneio: str = "",
    semana_atual: int | None = None,
    ano_atual: int | None = None,
) -> float:
    prob = _clamp_prob(prob_base)
    if not isinstance(jogador, dict):
        return prob

    energia = int(jogador.get("energia", 100) or 100)
    fadiga = int(jogador.get("fadiga", 0) or 0)
    moral = int(jogador.get("moral", 70) or 70)
    status_lesao = (
        jogador.get("status_lesao", {})
        if isinstance(jogador.get("status_lesao", {}), dict)
        else {}
    )
    status_doenca = (
        jogador.get("status_doenca", {})
        if isinstance(jogador.get("status_doenca", {}), dict)
        else {}
    )
    historico = jogador.get("historico_torneios", [])
    rank = int(rank or 10**9)
    tipo_normalizado = _normalizar_tipo(tipo)

    if status_lesao.get("lesionado"):
        return 0.01
    if status_doenca.get("doente"):
        prob *= 0.55

    nivel_lesao = str(status_lesao.get("nivel", "saudavel") or "saudavel").lower()
    if nivel_lesao == "limitado":
        prob *= 0.25
    elif nivel_lesao == "desconforto":
        prob *= 0.60

    if fadiga >= 85:
        prob *= 0.10
    elif fadiga >= 70:
        prob *= 0.32
    elif fadiga >= 55:
        prob *= 0.58
    elif fadiga <= 20:
        prob *= 1.04

    if energia <= 25:
        prob *= 0.15
    elif energia <= 40:
        prob *= 0.42
    elif energia <= 55:
        prob *= 0.75
    elif energia >= 85:
        prob *= 1.04

    consecutivas, recentes = _extrair_carga_recente(historico, semana_atual, ano_atual)
    if consecutivas >= 4:
        prob *= 0.25
    elif consecutivas == 3:
        prob *= 0.48
    elif consecutivas == 2:
        prob *= 0.72

    if recentes >= 5:
        prob *= 0.70
    elif recentes == 4:
        prob *= 0.84

    perfil = _perfil_agenda_npc(rank, jogador)
    prob *= _multiplicador_perfil(perfil, tipo_normalizado, consecutivas, recentes)
    prob *= _afinidade_torneio_historico(
        jogador,
        nome_torneio,
        semana_atual,
        ano_atual,
    )

    if moral <= 35:
        prob *= 0.92
    elif moral >= 80 and energia >= 75 and fadiga <= 30:
        prob *= 1.03

    return _clamp_prob(prob)
