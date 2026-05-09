from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from src.dados import carregar_patrocinadores, carregar_staff

# Regras de Negócio
LIMITE_PATROCINIO_MASTER = 1
LIMITE_PATROCINIO_MENORES = 3
_CATEGORIAS_MATERIAL_ESPORTIVO = {"raquete", "vestuario", "calcado", "acessorios"}

# Mapa de retrocompatibilidade para IDs antigos
_MAPA_PATROCINIO_LEGADO = {
    "raquete_local": "racket_local",
    "vestuario_pro": "clothing_regional",
    "raquete_pro": "racket_pro",
    "banco_master": "bank_global",
}


def _patrocinador_master_valido(patrocinador: dict) -> bool:
    """Verifica se um patrocinador master é de categoria permitida (material esportivo)."""
    if not isinstance(patrocinador, dict):
        return False
    if patrocinador.get("tier") != "master":
        return True
    categoria = str(patrocinador.get("categoria", "")).strip().lower()
    return categoria in _CATEGORIAS_MATERIAL_ESPORTIVO


def _normalizar_lista_patrocinios(jogador: Any) -> List[Any]:
    patrocinios = getattr(jogador, "patrocinios", [])
    if not isinstance(patrocinios, list):
        return []
    return patrocinios


def _normalizar_ids_patrocinios(
    patrocinios: List[Any], sponsors: Optional[Dict[str, Any]] = None
) -> List[str]:
    if sponsors is None:
        sponsors = carregar_patrocinadores()

    ids: List[str] = []
    for item in patrocinios:
        pat_id = resolver_id_patrocinio(item, sponsors)
        if pat_id and pat_id not in ids:
            ids.append(pat_id)
    return ids


