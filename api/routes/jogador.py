from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from api.routes._carta import carta_jogador
from api.session import obter_sessao_ativa, Session
from src.player_identity import derive_player_identity
from src.player_ratings import ajustar_atributo_duplas, calcular_overall_contextual
from src.constants.staff_constants import (
    EMPRESARIOS_DISPONIVEIS,
    PROFISSIONAIS_DISPONIVEIS,
)
from src.constants.torneio_constants import RANKING_POSICAO_FALLBACK, START_YEAR

router = APIRouter(prefix="/api/jogador")


class JogadorResponse(BaseModel):
    nome: str
    nacionalidade: str
    idade: int
    altura: int
    peso: int
    mao_dominante: str
    reves: str
    estilo_jogo: str
    pico_carreira: int
    tour: str
    ranking: int
    pontos: int
    overall: int
    resumo_fifa: dict[str, int]
    energia: int
    fadiga: int
    status_lesao: str | None
    dinheiro: int
    seguidores: int
    nivel: int
    xp: int
    xp_para_proximo_nivel: int
    atributos: dict[str, int]
    atributos_psicologicos: dict[str, int]
    carta: dict | None = None
    identity: dict | None = None
    historico_partidas: list[dict] | None = None
    historico_torneios: list[dict] | None = None
    trofeus: list[dict] | None = None


@router.get("", response_model=JogadorResponse)
def get_jogador(session: Session = Depends(obter_sessao_ativa)) -> JogadorResponse:
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessão não iniciada.")

    j = session.jogador
    # Encontrar posição no ranking
    rk = session.ranking_atp if j.genero == "masculino" else session.ranking_wta
    posicao = 0
    if rk:
        posicao = rk.obter_posicao(j.nome) or 0
    jogador_ranking = rk.buscar_jogador_por_nome(j.nome) if rk else {}

    jogador_payload = j.to_dict()
    ajustar_atributo_duplas(jogador_payload)
    attrs = jogador_payload["atributos"]
    resumo_fifa = {
        "MOV": int(attrs.get("velocidade", 60)),
        "SAQ": int(attrs.get("vel_saque", 60)),
        "FOR": int(attrs.get("forehand", 60)),
        "BAC": int(attrs.get("backhand", 60)),
        "FIS": int(attrs.get("resistencia", 60)),
        "TEC": int(
            (
                attrs.get("voleio", 60)
                + attrs.get("topspin", 60)
                + attrs.get("slice", 60)
                + attrs.get("lob", 60)
                + attrs.get("winner", 60)
            )
            / 5
        ),
    }
    overall = calcular_overall_contextual(
        {
            **jogador_payload,
            "pontos_ranking": (jogador_ranking or {}).get(
                "pontos_ranking", (jogador_ranking or {}).get("pontos", 0)
            ),
        },
        ranking_pos=posicao or None,
    )
    identity = derive_player_identity(
        jogador_payload,
        ranking_pos=posicao or None,
        modalidade="simples",
    )

    return JogadorResponse(
        nome=j.nome,
        nacionalidade=j.nacionalidade,
        idade=j.idade,
        altura=getattr(j, "altura", 185),
        peso=getattr(j, "peso", 80),
        mao_dominante=getattr(j, "mao_dominante", "Destro"),
        reves=getattr(j, "reves", "Duas mãos"),
        estilo_jogo=getattr(j, "estilo_jogo", "All-court"),
        pico_carreira=getattr(j, "pico_carreira", 28),
        tour="atp" if j.genero == "masculino" else "wta",
        ranking=posicao,
        pontos=j.pontos_ytd,
        overall=overall,
        resumo_fifa=resumo_fifa,
        energia=j.energia,
        fadiga=j.fadiga,
        status_lesao=(
            j.status_lesao.get("nivel")
            if (j.status_lesao or {}).get("lesionado")
            else None
        ),
        dinheiro=j.dinheiro,
        seguidores=j.seguidores,
        nivel=j.nivel,
        xp=j.xp,
        xp_para_proximo_nivel=getattr(j, "xp_para_proximo_nivel", 100),
        atributos=jogador_payload["atributos"],
        atributos_psicologicos=jogador_payload.get("atributos_psicologicos", {}),
        carta=carta_jogador(jogador_payload, posicao or RANKING_POSICAO_FALLBACK),
        identity=identity,
        historico_partidas=list(getattr(j, "historico_partidas", []) or []),
        historico_torneios=list(getattr(j, "historico_torneios", []) or []),
        trofeus=list(getattr(j, "trofeus", []) or []),
    )


