import random

from src.staff_constants import EMPRESARIOS_DISPONIVEIS


def _obter_empresarios_disponiveis():
    return EMPRESARIOS_DISPONIVEIS


PATROCINADORES_DISPONIVEIS = {
    "racket_local": {
        "nome": "AceGear",
        "categoria": "raquete",
        "tier": "menor",
        "pagamento_semanal": 50,
        "bonus_assinatura": 500,
        "bonus_titulo": 300,
        "requisito_ranking": 2000,
        "req_seguidores": 0,
        "descricao": "Marca local que apoia iniciantes.",
    },
    "clothing_regional": {
        "nome": "SportWear",
        "categoria": "vestuario",
        "tier": "menor",
        "pagamento_semanal": 120,
        "bonus_assinatura": 1200,
        "bonus_titulo": 600,
        "requisito_ranking": 500,
        "req_seguidores": 0,
        "descricao": "Vestuario esportivo regional em ascensao.",
    },
    "drink_energy": {
        "nome": "BoltDrink",
        "categoria": "alimentacao",
        "tier": "menor",
        "pagamento_semanal": 200,
        "bonus_assinatura": 2000,
        "bonus_titulo": 800,
        "requisito_ranking": 300,
        "req_seguidores": 5000,
        "descricao": "Bebida energetica para atletas competitivos.",
    },
    "racket_pro": {
        "nome": "BlazerTech",
        "categoria": "raquete",
        "tier": "menor",
        "pagamento_semanal": 400,
        "bonus_assinatura": 4000,
        "bonus_titulo": 2000,
        "requisito_ranking": 100,
        "req_seguidores": 0,
        "descricao": "Equipamento de elite para jogadores de ponta.",
    },
    "clothing_global": {
        "nome": "SpeedLine",
        "categoria": "vestuario",
        "tier": "menor",
        "pagamento_semanal": 700,
        "bonus_assinatura": 7000,
        "bonus_titulo": 4000,
        "requisito_ranking": 60,
        "req_seguidores": 20000,
        "descricao": "Marca global de moda esportiva premium.",
    },
    "watch_luxury": {
        "nome": "ChronoElite",
        "categoria": "relogio",
        "tier": "master",
        "pagamento_semanal": 900,
        "bonus_assinatura": 9000,
        "bonus_titulo": 6000,
        "requisito_ranking": 40,
        "req_seguidores": 50000,
        "descricao": "Relogios de luxo para atletas de elite. Contrato exclusivo.",
    },
    "car_nacional": {
        "nome": "MotorPro",
        "categoria": "automovel",
        "tier": "menor",
        "pagamento_semanal": 600,
        "bonus_assinatura": 6000,
        "bonus_titulo": 3000,
        "requisito_ranking": 50,
        "req_seguidores": 30000,
        "descricao": "Automoveis de performance para campeoes.",
    },
    "tech_startup": {
        "nome": "DataCourt",
        "categoria": "tecnologia",
        "tier": "menor",
        "pagamento_semanal": 500,
        "bonus_assinatura": 5000,
        "bonus_titulo": 2500,
        "requisito_ranking": 150,
        "req_seguidores": 80000,
        "descricao": "Startup de analise de dados esportivos.",
    },
    "racket_elite": {
        "nome": "PrecisionX",
        "categoria": "raquete",
        "tier": "master",
        "pagamento_semanal": 1000,
        "bonus_assinatura": 10000,
        "bonus_titulo": 8000,
        "requisito_ranking": 20,
        "req_seguidores": 0,
        "descricao": "A raquete dos campeoes de Grand Slam. Contrato exclusivo.",
    },
    "clothing_top": {
        "nome": "EliteWear",
        "categoria": "vestuario",
        "tier": "master",
        "pagamento_semanal": 1500,
        "bonus_assinatura": 15000,
        "bonus_titulo": 10000,
        "requisito_ranking": 15,
        "req_seguidores": 100000,
        "descricao": "Vestuario para os melhores do mundo. Contrato exclusivo.",
    },
    "bank_global": {
        "nome": "GlobalBank",
        "categoria": "financeiro",
        "tier": "master",
        "pagamento_semanal": 3000,
        "bonus_assinatura": 30000,
        "bonus_titulo": 20000,
        "requisito_ranking": 10,
        "req_seguidores": 200000,
        "descricao": "Patrocinador principal para estrelas do tenis. Contrato exclusivo.",
    },
    "racket_legend": {
        "nome": "LegacyFrame",
        "categoria": "raquete",
        "tier": "master",
        "pagamento_semanal": 5000,
        "bonus_assinatura": 50000,
        "bonus_titulo": 50000,
        "requisito_ranking": 3,
        "req_seguidores": 500000,
        "descricao": "A raquete das lendas. Exclusiva para o Top 3.",
    },
}

