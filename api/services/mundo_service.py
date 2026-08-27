from __future__ import annotations

import random

from fastapi import HTTPException
from api.session import Session
from src.calendario import obter_torneios_da_semana
from src.dados import (
    carregar_estado_torneio,
    get_caminho_ranking_save,
)
from src.jogador import normalizar_nome
from src.presenters.tournament_presenter import formatar_torneio_resumido
from src.ranking import SistemaRanking
from src.services.player_context_service import carregar_temporada_atual
from src.tournament_manager import WeekTournamentManager

_FLAGS: dict[str, str] = {
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
    "ESA": "🇸🇻", "PAK": "🇵🇰", "RSA": "🇿🇦", "SLO": "🇸🇮", "THA": "🇹🇭",
}


def obter_proximos(session: Session) -> dict:
    nome_save = session.nome_save_ativo
    jogador = session.jogador
    temporada = carregar_temporada_atual(nome_save)
    semana_atual = temporada["semana"]

    proximos = []
    for i in range(4):
        sem = ((semana_atual + i - 1) % 52) + 1
        for t in obter_torneios_da_semana(sem, genero=jogador.genero):
            proximos.append(formatar_torneio_resumido(t))

    return {"semana_atual": semana_atual, "torneios": proximos}


from src.services.narrative_news_service import NarrativeNewsService


def obter_noticias(session: Session) -> list:
    nome_save = session.nome_save_ativo
    jogador = session.jogador
    temp = carregar_temporada_atual(nome_save)
    semana = temp["semana"]
    
    # 1. Obter dados de contexto
    estado_t = carregar_estado_torneio(nome_save, genero=jogador.genero)
    rk = SistemaRanking(get_caminho_ranking_save(nome_save, genero=jogador.genero))
    posicao = rk.obter_posicao(jogador.nome) or 9999
    
    # 2. Gerar notícias via Service (DRY)
    noticias = NarrativeNewsService.generate_player_news(jogador, posicao, estado_t)
    
    try:
        manager = WeekTournamentManager(nome_save, semana, genero=jogador.genero)
        noticias.extend(NarrativeNewsService.generate_circuit_news(
            manager, 
            active_tournament_name=estado_t.get("torneio") if estado_t else None
        ))
    except Exception:
        pass

    # 3. Fillers (KISS)
    while len(noticias) < 4:
        noticias.append(NarrativeNewsService.get_filler_news())

    random.shuffle(noticias)
    return noticias[:6]


def obter_torneio(nome_save: str, semana: int, nome_torneio: str, genero: str) -> dict:
    manager = WeekTournamentManager(nome_save, semana, genero=genero)
    estado = manager.obter_torneio(nome_torneio)
    if not estado:
        raise HTTPException(status_code=404, detail="Torneio não encontrado ou não iniciado.")
    return estado


def obter_ao_vivo(nome_save: str, semana: int) -> list:
    resultado = []
    for genero, tour_label in [("masculino", "ATP"), ("feminino", "WTA")]:
        manager = WeekTournamentManager(nome_save, semana, genero=genero)
        for r in manager.obter_resumo_semanal():
            resultado.append(
                {
                    "nome": r.get("nome", "?"),
                    "tipo": r.get("tipo", ""),
                    "tour": tour_label,
                    "fase_atual": r.get("fase", "?"),
                    "campeao_simples": r.get("campeao") or None,
                    "campeao_duplas": r.get("campeao_duplas") or None,
                    "finalizado": r.get("fase") == "finalizado" or bool(r.get("campeao")),
                }
            )
    return resultado


