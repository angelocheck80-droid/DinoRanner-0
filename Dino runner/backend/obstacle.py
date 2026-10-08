import random

import pygame

from backend.constants import GROUND_Y


class Obstacle:
    def __init__(self, x, width=None, height=None, speed=5):
        self.x = x
        sprite_name = random.choice(("rock.png", "blush.png"))
        self.sprite_name = sprite_name
        default_width, default_height = (75, 60) if sprite_name == "blush.png" else (50, 55)
        self.width = width if width is not None else default_width
        self.height = height if height is not None else default_height
        self.speed = speed
        self.y = GROUND_Y - self.height

    @property
    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def update(self):
        self.x -= self.speed

    def collides_with(self, dino):
        dino_rect = pygame.Rect(dino.x, dino.y, dino.size, dino.size)
        return self.rect.colliderect(dino_rect)

