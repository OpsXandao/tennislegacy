from __future__ import annotations
import random
from typing import Any, List, Tuple, Dict, Optional
from src.dados import carregar_doencas

# Constantes de Recuperação
FADIGA_RECUPERACAO_SEMANAL = 30
ENERGIA_RECUPERACAO_SEMANAL_BASE = 18
ENERGIA_RECUPERACAO_SEMANAL_POR_FISICO = 0.5

STATUS_DOENCA_PADRAO = {
    "doente": False,
    "tipo": None,
    "nivel": "saudavel",
    "semanas_restantes": 0,
    "penalidade_atributos": 0.0,
    "penalidade_recuperacao_energia": 0.0,
}

STATUS_LESAO_PADRAO = {
    "lesionado": False,
    "semanas_restantes": 0,
    "nivel": "saudavel",
    "penalidade_atributos": 0.0,
}

def _get_val(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

def _set_val(obj: Any, key: str, val: Any):
    if isinstance(obj, dict):
        obj[key] = val
    else:
        setattr(obj, key, val)

def normalizar_status_doenca(status: Dict[str, Any]) -> Dict[str, Any]:
    """Garante que o dicionário de status de doença tenha todos os campos necessários."""
    status = status if isinstance(status, dict) else {}
    normalizado = STATUS_DOENCA_PADRAO.copy()
    normalizado.update(status)
    
    if not normalizado.get("doente"):
        for key in ["tipo", "nivel", "semanas_restantes", "penalidade_atributos", "penalidade_recuperacao_energia"]:
            normalizado[key] = STATUS_DOENCA_PADRAO[key]
    else:
        normalizado["semanas_restantes"] = max(1, int(normalizado.get("semanas_restantes", 1)))
    
    return normalizado

def normalizar_status_lesao(status: Dict[str, Any]) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else {}
    normalizado = STATUS_LESAO_PADRAO.copy()
    normalizado.update(status)
    return normalizado

def chance_doenca(entidade: Any, info_torneio: Optional[Dict[str, Any]] = None) -> float:
    """Calcula a probabilidade da entidade (Jogador ou NPC) ficar doente."""
    base = 0.03
    fadiga = int(_get_val(entidade, "fadiga", 0) or 0)
    energia = int(_get_val(entidade, "energia", 100) or 100)
    
    base += max(0.0, (fadiga - 40) / 600.0)
    base += max(0.0, (55 - energia) / 650.0)
    
    if info_torneio:
        base += 0.02
        
    return max(0.01, min(0.20, base))

def processar_recuperacao_semanal(entidade: Any, eventos: Optional[List[str]] = None, info_torneio: Optional[Dict[str, Any]] = None):
    """
    Processa a recuperação física semanal de uma entidade (Jogador ou NPC).
    Lida com Fadiga, Energia, Doença e Lesão.
    """
    # 1. Recuperação de Fadiga
    fadiga_atual = int(_get_val(entidade, "fadiga", 0) or 0)
    nova_fadiga = max(0, fadiga_atual - FADIGA_RECUPERACAO_SEMANAL)
    _set_val(entidade, "fadiga", nova_fadiga)

    # 2. Recuperação de Energia
    attrs = _get_val(entidade, "atributos", {})
    fisico = attrs.get("fisico", 50) if isinstance(attrs, dict) else 50
    
    rec_energia = int(round(ENERGIA_RECUPERACAO_SEMANAL_BASE + fisico * ENERGIA_RECUPERACAO_SEMANAL_POR_FISICO))
    
    status_doenca = normalizar_status_doenca(_get_val(entidade, "status_doenca", {}))
    penalidade_rec = float(status_doenca.get("penalidade_recuperacao_energia", 0.0))
    if penalidade_rec > 0:
        rec_energia = int(round(rec_energia * max(0.4, 1.0 - penalidade_rec)))

    if nova_fadiga <= 20:
        rec_energia += int(round((20 - nova_fadiga) * 0.5))
    elif nova_fadiga >= 70:
        rec_energia = int(round(rec_energia * 0.88))

    energia_antes = int(_get_val(entidade, "energia", 100) or 100)
    nova_energia = min(100, energia_antes + rec_energia)
    
    # Lógica de piso mínimo
    status_lesao = normalizar_status_lesao(_get_val(entidade, "status_lesao", {}))
    lesionado = bool(status_lesao.get("lesionado")) or status_lesao.get("nivel") in ("limitado", "desconforto")
    doente = bool(status_doenca.get("doente"))

    if nova_fadiga <= 20 and not lesionado and not doente:
        nova_energia = max(nova_energia, 78)
    if nova_fadiga <= 0 and not lesionado and not doente:
        nova_energia = max(nova_energia, 92)
        
    _set_val(entidade, "energia", nova_energia)

    if eventos is not None and not isinstance(entidade, dict): # Apenas para o jogador humano
        eventos.append(f"😌 Energia recuperada: {energia_antes}% -> {nova_energia}%.")

    # 3. Evolução da Doença
    if doente:
        status_doenca["semanas_restantes"] -= 1
        if status_doenca["semanas_restantes"] <= 0:
            status_doenca = normalizar_status_doenca({"doente": False})
            if eventos is not None: eventos.append("✅ Você se recuperou da doença!")
    _set_val(entidade, "status_doenca", status_doenca)

    # 4. Evolução da Lesão
    if status_lesao.get("semanas_restantes", 0) > 0:
        status_lesao["semanas_restantes"] -= 1
        if status_lesao["semanas_restantes"] <= 0:
            if status_lesao.get("lesionado"):
                status_lesao.update({"lesionado": False, "nivel": "desconforto", "penalidade_atributos": 0.06})
                if eventos is not None: eventos.append("🩹 Sua lesão melhorou, mas você ainda sente desconforto.")
            else:
                status_lesao.update({"nivel": "saudavel", "penalidade_atributos": 0.0})
                if eventos is not None: eventos.append("💪 Você está totalmente recuperado da lesão!")
    _set_val(entidade, "status_lesao", status_lesao)

    # 5. Moral (NPCs apenas)
    if isinstance(entidade, dict):
        moral_atual = int(entidade.get("moral", 70) or 70)
        # Tende ao equilíbrio (70)
        if moral_atual > 70: moral_atual -= 2
        elif moral_atual < 70: moral_atual += 2
        
        if nova_fadiga >= 80: moral_atual -= 3
        elif nova_fadiga <= 30: moral_atual += 1
        entidade["moral"] = max(0, min(100, moral_atual))

def tentar_doenca_semanal(entidade: Any, info_torneio: Optional[Dict[str, Any]] = None) -> List[str]:
    """Tenta aplicar doença à entidade e retorna eventos se houver."""
    eventos = []
    status_doenca = normalizar_status_doenca(_get_val(entidade, "status_doenca", {}))
    
    if status_doenca.get("doente"):
        return eventos

    if random.random() > chance_doenca(entidade, info_torneio):
        return eventos

    diseases = carregar_doencas()
    tipo = random.choices(list(diseases.keys()), weights=[d["peso"] for d in diseases.values()], k=1)[0]
    cfg = diseases[tipo]
    
    status_doenca.update({
        "doente": True,
        "tipo": tipo,
        "semanas_restantes": random.randint(cfg["duracao"][0], cfg["duracao"][1]),
        "penalidade_atributos": cfg["penalidade_atributos"],
        "penalidade_recuperacao_energia": cfg["penalidade_energia"],
    })
    _set_val(entidade, "status_doenca", status_doenca)
    
    # Impacto imediato
    energia = int(_get_val(entidade, "energia", 100))
    _set_val(entidade, "energia", max(0, energia - int(round(12 + cfg["penalidade_energia"] * 30))))
    _set_val(entidade, "fadiga", min(100, int(_get_val(entidade, "fadiga", 0)) + 8))
    
    msg = f"🤒 Ficou doente ({tipo})."
    eventos.append(msg)
    return eventos