PATROCINADORES_REAIS = [
    # Esportivas / equipamentos
    {
        "id": "nike",
        "nome": "Nike",
        "categoria": "vestuario",
        "tier": "master",
        "pagamento_semanal": 2600,
        "bonus_assinatura": 26000,
        "bonus_titulo": 18000,
        "requisito_ranking": 12,
        "req_seguidores": 160000,
    },
    {
        "id": "adidas",
        "nome": "Adidas",
        "categoria": "vestuario",
        "tier": "master",
        "pagamento_semanal": 2400,
        "bonus_assinatura": 24000,
        "bonus_titulo": 16000,
        "requisito_ranking": 15,
        "req_seguidores": 140000,
    },
    {
        "id": "puma",
        "nome": "Puma",
        "categoria": "vestuario",
        "tier": "menor",
        "pagamento_semanal": 1200,
        "bonus_assinatura": 12000,
        "bonus_titulo": 7000,
        "requisito_ranking": 35,
        "req_seguidores": 70000,
    },
    {
        "id": "under_armour",
        "nome": "Under Armour",
        "categoria": "vestuario",
        "tier": "menor",
        "pagamento_semanal": 900,
        "bonus_assinatura": 9000,
        "bonus_titulo": 5000,
        "requisito_ranking": 55,
        "req_seguidores": 45000,
    },
    {
        "id": "new_balance",
        "nome": "New Balance",
        "categoria": "vestuario",
        "tier": "menor",
        "pagamento_semanal": 950,
        "bonus_assinatura": 9500,
        "bonus_titulo": 5200,
        "requisito_ranking": 50,
        "req_seguidores": 42000,
    },
    {
        "id": "asics",
        "nome": "ASICS",
        "categoria": "vestuario",
        "tier": "menor",
        "pagamento_semanal": 850,
        "bonus_assinatura": 8500,
        "bonus_titulo": 4600,
        "requisito_ranking": 65,
        "req_seguidores": 36000,
    },
    {
        "id": "mizuno",
        "nome": "Mizuno",
        "categoria": "vestuario",
        "tier": "menor",
        "pagamento_semanal": 650,
        "bonus_assinatura": 6500,
        "bonus_titulo": 3400,
        "requisito_ranking": 85,
        "req_seguidores": 25000,
    },
    {
        "id": "fila",
        "nome": "Fila",
        "categoria": "vestuario",
        "tier": "menor",
        "pagamento_semanal": 620,
        "bonus_assinatura": 6200,
        "bonus_titulo": 3200,
        "requisito_ranking": 95,
        "req_seguidores": 22000,
    },
    {
        "id": "lotto",
        "nome": "Lotto",
        "categoria": "vestuario",
        "tier": "menor",
        "pagamento_semanal": 500,
        "bonus_assinatura": 5000,
        "bonus_titulo": 2500,
        "requisito_ranking": 120,
        "req_seguidores": 18000,
    },
    {
        "id": "wilson",
        "nome": "Wilson",
        "categoria": "raquete",
        "tier": "menor",
        "pagamento_semanal": 1300,
        "bonus_assinatura": 13000,
        "bonus_titulo": 7600,
        "requisito_ranking": 32,
        "req_seguidores": 65000,
    },
    {
        "id": "babolat",
        "nome": "Babolat",
        "categoria": "raquete",
        "tier": "menor",
        "pagamento_semanal": 1200,
        "bonus_assinatura": 12000,
        "bonus_titulo": 7000,
        "requisito_ranking": 36,
        "req_seguidores": 56000,
    },
    {
        "id": "head",
        "nome": "HEAD",
        "categoria": "raquete",
        "tier": "menor",
        "pagamento_semanal": 1250,
        "bonus_assinatura": 12500,
        "bonus_titulo": 7200,
        "requisito_ranking": 34,
        "req_seguidores": 60000,
    },
    {
        "id": "yonex",
        "nome": "Yonex",
        "categoria": "raquete",
        "tier": "menor",
        "pagamento_semanal": 980,
        "bonus_assinatura": 9800,
        "bonus_titulo": 5200,
        "requisito_ranking": 55,
        "req_seguidores": 42000,
    },
    {
        "id": "dunlop",
        "nome": "Dunlop",
        "categoria": "raquete",
        "tier": "menor",
        "pagamento_semanal": 780,
        "bonus_assinatura": 7800,
        "bonus_titulo": 4200,
        "requisito_ranking": 75,
        "req_seguidores": 30000,
    },
    {
        "id": "tecnifibre",
        "nome": "Tecnifibre",
        "categoria": "raquete",
        "tier": "menor",
        "pagamento_semanal": 740,
        "bonus_assinatura": 7400,
        "bonus_titulo": 3900,
        "requisito_ranking": 82,
        "req_seguidores": 28000,
    },
    {
        "id": "prince",
        "nome": "Prince",
        "categoria": "raquete",
        "tier": "menor",
        "pagamento_semanal": 620,
        "bonus_assinatura": 6200,
        "bonus_titulo": 3200,
        "requisito_ranking": 100,
        "req_seguidores": 22000,
    },
    {
        "id": "lacoste",
        "nome": "Lacoste",
        "categoria": "vestuario",
        "tier": "master",
        "pagamento_semanal": 1800,
        "bonus_assinatura": 18000,
        "bonus_titulo": 12000,
        "requisito_ranking": 20,
        "req_seguidores": 100000,
    },
    {
        "id": "uniqlo",
        "nome": "Uniqlo",
        "categoria": "vestuario",
        "tier": "menor",
        "pagamento_semanal": 820,
        "bonus_assinatura": 8200,
        "bonus_titulo": 4300,
        "requisito_ranking": 70,
        "req_seguidores": 32000,
    },
    # Bancos / pagamentos
    {
        "id": "jpmorgan",
        "nome": "JPMorgan Chase",
        "categoria": "financeiro",
        "tier": "master",
        "pagamento_semanal": 2900,
        "bonus_assinatura": 29000,
        "bonus_titulo": 19000,
        "requisito_ranking": 10,
        "req_seguidores": 180000,
    },
    {
        "id": "goldman_sachs",
        "nome": "Goldman Sachs",
        "categoria": "financeiro",
        "tier": "master",
        "pagamento_semanal": 3000,
        "bonus_assinatura": 30000,
        "bonus_titulo": 20000,
        "requisito_ranking": 9,
        "req_seguidores": 200000,
    },
    {
        "id": "morgan_stanley",
        "nome": "Morgan Stanley",
        "categoria": "financeiro",
        "tier": "master",
        "pagamento_semanal": 2600,
        "bonus_assinatura": 26000,
        "bonus_titulo": 17500,
        "requisito_ranking": 12,
        "req_seguidores": 160000,
    },
    {
        "id": "bank_of_america",
        "nome": "Bank of America",
        "categoria": "financeiro",
        "tier": "menor",
        "pagamento_semanal": 1400,
        "bonus_assinatura": 14000,
        "bonus_titulo": 9000,
        "requisito_ranking": 28,
        "req_seguidores": 85000,
    },
    {
        "id": "citi",
        "nome": "Citi",
        "categoria": "financeiro",
        "tier": "menor",
        "pagamento_semanal": 1350,
        "bonus_assinatura": 13500,
        "bonus_titulo": 8600,
        "requisito_ranking": 30,
        "req_seguidores": 82000,
    },
    {
        "id": "wells_fargo",
        "nome": "Wells Fargo",
        "categoria": "financeiro",
        "tier": "menor",
        "pagamento_semanal": 1180,
        "bonus_assinatura": 11800,
        "bonus_titulo": 7300,
        "requisito_ranking": 42,
        "req_seguidores": 62000,
    },
    {
        "id": "hsbc",
        "nome": "HSBC",
        "categoria": "financeiro",
        "tier": "menor",
        "pagamento_semanal": 1240,
        "bonus_assinatura": 12400,
        "bonus_titulo": 7600,
        "requisito_ranking": 38,
        "req_seguidores": 68000,
    },
    {
        "id": "santander",
        "nome": "Santander",
        "categoria": "financeiro",
        "tier": "menor",
        "pagamento_semanal": 1120,
        "bonus_assinatura": 11200,
        "bonus_titulo": 6800,
        "requisito_ranking": 48,
        "req_seguidores": 56000,
    },
    {
        "id": "bbva",
        "nome": "BBVA",
        "categoria": "financeiro",
        "tier": "menor",
        "pagamento_semanal": 980,
        "bonus_assinatura": 9800,
        "bonus_titulo": 5600,
        "requisito_ranking": 62,
        "req_seguidores": 43000,
    },
    {
        "id": "bnp_paribas",
        "nome": "BNP Paribas",
        "categoria": "financeiro",
        "tier": "menor",
        "pagamento_semanal": 1160,
        "bonus_assinatura": 11600,
        "bonus_titulo": 7000,
        "requisito_ranking": 44,
        "req_seguidores": 60000,
    },
    {
        "id": "deutsche_bank",
        "nome": "Deutsche Bank",
        "categoria": "financeiro",
        "tier": "menor",
        "pagamento_semanal": 1020,
        "bonus_assinatura": 10200,
        "bonus_titulo": 5900,
        "requisito_ranking": 58,
        "req_seguidores": 48000,
    },
    {
        "id": "barclays",
        "nome": "Barclays",
        "categoria": "financeiro",
        "tier": "menor",
        "pagamento_semanal": 1080,
        "bonus_assinatura": 10800,
        "bonus_titulo": 6400,
        "requisito_ranking": 54,
        "req_seguidores": 52000,
    },
    {
        "id": "ubs",
        "nome": "UBS",
        "categoria": "financeiro",
        "tier": "menor",
        "pagamento_semanal": 1300,
        "bonus_assinatura": 13000,
        "bonus_titulo": 8200,
        "requisito_ranking": 34,
        "req_seguidores": 76000,
    },
    {
        "id": "itau",
        "nome": "Itau",
        "categoria": "financeiro",
        "tier": "menor",
        "pagamento_semanal": 840,
        "bonus_assinatura": 8400,
        "bonus_titulo": 4700,
        "requisito_ranking": 72,
        "req_seguidores": 33000,
    },
    {
        "id": "bradesco",
        "nome": "Bradesco",
        "categoria": "financeiro",
        "tier": "menor",
        "pagamento_semanal": 780,
        "bonus_assinatura": 7800,
        "bonus_titulo": 4300,
        "requisito_ranking": 82,
        "req_seguidores": 29000,
    },
    {
        "id": "nubank",
        "nome": "Nubank",
        "categoria": "financeiro",
        "tier": "menor",
        "pagamento_semanal": 920,
        "bonus_assinatura": 9200,
        "bonus_titulo": 5200,
        "requisito_ranking": 66,
        "req_seguidores": 38000,
    },
    {
        "id": "visa",
        "nome": "Visa",
        "categoria": "financeiro",
        "tier": "master",
        "pagamento_semanal": 2400,
        "bonus_assinatura": 24000,
        "bonus_titulo": 15500,
        "requisito_ranking": 16,
        "req_seguidores": 130000,
    },
    {
        "id": "mastercard",
        "nome": "Mastercard",
        "categoria": "financeiro",
        "tier": "master",
        "pagamento_semanal": 2350,
        "bonus_assinatura": 23500,
        "bonus_titulo": 15000,
        "requisito_ranking": 16,
        "req_seguidores": 125000,
    },
    {
        "id": "american_express",
        "nome": "American Express",
        "categoria": "financeiro",
        "tier": "master",
        "pagamento_semanal": 2500,
        "bonus_assinatura": 25000,
        "bonus_titulo": 16500,
        "requisito_ranking": 14,
        "req_seguidores": 140000,
    },
    {
        "id": "paypal",
        "nome": "PayPal",
        "categoria": "financeiro",
        "tier": "menor",
        "pagamento_semanal": 1100,
        "bonus_assinatura": 11000,
        "bonus_titulo": 6600,
        "requisito_ranking": 52,
        "req_seguidores": 54000,
    },
    {
        "id": "stripe",
        "nome": "Stripe",
        "categoria": "financeiro",
        "tier": "menor",
        "pagamento_semanal": 980,
        "bonus_assinatura": 9800,
        "bonus_titulo": 5600,
        "requisito_ranking": 62,
        "req_seguidores": 42000,
    },
    # TI / tecnologia
    {
        "id": "apple",
        "nome": "Apple",
        "categoria": "tecnologia",
        "tier": "master",
        "pagamento_semanal": 2800,
        "bonus_assinatura": 28000,
        "bonus_titulo": 18500,
        "requisito_ranking": 11,
        "req_seguidores": 190000,
    },
    {
        "id": "samsung",
        "nome": "Samsung",
        "categoria": "tecnologia",
        "tier": "master",
        "pagamento_semanal": 2500,
        "bonus_assinatura": 25000,
        "bonus_titulo": 16500,
        "requisito_ranking": 14,
        "req_seguidores": 150000,
    },
    {
        "id": "sony",
        "nome": "Sony",
        "categoria": "tecnologia",
        "tier": "menor",
        "pagamento_semanal": 1400,
        "bonus_assinatura": 14000,
        "bonus_titulo": 9000,
        "requisito_ranking": 30,
        "req_seguidores": 86000,
    },
    {
        "id": "lg",
        "nome": "LG",
        "categoria": "tecnologia",
        "tier": "menor",
        "pagamento_semanal": 980,
        "bonus_assinatura": 9800,
        "bonus_titulo": 5600,
        "requisito_ranking": 62,
        "req_seguidores": 42000,
    },
    {
        "id": "microsoft",
        "nome": "Microsoft",
        "categoria": "tecnologia",
        "tier": "master",
        "pagamento_semanal": 2700,
        "bonus_assinatura": 27000,
        "bonus_titulo": 18000,
        "requisito_ranking": 12,
        "req_seguidores": 180000,
    },
    {
        "id": "google",
        "nome": "Google",
        "categoria": "tecnologia",
        "tier": "master",
        "pagamento_semanal": 2750,
        "bonus_assinatura": 27500,
        "bonus_titulo": 18200,
        "requisito_ranking": 12,
        "req_seguidores": 185000,
    },
    {
        "id": "amazon",
        "nome": "Amazon",
        "categoria": "tecnologia",
        "tier": "master",
        "pagamento_semanal": 2600,
        "bonus_assinatura": 26000,
        "bonus_titulo": 17500,
        "requisito_ranking": 13,
        "req_seguidores": 170000,
    },
    {
        "id": "intel",
        "nome": "Intel",
        "categoria": "tecnologia",
        "tier": "menor",
        "pagamento_semanal": 1220,
        "bonus_assinatura": 12200,
        "bonus_titulo": 7400,
        "requisito_ranking": 40,
        "req_seguidores": 66000,
    },
    {
        "id": "amd",
        "nome": "AMD",
        "categoria": "tecnologia",
        "tier": "menor",
        "pagamento_semanal": 1160,
        "bonus_assinatura": 11600,
        "bonus_titulo": 7000,
        "requisito_ranking": 45,
        "req_seguidores": 60000,
    },
    {
        "id": "nvidia",
        "nome": "NVIDIA",
        "categoria": "tecnologia",
        "tier": "menor",
        "pagamento_semanal": 1300,
        "bonus_assinatura": 13000,
        "bonus_titulo": 8200,
        "requisito_ranking": 34,
        "req_seguidores": 76000,
    },
    {
        "id": "qualcomm",
        "nome": "Qualcomm",
        "categoria": "tecnologia",
        "tier": "menor",
        "pagamento_semanal": 980,
        "bonus_assinatura": 9800,
        "bonus_titulo": 5600,
        "requisito_ranking": 62,
        "req_seguidores": 43000,
    },
    {
        "id": "oracle",
        "nome": "Oracle",
        "categoria": "tecnologia",
        "tier": "menor",
        "pagamento_semanal": 1200,
        "bonus_assinatura": 12000,
        "bonus_titulo": 7300,
        "requisito_ranking": 42,
        "req_seguidores": 64000,
    },
    {
        "id": "ibm",
        "nome": "IBM",
        "categoria": "tecnologia",
        "tier": "menor",
        "pagamento_semanal": 980,
        "bonus_assinatura": 9800,
        "bonus_titulo": 5600,
        "requisito_ranking": 62,
        "req_seguidores": 43000,
    },
    {
        "id": "cisco",
        "nome": "Cisco",
        "categoria": "tecnologia",
        "tier": "menor",
        "pagamento_semanal": 940,
        "bonus_assinatura": 9400,
        "bonus_titulo": 5400,
        "requisito_ranking": 66,
        "req_seguidores": 39000,
    },
    {
        "id": "dell",
        "nome": "Dell",
        "categoria": "tecnologia",
        "tier": "menor",
        "pagamento_semanal": 900,
        "bonus_assinatura": 9000,
        "bonus_titulo": 5000,
        "requisito_ranking": 70,
        "req_seguidores": 36000,
    },
    {
        "id": "hp",
        "nome": "HP",
        "categoria": "tecnologia",
        "tier": "menor",
        "pagamento_semanal": 860,
        "bonus_assinatura": 8600,
        "bonus_titulo": 4700,
        "requisito_ranking": 74,
        "req_seguidores": 34000,
    },
    {
        "id": "lenovo",
        "nome": "Lenovo",
        "categoria": "tecnologia",
        "tier": "menor",
        "pagamento_semanal": 840,
        "bonus_assinatura": 8400,
        "bonus_titulo": 4600,
        "requisito_ranking": 76,
        "req_seguidores": 33000,
    },
    {
        "id": "meta",
        "nome": "Meta",
        "categoria": "tecnologia",
        "tier": "menor",
        "pagamento_semanal": 1180,
        "bonus_assinatura": 11800,
        "bonus_titulo": 7200,
        "requisito_ranking": 44,
        "req_seguidores": 62000,
    },
    {
        "id": "salesforce",
        "nome": "Salesforce",
        "categoria": "tecnologia",
        "tier": "menor",
        "pagamento_semanal": 980,
        "bonus_assinatura": 9800,
        "bonus_titulo": 5600,
        "requisito_ranking": 62,
        "req_seguidores": 42000,
    },
    {
        "id": "sap",
        "nome": "SAP",
        "categoria": "tecnologia",
        "tier": "menor",
        "pagamento_semanal": 940,
        "bonus_assinatura": 9400,
        "bonus_titulo": 5400,
        "requisito_ranking": 66,
        "req_seguidores": 39000,
    },
    {
        "id": "cloudflare",
        "nome": "Cloudflare",
        "categoria": "tecnologia",
        "tier": "menor",
        "pagamento_semanal": 860,
        "bonus_assinatura": 8600,
        "bonus_titulo": 4700,
        "requisito_ranking": 74,
        "req_seguidores": 34000,
    },
]

