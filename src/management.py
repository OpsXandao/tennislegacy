from src.services.staff_service import (
    processar_pagamentos_equipe as _pay_staff,
    atualizar_contratos_staff as _update_staff,
    obter_limite_equipe as _get_limit,
    obter_detalhes_profissional
)
from src.constants.staff_constants import PROFISSIONAIS_DISPONIVEIS, EMPRESARIOS_DISPONIVEIS

# === HELPERS ===

def obter_profissional_da_equipe(equipe, categoria):
    """Retorna o dict do profissional de dada categoria na equipe, ou None."""
    for contrato in equipe:
        prof_id = contrato.get("id") if isinstance(contrato, dict) else contrato
        prof = obter_detalhes_profissional(prof_id)
        if prof and prof.get("categoria") == categoria:
            return prof
    return None


# === FUNCOES DE GESTAO SEMANAL (DELEGATED) ===

def processar_gastos_equipe(jogador, return_eventos: bool = False):
    eventos = _pay_staff(jogador)
    if jogador.dinheiro < 0:
        eventos.append({
            "tipo": "saldo_negativo",
            "mensagem": f"Atencao! Voce esta com saldo negativo: ${jogador.dinheiro:,}",
            "saldo": jogador.dinheiro,
        })
    return eventos if return_eventos else None


def processar_expiracoes_contratos(jogador, return_eventos: bool = False):
    eventos = _update_staff(jogador)
    return eventos if return_eventos else None


def obter_max_equipe(jogador):
    return _get_limit(jogador)


def processar_despesas_operacionais(jogador, temporada=None, info_torneio=None):

    """Despesas operacionais semanais (viagens, hospedagem, etc.)."""
    from src.dados import carregar_estado_torneio

    estado = carregar_estado_torneio(jogador.save_name, genero=jogador.genero)

    esta_jogando = False
    if estado and estado.get("torneio") == (
        info_torneio.get("nome") if info_torneio else None
    ):
        # Jogador só paga viagem se jogou ou está inscrito (não foi eliminado ANTES da semana começar)
        esta_jogando = True

    if info_torneio and esta_jogando:
        tipo = info_torneio.get("tipo", "")
        # Custos escalonados por nível de torneio (incluindo WTA)
        custos = {
            "Grand Slam": 450,
            "ATP 1000": 300,
            "WTA 1000": 300,
            "ATP 500": 180,
            "WTA 500": 180,
            "ATP 250": 100,
            "WTA 250": 100,
            "Davis Cup": 150,
            "Billie Jean King Cup": 150,
            "United Cup": 150,
        }
        custo = custos.get(tipo, 80)
        jogador.registrar_transacao(
            -custo,
            f"Despesas: viagem {info_torneio.get('nome', tipo)}",
            categoria="operacional",
        )
    elif not esta_jogando:
        # Custo de manutenção básica (moradia, alimentação em casa)
        jogador.registrar_transacao(
            -40, "Despesas: manutenção básica (folga)", categoria="operacional"
        )

    # Salario do empresario
    emp_contrato = getattr(jogador, "empresario", None)
    if isinstance(emp_contrato, dict):
        emp_id = emp_contrato.get("id")
        emp_data = EMPRESARIOS_DISPONIVEIS.get(emp_id)
        if emp_data:
            salario = emp_contrato.get("salario", emp_data["salario_semanal"])
            jogador.registrar_transacao(
                -salario,
                f"Salario: {emp_data['nome']} (empresário)",
                categoria="equipe",
            )


def processar_expiracoes_empresario(jogador, return_eventos: bool = False):
    """Reduz semanas do contrato do empresario e remove se expirado."""
    eventos = []
    emp = getattr(jogador, "empresario", None)
    if not isinstance(emp, dict):
        return eventos if return_eventos else None
    restantes = max(0, emp.get("semanas_restantes", 0) - 1)
    if restantes <= 0:
        emp_data = EMPRESARIOS_DISPONIVEIS.get(emp.get("id", ""), {})
        nome = emp_data.get("nome", "?")
        nac = emp_data.get("nacionalidade", "?")
        eventos.append(
            {
                "tipo": "empresario_expirado",
                "mensagem": f"Contrato de {nome} [{nac}] (empresario) expirou.",
                "empresario_id": emp.get("id", ""),
            }
        )
        jogador.empresario = None
    else:
        emp["semanas_restantes"] = restantes
    if return_eventos:
        return eventos
