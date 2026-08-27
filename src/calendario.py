"""
Módulo de calendário e orquestração de temporada.
Dismantled God Component: logic moved to specialized services.
"""

import os
import random
from src.dados import (
    obter_torneios_da_semana as core_obter_torneios,
    obter_torneio_por_nome as core_obter_por_nome,
    carregar_temporada as core_carregar_temporada,
    salvar_temporada as core_salvar_temporada,
)
from src.services.season_service import advance_week as core_advance_week
from src.services.tournament_entry_service import (
    selecionar_participantes as core_selecionar_participantes,
    ranking_limite_torneio as core_ranking_limite,
)
from src.services.ranking_service import (
    migrar_rankings_semana_se_preciso as core_migrar_rankings,
    processar_expiracao_ranking as core_processar_expiracao,
)
from src.services.health_service import (
    recuperar_npcs_semana as core_recuperar_npcs,
    processar_recuperacao_semanal,
)

from src.patrocinios import PATROCINADORES_DISPONIVEIS

# --- Re-exports para compatibilidade ---

def obter_torneios_da_semana(semana, genero="masculino"):
    return core_obter_torneios(semana, genero=genero)

def obter_torneio_por_nome(semana, nome_torneio, genero="masculino"):
    return core_obter_por_nome(semana, nome_torneio, genero=genero)

def carregar_temporada(nome_save):
    return core_carregar_temporada(nome_save)

def salvar_temporada(nome_save, data):
    core_salvar_temporada(nome_save, data)

def avancar_semana(nome_save, expected_week=None):
    from src.presenters.tournament_presenter import formatar_torneio_resumido
    resultado = core_advance_week(nome_save, expected_week=expected_week)
    torneios = resultado.get("torneios_disponiveis", [])
    if isinstance(torneios, list):
        resultado["torneios_disponiveis"] = [
            formatar_torneio_resumido(t) if isinstance(t, dict) else t for t in torneios
        ]
    return resultado

def _selecionar_participantes_para_torneio(info_torneio, ranking_ordenado, disponiveis_set, max_jogadores=None):
    return core_selecionar_participantes(info_torneio, ranking_ordenado, disponiveis_set, max_jogadores)

def _migrar_rankings_semana_se_preciso(rankings, semana_atual, ano_atual):
    core_migrar_rankings(rankings, semana_atual, ano_atual)

def _processar_expiracao_ranking(nome_save, semana_atual, ano_atual):
    core_processar_expiracao(nome_save, semana_atual, ano_atual)

def _recuperar_npcs_semana(rankings):
    core_recuperar_npcs(rankings)

# --- Métodos únicos que permanecem aqui por enquanto ---

def calcular_melhor_resultado_por_torneio(historico_torneios: list) -> dict:
    melhores = {}
    from src.jogador import normalizar_nome
    _PESOS_FASE = {
        "qualy_1": 0, "qualy_2": 1, "qualy_r1": 0, "qualy_r2": 1, "qualy_r3": 2,
        "r128": 3, "r96": 3, "r64": 4, "r32": 5, "r16": 6, "oitavas": 6,
        "quartas": 7, "semifinal": 8, "final": 9, "campeao": 10,
    }
    for h in (historico_torneios or []):
        if not isinstance(h, dict): continue
        nome = h.get("nome") or h.get("torneio")
        if not nome: continue
        fase = str(h.get("fase") or h.get("fase_alcancada", "")).lower()
        peso = _PESOS_FASE.get(fase, -1)
        if nome not in melhores or peso > _PESOS_FASE.get(str(melhores[nome].get("fase")).lower(), -1):
            melhores[nome] = h
    return melhores

def badge_entry_status(ranking_pos, torneio: dict) -> str:
    if ranking_pos is None: return "OUT"
    tipo = torneio.get("tipo", "")
    from src.services.tournament_entry_service import eh_elegivel_por_ranking_torneio
    if not eh_elegivel_por_ranking_torneio(ranking_pos, tipo): return "[Ineligible]"
    limite = 400 if "challenger" in str(tipo).lower() else core_ranking_limite(tipo)
    if ranking_pos <= (limite or 9999): return "MD"
    if ranking_pos <= (limite or 9999) + 32: return "Q"
    return "ALT"

def _marcar_historico_expirado(jogador, blocos_expirando, ano_novo=None, semana_nova=None):
    from src.jogador import normalizar_nome
    historico = (jogador.get("historico_torneios", []) if isinstance(jogador, dict) else getattr(jogador, "historico_torneios", []))
    if not isinstance(historico, list) or not isinstance(blocos_expirando, list): return 0
    marcados = 0
    for bloco in (blocos_expirando or []):
        if not isinstance(bloco, dict): continue
        nome_ref = normalizar_nome(bloco.get("torneio", ""))
        tipo_ref = str(bloco.get("tipo", "") or "")
        for entry in historico:
            if not isinstance(entry, dict) or entry.get("expirado"): continue
            if normalizar_nome(entry.get("nome", entry.get("torneio", ""))) == nome_ref:
                entry["expirado"] = True; marcados += 1; break
    return marcados

