from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from src.dados import carregar_patrocinadores

# Mapa de retrocompatibilidade para IDs antigos
_MAPA_PATROCINIO_LEGADO = {
    "raquete_local": "racket_local",
    "vestuario_pro": "clothing_regional",
    "raquete_pro": "racket_pro",
    "banco_master": "bank_global",
}

_CATEGORIAS_MATERIAL_ESPORTIVO = {"raquete", "vestuario", "calcado", "acessorios"}
_CONTRATO_DURACAO_SEMANAS = {"master": 16, "menor": 12}


# ---------------------------------------------------------------------------
# Funções puras de leitura de dados do jogador
# ---------------------------------------------------------------------------


def _total_vitorias_carreira(jogador: Any) -> int:
    historico = getattr(jogador, "historico_partidas", []) or []
    return sum(
        1
        for item in historico
        if isinstance(item, dict) and item.get("resultado") == "V"
    )


def _total_titulos_carreira(jogador: Any) -> int:
    trofeus = getattr(jogador, "trofeus", None)
    if isinstance(trofeus, list):
        return len(trofeus)
    historico = getattr(jogador, "historico_torneios", []) or []
    return sum(
        1 for item in historico if isinstance(item, dict) and item.get("campeao")
    )


def _ranking_referencia(jogador: Any, posicao: Optional[int]) -> int:
    if isinstance(posicao, int) and posicao > 0:
        return posicao
    historico = getattr(jogador, "historico_ranking", []) or []
    if historico:
        ultimo = historico[-1]
        if isinstance(ultimo, dict):
            valor = int(ultimo.get("posicao", 0) or 0)
            if valor > 0:
                return valor
    return 9999


# ---------------------------------------------------------------------------
# Funções puras de dados de patrocinador
# ---------------------------------------------------------------------------


def _duracao_contrato_semanas(patrocinador: Dict[str, Any]) -> int:
    tier = str(patrocinador.get("tier", "menor")).strip().lower()
    return _CONTRATO_DURACAO_SEMANAS.get(tier, 12)


def _perfil_marca(patrocinador: Dict[str, Any]) -> str:
    categoria = str(patrocinador.get("categoria", "")).strip().lower()
    tier = str(patrocinador.get("tier", "menor")).strip().lower()
    if tier == "master":
        return "elite global"
    if categoria in {"vestuario", "relogio", "automovel"}:
        return "visibilidade"
    if categoria in {"raquete", "tecnologia"}:
        return "performance"
    return "consistencia"


def _patrocinador_master_valido(patrocinador: dict) -> bool:
    """Verifica se um patrocinador master é de categoria permitida (material esportivo)."""
    if not isinstance(patrocinador, dict):
        return False
    if patrocinador.get("tier") != "master":
        return True
    categoria = str(patrocinador.get("categoria", "")).strip().lower()
    return categoria in _CATEGORIAS_MATERIAL_ESPORTIVO


# ---------------------------------------------------------------------------
# Criação de metas (estrutura de dados pura)
# ---------------------------------------------------------------------------


