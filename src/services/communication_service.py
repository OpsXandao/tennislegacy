from __future__ import annotations
import random
from typing import Dict, Any, List, Tuple, Optional
from src.dados import carregar_patrocinadores, carregar_staff
from src.services.sponsorship_service import pode_assinar_patrocinio


def gerar_propostas_carreira_email(jogador: Any, ranking: Any):
    gerar_proposta_patrocinio(jogador, ranking)
    gerar_proposta_empresario(jogador, ranking)
    gerar_convite_duplas_inbound(jogador, ranking)


def gerar_convite_duplas_inbound(jogador: Any, ranking: Any):
    """Gera convite de parceria de duplas vindo de um NPC."""
    from src.duplas import buscar_parceiros_disponiveis

    # Chance base de 10% por semana
    if random.random() > 0.12:
        return

    vinculos = getattr(jogador, "vinculos_dupla", {})
    parceiros = buscar_parceiros_disponiveis(jogador, ranking.ranking, n=5, vinculos=vinculos)
    
    if not parceiros:
        return

    # Escolhe um parceiro da lista (mais chance para quem tem vínculo)
    parceiro = random.choice(parceiros)
    
    # Evita duplicatas na caixa de entrada
    pendentes_nomes = {
        p.get("ref_id")
        for p in getattr(jogador, "caixa_email", [])
        if isinstance(p, dict) and p.get("tipo") == "convite_duplas" and p.get("status") == "pendente"
    }
    if parceiro["nome"] in pendentes_nomes:
        return

    # Carrega mensagens do JSON
    try:
        from pathlib import Path
        import json
        caminho = Path(__file__).parent.parent.parent / "db" / "narrativa_duplas.json"
        with open(caminho, "r", encoding="utf-8") as f:
            narrativa = json.load(f)
        mensagens = narrativa.get("convites", [
            f"Vi seu desempenho recente e acho que formaríamos uma ótima dupla. O que acha?",
            f"Estou procurando um parceiro para os próximos torneios e seu estilo combina com o meu.",
            f"Bora dominar o circuito de duplas juntos? Aceita o convite?",
        ])
    except Exception:
        mensagens = [f"Bora formar uma dupla para o próximo torneio?"]

    proposta = {
        "tipo": "convite_duplas",
        "status": "pendente",
        "ref_id": parceiro["nome"],
        "titulo": f"Convite de Parceria: {parceiro['nome']}",
        "mensagem": random.choice(mensagens),
        "oferta": {
            "nome": parceiro["nome"],
            "nacionalidade": parceiro["nacionalidade"],
            "overall": parceiro["overall"],
            "estilo_jogo": parceiro.get("estilo_jogo", "All-court")
        },
    }
    
    if not hasattr(jogador, "caixa_email") or not isinstance(jogador.caixa_email, list):
        jogador.caixa_email = []
    jogador.caixa_email.append(proposta)


def gerar_convites_midia_email(jogador: Any, ranking: Any):
    """Fluxo aposentado no frontend+backend atual; mantido como no-op explícito."""
    return None