def obter_race_to_finals(session: Session) -> dict:
    nome_save = session.nome_save_ativo
    jogador = session.jogador
    rk = SistemaRanking(get_caminho_ranking_save(nome_save, genero=jogador.genero))
    circuito = "ATP" if jogador.genero == "masculino" else "WTA"
    nome_norm = normalizar_nome(jogador.nome)

    todos_ytd = sorted(
        rk.ranking, key=lambda j: int(j.get("pontos_ytd", 0) or 0), reverse=True
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


def obter_bracket(nome_save: str, semana: int, nome_torneio: str, tour: str) -> dict:
    genero = "masculino" if tour.lower() == "atp" else "feminino"
    manager = WeekTournamentManager(nome_save, semana, genero=genero)
    estado = manager.obter_torneio(nome_torneio)
    if not estado:
        raise HTTPException(status_code=404, detail="Torneio não encontrado.")

    t_data = estado.get("tournament_data", {})

    def _serializar_confrontos(rodadas: dict) -> dict:
        out = {}
        for fase, confrontos in rodadas.items():
            out[fase] = [
                {
                    "j1": c[0].get("nome", str(c[0])) if isinstance(c[0], dict) else str(c[0]),
                    "j2": c[1].get("nome", str(c[1])) if isinstance(c[1], dict) else str(c[1]),
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
        "nome": t_data.get("nome", nome_torneio),
        "tipo": t_data.get("tipo", ""),
        "fase_atual": estado.get("fase_atual", "?"),
        "campeao_simples": estado.get("campeao_simples"),
        "campeao_duplas": estado.get("campeao_duplas"),
        "rodadas": _serializar_confrontos(estado.get("rodadas", {})),
        "resultados": _serializar_resultados(estado.get("resultados", {})),
        "rodadas_duplas": _serializar_confrontos(estado.get("rodadas_duplas", {})),
        "resultados_duplas": _serializar_resultados(estado.get("resultados_duplas", {})),
    }


def obter_ranking_nacoes() -> list:
    import os
    import json
    from src.dados import BASE_DIR
    caminho_json = os.path.join(BASE_DIR, "db", "ranking_nacoes_davis.json")

    if not os.path.exists(caminho_json):
        raise HTTPException(status_code=404, detail="Ranking de nações não encontrado.")

    try:
        with open(caminho_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        nacoes = data.get("nations", [])
        # Ordenação oficial: Pontos -> Confrontos jogados
        nacoes_ordenadas = sorted(
            nacoes,
            key=lambda x: (int(x.get("points", 0)), int(x.get("ties_played", 0))),
            reverse=True,
        )

        return [
            {
                "posicao": idx,
                "pais": n.get("name"),
                "codigo": n.get("code"),
                "pontos": int(n.get("points", 0)),
                "flag": _FLAGS.get(str(n.get("code", "")).upper(), "🏳️"),
                "evolucao": random.randint(-2, 2) if random.random() < 0.3 else 0 # Simulação de evolução por enquanto
            }
            for idx, n in enumerate(nacoes_ordenadas, 1)
        ]
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Erro ao carregar ranking de nações: {exc}"
        )


def _pontuar_titulo(tipo: str, nome: str = "") -> int:
    texto = f"{tipo} {nome}"
    if "Grand Slam" in texto:
        return 2000
    if "1000" in texto:
        return 1000
    if "500" in texto:
        return 500
    if "250" in texto:
        return 250
    if "Challenger" in texto:
        return 125
    if "ITF 100" in texto:
        return 100
    if "ITF 25" in texto:
        return 25
    return 0


def _normalizar_titulo_jogador(titulo) -> dict | None:
    if isinstance(titulo, str):
        nome = titulo.strip()
        if not nome:
            return None
        return {"torneio": nome, "nome": nome, "tipo": "", "ano": None, "adversario_final": ""}
    if not isinstance(titulo, dict):
        return None
    torneio = str(titulo.get("torneio") or titulo.get("nome") or "").strip()
    if not torneio:
        return None
    return {
        "torneio": torneio,
        "nome": torneio,
        "tipo": titulo.get("tipo") or titulo.get("categoria") or "",
        "categoria": titulo.get("categoria") or titulo.get("tipo") or "",
        "semana": titulo.get("semana"),
        "ano": titulo.get("ano"),
        "modalidade": titulo.get("modalidade", "simples"),
        "adversario_final": titulo.get("adversario_final") or titulo.get("adversario") or "",
    }


def _titulos_derivados_do_historico(historico_torneios: list | None) -> list[dict]:
    titulos = []
    for item in historico_torneios or []:
        if not isinstance(item, dict):
            continue
        fase = str(item.get("fase_alcancada") or item.get("fase") or "").lower()
        if fase != "campeao":
            continue
        titulo = _normalizar_titulo_jogador(item)
        if titulo:
            titulos.append(titulo)
    return titulos


def obter_goat(nome_save: str, trofeus: list, historico_torneios: list | None = None) -> dict:
    from src.dados import carregar_historico

    hist = carregar_historico(nome_save)
    recordes = hist.get("recordes", {})

    meus_titulos = []
    vistos = set()
    for origem in (trofeus or [], *_titulos_derivados_do_historico(historico_torneios)):
        titulo = _normalizar_titulo_jogador(origem)
        if not titulo:
            continue
        chave = (titulo.get("torneio"), titulo.get("ano"), titulo.get("modalidade"))
        if chave in vistos:
            continue
        vistos.add(chave)
        meus_titulos.append(titulo)

    pts = sum(_pontuar_titulo(str(t.get("tipo", "")), str(t.get("torneio", ""))) for t in meus_titulos)

    return {
        "recordes": recordes,
        "meus_titulos": meus_titulos,
        "goat_points": pts,
    }


def obter_campeoes(nome_save: str) -> dict:
    from src.dados import carregar_historico

    hist = carregar_historico(nome_save)
    return {"campeoes": hist.get("campeoes", {})}
