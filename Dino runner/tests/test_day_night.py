import unittest
from datetime import datetime

from backend.day_night import (
    MAX_NIGHT_OPACITY,
    night_opacity,
    night_gradient_strength,
    twilight_glow_strength,
)


class DayNightTests(unittest.TestCase):
    def test_night_is_dark_and_midday_is_clear(self):
        self.assertEqual(night_opacity(datetime(2026, 1, 1, 0)), MAX_NIGHT_OPACITY)
        self.assertEqual(night_opacity(datetime(2026, 1, 1, 12)), 0)

    def test_dawn_gradually_gets_brighter(self):
        early_dawn = night_opacity(datetime(2026, 1, 1, 5, 30))
        late_dawn = night_opacity(datetime(2026, 1, 1, 7, 30))

        self.assertGreater(early_dawn, late_dawn)
        self.assertGreater(late_dawn, 0)

    def test_dusk_gradually_gets_darker(self):
        early_dusk = night_opacity(datetime(2026, 1, 1, 16, 30))
        late_dusk = night_opacity(datetime(2026, 1, 1, 18, 30))

        self.assertLess(early_dusk, late_dusk)
        self.assertLess(early_dusk, MAX_NIGHT_OPACITY)

    def test_night_gradient_follows_the_full_night_and_fades_at_dawn(self):
        self.assertEqual(night_gradient_strength(datetime(2026, 1, 1, 16)), 0)
        self.assertAlmostEqual(
            night_gradient_strength(datetime(2026, 1, 1, 17, 30)), 0.5
        )
        self.assertEqual(night_gradient_strength(datetime(2026, 1, 1, 19)), 1)
        self.assertEqual(night_gradient_strength(datetime(2026, 1, 1, 23)), 1)
        self.assertEqual(night_gradient_strength(datetime(2026, 1, 2, 4)), 1)
        self.assertAlmostEqual(
            night_gradient_strength(datetime(2026, 1, 2, 6, 30)), 0.5
        )
        self.assertEqual(night_gradient_strength(datetime(2026, 1, 2, 8)), 0)

    def test_twilight_flashes_peak_at_sunset_and_dawn_then_fade(self):
        self.assertEqual(
            twilight_glow_strength(datetime(2026, 1, 1, 19)), 1
        )
        self.assertEqual(
            twilight_glow_strength(datetime(2026, 1, 1, 20)), 0.5
        )
        self.assertEqual(twilight_glow_strength(datetime(2026, 1, 1, 21)), 0)
        self.assertEqual(twilight_glow_strength(datetime(2026, 1, 1, 5)), 1)
        self.assertEqual(twilight_glow_strength(datetime(2026, 1, 1, 8)), 0)

    def test_sun_and_moon_fade_oppositely_through_the_day_night_cycle(self):
        noon = night_opacity(datetime(2026, 1, 1, 12))
        dusk = night_opacity(datetime(2026, 1, 1, 17, 30))
        night = night_opacity(datetime(2026, 1, 1, 19))

        self.assertEqual(1 - noon / MAX_NIGHT_OPACITY, 1)
        self.assertEqual(noon / MAX_NIGHT_OPACITY, 0)
        self.assertEqual(dusk / MAX_NIGHT_OPACITY, 0.5)
        self.assertEqual(1 - dusk / MAX_NIGHT_OPACITY, 0.5)
        self.assertEqual(night / MAX_NIGHT_OPACITY, 1)
        self.assertEqual(1 - night / MAX_NIGHT_OPACITY, 0)


if __name__ == "__main__":
    unittest.main()
