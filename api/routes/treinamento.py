from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from api.session import obter_sessao_ativa, Session, refresh_session
from api.services import training_service

router = APIRouter(prefix="/api/treinamento", tags=["treinamento"])


class TrainingRequest(BaseModel):
    foco: str  # "tecnico", "fisico", "psicologico"


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
        "jogador_status": training_service.serializar_status_jogador(j),
    }


@router.get("/opcoes")
def obter_opcoes():
    return {
        "opcoes": [
            {
                "id": "tecnico",
                "nome": "Treino Técnico",
                "descricao": "Melhora golpes, saque e voleio.",
                "custo_energia": 15,
            },
            {
                "id": "fisico",
                "nome": "Preparação Física",
                "descricao": "Foca em velocidade, força e resistência.",
                "custo_energia": 15,
            },
            {
                "id": "psicologico",
                "nome": "Treino Mental",
                "descricao": "Melhora concentração e determinação.",
                "custo_energia": 15,
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

    j, melhorias, resultado = training_service.executar_treino(session, req.foco)
    refresh_session(session.nome_save_ativo)

    return {
        "ok": True,
        "melhorias": melhorias,
        "semana": resultado.get("semana"),
        "ano": resultado.get("ano"),
        "eventos": resultado.get("eventos", []),
        "resumo_mundial": resultado.get("resumo_mundial", {"campeoes": []}),
        "jogador_status": training_service.serializar_status_jogador(j),
    }
