from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from src.dados import carregar_patrocinadores, carregar_staff
from src.services.sponsorship_data import (
    _criar_meta,
    _duracao_contrato_semanas,
    _metas_contrato_ativo,
    _normalizar_contrato_ativo,
    _normalizar_ids_patrocinios,
    _normalizar_lista_patrocinios,
    _patrocinador_master_valido,
    _perfil_marca,
    _ranking_referencia,
    _status_contrato,
    _total_titulos_carreira,
    _total_vitorias_carreira,
    resolver_id_patrocinio,
)

# Re-exporta para compatibilidade com importadores externos
__all__ = [
    "resolver_id_patrocinio",
    "migrar_patrocinios",
    "pode_assinar_patrocinio",
    "processar_pagamentos_patrocinio",
    "assinar_patrocinio",
    "serializar_patrocinio_ativo",
    "listar_patrocinios_ativos",
    "listar_patrocinios_disponiveis",
    "resumir_contexto_patrocinio",
]

# Regras de Negócio
LIMITE_PATROCINIO_MASTER = 1
LIMITE_PATROCINIO_MENORES = 3


def _carregar_narrativa() -> dict:
    try:
        from pathlib import Path
        import json

        caminho = (
            Path(__file__).parent.parent.parent / "db" / "narrativa_patrocinio.json"
        )
        if caminho.exists():
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


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


def pode_assinar_patrocinio(
    jogador: Any, pat_id: str, posicao: int, seguidores: int = 0
) -> Tuple[bool, str]:
    """Valida se o jogador preenche os requisitos para um patrocinador."""
    sponsors = carregar_patrocinadores()
    pat = sponsors.get(pat_id)
    narrativa = _carregar_narrativa()
    bloqueios = narrativa.get("motivos_bloqueio", {})

    if not pat:
        return False, bloqueios.get("desconhecido", "Patrocinador desconhecido.")

    patrocinios_atuais = _normalizar_ids_patrocinios(
        _normalizar_lista_patrocinios(jogador), sponsors
    )
    if pat_id in patrocinios_atuais:
        return False, bloqueios.get("ja_tem", "Você já tem este patrocínio.")

    # 1. Exclusividade de Categoria (Realismo FM)
    cat_nova = pat.get("categoria")
    for item in patrocinios_atuais:
        p_id = item.get("id") if isinstance(item, dict) else item
        p_data = sponsors.get(p_id, {})
        if p_data.get("categoria") == cat_nova:
            return False, f"Conflito de categoria: você já tem um patrocinador de {cat_nova}."

    tier = pat.get("tier", "menor")
    if tier == "master" and not _patrocinador_master_valido(pat):
        return False, bloqueios.get(
            "master_categoria", "Patrocinador master deve ser de material esportivo."
        )

    if tier == "master":
        masters_ativos = [
            p for p in patrocinios_atuais if sponsors.get(p, {}).get("tier") == "master"
        ]
        if masters_ativos:
            nome_atual = sponsors.get(masters_ativos[0], {}).get("nome", "atual")
            msg = bloqueios.get("master_conflito", "Conflito com master atual.").format(
                brand=nome_atual
            )
            return False, msg
    else:
        menores_ativos = [
            p
            for p in patrocinios_atuais
            if sponsors.get(p, {}).get("tier", "menor") != "master"
        ]
        if len(menores_ativos) >= LIMITE_PATROCINIO_MENORES:
            msg = bloqueios.get("limite_menores", "Limite atingido.").format(
                limit=LIMITE_PATROCINIO_MENORES
            )
            return False, msg

    req_seg = pat.get("req_seguidores", 0)
    req_rank = pat.get("requisito_ranking", 9999)

    # Influência do Empresário (Networking)
    # Empresários de elite (4-5 estrelas) reduzem requisitos
    emp_contrato = getattr(jogador, "empresario", None)
    if isinstance(emp_contrato, dict):
        emp_id = emp_contrato.get("id")
        staff_data = carregar_staff()
        emp_data = staff_data.get("agents", {}).get(emp_id)
        if emp_data:
            estrelas = int(emp_data.get("estrelas", 1) or 1)
            if estrelas >= 4:
                # Reduz requisito de ranking em 15% e seguidores em 20%
                req_rank = int(req_rank * 1.15) # Ex: precisa ser top 100, aceita top 115
                req_seg = int(req_seg * 0.80)

    if posicao > req_rank:
        msg = bloqueios.get("ranking_insuficiente", "Ranking insuficiente.").format(
            rank=req_rank
        )
        return False, msg

    if req_seg > 0 and seguidores < req_seg:
        msg = bloqueios.get(
            "seguidores_insuficientes", "Seguidores insuficientes."
        ).format(followers=req_seg)
        return False, msg

    return True, "OK"


