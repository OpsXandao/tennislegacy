from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from api.session import obter_sessao_ativa, Session, refresh_session
from api.services import training_service

router = APIRouter(prefix="/api/treinamento", tags=["treinamento"])


class TrainingRequest(BaseModel):
    foco: str  # "tecnico", "fisico", "psicologico"
    atributo: str | None = None


@router.post("/descanso")
def descansar(session: Session = Depends(obter_sessao_ativa)):
    j, resultado = training_service.executar_descanso(session)
    refresh_session(session.nome_save_ativo)
    return {
        "ok": True,
        "energia": j.energia,
        "fadiga": j.fadiga,
        "mensagem": "Semana de descanso. Energia recuperada.",
        "semana": resultado.get("semana"),
        "ano": resultado.get("ano"),
        "eventos": resultado.get("eventos", []),
        "resumo_mundial": resultado.get("resumo_mundial", {"campeoes": []}),
    }


@router.get("/opcoes")
def obter_opcoes(session: Session = Depends(obter_sessao_ativa)):
    j = session.jogador
    fisicos_chave = {"velocidade", "aceleracao", "resistencia", "forca", "agilidade"}
    attrs_tecnicos = [a for a in j.atributos if a not in fisicos_chave and a != "duplas"]
    attrs_fisicos = list(fisicos_chave)
    attrs_psico = list(j.atributos_psicologicos.keys())

    return {
        "opcoes": [
            {
                "id": "tecnico",
                "nome": "Treino Técnico",
                "descricao": "Foque em um golpe específico ou treine fundamentos gerais.",
                "custo_energia": 15,
                "atributos_foco": attrs_tecnicos,
            },
            {
                "id": "fisico",
                "nome": "Preparação Física",
                "descricao": "Foque em resistência, velocidade, força ou agilidade.",
                "custo_energia": 15,
                "atributos_foco": attrs_fisicos,
            },
            {
                "id": "psicologico",
                "nome": "Treino Mental",
                "descricao": "Fortaleça sua mente ou foque em um aspecto psicológico.",
                "custo_energia": 15,
                "atributos_foco": attrs_psico,
            },
        ]
    }


@router.post("/executar")
def executar_treino(
    req: TrainingRequest, session: Session = Depends(obter_sessao_ativa)
):
    j = session.jogador

    if j.energia < 30:
        raise HTTPException(
            status_code=400, detail="Energia insuficiente para treinar (mínimo 30)."
        )

    if req.foco != "psicologico" and getattr(j, "status_lesao", {}).get("lesionado"):
        raise HTTPException(
            status_code=400,
            detail="Você está lesionado e não pode realizar treinos físicos/técnicos.",
        )

    nivel_antes = getattr(j, "nivel", 1)
    j, melhorias, resultado = training_service.executar_treino(
        session, req.foco, atributo_foco=req.atributo
    )
    refresh_session(session.nome_save_ativo)

    nivel_novo = getattr(j, "nivel", 1)
    subiu_nivel = nivel_novo > nivel_antes

    return {
        "ok": True,
        "melhorias": melhorias,
        "semana": resultado.get("semana"),
        "ano": resultado.get("ano"),
        "eventos": resultado.get("eventos", []),
        "resumo_mundial": resultado.get("resumo_mundial", {"campeoes": []}),
        "jogador_status": training_service.serializar_status_jogador(j),
        "level_up": subiu_nivel,
        "nivel_novo": nivel_novo if subiu_nivel else None,
        "pontos_skill_ganhos": (nivel_novo - nivel_antes) * 5 if subiu_nivel else 0,
    }