for pat in PATROCINADORES_REAIS:
    pat.setdefault(
        "descricao", f"Marca real ({pat['categoria']}) com contrato progressivo."
    )
    PATROCINADORES_DISPONIVEIS.setdefault(pat["id"], pat)


_CATEGORIAS_MATERIAL_ESPORTIVO = {
    "raquete",
    "vestuario",
    "calcado",
    "acessorios",
}


def _patrocinador_master_valido(patrocinador: dict) -> bool:
    if not isinstance(patrocinador, dict):
        return False
    if patrocinador.get("tier") != "master":
        return True
    categoria = str(patrocinador.get("categoria", "")).strip().lower()
    return categoria in _CATEGORIAS_MATERIAL_ESPORTIVO


def _normalizar_tier_patrocinadores():
    """Garante coerência: patrocinador master deve ser de material esportivo."""
    for pat in PATROCINADORES_DISPONIVEIS.values():
        if isinstance(pat, dict) and pat.get("tier") == "master":
            if not _patrocinador_master_valido(pat):
                pat["tier"] = "menor"


_normalizar_tier_patrocinadores()

# --- Mapa de retrocompatibilidade ---
_MAPA_PATROCINIO_LEGADO = {
    "raquete_local": "racket_local",
    "vestuario_pro": "clothing_regional",
    "raquete_pro": "racket_pro",
    "banco_master": "bank_global",
}