@router.get("/financeiro")
def get_financeiro(session: Session = Depends(obter_sessao_ativa)):
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessão não iniciada.")

    j = session.jogador
    transacoes = getattr(j, "transacoes", [])

    # Agrupa por categoria
    por_categoria = {}
    for t in transacoes:
        cat = t.get("categoria", "outros")
        por_categoria[cat] = por_categoria.get(cat, 0) + t.get("valor", 0)

    return {
        "saldo": j.dinheiro,
        "transacoes": transacoes[-20:],  # Últimas 20
        "resumo_categorias": por_categoria,
    }


@router.get("/historico-partidas")
def get_historico_partidas(session: Session = Depends(obter_sessao_ativa)):
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessão não iniciada.")

    return {"historico": session.jogador.historico_partidas}


@router.get("/ranking-detalhado")
def get_ranking_detalhado(session: Session = Depends(obter_sessao_ativa)):
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessão não iniciada.")

    j = session.jogador
    from src.dados import get_caminho_ranking_duplas, carregar_temporada
    from src.ranking import SistemaRanking
    from api.routes._shared import carregar_temporada_atual

    nome_save = session.nome_save_ativo
    rk_s = session.ranking_atp if j.genero == "masculino" else session.ranking_wta
    path_d = get_caminho_ranking_duplas(nome_save, genero=j.genero)
    rk_d = SistemaRanking(path_d, modalidade="duplas")

    temporada = carregar_temporada_atual(nome_save)
    ano_atual = temporada.get("ano", START_YEAR)

    jogador_rk = rk_s.buscar_jogador_por_nome(j.nome) if rk_s else None
    jogador_rk_d = rk_d.buscar_jogador_por_nome(j.nome)

    pos_s = rk_s.obter_posicao(j.nome) if rk_s else None
    pos_d = rk_d.obter_posicao(j.nome)

    pontos_s = (jogador_rk or {}).get("pontos", 0)
    pontos_d = (jogador_rk_d or {}).get(
        "pontos_duplas", (jogador_rk_d or {}).get("pontos", 0)
    )

    def _extrair_resultados(j_rk, mod_label, ano):
        historico = (j_rk or {}).get("historico_torneios", [])
        resultados = [e for e in historico if e.get("ano") == ano]
        if not resultados:
            chave = (
                "pontos_detalhados"
                if mod_label == "simples"
                else "pontos_detalhados_duplas"
            )
            for b in (j_rk or {}).get(chave, []):
                if b.get("ano_origem") == ano and int(b.get("pontos", 0)) > 0:
                    resultados.append(
                        {
                            "nome": b.get("torneio", "?"),
                            "fase": b.get("fase", "?"),
                            "pontos": int(b.get("pontos", 0)),
                            "obrigatorio": b.get("tipo") in ("Grand Slam", "ATP 1000"),
                        }
                    )
        top = sorted(resultados, key=lambda x: x.get("pontos", 0), reverse=True)[:18]
        return [
            {
                "nome": e.get("nome", "?"),
                "fase": e.get("fase", "?"),
                "pontos": int(e.get("pontos", 0)),
                "obrigatorio": bool(e.get("obrigatorio")),
            }
            for e in top
        ]

    return {
        "posicao_simples": pos_s,
        "posicao_duplas": pos_d,
        "pontos_simples": pontos_s,
        "pontos_duplas": pontos_d,
        "pontos_ytd": getattr(j, "pontos_ytd", 0),
        "resultados_simples": _extrair_resultados(jogador_rk, "simples", ano_atual),
        "resultados_duplas": _extrair_resultados(jogador_rk_d, "duplas", ano_atual),
    }


@router.get("/carreira")
def get_carreira(session: Session = Depends(obter_sessao_ativa)):
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessão não iniciada.")

    j = session.jogador
    idade = getattr(j, "idade", 20)
    pico = getattr(j, "pico_carreira", 28)
    fase = j.obter_fase_carreira()

    rk_s = session.ranking_atp if j.genero == "masculino" else session.ranking_wta
    jogador_rk = rk_s.buscar_jogador_por_nome(j.nome) if rk_s else None
    titulos = (jogador_rk or {}).get("trofeus", [])

    return {
        "fase": fase,
        "idade": idade,
        "pico_carreira": pico,
        "nivel": getattr(j, "nivel", 1),
        "xp": getattr(j, "xp", 0),
        "xp_para_proximo": getattr(j, "xp_para_proximo_nivel", 100),
        "titulos": titulos,
    }


