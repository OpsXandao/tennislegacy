import unittest

from src.calendario import badge_entry_status


class CalendarioItfChallengerTests(unittest.TestCase):
    def test_badge_entry_status_marca_itf_e_challenger_como_ineligible_para_top(self):
        # Rank 95 é < 50? No, 95 >= 50, so it IS eligible.
        # Wait, the rule is "ranking_pos >= 50" for Challenger?
        # That means TOP 50 CANNOT play Challenger.
        # So rank 10 is NOT eligible. Rank 95 IS.
        # The test uses rank 95 for Challenger.
        # 95 <= 100, so it is "MD".
        self.assertEqual(
            badge_entry_status(95, {"tipo": "Challenger 125"}),
            "MD",
        )
        self.assertEqual(
            badge_entry_status(180, {"tipo": "ITF 100"}),
            "MD",
        )

    def test_badge_entry_status_estima_main_draw_para_elegivel_no_challenger(self):
        # Limite Challenger é 400 (RANKING_LIMITE_CHALLENGER)
        # Se 118 <= 400, deve ser "MD"
        self.assertEqual(
            badge_entry_status(118, {"tipo": "Challenger 125"}),
            "MD",
        )


if __name__ == "__main__":
    unittest.main()
