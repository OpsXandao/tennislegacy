from __future__ import annotations

import random
from typing import Any, List, Dict

from src.constants.staff_constants import PROFISSIONAIS_DISPONIVEIS


class StaffAdviceService:
    """
    Simulates proactive advice from the player's staff (FM-style).
    Generates emails/notifications based on game state.
    """

    @staticmethod
    def generate_weekly_advice(jogador: Any) -> List[Dict[str, Any]]:
        """Gera conselhos dos profissionais da equipe."""
        conselhos = []
        equipe = getattr(jogador, "equipe", [])
        
        for contrato in equipe:
            prof_id = contrato.get("id")
            info = PROFISSIONAIS_DISPONIVEIS.get(prof_id)
            if not info:
                continue
            
            cat = info.get("categoria")
            # Chance de dar conselho baseada nas estrelas (profissionais melhores falam mais/melhor)
            estrelas = info.get("estrelas", 1)
            chance = 0.05 + (estrelas * 0.05) # 10% a 30% de chance por semana
            
            if random.random() < chance:
                conselho = StaffAdviceService._get_advice_by_category(jogador, cat, info)
                if conselho:
                    conselhos.append(conselho)
        
        return conselhos

    @staticmethod
    def _get_advice_by_category(jogador: Any, categoria: str, info: dict) -> Dict[str, Any] | None:
        nome = info.get("nome", "Treinador")
        
        if categoria == "treinador":
            # Conselhos táticos ou de treino
            if jogador.energia < 50:
                msg = f"Notei que você está forçando demais o corpo. Sugiro uma semana de descanso ou treino leve para evitar lesões."
            else:
                pior_attr = min(jogador.atributos, key=jogador.atributos.get)
                msg = f"Seu {pior_attr} está abaixo do nível do circuito. Deveríamos focar nisso no próximo treino técnico."
            
            return StaffAdviceService._build_email(nome, "Sugestão Técnica", msg)

        if categoria == "fisioterapeuta":
            if jogador.fadiga > 40:
                msg = f"Sua fadiga acumulada está em níveis críticos ({int(jogador.fadiga)}%). Se não parar agora, o risco de uma lesão séria é de mais de 30%."
                return StaffAdviceService._build_email(nome, "Alerta de Saúde", msg)

        if categoria == "psicologo":
            if jogador.moral < 50:
                msg = f"Sua confiança parece abalada após os últimos resultados. Vamos focar em resiliência mental na próxima sessão?"
                return StaffAdviceService._build_email(nome, "Suporte Psicológico", msg)

        if categoria == "marketing":
            if jogador.seguidores < 5000:
                msg = f"Precisamos de uma vitória expressiva para engajar suas redes sociais. O público gosta de superação!"
                return StaffAdviceService._build_email(nome, "Estratégia de Imagem", msg)

        return None

    @staticmethod
    def _build_email(remetente: str, assunto: str, texto: str) -> Dict[str, Any]:
        return {
            "id": f"advice_{random.randint(1000, 9999)}",
            "remetente": remetente,
            "assunto": assunto,
            "texto": texto,
            "tipo": "notificacao",
            "lido": False
        }


def processar_satisfacao_staff(jogador: Any) -> List[str]:
    """
    Ajusta a satisfação da equipe baseado em:
    - Salário (se houver dívida, cai muito)
    - Resultados (vencer mantém, perder cai levemente)
    - Tempo de contrato
    """
    eventos = []
    equipe = getattr(jogador, "equipe", [])
    
    for contrato in equipe:
        # Inicializa satisfação se não existir
        if "satisfacao" not in contrato:
            contrato["satisfacao"] = 80
            
        # Impacto de Salário
        if jogador.dinheiro < 0:
            contrato["satisfacao"] = max(0, contrato["satisfacao"] - 15)
            if contrato["satisfacao"] < 30:
                eventos.append(f"ALERTA: {contrato.get('id')} está insatisfeito com os atrasos salariais.")
        
        # Impacto de Resultados (Vê se teve derrota pesada na semana)
        # Por enquanto, manutenção leve
        contrato["satisfacao"] = max(0, min(100, contrato["satisfacao"] + random.randint(-2, 2)))

        # Risco de Demissão Mútua (Poaching/Quitting)
        if contrato["satisfacao"] < 15:
            if random.random() < 0.4:
                # O profissional pede demissão
                prof_id = contrato.get("id")
                jogador.equipe = [c for c in jogador.equipe if c.get("id") != prof_id]
                eventos.append(f"DEMISSÃO: {prof_id} não acredita mais no projeto e pediu demissão imediata.")
                
    return eventos
