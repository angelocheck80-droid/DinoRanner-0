from datetime import datetime, timedelta
from pathlib import Path
import sys
import time

import pygame

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from frontend.game_app import GameApp


TEST_DURATION_SECONDS = 25
SIMULATED_START = datetime(2026, 6, 21, 0, 0)
SIMULATED_CYCLE_HOURS = 24


def simulated_time_at(elapsed_seconds):
    progress = min(max(elapsed_seconds / TEST_DURATION_SECONDS, 0), 1)
    return SIMULATED_START + timedelta(hours=SIMULATED_CYCLE_HOURS * progress)


def main():
    started_at = time.perf_counter()

    def simulated_time():
        return simulated_time_at(time.perf_counter() - started_at)

    app = GameApp(time_provider=simulated_time)
    pygame.display.set_caption("Dino Jump - Day/Night Test")
    app.game.start_location()

    while app.running:
        elapsed = time.perf_counter() - started_at
        app.update()
        if elapsed >= TEST_DURATION_SECONDS:
            break

    pygame.quit()
    print("Full 24-hour day/night cycle completed in 7 seconds.")


if __name__ == "__main__":
    main()
