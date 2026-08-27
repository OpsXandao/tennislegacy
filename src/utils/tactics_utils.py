from enum import Enum
from typing import Any
from src.constants.match_constants import EstrategiaSaque, IntencaoPonto, TipoSaque

def estrategia_padrao_ui() -> dict[str, Any]:
    return {
        "estilo": "atacar_do_fundo",
        "saque": EstrategiaSaque.SEGURO,
        "saque_tipo": TipoSaque.VARIADO,
        "intencao": IntencaoPonto.PACIENTE,
    }

def normalizar_pacote_tatico(valor: str | None) -> dict[str, str] | None:
    texto = str(valor or "").strip()
    if not texto:
        return None
    if texto.startswith("fm|"):
        partes = texto.split("|")
        if len(partes) >= 5:
            _, mentalidade, abordagem, instrucao, segundo_saque = partes[:5]
            return {
                "mentalidade": mentalidade.upper(),
                "abordagem": abordagem.upper(),
                "instrucao": instrucao.upper(),
                "segundo_saque": segundo_saque.upper(),
            }
    if "|" in texto:
        partes = texto.split("|")
        if len(partes) == 3:
            mentalidade, abordagem, instrucao = partes
            return {
                "mentalidade": mentalidade.upper(),
                "abordagem": abordagem.upper(),
                "instrucao": instrucao.upper(),
                "segundo_saque": "SEGURO",
            }
    return None

def estrategia_do_pacote_tatico(
    mentalidade: str,
    abordagem: str,
    instrucao: str,
    segundo_saque: str,
    estrategia_atual: dict[str, Any] | None = None,
) -> dict[str, Any]:
    estrategia = dict(estrategia_atual or estrategia_padrao_ui())

    if abordagem == "SERVE_VOLLEY":
        estrategia["estilo"] = "atacar_na_rede"
        estrategia["saque_tipo"] = TipoSaque.AGRESSIVO
    elif abordagem == "COUNTER":
        estrategia["estilo"] = "atacar_pelo_meio"
        estrategia["saque_tipo"] = TipoSaque.SEGURO
    else:
        estrategia["estilo"] = "atacar_do_fundo"
        estrategia["saque_tipo"] = (
            TipoSaque.AGRESSIVO if mentalidade == "OFENSIVA" else TipoSaque.VARIADO
        )

    if mentalidade == "OFENSIVA":
        estrategia["intencao"] = IntencaoPonto.ARRISCAR
        if estrategia["saque_tipo"] != TipoSaque.SEGURO:
            estrategia["saque_tipo"] = TipoSaque.AGRESSIVO
    elif mentalidade == "DEFENSIVA":
        estrategia["intencao"] = IntencaoPonto.DEFENSIVO
        estrategia["saque_tipo"] = TipoSaque.SEGURO
    else:
        estrategia["intencao"] = IntencaoPonto.PACIENTE

    if instrucao == "ATACAR_SAQUE":
        estrategia["intencao"] = IntencaoPonto.ARRISCAR
    elif instrucao == "TROCAS_LONGAS":
        estrategia["estilo"] = "atacar_do_fundo"
        estrategia["intencao"] = IntencaoPonto.DEFENSIVO
    elif instrucao == "FORCAR_BACKHAND":
        estrategia["estilo"] = "atacar_pelo_meio"
        if mentalidade != "DEFENSIVA":
            estrategia["intencao"] = IntencaoPonto.ARRISCAR

    estrategia["saque"] = (
        EstrategiaSaque.FORCAR
        if str(segundo_saque).upper() == "FORCAR"
        else EstrategiaSaque.SEGURO
    )
    estrategia["mentalidade"] = mentalidade
    estrategia["abordagem"] = abordagem
    estrategia["instrucao"] = instrucao
    return estrategia

def desserializar_estrategia(estrategia: dict[str, Any] | None) -> dict[str, Any]:
    data = dict(estrategia or {})
    if data.get("saque") in {"seguro", "forcar"}:
        data["saque"] = (
            EstrategiaSaque.FORCAR
            if data["saque"] == "forcar"
            else EstrategiaSaque.SEGURO
        )
    if data.get("saque_tipo") in {"agressivo", "seguro", "variado"}:
        mapa_tipo = {
            "agressivo": TipoSaque.AGRESSIVO,
            "seguro": TipoSaque.SEGURO,
            "variado": TipoSaque.VARIADO,
        }
        data["saque_tipo"] = mapa_tipo[data["saque_tipo"]]
    if data.get("intencao") in {"arriscar", "paciente", "defensivo"}:
        mapa_intencao = {
            "arriscar": IntencaoPonto.ARRISCAR,
            "paciente": IntencaoPonto.PACIENTE,
            "defensivo": IntencaoPonto.DEFENSIVO,
        }
        data["intencao"] = mapa_intencao[data["intencao"]]
    return data

def normalizar_estrategia(
    valor: str | None, estrategia_atual: dict[str, Any]
) -> dict[str, Any]:
    estrategia = dict(estrategia_atual or estrategia_padrao_ui())
    pacote = normalizar_pacote_tatico(valor)
    if pacote:
        return estrategia_do_pacote_tatico(
            pacote["mentalidade"],
            pacote["abordagem"],
            pacote["instrucao"],
            pacote["segundo_saque"],
            estrategia,
        )
    chave = str(valor or "").strip().lower()
    segundo_saque_override = None
    if "::" in chave:
        chave, segundo_saque_override = chave.split("::", 1)
        segundo_saque_override = segundo_saque_override.strip().lower()
    if chave in {"rede", "atacar_na_rede"}:
        estrategia["estilo"] = "atacar_na_rede"
    elif chave in {"variado", "atacar_pelo_meio"}:
        estrategia["estilo"] = "atacar_pelo_meio"
    elif chave in {"agressivo", "arriscar"}:
        estrategia["intencao"] = IntencaoPonto.ARRISCAR
        estrategia["saque"] = EstrategiaSaque.FORCAR
    elif chave in {"defensivo", "seguro"}:
        estrategia["intencao"] = IntencaoPonto.DEFENSIVO
        estrategia["saque"] = EstrategiaSaque.SEGURO
    else:
        estrategia["estilo"] = "atacar_do_fundo"
        estrategia["intencao"] = IntencaoPonto.PACIENTE

    if segundo_saque_override in {"seguro", "forcar"}:
        estrategia["saque"] = (
            EstrategiaSaque.FORCAR
            if segundo_saque_override == "forcar"
            else EstrategiaSaque.SEGURO
        )
    return estrategia

def serializar_estrategia(estrategia: dict[str, Any]) -> dict[str, Any]:
    def _enum_value(valor: Any) -> Any:
        if isinstance(valor, Enum): return valor.value
        return valor
    return {chave: _enum_value(valor) for chave, valor in (estrategia or {}).items()}
