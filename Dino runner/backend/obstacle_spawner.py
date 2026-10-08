import random

from backend.constants import SCREEN_WIDTH
from backend.obstacle import Obstacle


class ObstacleSpawner:
    def __init__(self, min_delay=60, max_delay=120):
        self.obstacles = [Obstacle(SCREEN_WIDTH + 120)]
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.spawn_timer = random.randint(min_delay, max_delay)

    def update(self, moving_right=False, spawn_x=SCREEN_WIDTH):
        if not moving_right:
            return

        for obstacle in self.obstacles:
            obstacle.update()

        self.obstacles = [
            obstacle
            for obstacle in self.obstacles
            if obstacle.x + obstacle.width >= 0
        ]

        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            self.obstacles.append(Obstacle(spawn_x))
            self.spawn_timer = random.randint(self.min_delay, self.max_delay)

    def collides_with(self, dino):
        return any(obstacle.collides_with(dino) for obstacle in self.obstacles)

