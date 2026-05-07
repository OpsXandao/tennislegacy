from __future__ import annotations

import random

from fastapi import APIRouter, Depends, HTTPException, Query

from api.session import Session, obter_sessao_ativa
from src.calendario import obter_torneios_da_semana
from src.dados import carregar_estado_torneio, carregar_ranking
from src.jogador import normalizar_nome
from src.presenters.tournament_presenter import formatar_torneio_resumido
from src.services.player_context_service import carregar_temporada_atual
from src.tournament_manager import WeekTournamentManager

router = APIRouter(prefix="/api/mundo", tags=["mundo"])


@router.get("/proximos")
def obter_proximos(session: Session = Depends(obter_sessao_ativa)):
    nome_save = session.nome_save_ativo
    jogador = session.jogador
    temporada = carregar_temporada_atual(nome_save)
    semana_atual = temporada["semana"]

    proximos = []
    for i in range(4):
        sem = ((semana_atual + i - 1) % 52) + 1
        torneios = obter_torneios_da_semana(sem, genero=jogador.genero)
        for t in torneios:
            proximos.append(formatar_torneio_resumido(t))

    return {"semana_atual": semana_atual, "torneios": proximos}


@router.get("/noticias")
def obter_noticias(session: Session = Depends(obter_sessao_ativa)):
    nome_save = session.nome_save_ativo
    jogador = session.jogador

    noticias = []

    estado_t = carregar_estado_torneio(nome_save, genero=jogador.genero)
    if estado_t and estado_t.get("fase_atual") == "finalizado":
        campeao = estado_t.get("campeao_simples")
        if campeao:
            if normalizar_nome(campeao) == normalizar_nome(jogador.nome):
                noticias.append(
                    f"CAMPEÃO! {jogador.nome.upper()} VENCE EM {estado_t['torneio'].upper()}!"
                )
            else:
                noticias.append(
                    f"{campeao.upper()} CONQUISTA O TÍTULO DE {estado_t['torneio'].upper()}."
                )

    from src.ranking import SistemaRanking
    from src.dados import get_caminho_ranking_save

    rk = SistemaRanking(get_caminho_ranking_save(nome_save, genero=jogador.genero))
    posicao = rk.obter_posicao(jogador.nome) or 9999

    if posicao <= 10:
        noticias.append(
            f"FENÔMENO: {jogador.nome.upper()} SE CONSOLIDA ENTRE OS MELHORES DO MUNDO!"
        )
    elif posicao <= 100:
        noticias.append(
            f"SUBINDO: {jogador.nome.upper()} GANHA DESTAQUE NO CIRCUITO MUNDIAL."
        )

    frases_mundo = [
        "AUDIÊNCIA DO TÊNIS SOBE 20% NESTA TEMPORADA.",
        "NOVAS REGRAS DE QUADRA ESTÃO SENDO TESTADAS PARA 2027.",
        "TOUR MUNDIAL ANUNCIA EXPANSÃO PARA NOVOS PAÍSES.",
        "RECORDE DE PÚBLICO EM GRAND SLAMS NESTE ANO.",
        "MARCA ESPORTIVA LANÇA NOVA LINHA DE RAQUETES DE ALTA PERFORMANCE.",
    ]
    noticias.append(random.choice(frases_mundo))

    if getattr(jogador, "patrocinios", []):
        noticias.append(
            f"MERCADO: {jogador.nome.upper()} ATRAI NOVOS INVESTIDORES APÓS RECENTES RESULTADOS."
        )

    return {"noticias": noticias}


@router.get("/torneio/{nome}")
def obter_detalhes_torneio(
    nome: str,
    tour: str | None = None,
    session: Session = Depends(obter_sessao_ativa),
):
    nome_save = session.nome_save_ativo
    jogador = session.jogador
    temporada = carregar_temporada_atual(nome_save)
    semana = temporada["semana"]

    genero = jogador.genero
    if tour == "atp":
        genero = "masculino"
    elif tour == "wta":
        genero = "feminino"

    manager = WeekTournamentManager(nome_save, semana, genero=genero)
    estado = manager.obter_torneio(nome)

    if not estado:
        raise HTTPException(
            status_code=404, detail="Torneio não encontrado ou não iniciado."
        )

    return estado


