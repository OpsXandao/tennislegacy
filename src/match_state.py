from dataclasses import dataclass
from enum import Enum


@dataclass
class EstatisticasPartida:
    """Estatísticas coletadas durante uma partida."""

    aces: int = 0
    duplas_faltas: int = 0
    primeiro_saque_in: int = 0
    primeiro_saque_total: int = 0
    winners: int = 0
    erros_nao_forcados: int = 0
    pontos_ganhos_saque: int = 0
    pontos_total_saque: int = 0
    pontos_ganhos_devolucao: int = 0
    pontos_total_devolucao: int = 0
    break_points_convertidos: int = 0
    break_points_total: int = 0
    break_points_salvos: int = 0
    break_points_enfrentados: int = 0
    rallies_curtos: int = 0
    rallies_medios: int = 0
    rallies_longos: int = 0

    def percentual_primeiro_saque(self) -> str:
        if self.primeiro_saque_total == 0:
            return "0%"
        pct = (self.primeiro_saque_in / self.primeiro_saque_total) * 100
        return f"{pct:.0f}%"

    def percentual_pontos_saque(self) -> str:
        if self.pontos_total_saque == 0:
            return "0%"
        pct = (self.pontos_ganhos_saque / self.pontos_total_saque) * 100
        return f"{pct:.0f}%"

    def percentual_pontos_devolucao(self) -> str:
        if self.pontos_total_devolucao == 0:
            return "0%"
        pct = (self.pontos_ganhos_devolucao / self.pontos_total_devolucao) * 100
        return f"{pct:.0f}%"

    def merge(self, other: "EstatisticasPartida"):
        self.aces += other.aces
        self.duplas_faltas += other.duplas_faltas
        self.primeiro_saque_in += other.primeiro_saque_in
        self.primeiro_saque_total += other.primeiro_saque_total
        self.winners += other.winners
        self.erros_nao_forcados += other.erros_nao_forcados
        self.pontos_ganhos_saque += other.pontos_ganhos_saque
        self.pontos_total_saque += other.pontos_total_saque
        self.pontos_ganhos_devolucao += other.pontos_ganhos_devolucao
        self.pontos_total_devolucao += other.pontos_total_devolucao
        self.break_points_convertidos += other.break_points_convertidos
        self.break_points_total += other.break_points_total
        self.break_points_salvos += other.break_points_salvos
        self.break_points_enfrentados += other.break_points_enfrentados
        self.rallies_curtos += other.rallies_curtos
        self.rallies_medios += other.rallies_medios
        self.rallies_longos += other.rallies_longos

    def exibir(
        self,
        nome_jogador: str,
        nome_adversario: str,
        stats_adversario: "EstatisticasPartida",
    ) -> str:
        bp_j = f"{self.break_points_convertidos}/{self.break_points_total}"
        bp_a = f"{stats_adversario.break_points_convertidos}/{stats_adversario.break_points_total}"
        linhas = [
            f"\n{'='*55}",
            f"{'ESTATISTICAS':^55}",
            f"{'='*55}",
            f"{'':25} {'Voce':>12} {'Adversario':>15}",
            f"{'-'*55}",
            f"{'Aces':<25} {self.aces:>12} {stats_adversario.aces:>15}",
            f"{'Duplas Faltas':<25} {self.duplas_faltas:>12} {stats_adversario.duplas_faltas:>15}",
            f"{'1o Saque %':<25} {self.percentual_primeiro_saque():>12} {stats_adversario.percentual_primeiro_saque():>15}",
            f"{'Winners':<25} {self.winners:>12} {stats_adversario.winners:>15}",
            f"{'Erros Nao Forcados':<25} {self.erros_nao_forcados:>12} {stats_adversario.erros_nao_forcados:>15}",
            f"{'Pontos no Saque %':<25} {self.percentual_pontos_saque():>12} {stats_adversario.percentual_pontos_saque():>15}",
            f"{'Pontos na Devolucao %':<25} {self.percentual_pontos_devolucao():>12} {stats_adversario.percentual_pontos_devolucao():>15}",
            f"{'Break Points':<25} {bp_j:>12} {bp_a:>15}",
            f"{'='*55}",
        ]
        return "\n".join(linhas)


class TipoGolpe(Enum):
    ACE = "ace"
    DUPLA_FALTA = "dupla_falta"
    WINNER_FOREHAND = "winner_forehand"
    WINNER_BACKHAND = "winner_backhand"
    WINNER_VOLEIO = "winner_voleio"
    ERRO_NAO_FORCADO = "erro_nao_forcado"
    PONTO_CONSTRUIDO = "ponto_construido"
    DROP_SHOT = "drop_shot"
    LOB_WINNER = "lob_winner"
    SAQUE_EM_JOGO = "saque_em_jogo"


@dataclass
class ContextoPonto:
    """Contexto do ponto atual na partida."""

    sacador: str
    placar_game: tuple
    placar_set: tuple
    placar_partida: tuple
    sets_para_vencer: int = 2
    is_tiebreak: bool = False
    tiebreak_alvo: int = 7

    def is_break_point(self) -> bool:
        if self.is_tiebreak:
            return False
        pj, pa = self.placar_game
        if self.sacador == "j":
            return pa >= 3 and pa > pj
        return pj >= 3 and pj > pa

    def is_set_point(self) -> bool:
        pj, pa = self.placar_game
        if self.is_tiebreak:
            alvo = max(2, int(self.tiebreak_alvo or 7))
            return (pj >= alvo - 1 and pj > pa) or (pa >= alvo - 1 and pa > pj)

        gj, ga = self.placar_set
        if gj >= 5 and gj > ga and pj >= 3 and pj > pa:
            return True
        if ga >= 5 and ga > gj and pa >= 3 and pa > pj:
            return True
        return False

    def is_match_point(self) -> bool:
        sj, sa = self.placar_partida
        pj, pa = self.placar_game

        if self.is_tiebreak:
            alvo = max(2, int(self.tiebreak_alvo or 7))
            jogador_tem_set_point = pj >= alvo - 1 and pj > pa
            adversario_tem_set_point = pa >= alvo - 1 and pa > pj
            if sj == self.sets_para_vencer - 1 and jogador_tem_set_point:
                return True
            if sa == self.sets_para_vencer - 1 and adversario_tem_set_point:
                return True
            return False

        gj, ga = self.placar_set
        if (
            sj == self.sets_para_vencer - 1
            and gj >= 5
            and gj > ga
            and pj >= 3
            and pj > pa
        ):
            return True
        if (
            sa == self.sets_para_vencer - 1
            and ga >= 5
            and ga > gj
            and pa >= 3
            and pa > pj
        ):
            return True
        return False

    def jogador_perdendo(self) -> bool:
        gj, ga = self.placar_set
        return ga >= gj + 2

    def adversario_perdendo(self) -> bool:
        gj, ga = self.placar_set
        return gj >= ga + 2


@dataclass
class ContextoPartida:
    """Contexto geral da partida."""

    superficie: str = "dura"
    stamina_j: float = 100.0
    stamina_a: float = 100.0
    moral_j: float = 70.0
    moral_a: float = 70.0
    ritmo_j: float = 50.0
    ritmo_a: float = 50.0
    momentum_j: int = 0
    momentum_a: int = 0
    clima: str = "ameno"
    vento: int = 0
    umidade: int = 50
    altitude_m: int = 0
    indoor: bool = False
    sequencia_j: int = 0
    sequencia_a: int = 0
    ultimo_vencedor: str | None = None
    condicao_j: int = 100
    condicao_a: int = 100
    set_atual: int = 1
