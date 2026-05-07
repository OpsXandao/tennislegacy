from src.math_utils import clamp


def multiplicador_lesao(status_lesao) -> float:
    if not isinstance(status_lesao, dict):
        return 1.0
    nivel = str(status_lesao.get("nivel", "")).lower()
    penalidade = float(status_lesao.get("penalidade_atributos", 0.0))
    if penalidade <= 0:
        if status_lesao.get("lesionado"):
            penalidade = 0.18
        elif nivel == "limitado":
            penalidade = 0.12
        elif nivel == "desconforto":
            penalidade = 0.06
    return clamp(1.0 - penalidade, 0.72, 1.0)


def multiplicador_doenca(status_doenca) -> float:
    if not isinstance(status_doenca, dict):
        return 1.0
    if not status_doenca.get("doente", False):
        return 1.0
    penalidade = float(status_doenca.get("penalidade_atributos", 0.0))
    if penalidade <= 0:
        nivel = str(status_doenca.get("nivel", "")).lower()
        penalidade = (
            0.12 if nivel == "grave" else (0.08 if nivel == "moderada" else 0.05)
        )
    return clamp(1.0 - penalidade, 0.75, 1.0)


def aplicar_multiplicador_atributos(atributos: dict, mult: float) -> dict:
    if mult >= 0.999:
        return atributos
    return {k: v * mult for k, v in atributos.items()}


def aplicar_saude_nos_atributos(atributos: dict, status_lesao, status_doenca) -> dict:
    atributos = aplicar_multiplicador_atributos(
        atributos, multiplicador_lesao(status_lesao)
    )
    atributos = aplicar_multiplicador_atributos(
        atributos, multiplicador_doenca(status_doenca)
    )
    return atributos


def calcular_mod_ambiente(
    clima: str, vento: int, umidade: int, altitude_m: int, indoor: bool
) -> dict:
    clima = (clima or "ameno").strip().lower()
    vento = max(0, min(100, int(vento or 0)))
    umidade = max(0, min(100, int(umidade or 50)))
    altitude = max(0, int(altitude_m or 0))
    indoor = bool(indoor)

    mod_saque = 1.0
    mod_ace = 1.0
    mod_falta = 1.0
    mod_rally = 1.0
    mod_erro = 1.0

    if clima == "quente":
        mod_rally *= 0.99
        mod_erro *= 1.02
    elif clima == "frio":
        mod_saque *= 0.98
        mod_ace *= 0.95
        mod_rally *= 1.01
    elif clima == "chuvoso":
        mod_saque *= 0.96
        mod_falta *= 1.10
        mod_erro *= 1.08

    if not indoor:
        mod_falta *= 1.0 + (vento / 330.0)
        mod_ace *= max(0.82, 1.0 - (vento / 260.0))
        mod_erro *= 1.0 + (vento / 420.0)

    if umidade > 70:
        mod_saque *= 0.97
        mod_rally *= 0.99
        mod_erro *= 1.03
    elif umidade < 35:
        mod_saque *= 1.02
        mod_ace *= 1.03

    if altitude >= 1000:
        fator_alt = min(0.12, (altitude - 800) / 7000.0)
        mod_saque *= 1.0 + fator_alt
        mod_ace *= 1.0 + fator_alt * 1.2
        mod_rally *= 1.0 - fator_alt * 0.3
        mod_erro *= 1.0 + fator_alt * 0.45

    return {
        "saque": clamp(mod_saque, 0.86, 1.18),
        "ace": clamp(mod_ace, 0.7, 1.25),
        "falta": clamp(mod_falta, 0.82, 1.35),
        "rally": clamp(mod_rally, 0.86, 1.12),
        "erro": clamp(mod_erro, 0.86, 1.25),
    }
