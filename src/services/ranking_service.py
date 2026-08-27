from src.repositories.ranking_repository import load_all_rankings

def migrar_rankings_semana_se_preciso(rankings: dict, semana_atual: int, ano_atual: int):
    """Garante que os rankings acompanhem a semana da temporada."""
    for r_obj in rankings.values():
        if hasattr(r_obj, "semana") and r_obj.semana != semana_atual:
            r_obj.semana = semana_atual
            r_obj.ano = ano_atual
            r_obj.salvar_ranking()

def calcular_expiracao_pontos(semana_atual: int, ano_atual: int) -> tuple[int, int]:
    # Pontos expiram depois de 52 semanas
    ano_expiracao = ano_atual - 1
    semana_expiracao = semana_atual
    return semana_expiracao, ano_expiracao

def processar_expiracao_ranking(nome_save: str, semana_atual: int, ano_atual: int):
    sem_exp, ano_exp = calcular_expiracao_pontos(semana_atual, ano_atual)
    rankings = load_all_rankings(nome_save)
    for r_obj in rankings.values():
        if hasattr(r_obj, "expirar_pontos"):
            r_obj.expirar_pontos(sem_exp, ano_exp)
            r_obj.salvar_ranking()