# Métodos que season_service ainda chama (precisam ser removidos de lá depois)
def _atualizar_recuperacao_jogador(jogador, info_torneio=None) -> list:
    eventos = []
    processar_recuperacao_semanal(jogador, eventos=eventos, info_torneio=info_torneio)
    return eventos

def _processar_rotinas_semanais_jogador(jogador, temporada, ranking, torneio_info_semana, jogador_participou, eventos_api):
    from src.services.season_service import _processar_rotinas_semanais_jogador as core_routines
    core_routines(jogador, temporada, ranking, torneio_info_semana, jogador_participou, eventos_api)

def _inicializar_torneios_nova_semana(nome_save, semana_nova, jogador_nome):
    from src.tournament_manager import WeekTournamentManager
    for gen in ["masculino", "feminino"]:
        manager = WeekTournamentManager(nome_save, semana_nova, genero=gen)
        torneios_info = obter_torneios_da_semana(semana_nova, genero=gen)
        manager.inicializar_torneios(torneios_info, jogador_nome=jogador_nome)

def _processar_virada_ano(temporada, jogador, rankings, eventos_api):
    from src.services.season_service import _processar_virada_ano as core_year
    core_year(temporada, jogador, rankings, eventos_api)

def _estado_torneio_ativo(estado_torneio, semana_referencia=None):
    if not estado_torneio: return False
    fase = estado_torneio.get("fase_atual")
    if not fase or fase == "finalizado": return False
    if semana_referencia is not None:
        if estado_torneio.get("semana") != semana_referencia: return False
    return True

def _semana_estado_torneio(estado_torneio):
    if not estado_torneio:
        return None
    try:
        return int(estado_torneio.get("semana"))
    except (TypeError, ValueError):
        return None

def processar_progressao_semanal(jogador) -> list:
    from src.constants.staff_constants import PROFISSIONAIS_DISPONIVEIS
    eventos: list = []
    equipe = getattr(jogador, "equipe", [])
    for contrato in equipe:
        prof_id = contrato.get("id") if isinstance(contrato, dict) else contrato
        prof = PROFISSIONAIS_DISPONIVEIS.get(prof_id)
        if not prof:
            continue
        categoria = str(prof.get("categoria", "") or "").lower()
        if categoria == "psicologo":
            bonus = int(prof.get("bonus_mental", 0) or 0)
            if bonus > 0:
                psico = getattr(jogador, "atributos_psicologicos", {})
                if isinstance(psico, dict):
                    for k in psico:
                        psico[k] = min(100, psico[k] + bonus)
                    eventos.append(f"🧠 Apoio psicológico ({prof['nome']}): +{bonus} em todos os atributos mentais.")
        elif categoria == "treinador":
            bonus = float(prof.get("bonus_progressao", 0) or 0)
            if bonus > 0:
                eventos.append(f"🎾 {prof['nome']} ajustou o plano de treino (+{int(bonus * 100)}% eficiência).")
    return eventos

def processar_seguidores(jogador, ranking, participou=True):
    if not participou:
        return 0

    posicao = ranking.obter_posicao(getattr(jogador, "nome", "")) if ranking else None
    ganho = 0
    if posicao is not None:
        ganho += max(0, 1100 - int(posicao) * 10)

    save_name = getattr(jogador, "save_name", None)
    if save_name:
        from src import dados

        estado = dados.carregar_estado_torneio(
            save_name, genero=getattr(jogador, "genero", "masculino")
        )
        fase = str((estado or {}).get("fase_atual") or "").lower()
        if fase in {"r16", "oitavas", "quartas", "semifinal", "final", "campeao"}:
            ganho = max(ganho, 1000)

    atual = int(getattr(jogador, "seguidores", 0) or 0)
    setattr(jogador, "seguidores", atual + ganho)
    return ganho

def processar_avisos_patrocinio(jogador, ranking):
    avisos = getattr(jogador, "avisos_patrocinio", None)
    if not isinstance(avisos, dict):
        avisos = {}
        setattr(jogador, "avisos_patrocinio", avisos)

    posicao = ranking.obter_posicao(getattr(jogador, "nome", "")) if ranking else None
    seguidores = int(getattr(jogador, "seguidores", 0) or 0)
    for pat_id in list(getattr(jogador, "patrocinios", []) or []):
        patrocinador = PATROCINADORES_DISPONIVEIS.get(pat_id, {})
        req_rank = patrocinador.get("requisito_ranking")
        req_followers = patrocinador.get("req_seguidores", 0)
        motivos = []
        if req_rank is not None and (posicao is None or int(posicao) > int(req_rank)):
            motivos.append("ranking")
        if seguidores < int(req_followers or 0):
            motivos.append("seguidores")
        if motivos:
            avisos[pat_id] = {"motivos": motivos, "semanas": avisos.get(pat_id, {}).get("semanas", 0) + 1}
    return avisos

def _simular_torneios_semanais_npc(nome_save, semana_atual, ranking, jogador, player_active_tournament_state):
    from src.services.tournament_npc_service import simular_torneios_semanais_npc
    return simular_torneios_semanais_npc(nome_save, semana_atual, jogador, player_active_tournament_state)