def _resolver_id_patrocinio(item):
    """Resolve item de patrocinio (id legado/dict/nome) para um id válido."""
    if not item:
        return None

    if isinstance(item, dict):
        if item.get("id"):
            item = item.get("id")
        elif item.get("nome"):
            nome = str(item.get("nome", "")).strip().lower()
            for pid, pat in PATROCINADORES_DISPONIVEIS.items():
                if str(pat.get("nome", "")).strip().lower() == nome:
                    return pid
            return None
        else:
            return None

    if not isinstance(item, str):
        item = str(item)
    novo = _MAPA_PATROCINIO_LEGADO.get(item, item)
    return novo if novo in PATROCINADORES_DISPONIVEIS else None


def migrar_patrocinios(patrocinios_raw):
    """Converte IDs legados para os novos e descarta IDs desconhecidos."""
    if not isinstance(patrocinios_raw, (list, tuple, set)):
        return []

    resultado = []
    for p in patrocinios_raw:
        novo = _resolver_id_patrocinio(p)
        if novo and novo not in resultado:
            resultado.append(novo)
    return resultado


def processar_pagamentos_patrocinio(jogador):
    """Recebe pagamentos semanais dos patrocinadores com bônus e dedução de comissão do empresário."""
    patrocinios_normalizados = migrar_patrocinios(getattr(jogador, "patrocinios", []))
    jogador.patrocinios = patrocinios_normalizados

    bonus_emp = 0.0
    comissao_pct = 0.0
    emp_nome = ""
    empresarios = _obter_empresarios_disponiveis()
    if isinstance(getattr(jogador, "empresario", None), dict):
        emp_id = jogador.empresario.get("id")
        emp_data = empresarios.get(emp_id)
        if emp_data:
            bonus_emp = emp_data.get("bonus_patrocinio", 0.0)
            comissao_pct = emp_data.get(
                "comissao_agenciamento", 0.15
            )  # Default 15% se não definido
            emp_nome = emp_data.get("nome", "Empresário")

    for pat_id in patrocinios_normalizados:
        pat = PATROCINADORES_DISPONIVEIS.get(pat_id)
        if pat:
            valor_bruto = pat["pagamento_semanal"]
            bonus_valor = int(valor_bruto * bonus_emp)
            valor_com_bonus = valor_bruto + bonus_valor

            # Comissão do empresário sobre o valor total recebido (base + bônus)
            valor_comissao = int(valor_com_bonus * comissao_pct)
            valor_liquido = valor_com_bonus - valor_comissao

            desc = f"Patrocínio: {pat['nome']}"
            if bonus_emp > 0:
                desc += f" (+{int(bonus_emp*100)}% bônus)"
            if comissao_pct > 0:
                desc += f" (-{int(comissao_pct*100)}% comissão {emp_nome})"

            jogador.registrar_transacao(
                valor_liquido,
                desc,
                categoria="patrocinio",
            )


