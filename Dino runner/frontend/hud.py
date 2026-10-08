from pathlib import Path

import pygame

from backend.constants import GREEN, RED, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE


class HUD:
    def __init__(self):
        self.pixel_scale = 1
        self.title_font = pygame.font.Font(None, 21)
        self.text_font = pygame.font.Font(None, 16)
        self.small_font = pygame.font.Font(None, 16)
        self.dialogue_name_font = pygame.font.Font(None, 9)
        self.dialogue_font = pygame.font.Font(None, 14)
        dialogue_path = Path(__file__).parent.parent / "UI" / "dialogue.png"
        if dialogue_path.is_file():
            dialogue_bubble = pygame.image.load(dialogue_path).convert_alpha()
            self.dialogue_bubble = pygame.transform.scale(dialogue_bubble, (120, 120))
            self.dialogue_bubble.set_alpha(122)
        else:
            self.dialogue_bubble = None

    def draw_hp(self, screen, hp):
        bar_x, bar_y = 16, 18
        bar_width, bar_height = 80, 14
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        current_width = max(0, min(bar_width, (hp / 100) * bar_width))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, current_width, bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)

        hp_text = self._pixel_text(f"HP: {hp}", self.small_font)
        screen.blit(hp_text, (bar_x + bar_width + 12, bar_y - 2))

    def draw_menu(self, screen):
        self._draw_panel(screen)
        self._draw_centered(screen, "DINO ADVENTURE", self.title_font, 48)
        self._draw_centered(screen, "SPACE - NEW GAME   L - CONTINUE", self.text_font, 100)
        self._draw_centered(
            screen,
            "A/D MOVE   W ENTER   T FORM   F5 SAVE   F9 LOAD",
            self.small_font,
            140,
        )

    def draw_game_over(self, screen, score):
        self._draw_panel(screen)
        self._draw_centered(screen, "GAME OVER", self.title_font, 42)
        self._draw_centered(screen, f"SCORE: {score}", self.text_font, 92)
        self._draw_centered(screen, "R - RESTART    M - MENU", self.small_font, 140)

    def draw_dialog(self, screen, npc_name, text, anchor, opacity=255):
        panel_width, panel_height = 120, 120
        anchor_x, anchor_y = anchor
        panel_x = max(
            8,
            min(SCREEN_WIDTH - panel_width - 8, anchor_x + 30),
        )
        panel_y = max(6, anchor_y - panel_height + 40)
        dialogue_layer = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        if self.dialogue_bubble:
            dialogue_layer.blit(self.dialogue_bubble, (panel_x, panel_y))
        else:
            panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            panel.fill((245, 239, 211, 245))
            pygame.draw.rect(
                panel, (49, 62, 42), panel.get_rect(), 2, border_radius=20
            )
            dialogue_layer.blit(panel, (panel_x, panel_y))

        text_color = (22, 22, 22)
        name_label = self.dialogue_name_font.render(npc_name, False, text_color)
        dialogue_layer.blit(name_label, (panel_x + 15, panel_y + 20))
        wrapped_lines = self._wrap_text(text, self.dialogue_font, panel_width + 60)
        line_height = self.dialogue_font.get_height()
        base_y = panel_y + 60
        for index, line in enumerate(wrapped_lines[:3]):
            line_surface = self.dialogue_font.render(line, False, text_color)
            dialogue_layer.blit(line_surface, (panel_x + 25, base_y + index * line_height))

        tail_start = (panel_x + 20, panel_y + panel_height - 2)
        tail_end = (anchor_x, anchor_y)
        for index, radius in enumerate((4, 3, 2), start=1):
            progress = index / 4
            center = (
                round(tail_start[0] + (tail_end[0] - tail_start[0]) * progress),
                round(tail_start[1] + (tail_end[1] - tail_start[1]) * progress),
            )
            pygame.draw.circle(dialogue_layer, text_color, center, radius + 1)
            pygame.draw.circle(dialogue_layer, (245, 239, 211), center, radius)

        dialogue_layer.set_alpha(max(0, min(255, opacity)))
        screen.blit(dialogue_layer, (0, 0))

    def _wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            candidate = f"{current_line} {word}".strip()
            if font.size(candidate)[0] <= max_width:
                current_line = candidate
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines or [text]

    def _draw_panel(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))

    def _draw_centered(self, screen, text, font, y):
        rendered_text = self._pixel_text(text, font)
        text_rect = rendered_text.get_rect(center=(SCREEN_WIDTH // 2, y))
        screen.blit(rendered_text, text_rect)

    def _pixel_text(self, text, font):
        rendered_text = font.render(text, False, WHITE)
        scaled_size = (
            rendered_text.get_width() * self.pixel_scale,
            rendered_text.get_height() * self.pixel_scale,
        )
        return pygame.transform.scale(rendered_text, scaled_size)