@router.get("/ao-vivo")
def ao_vivo(session: Session = Depends(obter_sessao_ativa)):
    nome_save = session.nome_save_ativo
    temporada = carregar_temporada_atual(nome_save)
    semana = temporada["semana"]

    resultado = []
    for genero, tour_label in [("masculino", "ATP"), ("feminino", "WTA")]:
        manager = WeekTournamentManager(nome_save, semana, genero=genero)
        resumo = manager.obter_resumo_semanal()
        for r in resumo:
            resultado.append(
                {
                    "nome": r.get("nome", "?"),
                    "tipo": r.get("tipo", ""),
                    "tour": tour_label,
                    "fase_atual": r.get("fase", "?"),
                    "campeao_simples": r.get("campeao") or None,
                    "campeao_duplas": r.get("campeao_duplas") or None,
                    "finalizado": r.get("fase") == "finalizado"
                    or bool(r.get("campeao")),
                }
            )

    return {"semana": semana, "torneios": resultado}


@router.get("/race-to-finals")
def race_to_finals(session: Session = Depends(obter_sessao_ativa)):
    nome_save = session.nome_save_ativo
    jogador = session.jogador

    from src.dados import get_caminho_ranking_save
    from src.ranking import SistemaRanking

    rk = SistemaRanking(get_caminho_ranking_save(nome_save, genero=jogador.genero))
    circuito = "ATP" if jogador.genero == "masculino" else "WTA"
    nome_norm = normalizar_nome(jogador.nome)

    todos_ytd = sorted(
        rk.ranking,
        key=lambda j: int(j.get("pontos_ytd", 0) or 0),
        reverse=True,
    )
    top8 = todos_ytd[:8]

    pos_jogador = None
    pts_jogador = 0
    for idx, j in enumerate(todos_ytd, 1):
        if normalizar_nome(j.get("nome", "")) == nome_norm:
            pos_jogador = idx
            pts_jogador = int(j.get("pontos_ytd", 0) or 0)
            break

    pts_8 = int(top8[7].get("pontos_ytd", 0) or 0) if len(top8) >= 8 else 0
    faltam = max(0, pts_8 - pts_jogador + 1) if pos_jogador and pos_jogador > 8 else 0

    return {
        "tour": circuito,
        "top8": [
            {
                "posicao": i + 1,
                "nome": j.get("nome", "?"),
                "nacionalidade": j.get("nacionalidade", "??"),
                "pontos_ytd": int(j.get("pontos_ytd", 0) or 0),
                "e_jogador": normalizar_nome(j.get("nome", "")) == nome_norm,
            }
            for i, j in enumerate(top8)
        ],
        "posicao_jogador": pos_jogador,
        "pontos_jogador": pts_jogador,
        "faltam_para_classificar": faltam,
    }


@router.get("/bracket")
def bracket_torneio_externo(
    torneio: str = Query(...),
    tour: str = Query(default="atp"),
    session: Session = Depends(obter_sessao_ativa),
):
    nome_save = session.nome_save_ativo
    temporada = carregar_temporada_atual(nome_save)
    semana = temporada["semana"]

    genero = "masculino" if tour.lower() == "atp" else "feminino"
    manager = WeekTournamentManager(nome_save, semana, genero=genero)
    estado = manager.obter_torneio(torneio)

    if not estado:
        raise HTTPException(status_code=404, detail="Torneio não encontrado.")

    t_data = estado.get("tournament_data", {})

    def _serializar_confrontos(rodadas: dict) -> dict:
        out = {}
        for fase, confrontos in rodadas.items():
            out[fase] = [
                {
                    "j1": (
                        c[0].get("nome", str(c[0]))
                        if isinstance(c[0], dict)
                        else str(c[0])
                    ),
                    "j2": (
                        c[1].get("nome", str(c[1]))
                        if isinstance(c[1], dict)
                        else str(c[1])
                    ),
                }
                for c in confrontos
                if len(c) >= 2
            ]
        return out

    def _serializar_resultados(resultados: dict) -> dict:
        out = {}
        for fase, lista in resultados.items():
            out[fase] = [
                {
                    "j1": r.get("jogador_a", r.get("dupla_a", "?")),
                    "j2": r.get("jogador_b", r.get("dupla_b", "?")),
                    "vencedor": r.get("vencedor", "?"),
                    "placar": r.get("placar", r.get("resultado", "")),
                }
                for r in lista
                if isinstance(r, dict)
            ]
        return out

    return {
        "nome": t_data.get("nome", torneio),
        "tipo": t_data.get("tipo", ""),
        "fase_atual": estado.get("fase_atual", "?"),
        "campeao_simples": estado.get("campeao_simples"),
        "campeao_duplas": estado.get("campeao_duplas"),
        "rodadas": _serializar_confrontos(estado.get("rodadas", {})),
        "resultados": _serializar_resultados(estado.get("resultados", {})),
        "rodadas_duplas": _serializar_confrontos(estado.get("rodadas_duplas", {})),
        "resultados_duplas": _serializar_resultados(
            estado.get("resultados_duplas", {})
        ),
    }


