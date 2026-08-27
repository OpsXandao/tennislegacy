from __future__ import annotations

from typing import Dict

# Mapeamento de códigos de países para continentes
PAIS_PARA_CONTINENTE: Dict[str, str] = {
    "AU": "Oceania",
    "NZ": "Oceania",
    "CN": "Asia",
    "TH": "Asia",
    "QA": "Asia",
    "AE": "Asia",
    "KZ": "Asia",
    "JP": "Asia",
    "US": "America do Norte",
    "MX": "America do Norte",
    "CA": "America do Norte",
    "DO": "America do Norte",
    "AR": "America do Sul",
    "BR": "America do Sul",
    "CL": "America do Sul",
    "CO": "America do Sul",
    "FR": "Europa",
    "NL": "Europa",
    "TR": "Europa",
    "SI": "Europa",
    "GR": "Europa",
    "ES": "Europa",
    "CY": "Europa",
    "MA": "Africa",
    "TN": "Africa",
    "PT": "Europa",
    "MC": "Europa",
    "DE": "Europa",
    "RO": "Europa",
    "CZ": "Europa",
    "IT": "Europa",
    "AT": "Europa",
    "HR": "Europa",
    "CH": "Europa",
    "BA": "Europa",
    "GB": "Europa",
    "SE": "Europa",
    "BE": "Europa",
    "SK": "Europa",
    "RS": "Europa",
}

def extrair_codigo_pais(pais_sede: str) -> str:
    """Extrai 'AU' de '[AU] Austrália'."""
    if not pais_sede or "[" not in pais_sede:
        return "INT" # Internacional/Desconhecido
    try:
        return pais_sede.split("[")[1].split("]")[0].upper()
    except IndexError:
        return "INT"

def obter_continente(pais_sede: str) -> str:
    """Retorna o continente baseado no país sede."""
    codigo = extrair_codigo_pais(pais_sede)
    return PAIS_PARA_CONTINENTE.get(codigo, "Europa") # Default Europa (maioria dos torneios)

def calcular_custo_viagem(origem: str, destino: str) -> int:
    """Calcula custo financeiro básico entre continentes."""
    if origem == destino:
        return 500 # Viagem local/curta
    return 3500 # Viagem transcontinental

def calcular_fadiga_viagem(origem: str, destino: str) -> int:
    """Calcula perda de energia por jet lag."""
    if origem == destino:
        return 2
    return 12 # Jet lag pesado
