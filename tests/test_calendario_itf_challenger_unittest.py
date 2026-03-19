import unittest

from src.calendario import badge_entry_status


class CalendarioItfChallengerTests(unittest.TestCase):
    def test_badge_entry_status_marca_itf_e_challenger_como_ineligible_para_top(self):
        self.assertEqual(
            badge_entry_status(95, {"tipo": "Challenger 125"}),
            "[Ineligible]",
        )
        self.assertEqual(
            badge_entry_status(180, {"tipo": "ITF 100"}),
            "[Ineligible]",
        )

    def test_badge_entry_status_estima_main_draw_para_elegivel_no_challenger(self):
        self.assertEqual(
            badge_entry_status(118, {"tipo": "Challenger 125"}),
            "[Main Draw]",
        )


if __name__ == "__main__":
    unittest.main()
