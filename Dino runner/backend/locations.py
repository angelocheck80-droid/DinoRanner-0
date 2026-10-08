import pygame

from backend.constants import GROUND_Y
from backend.dialogue_manager import DialogueManager


class Location:
    def __init__(self):
        self.location_id = "test_location"
        self.door_x = 850
        self.house_x = 690
        self.house_width = 280
        self.inside = False
        self.npc_x = 560
        self.npc_y = GROUND_Y - 52
        self.npc_w = 38
        self.npc_h = 52
        self.dialogue_manager = DialogueManager("old_man.json")
        self.npc_name = self.dialogue_manager.npc_name

    def reset(self):
        self.inside = False

    def near_door(self, player):
        return abs(player.x - self.door_x) < 70

    def near_npc(self, player):
        npc_rect = pygame.Rect(self.npc_x, self.npc_y, self.npc_w, self.npc_h)
        player_rect = pygame.Rect(player.x, player.y, player.size, player.size)
        return player_rect.colliderect(npc_rect)

    def npc_distance(self, player):
        player_center = player.x + player.size / 2
        npc_center = self.npc_x + self.npc_w / 2
        return abs(player_center - npc_center)

    def get_next_dialogue(self):
        return self.dialogue_manager.get_next_line()

    def enter(self):
        self.inside = True

    def leave(self):
        self.inside = False
