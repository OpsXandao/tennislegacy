def is_grand_slam(tipo: str) -> bool:
    return str(tipo or "") == "Grand Slam"

def is_atp_1000(tipo: str) -> bool:
    return "1000" in str(tipo or "")

def is_finals(tipo: str) -> bool:
    v = str(tipo or "")
    return v in {"ATP Finals", "WTA Finals", "Next Gen ATP Finals"}

def is_davis_cup(tipo: str) -> bool:
    return str(tipo or "") in {"Davis Cup", "Billie Jean King Cup"}

def is_merge_phase_to_main_draw(fase: str, proxima_fase: str, merge_transitions: list) -> bool:
    return (fase, proxima_fase) in merge_transitions

def multiplicador_desgaste_segundo_jogo(tipo: str) -> float:
    if is_grand_slam(tipo): return 1.4
    if is_atp_1000(tipo): return 1.25
    return 1.15

def multiplicador_recuperacao_mesmo_dia(tipo: str) -> float:
    if is_grand_slam(tipo): return 0.7
    if is_atp_1000(tipo): return 0.85
    return 1.0

def estimar_pressao_adversario(ranking_pos: int) -> float:
    if ranking_pos <= 10: return 0.9
    if ranking_pos <= 50: return 0.7
    return 0.4
