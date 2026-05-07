from src.staff_constants import PROFISSIONAIS_DISPONIVEIS, EMPRESARIOS_DISPONIVEIS

# === HELPERS ===


def estrelas_display(n):
    """Retorna string de estrelas, ex.: 3 -> '***oo' (usando * e o)."""
    n = max(1, min(5, int(n)))
    return "*" * n + "o" * (5 - n)


def obter_profissional_da_equipe(equipe, categoria):
    """Retorna o dict do profissional de dada categoria na equipe, ou None."""
    for contrato in equipe:
        prof_id = contrato.get("id") if isinstance(contrato, dict) else contrato
        prof = PROFISSIONAIS_DISPONIVEIS.get(prof_id)
        if prof and prof.get("categoria") == categoria:
            return prof
    return None


# === FUNCOES DE GESTAO SEMANAL ===


def processar_gastos_equipe(jogador, return_eventos: bool = False):
    """Deduz salarios semanais de cada membro da equipe."""
    eventos = []
    equipe = getattr(jogador, "equipe", [])
    for contrato in equipe:
        prof_id = contrato.get("id") if isinstance(contrato, dict) else contrato
        salario = (
            contrato.get("salario", 0)
            if isinstance(contrato, dict)
            else PROFISSIONAIS_DISPONIVEIS.get(prof_id, {}).get("salario_semanal", 0)
        )
        prof = PROFISSIONAIS_DISPONIVEIS.get(prof_id)
        if prof and salario > 0:
            jogador.registrar_transacao(
                -salario, f"Salario: {prof['nome']}", categoria="equipe"
            )
    if jogador.dinheiro < 0:
        eventos.append(
            {
                "tipo": "saldo_negativo",
                "mensagem": f"Atencao! Voce esta com saldo negativo: ${jogador.dinheiro:,}",
                "saldo": jogador.dinheiro,
            }
        )
    if return_eventos:
        return eventos


def processar_expiracoes_contratos(jogador, return_eventos: bool = False):
    """Reduz semanas restantes dos contratos e remove os expirados."""
    eventos = []
    equipe = getattr(jogador, "equipe", [])
    equipe_nova = []
    for contrato in equipe:
        if not isinstance(contrato, dict):
            equipe_nova.append(contrato)
            continue
        restantes = max(0, contrato.get("semanas_restantes", 0) - 1)
        if restantes <= 0:
            prof = PROFISSIONAIS_DISPONIVEIS.get(contrato.get("id", ""), {})
            nome = prof.get("nome", "?")
            nac = prof.get("nacionalidade", "?")
            eventos.append(
                {
                    "tipo": "contrato_expirado",
                    "mensagem": f"Contrato de {nome} [{nac}] expirou.",
                    "profissional_id": contrato.get("id", ""),
                }
            )
        else:
            contrato["semanas_restantes"] = restantes
            equipe_nova.append(contrato)
    jogador.equipe = equipe_nova
    if return_eventos:
        return eventos


def obter_max_equipe(jogador):
    """Retorna o limite maximo de profissionais baseado no empresario contratado."""
    empresario_id = None
    if isinstance(getattr(jogador, "empresario", None), dict):
        empresario_id = jogador.empresario.get("id")
    if empresario_id:
        emp = EMPRESARIOS_DISPONIVEIS.get(empresario_id, {})
        return emp.get("max_equipe", 3)
    return 2


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
