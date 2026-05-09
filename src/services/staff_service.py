from __future__ import annotations
from typing import Any, List, Optional, Dict
from src.dados import carregar_staff

def obter_detalhes_profissional(prof_id: str) -> Optional[Dict]:
    """Retorna os dados estáticos de um profissional a partir do JSON."""
    data = carregar_staff()
    # Busca em profissionais
    prof = data.get("professionals", {}).get(prof_id)
    if not prof:
        # Busca em empresários (agents)
        prof = data.get("agents", {}).get(prof_id)
    return prof

def processar_pagamentos_equipe(jogador: Any) -> List[Dict]:
    """
    Deduz salários semanais de cada membro da equipe.
    Retorna eventos de notificação se necessário.
    """
    eventos = []
    equipe = getattr(jogador, "equipe", [])
    staff_data = carregar_staff().get("professionals", {})
    
    for contrato in equipe:
        if not isinstance(contrato, dict):
            continue
            
        prof_id = contrato.get("id")
        prof_info = staff_data.get(prof_id)
        salario = contrato.get("salario", 0)
        
        if prof_info and salario > 0:
            jogador.registrar_transacao(
                -salario, 
                f"Salário: {prof_info['nome']} ({prof_info['categoria']})", 
                categoria="equipe"
            )
            
    return eventos

def atualizar_contratos_staff(jogador: Any) -> List[Dict]:
    """
    Reduz semanas restantes dos contratos e remove os expirados.
    Retorna lista de eventos de expiração.
    """
    eventos = []
    equipe_atual = getattr(jogador, "equipe", [])
    nova_equipe = []
    staff_data = carregar_staff().get("professionals", {})

    for contrato in equipe_atual:
        if not isinstance(contrato, dict):
            continue
            
        restantes = contrato.get("semanas_restantes", 0) - 1
        if restantes <= 0:
            prof_info = staff_data.get(contrato.get("id"), {})
            nome = prof_info.get("nome", "Profissional")
            eventos.append({
                "tipo": "contrato_expirado",
                "mensagem": f"O contrato de {nome} chegou ao fim.",
                "profissional_id": contrato.get("id")
            })
        else:
            contrato["semanas_restantes"] = restantes
            nova_equipe.append(contrato)
            
    jogador.equipe = nova_equipe
    return eventos

def obter_limite_equipe(jogador: Any) -> int:
    """Retorna o limite de profissionais baseado no empresário atual."""
    emp_contrato = getattr(jogador, "empresario", None)
    if not isinstance(emp_contrato, dict):
        return 2 # Limite base sem empresário
        
    staff_data = carregar_staff()
    emp_id = emp_contrato.get("id")
    emp_info = staff_data.get("agents", {}).get(emp_id, {})
    
    return int(emp_info.get("max_equipe", 2))
