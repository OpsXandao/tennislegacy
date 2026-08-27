import random
from dataclasses import dataclass
from typing import Optional

from src.utils.superficie_utils import normalizar_superficie


@dataclass
class ConfigPartida:
    superficie: str = "dura"
    melhor_de: int = 3
    tiebreak_decisivo_pontos: int = 7
    nome_torneio: Optional[str] = None
    tipo_torneio: Optional[str] = None
    clima: str = "ameno"
    vento: int = 0
    umidade: int = 50
    altitude_m: int = 0
    indoor: bool = False
    modalidade: str = "simples"  # "simples" | "duplas" — afeta bônus de carta DS


def _nome_entidade(entidade, padrao: str = "Jogador") -> str:
    if isinstance(entidade, dict):
        return str(entidade.get("nome", padrao))
    return str(getattr(entidade, "nome", padrao))


def _gerar_condicoes_partida(info_torneio: dict) -> dict:
    local = str(info_torneio.get("local", "global")).strip().lower()
    superficie = normalizar_superficie(info_torneio.get("quadra", "dura"))
    tipo = str(info_torneio.get("tipo", "")).strip().lower()
    indoor = "indoor" in str(info_torneio.get("quadra", "")).lower()

    seed = f"{info_torneio.get('nome', '')}-{local}-{superficie}-{tipo}"
    rng = random.Random(seed)

    clima = "ameno"
    if (
        "melbourne" in local
        or "australia" in local
        or "doha" in local
        or "dubai" in local
    ):
        clima = rng.choices(["quente", "ameno"], weights=[0.75, 0.25], k=1)[0]
    elif "londres" in local or "paris" in local or "rotterdam" in local:
        clima = rng.choices(
            ["frio", "ameno", "chuvoso"], weights=[0.45, 0.4, 0.15], k=1
        )[0]
    elif "rio" in local or "acapulco" in local or "buenos aires" in local:
        clima = rng.choices(
            ["quente", "ameno", "chuvoso"], weights=[0.55, 0.3, 0.15], k=1
        )[0]

    if indoor:
        vento = 0
        umidade = rng.randint(35, 55)
    else:
        vento = rng.randint(5, 32)
        umidade = rng.randint(45, 80)

    altitude = 0
    if "acapulco" in local:
        altitude = 30
    elif "madrid" in local:
        altitude = 657
    elif "quito" in local:
        altitude = 2850
    elif "bogota" in local:
        altitude = 2640

    if superficie == "saibro":
        umidade = min(90, umidade + 8)
    if tipo == "grand slam":
        vento = max(0, vento - 2)

    return {
        "clima": info_torneio.get("clima", clima),
        "vento": int(info_torneio.get("vento", vento)),
        "umidade": int(info_torneio.get("umidade", umidade)),
        "altitude_m": int(info_torneio.get("altitude_m", altitude)),
        "indoor": bool(info_torneio.get("indoor", indoor)),
    }


def criar_config_partida(info_torneio: Optional[dict]) -> ConfigPartida:
    if not info_torneio:
        return ConfigPartida()
    tipo = info_torneio.get("tipo", "")
    superficie = info_torneio.get("quadra", "dura")
    melhor_de = 5 if tipo.strip().lower() == "grand slam" else 3
    tiebreak_decisivo = 10 if melhor_de == 5 else 7
    condicoes = _gerar_condicoes_partida(info_torneio)
    return ConfigPartida(
        superficie=superficie,
        melhor_de=melhor_de,
        tiebreak_decisivo_pontos=tiebreak_decisivo,
        nome_torneio=info_torneio.get("nome"),
        tipo_torneio=tipo,
        clima=condicoes["clima"],
        vento=condicoes["vento"],
        umidade=condicoes["umidade"],
        altitude_m=condicoes["altitude_m"],
        indoor=condicoes["indoor"],
    )
