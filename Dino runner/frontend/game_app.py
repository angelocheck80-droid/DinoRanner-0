import sqlite3

import pygame

from backend.constants import FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from backend.game import Game
from backend.persistence import SaveRepository
from frontend.inventory_ui import InventoryUI
from frontend.renderer import GameRenderer


class GameApp:
    def __init__(self, save_repository=None, time_provider=None):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dino Jump")
        self.game = Game()
        self.save_repository = save_repository or SaveRepository()
        self.inventory_ui = InventoryUI(self.game.inventory)
        self.renderer = GameRenderer(time_provider)
        self.clock = pygame.time.Clock()
        self.status_font = pygame.font.Font(None, 20)
        self.status_message = ""
        self.status_timer = 0
        self.running = True

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event)
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event)

    def _handle_click(self, event):
        if self.game.state != "location":
            return

        if self.inventory_ui.visible:
            return
        if self.game.dialogue_active:
            self.game.handle_action("dialogue_next")
        else:
            self.game.handle_action("talk")

    def _handle_key(self, event):
        if self.game.state == "menu":
            if event.key == pygame.K_SPACE:
                self.game.handle_action("start")
            elif event.key == pygame.K_l:
                self._load_game()
            return

        if self.game.state != "location":
            return

        if event.key == pygame.K_F5:
            self._save_game()
            return
        if event.key == pygame.K_F9:
            self._load_game()
            return

        if self.inventory_ui.visible:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                self.inventory_ui.visible = False
            return

        if self.game.dialogue_active:
            if event.key in (pygame.K_e, pygame.K_ESCAPE, pygame.K_RETURN):
                self.game.handle_action("dialogue_close")
            return

        if event.key == pygame.K_t:
            self.game.handle_action("transform")
            self.renderer.play_transform_effect(self.game.dino)
            form_message = (
                "Dragon-human form"
                if self.game.dino.form == "dragon_human"
                else "Dinosaur form"
            )
            self._show_status(form_message)
        elif event.key == pygame.K_q:
            self.inventory_ui.visible = True
        elif event.key == pygame.K_SPACE:
            self.game.handle_action("jump")
        elif not self.game.location.inside and event.key in (pygame.K_w, pygame.K_UP):
            self.game.handle_action("enter")
        elif self.game.location.inside and event.key in (pygame.K_e, pygame.K_ESCAPE):
            self.game.handle_action("leave")

    def update(self):
        self._handle_events()
        if self.game.state == "location" and not self.inventory_ui.visible:
            keys = pygame.key.get_pressed()
            moving_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            direction = 1 if moving_right and not moving_left else -1 if moving_left else 0
            self.game.update(direction)

        self.renderer.draw(self.screen, self.game, self.inventory_ui)
        if self.status_timer > 0:
            status_surface = self.status_font.render(
                self.status_message, True, (255, 255, 255)
            )
            status_rect = status_surface.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 14)
            )
            pygame.draw.rect(
                self.screen,
                (25, 35, 28),
                status_rect.inflate(14, 8),
                border_radius=4,
            )
            self.screen.blit(status_surface, status_rect)
            self.status_timer -= 1
        pygame.display.flip()
        self.clock.tick(FPS)

    def _save_game(self):
        try:
            self.save_repository.save(self.game)
        except (sqlite3.Error, ValueError):
            self._show_status("Save failed")
        else:
            self._show_status("Game saved")

    def _load_game(self):
        try:
            loaded = self.save_repository.load(self.game)
        except (sqlite3.Error, ValueError):
            loaded = False
        self._show_status("Game loaded" if loaded else "No save found")

    def _show_status(self, message):
        self.status_message = message
        self.status_timer = FPS * 2

    def run(self):
        while self.running:
            self.update()