def _carregar_narrativa_patrocinio() -> dict:
    try:
        from pathlib import Path
        import json
        caminho = Path(__file__).parent.parent.parent / "db" / "narrativa_patrocinio.json"
        if caminho.exists():
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def gerar_proposta_patrocinio(jogador: Any, ranking: Any):
    """Gera proposta de patrocínio e entrega na caixa de e-mail do jogador."""
    sponsors = carregar_patrocinadores()
    staff_data = carregar_staff()
    agents = staff_data.get("agents", {})
    narrativa = _carregar_narrativa_patrocinio()
    templates = narrativa.get("email_templates", {}).get("patrocinio", {})
    
    posicao = ranking.obter_posicao(jogador.nome) or 9999
    seguidores = getattr(jogador, "seguidores", 0)
    
    emp_bonus = 0.0
    emp_estrelas = 1
    emp_contrato = getattr(jogador, "empresario", None)
    if isinstance(emp_contrato, dict):
        emp_id = emp_contrato.get("id")
        emp = agents.get(emp_id, {})
        emp_bonus = float(emp.get("bonus_patrocinio", 0.0) or 0.0)
        emp_estrelas = int(emp.get("estrelas", 1) or 1)

    # Chance de inbound
    chance = 0.20 + (emp_bonus * 0.9)
    if posicao <= 500: chance += 0.08
    if posicao <= 100: chance += 0.07
    if seguidores >= 10000: chance += 0.05
    chance = max(0.15, min(0.60, chance))
    
    if random.random() > chance:
        return

    pendentes_ids = {
        p.get("ref_id")
        for p in getattr(jogador, "caixa_email", [])
        if isinstance(p, dict) and p.get("tipo") == "patrocinio" and p.get("status") == "pendente"
    }
    
    pos_efetiva = min(posicao, 2000)
    candidatos = []
    for pat_id, pat in sponsors.items():
        pode, _ = pode_assinar_patrocinio(jogador, pat_id, pos_efetiva, seguidores)
        if not pode or pat_id in pendentes_ids:
            continue
        
        tier = pat.get("tier", "menor")
        score = 1.0
        score += min(3.0, max(0.0, (150 - min(posicao, 150)) / 70.0))
        score += min(2.0, seguidores / 80000.0)
        if tier == "master":
            score += max(0.2, (emp_estrelas - 1) * 0.85)
        
        score += (pat.get("pagamento_semanal", 0) / 1000.0) * (0.35 + emp_bonus)
        candidatos.append((pat_id, pat, max(0.2, score)))

    if not candidatos:
        return

    pesos = [c[2] for c in candidatos]
    escolhido = random.choices(candidatos, weights=pesos, k=1)[0]
    pat_id, pat, _ = escolhido

    brand_name = pat.get('nome', pat_id)
    titulo = templates.get("titulo", "Proposta: {brand}").format(brand=brand_name)
    mensagem = templates.get("corpo", "{brand} proposta.").format(
        brand=brand_name,
        weekly=pat.get('pagamento_semanal', 0),
        signing=pat.get('bonus_assinatura', 0)
    )

    proposta = {
        "tipo": "patrocinio",
        "status": "pendente",
        "ref_id": pat_id,
        "titulo": titulo,
        "mensagem": mensagem,
        "oferta": {
            "pagamento_semanal": int(pat.get("pagamento_semanal", 0) or 0),
            "bonus_assinatura": int(pat.get("bonus_assinatura", 0) or 0),
            "bonus_titulo": int(pat.get("bonus_titulo", 0) or 0),
            "categoria": pat.get("categoria", ""),
            "tier": pat.get("tier", "menor"),
        },
    }
    if not hasattr(jogador, "caixa_email") or not isinstance(jogador.caixa_email, list):
        jogador.caixa_email = []
    jogador.caixa_email.append(proposta)

def gerar_proposta_empresario(jogador: Any, ranking: Any):
    """Gera proposta inbound de empresário para a caixa de e-mail."""
    staff_data = carregar_staff()
    agents = staff_data.get("agents", {})
    narrativa = _carregar_narrativa_patrocinio()
    templates = narrativa.get("email_templates", {}).get("empresario", {})
    
    posicao = ranking.obter_posicao(jogador.nome) or 9999
    seguidores = int(getattr(jogador, "seguidores", 0) or 0)

    chance = 0.05
    if posicao <= 250: chance += 0.05
    if seguidores >= 20000: chance += 0.04
    chance = max(0.04, min(0.24, chance))
    
    if random.random() > chance:
        return

    pendentes_ids = {
        p.get("ref_id")
        for p in getattr(jogador, "caixa_email", [])
        if isinstance(p, dict) and p.get("tipo") == "empresario" and p.get("status") == "pendente"
    }
    
    emp_atual = getattr(jogador, "empresario", None)
    id_atual = emp_atual.get("id") if isinstance(emp_atual, dict) else None

    candidatos = []
    for emp_id, emp in agents.items():
        if emp_id in pendentes_ids or emp_id == id_atual:
            continue
        
        estrelas = int(emp.get("estrelas", 1) or 1)
        score = 1.0 + (6 - max(1, min(posicao, 600)) / 120.0)
        score += estrelas * 0.55
        
        desconto = 1.0 - min(0.12, max(0.0, (estrelas - 2) * 0.04))
        salario_oferta = int(round(emp.get("salario_semanal", 0) * desconto))
        candidatos.append((emp_id, emp, max(0.25, score), salario_oferta))

    if not candidatos:
        return

    escolhido = random.choices(candidatos, weights=[c[2] for c in candidatos], k=1)[0]
    emp_id, emp, _, salario_oferta = escolhido
    
    agent_name = emp.get('nome', emp_id)
    titulo = templates.get("titulo", "Proposta Agente").format(name=agent_name)
    mensagem = templates.get("corpo", "{name} oferta").format(
        name=agent_name,
        salary=salario_oferta,
        weeks=26
    )

    proposta = {
        "tipo": "empresario",
        "status": "pendente",
        "ref_id": emp_id,
        "titulo": titulo,
        "mensagem": mensagem,
        "oferta": {
            "salario_semanal": int(max(50, salario_oferta)),
            "duracao_semanas": 26,
            "max_equipe": int(emp.get("max_equipe", 2) or 2),
            "bonus_patrocinio": float(emp.get("bonus_patrocinio", 0.0) or 0.0),
            "estrelas": int(emp.get("estrelas", 1) or 1),
        },
    }
    if not hasattr(jogador, "caixa_email") or not isinstance(jogador.caixa_email, list):
        jogador.caixa_email = []
    jogador.caixa_email.append(proposta)