def resolver_id_patrocinio(item: Any, sponsors: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Resolve ID legado, dicionário ou nome para um ID de patrocinador válido."""
    if not item:
        return None
    
    if sponsors is None:
        sponsors = carregar_patrocinadores()

    if isinstance(item, dict):
        if item.get("id"):
            item = item.get("id")
        elif item.get("nome"):
            nome = str(item.get("nome", "")).strip().lower()
            for pid, pat in sponsors.items():
                if str(pat.get("nome", "")).strip().lower() == nome:
                    return pid
            return None
        else:
            return None

    if not isinstance(item, str):
        item = str(item)
    
    # Tenta resolver ID legado
    novo_id = _MAPA_PATROCINIO_LEGADO.get(item, item)
    return novo_id if novo_id in sponsors else None


def migrar_patrocinios(patrocinios_raw: List[Any]) -> List[str]:
    """Converte lista de patrocínios legados para o novo formato."""
    if not isinstance(patrocinios_raw, (list, tuple, set)):
        return []

    sponsors = carregar_patrocinadores()
    resultado = []
    for p in patrocinios_raw:
        novo = resolver_id_patrocinio(p, sponsors)
        if novo and novo not in resultado:
            resultado.append(novo)
    return resultado


def serializar_patrocinio_ativo(
    item: Any, sponsors: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """Converte um contrato ativo em payload pronto para API."""
    if sponsors is None:
        sponsors = carregar_patrocinadores()

    if isinstance(item, dict):
        pat_id = resolver_id_patrocinio(item, sponsors)
        semanas_restantes = int(
            item.get("semanas_restantes", item.get("duracao_semanas", 0)) or 0
        )
    else:
        pat_id = resolver_id_patrocinio(item, sponsors)
        semanas_restantes = 0

    if not pat_id:
        return None

    patrocinador = sponsors.get(pat_id)
    if not patrocinador:
        return None

    return {
        "id": pat_id,
        "nome": patrocinador.get("nome", str(pat_id)),
        "categoria": patrocinador.get("categoria", ""),
        "nivel": patrocinador.get("tier", "menor"),
        "valor": int(patrocinador.get("pagamento_semanal", 0) or 0),
        "semanas_restantes": semanas_restantes,
    }


def listar_patrocinios_ativos(
    jogador: Any, sponsors: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Lista contratos de patrocínio ativos já serializados."""
    if sponsors is None:
        sponsors = carregar_patrocinadores()

    ativos: List[Dict[str, Any]] = []
    for item in _normalizar_lista_patrocinios(jogador):
        payload = serializar_patrocinio_ativo(item, sponsors)
        if payload:
            ativos.append(payload)
    return ativos


def listar_patrocinios_disponiveis(
    jogador: Any,
    posicao: int,
    seguidores: int = 0,
    sponsors: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Lista oportunidades de patrocínio disponíveis para busca ativa no frontend."""
    if sponsors is None:
        sponsors = carregar_patrocinadores()

    disponiveis: List[Dict[str, Any]] = []
    for pat_id, patrocinador in sponsors.items():
        pode, motivo = pode_assinar_patrocinio(jogador, pat_id, posicao, seguidores)
        disponiveis.append(
            {
                "id": pat_id,
                "nome": patrocinador.get("nome"),
                "categoria": patrocinador.get("categoria", ""),
                "nivel": patrocinador.get("tier", "menor"),
                "valor_mensal": int(patrocinador.get("pagamento_semanal", 0) or 0) * 4,
                "valor_semanal": int(patrocinador.get("pagamento_semanal", 0) or 0),
                "bonus_assinatura": int(
                    patrocinador.get("bonus_assinatura", 0) or 0
                ),
                "requisito_ranking": int(
                    patrocinador.get("requisito_ranking", 0) or 0
                ),
                "requisito_seguidores": int(
                    patrocinador.get("req_seguidores", 0) or 0
                ),
                "elegivel": pode,
                "motivo_bloqueio": motivo if not pode else None,
                "descricao": patrocinador.get("descricao", ""),
            }
        )

    return disponiveis


def resumir_contexto_patrocinio(
    jogador: Any,
    posicao: int,
    sponsors: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Resume a capacidade atual do jogador para busca e assinatura de contratos."""
    if sponsors is None:
        sponsors = carregar_patrocinadores()

    ativos = listar_patrocinios_ativos(jogador, sponsors)
    master_ativos = [pat for pat in ativos if pat.get("nivel") == "master"]
    menores_ativos = [pat for pat in ativos if pat.get("nivel") != "master"]

    return {
        "ranking_atual": int(posicao or 0),
        "seguidores_atuais": int(getattr(jogador, "seguidores", 0) or 0),
        "patrocinios_ativos": len(ativos),
        "slots_menores_restantes": max(
            LIMITE_PATROCINIO_MENORES - len(menores_ativos), 0
        ),
        "slot_master_disponivel": len(master_ativos) < LIMITE_PATROCINIO_MASTER,
    }


def pode_assinar_patrocinio(jogador: Any, pat_id: str, posicao: int, seguidores: int = 0) -> Tuple[bool, str]:
    """Valida se o jogador preenche os requisitos para um patrocinador."""
    sponsors = carregar_patrocinadores()
    pat = sponsors.get(pat_id)
    if not pat:
        return False, "Patrocinador desconhecido."

    patrocinios_atuais = _normalizar_ids_patrocinios(
        _normalizar_lista_patrocinios(jogador), sponsors
    )
    if pat_id in patrocinios_atuais:
        return False, "Você já tem este patrocínio."

    tier = pat.get("tier", "menor")
    if tier == "master" and not _patrocinador_master_valido(pat):
        return False, "Patrocinador master deve ser de material esportivo."
    
    if tier == "master":
        masters_ativos = [
            p for p in patrocinios_atuais 
            if sponsors.get(p, {}).get("tier") == "master"
        ]
        if masters_ativos:
            nome_atual = sponsors.get(masters_ativos[0], {}).get("nome", "atual")
            return False, f"Você já tem o patrocinador master {nome_atual}. Encerre-o primeiro."
    else:
        menores_ativos = [
            p for p in patrocinios_atuais 
            if sponsors.get(p, {}).get("tier", "menor") != "master"
        ]
        if len(menores_ativos) >= LIMITE_PATROCINIO_MENORES:
            return False, f"Limite de {LIMITE_PATROCINIO_MENORES} patrocínios menores atingido."

    if posicao > pat.get("requisito_ranking", 9999):
        return False, f"Ranking insuficiente (requerido: #{pat['requisito_ranking']})."
    
    req_seg = pat.get("req_seguidores", 0)
    if req_seg > 0 and seguidores < req_seg:
        return False, f"Seguidores insuficientes (requerido: {req_seg:,})."
    
    return True, "OK"

def processar_pagamentos_patrocinio(jogador: Any):
    """Executa o processamento semanal de receitas de patrocínio."""
    sponsors = carregar_patrocinadores()
    staff_data = carregar_staff()
    agents = staff_data.get("agents", {})
    
    # Garantir que os IDs estão normalizados
    patrocinios_atuais = migrar_patrocinios(getattr(jogador, "patrocinios", []))
    jogador.patrocinios = patrocinios_atuais
    
    bonus_emp = 0.0
    comissao_pct = 0.15  # Default 15%
    emp_nome = "Empresário"
    
    emp_contrato = getattr(jogador, "empresario", None)
    if isinstance(emp_contrato, dict):
        emp_id = emp_contrato.get("id")
        emp_data = agents.get(emp_id)
        if emp_data:
            bonus_emp = float(emp_data.get("bonus_patrocinio", 0.0) or 0.0)
            comissao_pct = float(emp_data.get("comissao_agenciamento", 0.15) or 0.15)
            emp_nome = emp_data.get("nome", "Empresário")

    for pat_id in patrocinios_atuais:
        pat = sponsors.get(pat_id)
        if pat:
            valor_bruto = pat.get("pagamento_semanal", 0)
            bonus_valor = int(valor_bruto * bonus_emp)
            valor_com_bonus = valor_bruto + bonus_valor
            
            valor_comissao = int(valor_com_bonus * comissao_pct)
            valor_liquido = valor_com_bonus - valor_comissao

            desc = f"Patrocínio: {pat['nome']}"
            if bonus_emp > 0:
                desc += f" (+{int(bonus_emp*100)}% bônus)"
            if comissao_pct > 0:
                desc += f" (-{int(comissao_pct*100)}% comissão {emp_nome})"

            jogador.registrar_transacao(valor_liquido, desc, categoria="patrocinio")


def assinar_patrocinio(
    nome_save: str,
    jogador: Any,
    patrocinio_id: str,
    posicao: int,
) -> dict:
    """Valida e registra a assinatura de um patrocínio, salvando o jogador."""
    from src.save import salvar_jogo

    sponsors = carregar_patrocinadores()
    pode, motivo = pode_assinar_patrocinio(jogador, patrocinio_id, posicao, getattr(jogador, "seguidores", 0))
    if not pode:
        return {"ok": False, "mensagem": motivo}

    pat = sponsors.get(patrocinio_id)
    if not pat:
        return {"ok": False, "mensagem": "Patrocinador não encontrado.", "status": 404}

    jogador.patrocinios.append(patrocinio_id)
    bonus = int(pat.get("bonus_assinatura", 0) or 0)
    if bonus > 0:
        jogador.registrar_transacao(
            bonus,
            f"Bônus Assinatura: {pat.get('nome', patrocinio_id)}",
            categoria="patrocinio",
        )

    salvar_jogo(nome_save, jogador)
    return {"ok": True, "mensagem": f"Contrato assinado com {pat.get('nome')}!"}