def processar_pagamentos_patrocinio(jogador: Any):
    """Executa o processamento semanal de receitas de patrocínio."""
    sponsors = carregar_patrocinadores()
    staff_data = carregar_staff()
    agents = staff_data.get("agents", {})
    narrativa = _carregar_narrativa()
    trans = narrativa.get("transacoes", {})

    contratos_normalizados: List[Dict[str, Any]] = []
    for item in _normalizar_lista_patrocinios(jogador):
        contrato = _normalizar_contrato_ativo(item, jogador, None, sponsors)
        if contrato:
            contratos_normalizados.append(contrato)
    jogador.patrocinios = contratos_normalizados

    # 2. Cláusula de Inatividade (Realismo FM)
    # Se não joga há 3 semanas, corta pagamento pela metade
    semanas_sem_jogar = getattr(jogador, "semanas_sem_jogar", 0)
    penalidade_inatividade = 0.5 if semanas_sem_jogar >= 3 else 1.0

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

    contratos_renovados: List[Dict[str, Any]] = []
    for contrato in contratos_normalizados:
        pat_id = contrato.get("id")
        pat = sponsors.get(pat_id)
        if pat:
            # 3. Motor de Confiança da Marca
            satisfacao = contrato.get("satisfacao", 80)
            if semanas_sem_jogar > 0:
                satisfacao = max(0, satisfacao - (2 * semanas_sem_jogar))

            valor_bruto = int(pat.get("pagamento_semanal", 0) or 0)
            valor_bruto = int(valor_bruto * penalidade_inatividade)
            
            # 4. Valorização por Ranking (Renegociação Automática)
            req_rank = pat.get("requisito_ranking", 500)
            ranking_atual = getattr(jogador, "ranking_pos", 999) or 999
            if ranking_atual < (req_rank / 2): # Melhorou o ranking pela metade do requisito
                ajuste_valorizacao = 1.25 # +25% de valorização por estar voando
                valor_bruto = int(valor_bruto * ajuste_valorizacao)

            bonus_valor = int(valor_bruto * bonus_emp)
            valor_com_bonus = valor_bruto + bonus_valor

            valor_comissao = int(valor_com_bonus * comissao_pct)
            valor_liquido = valor_com_bonus - valor_comissao

            desc = trans.get("pagamento_semanal", "Patrocínio: {brand}").format(
                brand=pat["nome"]
            )
            if bonus_emp > 0:
                desc += trans.get("bonus_empresario", " (+{percent}% bônus)").format(
                    percent=int(bonus_emp * 100)
                )
            if comissao_pct > 0:
                desc += trans.get(
                    "comissao_empresario", " (-{percent}% comissão {agent})"
                ).format(percent=int(comissao_pct * 100), agent=emp_nome)

            jogador.registrar_transacao(valor_liquido, desc, categoria="patrocinio")
            
            # 5. Bônus Escalonado por Rodada (Realismo FM)
            ultimo_torneio = (jogador.historico_torneios[-1] if jogador.historico_torneios else {})
            fase = ultimo_torneio.get("fase", "")
            if fase:
                mult_fase = 0
                if fase == "campeao": mult_fase = 1.0
                elif fase == "final": mult_fase = 0.6
                elif fase == "semifinal": mult_fase = 0.4
                elif fase == "quartas": mult_fase = 0.2
                
                if mult_fase > 0:
                    tier_torneio = ultimo_torneio.get("tipo", "")
                    mult_tier = {"Grand Slam": 5, "ATP 1000": 3, "ATP 500": 2}.get(tier_torneio, 1)
                    bonus_total = int(pat.get("pagamento_semanal", 0) * mult_tier * mult_fase)
                    if bonus_total > 0:
                        satisfacao = min(100, satisfacao + 5)
                        desc_bt = f"Bônus de Performance ({fase}): {pat['nome']}"
                        jogador.registrar_transacao(bonus_total, desc_bt, categoria="patrocinio")

            semanas_restantes = max(0, int(contrato.get("semanas_restantes", 0) or 0) - 1)
            contrato["satisfacao"] = satisfacao

            # 6. Renovação Proativa (Realismo FM)
            if semanas_restantes <= 3 and satisfacao >= 80:
                if not any(e.get("id") == f"renew_{pat_id}" for e in jogador.caixa_email):
                    jogador.caixa_email.append({
                        "id": f"renew_{pat_id}",
                        "remetente": pat["nome"],
                        "assunto": "Proposta de Extensão de Contrato",
                        "texto": f"Estamos muito felizes com nossa parceria. Gostaríamos de estender seu contrato por mais {contrato['duracao_semanas']} semanas!",
                        "tipo": "patrocinio",
                        "ref_id": pat_id,
                        "status": "pendente",
                        "lido": False
                    })

            if semanas_restantes > 0:
                contrato["semanas_restantes"] = semanas_restantes
                contratos_renovados.append(contrato)
            else:
                # Narrativa de Fim de Contrato
                jogador.caixa_email.append({
                    "id": f"end_{pat_id}",
                    "remetente": pat.get("nome", "Patrocinador"),
                    "assunto": "Encerramento de Ciclo",
                    "texto": f"Nosso contrato chegou ao fim. Foi um prazer apoiar sua carreira até aqui!",
                    "tipo": "notificacao",
                    "lido": False
                })

    jogador.patrocinios = contratos_renovados


