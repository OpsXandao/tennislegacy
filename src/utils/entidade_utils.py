def obter_atributos(entidade) -> dict:
    if hasattr(entidade, "atributos"):
        return entidade.atributos
    if isinstance(entidade, dict):
        return entidade.get("atributos", {})
    return {}


def obter_atributos_psicologicos(entidade, copiar: bool = False) -> dict:
    if hasattr(entidade, "atributos_psicologicos"):
        psico = entidade.atributos_psicologicos
    elif isinstance(entidade, dict):
        psico = entidade.get("atributos_psicologicos", {})
    else:
        psico = {}
    if copiar:
        return psico.copy()
    return psico
