import logging
import os
import re
import shutil
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator

from api.logging_utils import log_event, log_exception
from api.session import (
    obter_nome_save_opcional,
    obter_sessao_ativa,
    Session,
    clear_sessao,
)
from src.dados import (
    listar_saves,
    carregar_temporada,
    carregar_nacionalidades,
    SAVES_DIR,
)
from src.jogador import (
    Jogador,
    carregar_jogador,
    _inicializar_arquivos_save,
    criar_jogador_alexandre_paiva,
)
from src.save import salvar_jogo
from src.ranking import SistemaRanking
from src.dados import get_caminho_ranking_save
from src.constantes import (
    ARCHETYPES,
    MENTAL_ARCHETYPES,
)
from src.services.tournament_service import get_tournament_state

router = APIRouter(prefix="/api")


class CreateSaveRequest(BaseModel):
    nome: str = Field(..., description="Nome único do save/pasta")
    nome_jogador: str = Field(..., description="Nome de exibição do jogador")
    nacionalidade: str = Field(
        ..., description="Nacionalidade formatada como [CC] Nome"
    )
    tour: str = Field(..., description="'atp' ou 'wta'")
    idade: int = Field(default=18, ge=14, le=50)
    archetype_id: str = Field(default="3")
    mental_id: str = Field(default="5")

    @validator("nome")
    def nome_valido(cls, v):
        if not re.match(r"^[a-zA-Z0-9_-]{1,32}$", v):
            raise ValueError(
                "Nome deve conter apenas letras, números, _ e - (máx 32 chars)"
            )
        return v


class LoadSaveRequest(BaseModel):
    nome: str

    @validator("nome")
    def nome_valido(cls, v):
        if not re.match(r"^[a-zA-Z0-9_-]{1,32}$", v):
            raise ValueError(
                "Nome deve conter apenas letras, números, _ e - (máx 32 chars)"
            )
        return v


def _serializar_jogador(session: Session, jogador_inst: Jogador) -> dict:
    rk = (
        session.ranking_atp
        if jogador_inst.genero == "masculino"
        else session.ranking_wta
    )
    ranking = 0
    if rk:
        ranking = rk.obter_posicao(jogador_inst.nome) or 0

    return {
        "nome": jogador_inst.nome,
        "nacionalidade": jogador_inst.nacionalidade,
        "tour": "atp" if jogador_inst.genero == "masculino" else "wta",
        "ranking": ranking,
        "pontos": jogador_inst.pontos_ytd,
        "overall": jogador_inst.calcular_overall(),
        "energia": jogador_inst.energia,
        "fadiga": jogador_inst.fadiga,
        "status_lesao": (
            jogador_inst.status_lesao["nivel"]
            if jogador_inst.status_lesao["lesionado"]
            else None
        ),
        "dinheiro": jogador_inst.dinheiro,
        "seguidores": jogador_inst.seguidores,
        "nivel": jogador_inst.nivel,
        "xp": jogador_inst.xp,
        "xp_para_proximo_nivel": getattr(jogador_inst, "xp_para_proximo_nivel", 100),
        "atributos": jogador_inst.atributos,
    }


@router.get("/save/arquetipos")
def get_arquetipos():
    return {"tecnicos": ARCHETYPES, "mentais": MENTAL_ARCHETYPES}


@router.get("/save/nacionalidades")
def get_nacionalidades():
    data = carregar_nacionalidades()
    nacionalidades = []
    for grupo in data.values():
        if isinstance(grupo, list):
            nacionalidades.extend(str(item) for item in grupo)
    unicos = list(dict.fromkeys(nacionalidades))
    unicos.sort(key=lambda item: item.split("] ", 1)[-1].casefold())
    return {"nacionalidades": unicos}


@router.get("/save/{nome}/preview")
def get_save_preview(nome: str):
    if nome not in listar_saves():
        raise HTTPException(status_code=404, detail="Save não encontrado.")

    jogador = carregar_jogador(nome)
    if not jogador:
        raise HTTPException(status_code=404, detail="Dados do jogador não encontrados.")

    temporada = carregar_temporada(nome) or {"semana": 1, "ano": 2026}

    rk_path = get_caminho_ranking_save(nome, genero=jogador.genero)
    ranking_pos = 0
    if os.path.exists(rk_path):
        rk = SistemaRanking(rk_path)
        ranking_pos = rk.obter_posicao(jogador.nome) or 0

    return {
        "nome": nome,
        "jogador_nome": jogador.nome,
        "tour": "atp" if jogador.genero == "masculino" else "wta",
        "semana": temporada.get("semana", 1),
        "ano": temporada.get("ano", 2026),
        "ranking_estimado": ranking_pos,
    }