def _criar_meta(
    meta_id: str,
    titulo: str,
    descricao: str,
    atual: int,
    alvo: int,
    unidade: str,
    direcao: str,
    tom: str,
) -> Dict[str, Any]:
    if direcao == "min":
        if atual <= alvo:
            status = "ok"
            progresso = 100
        elif atual <= alvo + max(2, alvo // 10):
            status = "atencao"
            progresso = 65
        else:
            status = "risco"
            progresso = 30
    else:
        if atual >= alvo:
            status = "ok"
            progresso = 100
        elif alvo <= 0:
            status = "ok"
            progresso = 100
        else:
            ratio = max(0.0, min(1.0, atual / alvo))
            if ratio >= 0.8:
                status = "atencao"
            else:
                status = "risco"
            progresso = int(ratio * 100)
    return {
        "id": meta_id,
        "titulo": titulo,
        "descricao": descricao,
        "atual": int(atual),
        "alvo": int(alvo),
        "unidade": unidade,
        "direcao": direcao,
        "status": status,
        "progresso": progresso,
        "tom": tom,
    }


def _status_contrato(metas: List[Dict[str, Any]]) -> Tuple[str, int]:
    if not metas:
        return "em_dia", 100
    confianca = int(
        sum(int(meta.get("progresso", 0) or 0) for meta in metas) / len(metas)
    )
    if confianca >= 80:
        return "em_dia", confianca
    if confianca >= 55:
        return "sob_pressao", confianca
    return "em_risco", confianca


# ---------------------------------------------------------------------------
# Resolução/normalização de IDs e listas
# ---------------------------------------------------------------------------


def resolver_id_patrocinio(
    item: Any, sponsors: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """Resolve ID legado, dicionário ou nome para um ID de patrocinador válido."""
    if not item:
        return None

    if sponsors is None:
        sponsors = carregar_patrocinadores()

    if isinstance(item, dict):
        if item.get("id"):
            item = item.get("id")
        elif item.get("nome"):
            nome = str(item.get("nome", "")).strip().lower()
            for pid, pat in sponsors.items():
                if str(pat.get("nome", "")).strip().lower() == nome:
                    return pid
            return None
        else:
            return None

    if not isinstance(item, str):
        item = str(item)

    # Tenta resolver ID legado
    novo_id = _MAPA_PATROCINIO_LEGADO.get(item, item)
    return novo_id if novo_id in sponsors else None


def _normalizar_lista_patrocinios(jogador: Any) -> List[Any]:
    patrocinios = getattr(jogador, "patrocinios", [])
    if not isinstance(patrocinios, list):
        return []
    return patrocinios


def _normalizar_ids_patrocinios(
    patrocinios: List[Any], sponsors: Optional[Dict[str, Any]] = None
) -> List[str]:
    if sponsors is None:
        sponsors = carregar_patrocinadores()

    ids: List[str] = []
    for item in patrocinios:
        pat_id = resolver_id_patrocinio(item, sponsors)
        if pat_id and pat_id not in ids:
            ids.append(pat_id)
    return ids


# ---------------------------------------------------------------------------
# Normalização de contratos ativos e cálculo de metas
# ---------------------------------------------------------------------------


def _normalizar_contrato_ativo(
    item: Any,
    jogador: Any,
    posicao: Optional[int],
    sponsors: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    if sponsors is None:
        sponsors = carregar_patrocinadores()

    pat_id = resolver_id_patrocinio(item, sponsors)
    if not pat_id:
        return None
    patrocinador = sponsors.get(pat_id)
    if not patrocinador:
        return None

    referencia_ranking = _ranking_referencia(jogador, posicao)
    seguidores = int(getattr(jogador, "seguidores", 0) or 0)
    vitorias = _total_vitorias_carreira(jogador)
    titulos = _total_titulos_carreira(jogador)
    duracao = _duracao_contrato_semanas(patrocinador)

    if isinstance(item, dict):
        semanas_restantes = int(
            item.get("semanas_restantes", item.get("duracao_semanas", duracao))
            or duracao
        )
        contrato = {
            "id": pat_id,
            "semanas_restantes": semanas_restantes,
            "duracao_semanas": int(item.get("duracao_semanas", duracao) or duracao),
            "ranking_assinatura": int(
                item.get("ranking_assinatura", referencia_ranking) or referencia_ranking
            ),
            "seguidores_assinatura": int(
                item.get("seguidores_assinatura", seguidores) or seguidores
            ),
            "vitorias_assinatura": int(
                item.get("vitorias_assinatura", vitorias) or vitorias
            ),
            "titulos_assinatura": int(
                item.get("titulos_assinatura", titulos) or titulos
            ),
        }
    else:
        contrato = {
            "id": pat_id,
            "semanas_restantes": duracao,
            "duracao_semanas": duracao,
            "ranking_assinatura": referencia_ranking,
            "seguidores_assinatura": seguidores,
            "vitorias_assinatura": vitorias,
            "titulos_assinatura": titulos,
        }

    return contrato


def _metas_contrato_ativo(
    contrato: Dict[str, Any],
    patrocinador: Dict[str, Any],
    jogador: Any,
    posicao: Optional[int],
) -> List[Dict[str, Any]]:
    ranking_atual = _ranking_referencia(jogador, posicao)
    seguidores_atuais = int(getattr(jogador, "seguidores", 0) or 0)
    vitorias_atuais = _total_vitorias_carreira(jogador)
    titulos_atuais = _total_titulos_carreira(jogador)

    tier = str(patrocinador.get("tier", "menor")).strip().lower()
    perfil = _perfil_marca(patrocinador)
    seguidores_base = int(
        contrato.get("seguidores_assinatura", seguidores_atuais) or seguidores_atuais
    )
    vitorias_base = int(
        contrato.get("vitorias_assinatura", vitorias_atuais) or vitorias_atuais
    )
    titulos_base = int(
        contrato.get("titulos_assinatura", titulos_atuais) or titulos_atuais
    )

    metas: List[Dict[str, Any]] = []
    requisito_ranking = int(patrocinador.get("requisito_ranking", 0) or 0)
    if requisito_ranking > 0:
        metas.append(
            _criar_meta(
                "ranking",
                "Presença no ranking",
                f"Manter o contrato dentro do Top {requisito_ranking}.",
                ranking_atual,
                requisito_ranking,
                "ranking",
                "min",
                "warning" if tier == "master" else "info",
            )
        )

    requisito_seguidores = int(patrocinador.get("req_seguidores", 0) or 0)
    alvo_seguidores = max(
        requisito_seguidores,
        seguidores_base
        + (20000 if perfil == "visibilidade" else 12000 if tier == "master" else 5000),
    )
    metas.append(
        _criar_meta(
            "seguidores",
            "Audiência da marca",
            "Fazer a marca crescer junto com a sua exposição.",
            seguidores_atuais,
            alvo_seguidores,
            "seguidores",
            "max",
            "info",
        )
    )

    alvo_vitorias = 7 if tier == "master" else 4
    if perfil == "performance":
        alvo_vitorias += 2
    metas.append(
        _criar_meta(
            "vitorias",
            "Vitórias no contrato",
            "Entregar resultado em quadra durante a vigência.",
            max(0, vitorias_atuais - vitorias_base),
            alvo_vitorias,
            "vitorias",
            "max",
            "positive",
        )
    )

    if tier == "master":
        metas.append(
            _criar_meta(
                "titulos",
                "Impacto esportivo",
                "Conquistar pelo menos um título durante o vínculo.",
                max(0, titulos_atuais - titulos_base),
                1,
                "titulos",
                "max",
                "warning",
            )
        )

    return metas