@router.get("/atributos")
def get_atributos(session: Session = Depends(obter_sessao_ativa)):
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessão não iniciada.")

    j = session.jogador
    return {
        "atributos": j.atributos,
        "atributos_psicologicos": j.atributos_psicologicos,
        "overall": j.calcular_overall(),
    }


@router.get("/ranking-historico")
def get_ranking_historico(session: Session = Depends(obter_sessao_ativa)):
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessão não iniciada.")

    return {"semanas": getattr(session.jogador, "historico_ranking", [])}


@router.get("/forma-recente")
def get_forma_recente(session: Session = Depends(obter_sessao_ativa)):
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessão não iniciada.")

    from src.match_history import MatchHistoryManager
    from src.utils.nome_utils import normalizar_nome

    manager = MatchHistoryManager(session.nome_save_ativo)
    partidas = manager.buscar_por_jogador(session.jogador.nome)

    # Ordena por ano e semana decrescente
    partidas.sort(
        key=lambda p: (int(p.get("ano", 0) or 0), int(p.get("semana", 0) or 0)),
        reverse=True,
    )

    ultimas = partidas[:5]
    forma = []
    detalhes = []

    j_norm = normalizar_nome(session.jogador.nome)

    for p in ultimas:
        # Identificar adversário
        jogadores = p.get("jogadores", [])
        adversario = "Desconhecido"
        for jog in jogadores:
            if normalizar_nome(jog) != j_norm:
                adversario = jog
                break

        # Verificar se venceu
        vencedor = p.get("vencedor")
        venceu = False
        if isinstance(vencedor, list):
            venceu = any(normalizar_nome(v) == j_norm for v in vencedor)
        else:
            venceu = normalizar_nome(str(vencedor or "")) == j_norm

        forma.append("V" if venceu else "D")
        detalhes.append(
            {
                "adversario": adversario,
                "resultado": p.get("resultado"),
                "torneio": p.get("torneio"),
                "semana": p.get("semana"),
                "ano": p.get("ano"),
                "venceu": venceu,
            }
        )

    return {"forma": forma, "partidas": detalhes}


@router.get("/rivalidades")
def get_rivalidades(session: Session = Depends(obter_sessao_ativa)):
    if not session.jogador:
        raise HTTPException(status_code=400, detail="Sessão não iniciada.")

    from src.match_history import MatchHistoryManager
    from src.utils.nome_utils import normalizar_nome

    manager = MatchHistoryManager(session.nome_save_ativo)
    partidas = manager.buscar_por_jogador(session.jogador.nome)
    j_norm = normalizar_nome(session.jogador.nome)

    # Contabilizar confrontos por adversário
    stats_rival = {}

    for p in partidas:
        jogadores = p.get("jogadores", [])
        adversario = None
        for jog in jogadores:
            if normalizar_nome(jog) != j_norm:
                adversario = jog
                break

        if not adversario:
            continue

        adv_norm = normalizar_nome(adversario)
        if adv_norm not in stats_rival:
            stats_rival[adv_norm] = {
                "nome": adversario,
                "confrontos": 0,
                "vitorias": 0,
                "derrotas": 0,
                "ultima_semana": 0,
                "ultimo_ano": 0,
            }

        stats = stats_rival[adv_norm]
        stats["confrontos"] += 1

        vencedor = p.get("vencedor")
        venceu = False
        if isinstance(vencedor, list):
            venceu = any(normalizar_nome(v) == j_norm for v in vencedor)
        else:
            venceu = normalizar_nome(str(vencedor or "")) == j_norm

        if venceu:
            stats["vitorias"] += 1
        else:
            stats["derrotas"] += 1

        ano = int(p.get("ano", 0) or 0)
        semana = int(p.get("semana", 0) or 0)
        if ano > stats["ultimo_ano"] or (
            ano == stats["ultimo_ano"] and semana > stats["ultima_semana"]
        ):
            stats["ultimo_ano"] = ano
            stats["ultima_semana"] = semana

    # Filtrar apenas quem tem 3+ confrontos (conforme X2-1)
    rivalidades = [s for s in stats_rival.values() if s["confrontos"] >= 3]

    # Adicionar win_rate e flag de rival ativo (win_rate > 60% ou < 40%)
    for r in rivalidades:
        win_rate = r["vitorias"] / r["confrontos"] if r["confrontos"] > 0 else 0.0
        r["win_rate"] = round(win_rate, 3)
        r["rival_ativo"] = win_rate > 0.6 or win_rate < 0.4

    return {"rivalidades": rivalidades}