LIMITE_PATROCINIO_MASTER = 1
LIMITE_PATROCINIO_MENORES = 3


def pode_assinar_patrocinio(jogador, pat_id, posição, seguidores=0):
    """Retorna (pode: bool, motivo: str). Regra: 1 master + 3 menores (max 4 total)."""
    pat = PATROCINADORES_DISPONIVEIS.get(pat_id)
    if not pat:
        return False, "Patrocinador desconhecido."
    patrocinios_atuais = getattr(jogador, "patrocinios", [])
    if pat_id in patrocinios_atuais:
        return False, "Voce ja tem este patrocinio."

    tier = pat.get("tier", "menor")
    if tier == "master" and not _patrocinador_master_valido(pat):
        return False, "Patrocinador master deve ser de material esportivo."
    if tier == "master":
        masters_ativos = [
            p
            for p in patrocinios_atuais
            if PATROCINADORES_DISPONIVEIS.get(p, {}).get("tier") == "master"
        ]
        if masters_ativos:
            nome_atual = PATROCINADORES_DISPONIVEIS[masters_ativos[0]]["nome"]
            return (
                False,
                f"Voce ja tem o patrocinador master {nome_atual}. Encerre-o primeiro.",
            )
    else:
        menores_ativos = [
            p
            for p in patrocinios_atuais
            if PATROCINADORES_DISPONIVEIS.get(p, {}).get("tier", "menor") != "master"
        ]
        if len(menores_ativos) >= LIMITE_PATROCINIO_MENORES:
            return (
                False,
                f"Limite de {LIMITE_PATROCINIO_MENORES} patrocinios menores atingido.",
            )

    if posição > pat["requisito_ranking"]:
        return False, f"Ranking insuficiente (requerido: #{pat['requisito_ranking']})."
    req_seg = pat.get("req_seguidores", 0)
    if req_seg > 0 and seguidores < req_seg:
        return False, f"Seguidores insuficientes (requerido: {req_seg:,})."
    return True, "OK"


