from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class RankingEntry(BaseModel):
    nome: str
    nacionalidade: str
    pontos: int = 0
    pontos_duplas: int = 0
    pontos_ranking: int = 0
    pontos_ranking_duplas: int = 0
    pontos_ytd: int = 0
    overall: int = 0
    energia: int = 100
    fadiga: int = 0
    moral: int = 70
    is_lean: bool = True
    is_bot: bool = False
    e_ficticio: bool = False
    atributos: Dict[str, int] = Field(default_factory=dict)
    atributos_psicologicos: Dict[str, int] = Field(default_factory=dict)
    historico_torneios: List[dict] = Field(default_factory=list)
    historico_partidas: List[dict] = Field(default_factory=list)
    pontos_detalhados: List[dict] = Field(default_factory=list)
    pontos_detalhados_duplas: List[dict] = Field(default_factory=list)
    status_lesao: Dict = Field(default_factory=dict)
    status_doenca: Dict = Field(default_factory=dict)
    protected_ranking: Optional[int] = None
    protected_ranking_semanas: int = 0

    class Config:
        extra = "allow"