def serializar_patrocinio_ativo(
    item: Any,
    jogador: Any,
    posicao: Optional[int],
    sponsors: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Converte um contrato ativo em payload pronto para API."""
    if sponsors is None:
        sponsors = carregar_patrocinadores()
    contrato = _normalizar_contrato_ativo(item, jogador, posicao, sponsors)
    if not contrato:
        return None
    pat_id = contrato["id"]
    patrocinador = sponsors.get(pat_id)
    if not patrocinador:
        return None
    metas = _metas_contrato_ativo(contrato, patrocinador, jogador, posicao)
    status, confianca = _status_contrato(metas)

    return {
        "id": pat_id,
        "nome": patrocinador.get("nome", str(pat_id)),
        "categoria": patrocinador.get("categoria", ""),
        "nivel": patrocinador.get("tier", "menor"),
        "valor": int(patrocinador.get("pagamento_semanal", 0) or 0),
        "semanas_restantes": int(contrato.get("semanas_restantes", 0) or 0),
        "duracao_semanas": int(contrato.get("duracao_semanas", 0) or 0),
        "perfil": _perfil_marca(patrocinador),
        "status": status,
        "confianca": confianca,
        "metas": metas,
    }


def listar_patrocinios_ativos(
    jogador: Any,
    posicao: Optional[int] = None,
    sponsors: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Lista contratos de patrocínio ativos já serializados."""
    if sponsors is None:
        sponsors = carregar_patrocinadores()

    ativos: List[Dict[str, Any]] = []
    for item in _normalizar_lista_patrocinios(jogador):
        payload = serializar_patrocinio_ativo(item, jogador, posicao, sponsors)
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
                "bonus_assinatura": int(patrocinador.get("bonus_assinatura", 0) or 0),
                "requisito_ranking": int(patrocinador.get("requisito_ranking", 0) or 0),
                "requisito_seguidores": int(patrocinador.get("req_seguidores", 0) or 0),
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

    ativos = listar_patrocinios_ativos(jogador, posicao, sponsors)
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


def assinar_patrocinio(
    nome_save: str,
    jogador: Any,
    patrocinio_id: str,
    posicao: int,
) -> dict:
    """Valida e registra a assinatura de um patrocínio, salvando o jogador."""
    from src.save import salvar_jogo

    sponsors = carregar_patrocinadores()
    pode, motivo = pode_assinar_patrocinio(
        jogador, patrocinio_id, posicao, getattr(jogador, "seguidores", 0)
    )
    if not pode:
        return {"ok": False, "mensagem": motivo}

    pat = sponsors.get(patrocinio_id)
    if not pat:
        return {"ok": False, "mensagem": "Patrocinador não encontrado.", "status": 404}

    jogador.patrocinios.append(
        {
            "id": patrocinio_id,
            "semanas_restantes": _duracao_contrato_semanas(pat),
            "duracao_semanas": _duracao_contrato_semanas(pat),
            "ranking_assinatura": _ranking_referencia(jogador, posicao),
            "seguidores_assinatura": int(getattr(jogador, "seguidores", 0) or 0),
            "vitorias_assinatura": _total_vitorias_carreira(jogador),
            "titulos_assinatura": _total_titulos_carreira(jogador),
        }
    )

    narrativa = _carregar_narrativa()
    trans = narrativa.get("transacoes", {})
    avisos = narrativa.get("avisos", {})

    bonus = int(pat.get("bonus_assinatura", 0) or 0)
    if bonus > 0:
        desc_bonus = trans.get("bonus_assinatura", "Bônus Assinatura: {brand}").format(
            brand=pat.get("nome", patrocinio_id)
        )
        jogador.registrar_transacao(
            bonus,
            desc_bonus,
            categoria="patrocinio",
        )

    salvar_jogo(nome_save, jogador)
    msg_sucesso = avisos.get(
        "contrato_assinado", "Contrato assinado com {brand}!"
    ).format(brand=pat.get("nome"))
    return {"ok": True, "mensagem": msg_sucesso}