def gerar_proposta_patrocinio(jogador, ranking):
    """Gera proposta de patrocinio e entrega na caixa de e-mail do jogador."""
    posicao = ranking.obter_posicao(jogador.nome) or 9999
    seguidores = getattr(jogador, "seguidores", 0)
    caixa = getattr(jogador, "caixa_email", [])
    jogador.caixa_email = caixa if isinstance(caixa, list) else []

    emp_bonus = 0.0
    emp_estrelas = 1
    empresarios = _obter_empresarios_disponiveis()
    if isinstance(getattr(jogador, "empresario", None), dict):
        emp_id = jogador.empresario.get("id")
        emp = empresarios.get(emp_id, {})
        emp_bonus = float(emp.get("bonus_patrocinio", 0.0) or 0.0)
        emp_estrelas = int(emp.get("estrelas", 1) or 1)

    # Empresario melhor + boa fase aumentam chance de inbound.
    chance = 0.20 + (emp_bonus * 0.9)
    if posicao <= 500:
        chance += 0.08
    if posicao <= 100:
        chance += 0.07
    if seguidores >= 10000:
        chance += 0.05
    if seguidores >= 50000:
        chance += 0.05
    chance = max(0.15, min(0.60, chance))
    if random.random() > chance:
        return

    pendentes_ids = {
        p.get("ref_id")
        for p in jogador.caixa_email
        if isinstance(p, dict)
        and p.get("tipo") == "patrocinio"
        and p.get("status", "pendente") == "pendente"
    }
    # Usa posição efetiva para candidatos: jogadores fora do top-2000 ainda
    # recebem propostas dos patrocinadores de entrada (Wilson/Babolat).
    pos_efetiva = min(posicao, 2000)
    candidatos = []
    for pat_id, pat in PATROCINADORES_DISPONIVEIS.items():
        pode, _ = pode_assinar_patrocinio(jogador, pat_id, pos_efetiva, seguidores)
        if not pode or pat_id in pendentes_ids:
            continue
        tier = pat.get("tier", "menor")
        score = 1.0
        score += min(3.0, max(0.0, (150 - min(posicao, 150)) / 70.0))
        score += min(2.0, seguidores / 80000.0)
        if tier == "master":
            score += max(0.2, (emp_estrelas - 1) * 0.85)
        score += max(0.1, (emp_estrelas - 1) * 0.25)
        score += (pat.get("pagamento_semanal", 0) / 1000.0) * (0.35 + emp_bonus)
        candidatos.append((pat_id, pat, max(0.2, score)))

    if not candidatos:
        return

    pesos = [c[2] for c in candidatos]
    escolhido = random.choices(candidatos, weights=pesos, k=1)[0]
    pat_id, pat, _ = escolhido

    proposta = {
        "tipo": "patrocinio",
        "status": "pendente",
        "ref_id": pat_id,
        "titulo": f"Proposta de Patrocinio: {pat.get('nome', pat_id)}",
        "mensagem": (
            f"{pat.get('nome', pat_id)} quer te patrocinar. "
            f"Oferta: ${pat.get('pagamento_semanal', 0)}/sem + "
            f"bonus assinatura ${pat.get('bonus_assinatura', 0):,}."
        ),
        "oferta": {
            "pagamento_semanal": int(pat.get("pagamento_semanal", 0) or 0),
            "bonus_assinatura": int(pat.get("bonus_assinatura", 0) or 0),
            "bonus_titulo": int(pat.get("bonus_titulo", 0) or 0),
            "categoria": pat.get("categoria", ""),
            "tier": pat.get("tier", "menor"),
            "requisito_ranking": int(pat.get("requisito_ranking", 9999) or 9999),
            "req_seguidores": int(pat.get("req_seguidores", 0) or 0),
        },
    }
    jogador.caixa_email.append(proposta)


