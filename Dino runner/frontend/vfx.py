import math

import pygame

from backend.constants import SCREEN_HEIGHT, SCREEN_WIDTH


class TransformVFX:
    DURATION_MS = 620
    PARTICLE_COUNT = 10
    COLORS = ((115, 245, 205), (255, 218, 112))

    def __init__(self):
        self.surface = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        self.active = False
        self.started_at = 0
        self.world_x = 0
        self.world_y = 0

    def start(self, player):
        self.world_x = player.x + player.size / 2
        self.world_y = player.y + player.size / 2 - 5
        self.started_at = pygame.time.get_ticks()
        self.active = True

    def draw(self, screen, camera_x):
        if not self.active:
            return

        elapsed = pygame.time.get_ticks() - self.started_at
        progress = elapsed / self.DURATION_MS
        if progress >= 1:
            self.active = False
            return

        self.surface.fill((0, 0, 0, 0))
        center_x = round(self.world_x - camera_x)
        center_y = round(self.world_y)
        opacity = round(255 * (1 - progress) ** 1.2)
        ring_radius = round(9 + 31 * progress)

        pygame.draw.circle(
            self.surface,
            (*self.COLORS[0], opacity),
            (center_x, center_y),
            ring_radius,
            2,
        )
        pygame.draw.circle(
            self.surface,
            (*self.COLORS[1], round(opacity * 0.75)),
            (center_x, center_y),
            max(2, ring_radius - 7),
            1,
        )

        for particle_index in range(self.PARTICLE_COUNT):
            angle = (math.tau * particle_index / self.PARTICLE_COUNT) + progress * 1.4
            distance = 10 + 37 * progress
            particle_x = round(center_x + math.cos(angle) * distance)
            particle_y = round(center_y + math.sin(angle) * distance)
            size = max(1, round(4 - 2 * progress))
            color = self.COLORS[particle_index % len(self.COLORS)]
            diamond = (
                (particle_x, particle_y - size),
                (particle_x + size, particle_y),
                (particle_x, particle_y + size),
                (particle_x - size, particle_y),
            )
            pygame.draw.polygon(
                self.surface, (*color, opacity), diamond
            )

        smoke_progress = max(0, (progress - 0.3) / 0.7)
        smoke_opacity = round(245 * (1 - _smoothstep(smoke_progress)))
        if smoke_opacity:
            smoke_width = 42 + round(12 * progress)
            smoke_height = 52 + round(10 * progress)
            smoke_color = (247, 249, 255, smoke_opacity)
            pygame.draw.ellipse(
                self.surface,
                smoke_color,
                pygame.Rect(
                    center_x - smoke_width // 2,
                    center_y - smoke_height // 2,
                    smoke_width,
                    smoke_height,
                ),
            )
            puff_radius = 12 + round(3 * progress)
            for offset_x, offset_y in (
                (-15, -13),
                (15, -13),
                (-17, 7),
                (17, 7),
                (-8, -23),
                (8, 23),
            ):
                pygame.draw.circle(
                    self.surface,
                    smoke_color,
                    (center_x + offset_x, center_y + offset_y),
                    puff_radius,
                )

        screen.blit(self.surface, (0, 0))


def _smoothstep(progress):
    progress = max(0, min(1, progress))
    return progress * progress * (3 - 2 * progress)
