"""
Módulo de Patrocínios (DEPRECATED)
Este módulo foi refatorado para src/services/sponsorship_service.py e src/services/communication_service.py.
Mantido apenas para retrocompatibilidade de imports.
"""

import warnings
from src.services.sponsorship_service import (
    pode_assinar_patrocinio,
    processar_pagamentos_patrocinio,
    migrar_patrocinios,
    resolver_id_patrocinio as _resolver_id_patrocinio,
)
from src.services.communication_service import (
    gerar_proposta_patrocinio,
    gerar_proposta_empresario,
)
from src.dados import carregar_patrocinadores, carregar_staff

warnings.warn(
    "O módulo src.patrocinios está depreciado. Use src.services.sponsorship_service.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-exporting constants for compatibility
PATROCINADORES_DISPONIVEIS = carregar_patrocinadores()


def gerar_propostas_carreira_email(jogador, ranking):
    from src.services.communication_service import (
        gerar_proposta_patrocinio,
        gerar_proposta_empresario,
    )

    gerar_proposta_patrocinio(jogador, ranking)
    gerar_proposta_empresario(jogador, ranking)


def gerar_convites_midia_email(jogador, ranking):
    """Shim legado: convites de mídia foram aposentados no fluxo frontend+backend atual."""
    return None


def processar_acao_email_carreira(jogador, proposta, acao, ranking):
    from src.services.communication_service import processar_acao_email

    return processar_acao_email(jogador, proposta, acao, ranking)


# Mocking legacy globals that might be used
LIMITE_PATROCINIO_MASTER = 1
LIMITE_PATROCINIO_MENORES = 3