def gerar_proposta_empresario(jogador, ranking):
    """Gera proposta inbound de empresario para a caixa de e-mail."""
    caixa = getattr(jogador, "caixa_email", [])
    jogador.caixa_email = caixa if isinstance(caixa, list) else []
    posição = ranking.obter_posicao(jogador.nome) or 9999
    seguidores = int(getattr(jogador, "seguidores", 0) or 0)
    reputação = int(getattr(jogador, "reputacao_imprensa", 50) or 50)
    empresarios = _obter_empresarios_disponiveis()

    chance = 0.05
    if posição <= 250:
        chance += 0.05
    if seguidores >= 20000:
        chance += 0.04
    if reputação >= 65:
        chance += 0.03
    chance = max(0.04, min(0.24, chance))
    if random.random() > chance:
        return

    pendentes_ids = {
        p.get("ref_id")
        for p in jogador.caixa_email
        if isinstance(p, dict)
        and p.get("tipo") == "empresario"
        and p.get("status", "pendente") == "pendente"
    }
    atuais = set()
    emp_atual = getattr(jogador, "empresario", None)
    if isinstance(emp_atual, dict):
        atuais.add(emp_atual.get("id"))

    candidatos = []
    for emp_id, emp in empresarios.items():
        if emp_id in pendentes_ids or emp_id in atuais:
            continue
        estrelas = int(emp.get("estrelas", 1) or 1)
        score = 1.0 + (6 - max(1, min(posição, 600)) / 120.0)
        score += seguidores / 120000.0
        score += reputação / 180.0
        score += estrelas * 0.55
        # Empresarios de elite tendem a oferecer desconto inicial para entrar.
        desconto = 1.0 - min(0.12, max(0.0, (estrelas - 2) * 0.04))
        salario_oferta = int(round(emp.get("salario_semanal", 0) * desconto))
        candidatos.append((emp_id, emp, max(0.25, score), salario_oferta))

    if not candidatos:
        return

    escolhido = random.choices(candidatos, weights=[c[2] for c in candidatos], k=1)[0]
    emp_id, emp, _, salario_oferta = escolhido
    proposta = {
        "tipo": "empresario",
        "status": "pendente",
        "ref_id": emp_id,
        "titulo": f"Proposta de Empresario: {emp.get('nome', emp_id)}",
        "mensagem": (
            f"{emp.get('nome', emp_id)} quer representar sua carreira. "
            f"Oferta inicial: ${salario_oferta}/sem por 26 semanas."
        ),
        "oferta": {
            "salario_semanal": int(max(50, salario_oferta)),
            "duracao_semanas": 26,
            "max_equipe": int(emp.get("max_equipe", 2) or 2),
            "bonus_patrocinio": float(emp.get("bonus_patrocinio", 0.0) or 0.0),
            "estrelas": int(emp.get("estrelas", 1) or 1),
        },
    }
    jogador.caixa_email.append(proposta)


def gerar_propostas_carreira_email(jogador, ranking):
    """Dispara geracao semanal de propostas de carreira na caixa de e-mail."""
    gerar_proposta_patrocinio(jogador, ranking)
    gerar_proposta_empresario(jogador, ranking)