@router.get("/saves")
def get_saves():
    return {"saves": listar_saves()}


@router.post("/save/criar")
def criar_save(req: CreateSaveRequest):
    existing_saves = [s.lower() for s in listar_saves()]
    if req.nome.lower() in existing_saves:
        raise HTTPException(
            status_code=400, detail=f"O nome da carreira '{req.nome}' já está em uso."
        )

    genero = "masculino" if req.tour.lower() == "atp" else "feminino"

    archetype_data = ARCHETYPES.get(req.archetype_id) or ARCHETYPES.get("3")
    mental_data = MENTAL_ARCHETYPES.get(req.mental_id) or MENTAL_ARCHETYPES.get("5")

    archetype_attrs = archetype_data["atributos"]
    mental_attrs = mental_data["atributos"]

    jogador_inst = Jogador(
        nome=req.nome_jogador,
        idade=req.idade,
        nacionalidade=req.nacionalidade,
        save_name=req.nome,
        genero=genero,
    )
    jogador_inst.atributos = archetype_attrs.copy()
    jogador_inst.atributos_psicologicos = mental_attrs.copy()

    _inicializar_arquivos_save(req.nome, genero=genero)
    salvar_jogo(req.nome, jogador_inst)

    ranking_path = get_caminho_ranking_save(req.nome, genero=genero)
    if os.path.exists(ranking_path):
        rk = SistemaRanking(ranking_path)
        rk.adicionar_jogador_novo(vars(jogador_inst))

    return {"ok": True, "save": req.nome}


@router.post("/save/criar-alexandre")
def criar_save_alexandre(req: LoadSaveRequest):
    existing_saves = [s.lower() for s in listar_saves()]
    if req.nome.lower() in existing_saves:
        raise HTTPException(
            status_code=400, detail=f"O nome da carreira '{req.nome}' já está em uso."
        )

    criar_jogador_alexandre_paiva(req.nome)
    return {"ok": True, "save": req.nome}


@router.delete("/save/{nome}")
def deletar_save(nome: str):
    if nome not in listar_saves():
        raise HTTPException(status_code=404, detail="Save não encontrado.")

    caminho = os.path.join(SAVES_DIR, nome)
    try:
        shutil.rmtree(caminho)
        clear_sessao(nome_save=nome)
        log_event(logging.INFO, "save_deletado", save=nome)
        return {"ok": True}
    except Exception as exc:
        log_exception("erro_ao_deletar_save", exc, save=nome, caminho=caminho)
        raise HTTPException(status_code=500, detail="Falha ao deletar o save.")


@router.post("/save/carregar")
def carregar_save(req: LoadSaveRequest):
    saves_disponiveis = listar_saves()
    if req.nome not in saves_disponiveis:
        raise HTTPException(status_code=404, detail=f"Save '{req.nome}' não encontrado.")

    jogador_inst = carregar_jogador(req.nome)
    if not jogador_inst:
        raise HTTPException(status_code=500, detail="Erro ao carregar jogador.")

    # Inicia sessão no pool e força rebuild dos rankings
    session = Session(req.nome)
    session.rebuild_rankings()

    log_event(logging.INFO, "save_carregado", save=req.nome, jogador=jogador_inst.nome)

    return {
        "ok": True,
        "jogador": _serializar_jogador(session, jogador_inst),
        "semana": jogador_inst.semana,
        "ano": getattr(jogador_inst, "ano", 2026),
        "torneio": get_tournament_state(req.nome),
    }


@router.post("/save/salvar")
def salvar_save_atual(session: Session = Depends(obter_sessao_ativa)):
    if not session.nome_save_ativo:
        raise HTTPException(status_code=400, detail="Nenhum save ativo.")

    jogador = session.jogador
    if not jogador:
        raise HTTPException(status_code=404, detail="Dados do jogador não encontrados.")

    salvar_jogo(session.nome_save_ativo, jogador)
    return {"ok": True, "save": session.nome_save_ativo}


@router.get("/sessao")
def get_sessao(save_ativo: str | None = Depends(obter_nome_save_opcional)):
    return {"save_ativo": save_ativo}
