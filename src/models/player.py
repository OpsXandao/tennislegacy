from typing import Optional, List, Dict

try:
    from pydantic import BaseModel, Field
except Exception:
    class BaseModel:
        def __init__(self, **kwargs):
            for chave, valor in kwargs.items():
                setattr(self, chave, valor)

    def Field(default=None, default_factory=None, **_kwargs):
        if default_factory is not None:
            return default_factory()
        return default

class PlayerModel(BaseModel):
    nome: str
    idade: int
    nacionalidade: str
    save_name: str = "default"
    genero: str = "masculino"
    altura: int = 180
    peso: int = 75
    mao_dominante: str = "Destro"
    reves: str = "Duas mãos"
    estilo_jogo: str = "All-court"
    
    semana: int = 1
    energia: int = 100
    ritmo_jogo: int = 50
    moral: int = 70
    dinheiro: int = 500
    fadiga: int = 0
    
    status_lesao: Dict = Field(default_factory=dict)
    status_doenca: Dict = Field(default_factory=dict)
    
    modalidade_atual: str = "simples"
    parceiro_duplas: Optional[Dict] = None
    vinculos_dupla: Dict[str, Dict] = Field(default_factory=dict)
    
    empresario: Optional[Dict] = None
    equipe: List[Dict] = Field(default_factory=list)
    patrocinios: List[Dict] = Field(default_factory=list)
    seguidores: int = 0
    avisos_patrocinio: Dict[str, bool] = Field(default_factory=dict)
    reputacao_imprensa: int = 50
    caixa_email: List[Dict] = Field(default_factory=list)
    
    nivel: int = 1
    xp: int = 0
    xp_para_proximo_nivel: int = 100
    pontos_de_skill: int = 0
    pico_carreira: int = 28
    
    historico_partidas: List[Dict] = Field(default_factory=list)
    historico_torneios: List[Dict] = Field(default_factory=list)
    historico_ranking: List[Dict] = Field(default_factory=list)
    rivalidades: Dict[str, Dict] = Field(default_factory=dict)
    pontos_ytd: int = 0
    transacoes: List[Dict] = Field(default_factory=list)
    snapshots_carreira: List[Dict] = Field(default_factory=list)
    
    protected_ranking: Optional[int] = None
    protected_ranking_semanas: int = 0
    
    atributos: Dict[str, int] = Field(default_factory=dict)
    atributos_psicologicos: Dict[str, int] = Field(default_factory=dict)

    class Config:
        extra = "allow"