def gerar_convites_midia_email(jogador, ranking):
    """Gera convites de midia (TV/comercial) na caixa de e-mail."""
    caixa = getattr(jogador, "caixa_email", [])
    jogador.caixa_email = caixa if isinstance(caixa, list) else []
    posicao = ranking.obter_posicao(jogador.nome) or 9999
    seguidores = int(getattr(jogador, "seguidores", 0) or 0)
    reputacao = int(getattr(jogador, "reputacao_imprensa", 50) or 50)

    chance_base = 0.03
    if posicao <= 200:
        chance_base += 0.04
    if seguidores >= 10000:
        chance_base += 0.04
    if reputacao >= 60:
        chance_base += 0.03
    if random.random() > max(0.03, min(0.26, chance_base)):
        return

    tipo = random.choices(["programa_tv", "comercial"], weights=[0.6, 0.4], k=1)[0]
    ano = int(getattr(jogador, "ano", 2026) or 2026)
    semana = int(getattr(jogador, "semana", 1) or 1)

    if tipo == "programa_tv":
        ganho_seg = random.randint(1200, 6500) + int(reputacao * 12)
        ganho_cash = random.randint(500, 2500)
        proposta = {
            "tipo": "programa_tv",
            "status": "pendente",
            "ref_id": f"tv-{ano}-{semana}-{random.randint(1000, 9999)}",
            "titulo": "Convite: Programa de TV Esportivo",
            "mensagem": (
                "Um programa esportivo quer te entrevistar no horario nobre. "
                "Boa chance de ganhar seguidores."
            ),
            "oferta": {
                "ganho_seguidores": ganho_seg,
                "cache": ganho_cash,
                "fadiga_extra": 4,
            },
        }
    else:
        ganho_cash = random.randint(2500, 12000) + int(
            max(0, (200 - min(posicao, 200))) * 25
        )
        ganho_seg = random.randint(800, 3500)
        proposta = {
            "tipo": "comercial",
            "status": "pendente",
            "ref_id": f"ad-{ano}-{semana}-{random.randint(1000, 9999)}",
            "titulo": "Convite: Gravacao de Comercial",
            "mensagem": (
                "Uma marca quer gravar um comercial com voce nesta semana. "
                "Excelente retorno financeiro."
            ),
            "oferta": {
                "ganho_seguidores": ganho_seg,
                "cache": ganho_cash,
                "fadiga_extra": 6,
            },
        }
    jogador.caixa_email.append(proposta)


def processar_acao_email_carreira(jogador, proposta, acao, ranking):
    """Processa aceitar/recusar em proposta da caixa de e-mail.
    Retorna (sucesso: bool, mensagem: str).
    """
    if not isinstance(proposta, dict):
        return False, "Proposta inválida."
    if proposta.get("status", "pendente") != "pendente":
        return False, "Esta proposta já foi processada."

    tipo = proposta.get("tipo", "")
    if acao not in {"aceitar", "recusar"}:
        return False, "Ação inválida."
    if acao == "recusar":
        proposta["status"] = "recusada"
        if tipo in {"programa_tv", "comercial"}:
            jogador.reputacao_imprensa = max(
                0, int(getattr(jogador, "reputacao_imprensa", 50)) - 1
            )
        return True, "Proposta recusada."

    if tipo == "patrocinio":
        pat_id = proposta.get("ref_id")
        pat = PATROCINADORES_DISPONIVEIS.get(pat_id)
        if not pat:
            proposta["status"] = "expirada"
            return False, "Patrocinador não encontrado."
        posição = ranking.obter_posicao(jogador.nome) or 9999
        seguidores = int(getattr(jogador, "seguidores", 0) or 0)
        pode, motivo = pode_assinar_patrocinio(jogador, pat_id, posição, seguidores)
        if not pode:
            return False, motivo
        jogador.patrocinios.append(pat_id)
        bonus = int(pat.get("bonus_assinatura", 0) or 0)
        if bonus > 0:
            jogador.registrar_transacao(
                bonus,
                f"Bônus Assinatura: {pat.get('nome', pat_id)}",
                categoria="patrocinio",
            )
        proposta["status"] = "aceita"
        return True, f"Contrato assinado com {pat.get('nome', pat_id)}."

    if tipo == "empresario":
        emp_id = proposta.get("ref_id")
        empresarios = _obter_empresarios_disponiveis()
        emp = empresarios.get(emp_id)
        if not emp:
            proposta["status"] = "expirada"
            return False, "Empresário não encontrado."
        oferta = proposta.get("oferta", {})
        salario = int(oferta.get("salario_semanal", emp.get("salario_semanal", 0)) or 0)
        duracao = int(oferta.get("duracao_semanas", 26) or 26)
        emp_atual = getattr(jogador, "empresario", None)
        if isinstance(emp_atual, dict):
            sal_atual = int(emp_atual.get("salario", 0) or 0)
            sem_rest = int(emp_atual.get("semanas_restantes", 0) or 0)
            multa = max(0, (sal_atual // 2) * sem_rest)
            if multa > 0:
                jogador.registrar_transacao(
                    -multa, "Rescisao empresario", categoria="equipe"
                )
        jogador.empresario = {
            "id": emp_id,
            "semanas_restantes": duracao,
            "salario": salario,
        }
        proposta["status"] = "aceita"
        return True, f"{emp.get('nome', emp_id)} agora representa sua carreira."

    if tipo in {"programa_tv", "comercial"}:
        oferta = proposta.get("oferta", {})
        ganho_seg = int(oferta.get("ganho_seguidores", 0) or 0)
        cache = int(oferta.get("cache", 0) or 0)
        fadiga_extra = int(oferta.get("fadiga_extra", 0) or 0)
        jogador.seguidores = max(
            0, int(getattr(jogador, "seguidores", 0) or 0) + ganho_seg
        )
        if cache > 0:
            jogador.registrar_transacao(
                cache, f"Campanha de mídia ({tipo})", categoria="patrocinio"
            )
        jogador.fadiga = min(
            100, int(getattr(jogador, "fadiga", 0) or 0) + fadiga_extra
        )
        jogador.reputacao_imprensa = min(
            100, int(getattr(jogador, "reputacao_imprensa", 50) or 50) + 2
        )
        proposta["status"] = "aceita"
        return True, f"Convite aceito. +{ganho_seg:,} seguidores e +${cache:,}."

    proposta["status"] = "expirada"
    return False, f"Tipo de proposta desconhecido: {tipo}"