def processar_acao_email(jogador: Any, proposta: dict, acao: str, ranking: Any) -> Tuple[bool, str]:
    """Processa aceitar/recusar em propostas de e-mail."""
    if proposta.get("status") != "pendente":
        return False, "Esta proposta já foi processada."
    
    if acao not in {"aceitar", "recusar"}:
        return False, "Ação inválida."
        
    if acao == "recusar":
        proposta["status"] = "recusada"
        return True, "Proposta recusada."

    tipo = proposta.get("tipo")
    
    if tipo == "patrocinio":
        from src.services.sponsorship_service import pode_assinar_patrocinio
        pat_id = proposta.get("ref_id")
        posicao = ranking.obter_posicao(jogador.nome) or 9999
        seguidores = int(getattr(jogador, "seguidores", 0) or 0)
        
        pode, motivo = pode_assinar_patrocinio(jogador, pat_id, posicao, seguidores)
        if not pode: return False, motivo
        
        if not hasattr(jogador, "patrocinios"): jogador.patrocinios = []
        jogador.patrocinios.append(pat_id)
        
        oferta = proposta.get("oferta", {})
        bonus = oferta.get("bonus_assinatura", 0)
        if bonus > 0:
            jogador.registrar_transacao(bonus, f"Bônus Assinatura: {proposta['titulo']}", categoria="patrocinio")
            
        proposta["status"] = "aceita"
        return True, "Contrato assinado com sucesso."

    if tipo == "empresario":
        emp_id = proposta.get("ref_id")
        oferta = proposta.get("oferta", {})
        
        # Rescisão do anterior se houver
        emp_atual = getattr(jogador, "empresario", None)
        if isinstance(emp_atual, dict):
            multa = max(0, (emp_atual.get("salario", 0) // 2) * emp_atual.get("semanas_restantes", 0))
            if multa > 0:
                jogador.registrar_transacao(-multa, "Rescisão empresário anterior", categoria="equipe")
        
        jogador.empresario = {
            "id": emp_id,
            "semanas_restantes": oferta.get("duracao_semanas", 26),
            "salario": oferta.get("salario_semanal", 0),
        }
        proposta["status"] = "aceita"
        return True, "Novo empresário contratado."

    if tipo == "convite_duplas":
        oferta = proposta.get("oferta", {})
        jogador.parceiro_duplas = {
            "nome": oferta.get("nome"),
            "nacionalidade": oferta.get("nacionalidade")
        }
        proposta["status"] = "aceita"
        return True, f"Parceria com {oferta.get('nome')} iniciada!"

    return False, "Tipo de proposta desconhecido."


def _email_id_matches(email: dict, email_id: str) -> bool:
    return email.get("id") == email_id or email.get("ref_id") == email_id


def marcar_emails_lidos(nome_save: str, jogador: Any) -> bool:
    """Marca todos os emails como lidos e salva se houve mudança."""
    from src.save import salvar_jogo

    caixa = getattr(jogador, "caixa_email", [])
    houve_mudanca = False
    for email in caixa:
        if not email.get("lido"):
            email["lido"] = True
            houve_mudanca = True
    if houve_mudanca:
        salvar_jogo(nome_save, jogador)
    return houve_mudanca


def marcar_email_especifico_lido(nome_save: str, jogador: Any, email_id: str) -> bool:
    """Marca um email específico como lido."""
    from src.save import salvar_jogo

    caixa = getattr(jogador, "caixa_email", [])
    for email in caixa:
        if _email_id_matches(email, email_id):
            if not email.get("lido"):
                email["lido"] = True
                salvar_jogo(nome_save, jogador)
                return True
            break
    return False


def remover_email(nome_save: str, jogador: Any, email_id: str) -> dict:
    """Remove um email da caixa de entrada e salva."""
    from src.save import salvar_jogo

    caixa = getattr(jogador, "caixa_email", [])
    proposta = next((p for p in caixa if _email_id_matches(p, email_id)), None)
    if not proposta:
        return {"ok": False, "status": 404, "mensagem": "E-mail não encontrado."}
    jogador.caixa_email = [p for p in caixa if not _email_id_matches(p, email_id)]
    salvar_jogo(nome_save, jogador)
    return {"ok": True, "mensagem": "E-mail removido."}


def aceitar_email(nome_save: str, jogador: Any, email_id: str, ranking: Any) -> dict:
    """Aceita um email, processa sua ação e salva."""
    from src.save import salvar_jogo

    caixa = getattr(jogador, "caixa_email", [])
    proposta = next((p for p in caixa if _email_id_matches(p, email_id)), None)
    if not proposta:
        return {"ok": False, "status": 404, "mensagem": "E-mail não encontrado."}
    sucesso, msg = processar_acao_email(jogador, proposta, "aceitar", ranking)
    if sucesso:
        jogador.caixa_email = [p for p in caixa if not _email_id_matches(p, email_id)]
        salvar_jogo(nome_save, jogador)
        return {"ok": True, "mensagem": msg}
    return {"ok": False, "status": 400, "mensagem": msg}
