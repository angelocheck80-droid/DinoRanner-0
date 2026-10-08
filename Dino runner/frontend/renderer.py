from pathlib import Path

import pygame

from backend.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from backend.day_night import night_opacity
from frontend.hud import HUD
from frontend.location_renderer import LocationRenderer
from frontend.vfx import TransformVFX


class GameRenderer:
    def __init__(self, time_provider=None):
        self.time_provider = time_provider
        assets_path = Path(__file__).parent.parent / "UI"
        player_files = {
            "idle": "Dino_idle.png",
            "jump": "Dino_jump.png",
            "run": "Dino_run.png",
        }
        self.player_images = {
            name: pygame.transform.scale(
                pygame.image.load(assets_path / filename).convert_alpha(), (50, 50)
            )
            for name, filename in player_files.items()
        }
        self.player_bottom_offsets = {
            name: image.get_height() - image.get_bounding_rect(min_alpha=1).bottom
            for name, image in self.player_images.items()
        }
        dragon_human_source = pygame.image.load(
            assets_path / "Композиция 1" / "man1_00000.png"
        ).convert_alpha()
        self.dragon_human_image = pygame.transform.smoothscale(
            dragon_human_source, (48, 62)
        )
        obstacle_path = assets_path / "Obstacle_sprites"
        self.obstacle_images = {
            name: pygame.image.load(obstacle_path / name).convert_alpha()
            for name in ("rock.png", "blush.png")
        }
        self.hud = HUD()
        self.location_renderer = LocationRenderer()
        self.transform_vfx = TransformVFX()

    def play_transform_effect(self, player):
        self.transform_vfx.start(player)

    def draw(self, screen, game, inventory_ui):
        if game.state == "menu":
            screen.fill((0, 0, 0))
            self.hud.draw_menu(screen)
        elif game.state == "location":
            current_time = self.time_provider() if self.time_provider else None
            opacity = (
                night_opacity(current_time) if not game.location.inside else 0
            )
            self.location_renderer.draw(
                screen,
                game.location,
                game.dino,
                game.camera_x,
                opacity,
                current_time,
            )
            self._draw_player(screen, game.dino, game.camera_x)
            self.transform_vfx.draw(screen, game.camera_x)
            self.hud.draw_hp(screen, game.hp)
            if game.dialogue_active:
                dialogue_anchor = (
                    game.location.npc_x - game.camera_x + game.location.npc_w // 2,
                    game.location.npc_y,
                )
                self.hud.draw_dialog(
                    screen,
                    game.location.npc_name,
                    game.dialogue_text,
                    dialogue_anchor,
                    game.dialogue_alpha,
                )
            if inventory_ui.visible:
                panel_pos = inventory_ui.get_centered_pos(
                    SCREEN_WIDTH, SCREEN_HEIGHT
                )
                inventory_ui.draw(screen, panel_pos)

    def draw_obstacles(self, screen, obstacle_spawner, camera_x=0):
        for obstacle in obstacle_spawner.obstacles:
            image = pygame.transform.scale(
                self.obstacle_images[obstacle.sprite_name],
                (obstacle.width, obstacle.height),
            )
            screen.blit(image, (obstacle.x - camera_x, obstacle.y))

    def _draw_player(self, screen, player, camera_x):
        if player.form == "dragon_human":
            image = self.dragon_human_image
            if player.direction < 0:
                image = pygame.transform.flip(image, True, False)
            screen.blit(
                image,
                (
                    player.x - camera_x - (image.get_width() - player.size) // 2,
                    player.y + player.size - image.get_height(),
                ),
            )
            return

        if player.jumping:
            image = self.player_images["jump"]
        elif player.direction and player.animation_timer >= 10:
            image = self.player_images["run"]
        else:
            image = self.player_images["idle"]

        if player.direction < 0:
            image = pygame.transform.flip(image, True, False)
        image_name = "jump" if player.jumping else "run" if player.direction and player.animation_timer >= 10 else "idle"
        screen.blit(
            image,
            (player.x - camera_x, player.y + self.player_bottom_offsets[image_name]),
        )