@router.get("/ranking-nacoes")
def get_ranking_nacoes():
    import json
    import os
    from src.dados import BASE_DIR

    caminho = os.path.join(BASE_DIR, "db", "ranking_nacoes_davis.json")
    if not os.path.exists(caminho):
        raise HTTPException(status_code=404, detail="Ranking de nações não encontrado.")

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            data = json.load(f)

        nacoes_raw = data.get("nations", [])
        
        # Mapa simples de códigos para emojis de bandeira
        # (Em produção isso viria de uma biblioteca ou db mais completo)
        FLAGS = {
            "ITA": "🇮🇹", "ESP": "🇪🇸", "GER": "🇩🇪", "BEL": "🇧🇪", "USA": "🇺🇸",
            "FRA": "🇫🇷", "CZE": "🇨🇿", "AUS": "🇦🇺", "AUT": "🇦🇹", "ARG": "🇦🇷",
            "NED": "🇳🇱", "CAN": "🇨🇦", "GBR": "🇬🇧", "CHI": "🇨🇱", "CRO": "🇭🇷",
            "KOR": "🇰🇷", "HUN": "🇭🇺", "BRA": "🇧🇷", "IND": "🇮🇳", "FIN": "🇫🇮",
            "DEN": "🇩🇰", "SRB": "🇷🇸", "ECU": "🇪🇨", "SVK": "🇸🇰", "JPN": "🇯🇵",
            "NOR": "🇳🇴", "SWE": "🇸🇪", "PER": "🇵🇪", "POL": "🇵🇱", "SUI": "🇨🇭",
            "BUL": "🇧🇬", "TPE": "🇹🇼", "TUR": "🇹🇷", "COL": "🇨🇴", "MON": "🇲🇨",
            "LTU": "🇱🇹", "GRE": "🇬🇷", "POR": "🇵🇹", "LUX": "🇱🇺", "BIH": "🇧🇦",
            "ISR": "🇮🇱", "KAZ": "🇰🇿", "NZL": "🇳🇿", "EGY": "🇪🇬", "CHN": "🇨🇳",
            "ROU": "🇷🇴", "UKR": "🇺🇦", "MAR": "🇲🇦", "MEX": "🇲🇽", "URU": "🇺🇾",
            "TUN": "🇹🇳", "LBN": "🇱🇧", "HKG": "🇭🇰", "PAR": "🇵🇾", "EST": "🇪🇪",
            "ESA": "🇸🇻", "PAK": "🇵🇰", "RSA": "🇿🇦", "SLO": "🇸🇮", "THA": "🇹🇭"
        }

        nacoes = []
        for idx, n in enumerate(nacoes_raw, 1):
            nacoes.append({
                "posicao": idx,
                "pais": n.get("name"),
                "codigo": n.get("code"),
                "pontos": n.get("points"),
                "flag": FLAGS.get(n.get("code"), "🏳️")
            })

        return {"nacoes": nacoes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar ranking de nações: {e}")
