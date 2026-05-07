import unittest

from scripts.fetch_real_data import (
    build_local_player_bio_index,
    classify_title_category,
    parse_hand_code,
    parse_height_cm,
    parse_plays,
    parse_weight_kg,
    resolve_local_sackmann_dir,
)


class FetchRealDataTests(unittest.TestCase):
    def test_parse_height_cm_from_metric(self):
        self.assertEqual(parse_height_cm("1.88 m (6 ft 2 in)"), 188)
        self.assertEqual(parse_height_cm("182 cm"), 182)

    def test_parse_weight_kg_from_metric_and_imperial(self):
        self.assertEqual(parse_weight_kg("77 kg (170 lb)"), 77)
        self.assertEqual(parse_weight_kg("170 lb"), 77)

    def test_parse_plays_detects_handedness_and_backhand(self):
        self.assertEqual(parse_plays("Right-handed (two-handed backhand)"), ("Destro", "Duas mãos"))
        self.assertEqual(parse_plays("Left-handed (one-handed backhand)"), ("Canhoto", "Uma mão"))

    def test_parse_hand_code_maps_sackmann_codes(self):
        self.assertEqual(parse_hand_code("R"), "Destro")
        self.assertEqual(parse_hand_code("R", genero="feminino"), "Destra")
        self.assertEqual(parse_hand_code("L"), "Canhoto")
        self.assertIsNone(parse_hand_code("U"))

    def test_classify_title_category_handles_core_levels(self):
        self.assertEqual(
            classify_title_category("atp", {"tourney_level": "G", "tourney_name": "Wimbledon"}),
            "Grand Slam",
        )
        self.assertEqual(
            classify_title_category("atp", {"tourney_level": "A", "tourney_name": "Paris Olympics"}),
            "Olympics",
        )
        self.assertEqual(
            classify_title_category("atp", {"tourney_level": "M", "tourney_name": "Miami"}),
            "ATP 1000",
        )
        self.assertEqual(
            classify_title_category("wta", {"tourney_level": "F", "tourney_name": "WTA Finals Riyadh"}),
            "WTA Finals",
        )

    def test_classify_title_category_uses_name_fallback_for_tour_events(self):
        self.assertEqual(
            classify_title_category("atp", {"tourney_level": "A", "tourney_name": "Barcelona Open"}),
            "ATP 500",
        )
        self.assertEqual(
            classify_title_category("wta", {"tourney_level": "A", "tourney_name": "Berlin Ladies Open"}),
            "WTA 500",
        )
        self.assertEqual(
            classify_title_category("wta", {"tourney_level": "A", "tourney_name": "Hong Kong Open"}),
            "WTA 250",
        )

    def test_build_local_player_bio_index_reads_local_sackmann_csv(self):
        self.assertIsNotNone(resolve_local_sackmann_dir("atp"))
        bios = build_local_player_bio_index("atp")
        novak = bios["novak djokovic"]
        self.assertEqual(novak["altura"], 188)
        self.assertEqual(novak["mao_dominante"], "Destro")


if __name__ == "__main__":
    unittest.main()
