import unittest
from datetime import timedelta

from backend.day_night import MAX_NIGHT_OPACITY, night_opacity
from tools.day_night_demo import (
    SIMULATED_START,
    TEST_DURATION_SECONDS,
    simulated_time_at,
)


class DayNightDemoTests(unittest.TestCase):
    def test_seven_seconds_cover_a_full_day_and_return_to_night(self):
        checkpoints = (
            0,
            TEST_DURATION_SECONDS * 5 / 24,
            TEST_DURATION_SECONDS * 8 / 24,
            TEST_DURATION_SECONDS * 16 / 24,
            TEST_DURATION_SECONDS * 19 / 24,
            TEST_DURATION_SECONDS,
        )
        expected_opacity = (
            MAX_NIGHT_OPACITY,
            MAX_NIGHT_OPACITY,
            0,
            0,
            MAX_NIGHT_OPACITY,
            MAX_NIGHT_OPACITY,
        )

        self.assertEqual(
            simulated_time_at(TEST_DURATION_SECONDS),
            SIMULATED_START + timedelta(days=1),
        )
        self.assertEqual(
            [night_opacity(simulated_time_at(point)) for point in checkpoints],
            list(expected_opacity),
        )

    def test_elapsed_time_is_clamped_to_the_complete_cycle(self):
        end_of_cycle = SIMULATED_START + timedelta(days=1)
        self.assertEqual(simulated_time_at(TEST_DURATION_SECONDS + 5), end_of_cycle)


if __name__ == "__main__":
    unittest.main()
