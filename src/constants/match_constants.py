from enum import Enum
from dataclasses import dataclass, asdict, field
from typing import Any


class ModoSimulacao(Enum):
    RAPIDO = "rapido"
    DETALHADO = "detalhado"
    ESTRATEGISTA = "estrategista"


class TipoSaque(Enum):
    AGRESSIVO = "agressivo"
    SEGURO = "seguro"
    VARIADO = "variado"


class EstrategiaAtaque(Enum):
    REDE = "rede"
    FUNDO = "fundo"
    VARIADO = "variado"


class EstrategiaDefesa(Enum):
    CONTRA_ATAQUE = "contra_ataque"
    CONSISTENCIA = "consistencia"
    NEUTRALIZAR = "neutralizar"


class EstrategiaSaque(Enum):
    SEGURO = "seguro"
    FORCAR = "forcar"


class IntencaoPonto(Enum):
    DEFENSIVO = "defensivo"
    PACIENTE = "paciente"
    ARRISCAR = "arriscar"


@dataclass
class MatchPointStats:
    """
    Snapshot tipado do resultado estatístico de um ponto.
    """

    sacador: str
    primeiro_saque_in: bool = False
    ace: bool = False
    dupla_falta: bool = False
    winner: bool = False
    erro_nao_forcado: bool = False
    intensidade: str = "medio"
    insights: list[str] = field(default_factory=list)

    # Visualização (coordenadas 0-100)
    # X: 0 (esquerda) a 100 (direita)
    # Y: 0 (fundo sacador) a 100 (fundo receptor)
    origem: tuple[int, int] = (50, 0)
    destino: tuple[int, int] = (50, 80)

    @classmethod
    def novo(cls, sacador: str) -> "MatchPointStats":
        return cls(sacador=sacador)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __contains__(self, key: str) -> bool:
        return hasattr(self, key)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
