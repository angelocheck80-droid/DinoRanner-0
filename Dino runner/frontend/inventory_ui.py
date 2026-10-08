from pathlib import Path

import pygame


class InventoryUI:
    SLOT_SIZE = 24
    GAP = 4
    COLS = 4
    PANEL_WIDTH = 300
    PANEL_HEIGHT = 200

    def __init__(self, inventory):
        self.inventory = inventory
        self.item_font = pygame.font.SysFont("Arial", 10, bold=True)
        self.quantity_font = pygame.font.SysFont("Arial", 8, bold=True)

        self.rows = (inventory.max_slots + self.COLS - 1) // self.COLS
        self.grid_w = self.COLS * self.SLOT_SIZE + (self.COLS - 1) * self.GAP
        self.grid_h = self.rows * self.SLOT_SIZE + (self.rows - 1) * self.GAP

        self.panel_w = self.PANEL_WIDTH
        self.panel_h = self.PANEL_HEIGHT
        self.panel = pygame.Surface((self.panel_w, self.panel_h), pygame.SRCALPHA)
        asset_path = Path(__file__).parent.parent / "UI" / "Inventory" / "inventory.png"
        if asset_path.is_file():
            self.background = pygame.transform.scale(
                pygame.image.load(asset_path).convert_alpha(),
                (self.panel_w, self.panel_h),
            )
        else:
            self.background = pygame.Surface(
                (self.panel_w, self.panel_h), pygame.SRCALPHA
            )
            self.background.fill((38, 54, 39, 235))
            pygame.draw.rect(
                self.background,
                (139, 161, 94),
                self.background.get_rect(),
                2,
                border_radius=12,
            )

        self.visible = False
        
    def get_centered_pos(self, screen_width, screen_height):
        x = (screen_width - self.panel_w) // 2
        y = (screen_height - self.panel_h) // 2
        return x, y


    def _rect_slot(self, index):
        col = index % self.COLS
        row = index // self.COLS
        grid_left = (self.panel_w - self.grid_w) // 2
        grid_top = (self.panel_h - self.grid_h) // 2
        x = grid_left + col * (self.SLOT_SIZE + self.GAP)
        y = grid_top + row * (self.SLOT_SIZE + self.GAP)
        return pygame.Rect(x, y, self.SLOT_SIZE, self.SLOT_SIZE)

    def draw(self, surface, pos=(0, 0)):
        if not self.visible:
            return

        self.panel.fill((0, 0, 0, 0))
        self.panel.blit(self.background, (0, 0))

        items = self.inventory.get_items()

        # слоты
        for i in range(self.inventory.max_slots):
            rect = self._rect_slot(i)
            pygame.draw.rect(self.panel, (34, 49, 35, 220), rect, border_radius=4)
            pygame.draw.rect(self.panel, (139, 161, 94), rect, 1, border_radius=4)

            if i < len(items):
                item = items[i]
                item_surf = self.item_font.render(item.name[:1].upper(), True, (232, 220, 174))
                self.panel.blit(item_surf, item_surf.get_rect(center=rect.center))
                if item.quantity > 1:
                    qty_surf = self.quantity_font.render(str(item.quantity), True, (255, 245, 210))
                    self.panel.blit(qty_surf, (rect.right - qty_surf.get_width() - 2, rect.bottom - qty_surf.get_height() - 1))

        surface.blit(self.panel, pos)

