from backend.constants import DINO_SIZE, GROUND_Y, MAX_HP, SCREEN_HEIGHT, SCREEN_WIDTH
from backend.inventory import Inventory
from backend.locations import Location
from backend.player import Player


class Game:
    DIALOGUE_FADE_START_DISTANCE = 60
    DIALOGUE_FADE_END_DISTANCE = 180

    def __init__(self):
        ground_y = GROUND_Y - DINO_SIZE
        self.dino = Player(SCREEN_WIDTH // 2, ground_y)
        self.location = Location()
        self.inventory = Inventory()
        self.state = "menu"
        self.camera_x = 0
        self.hp = MAX_HP
        self.dialogue_active = False
        self.dialogue_text = ""
        self.dialogue_alpha = 0
        self._npc_was_near = False

    def start_game(self):
        self.start_location()

    def start_location(self):
        ground_y = GROUND_Y - DINO_SIZE
        self.dino = Player(300, ground_y)
        self.location.reset()
        self.camera_x = 0
        self.hp = MAX_HP
        self.state = "location"
        self.dialogue_active = False
        self.dialogue_text = ""
        self.dialogue_alpha = 0
        self._npc_was_near = False

    def handle_action(self, action):
        if self.state == "menu":
            if action == "start":
                self.start_location()
            return

        if self.state != "location":
            return

        if self.dialogue_active:
            if action == "dialogue_next":
                self.dialogue_text = self.location.get_next_dialogue()
            elif action == "dialogue_close":
                self.dialogue_active = False
                self.dialogue_text = ""
                self.dialogue_alpha = 0
            return

        if action == "transform":
            self.dino.toggle_form()
        elif action == "jump":
            self.dino.jump()
        elif action == "talk" and not self.location.inside and self.location.near_npc(self.dino):
            self.dialogue_active = True
            self.dialogue_text = self.location.get_next_dialogue()
        elif action == "enter" and not self.location.inside and self.location.near_door(self.dino):
            self.location.enter()
        elif action == "leave" and self.location.inside:
            self.location.leave()

    def update(self, direction=0):
        if self.state != "location":
            return

        self.dino.update(direction=direction)
        self.camera_x = max(0, self.dino.x - SCREEN_WIDTH // 2)

        near_npc = not self.location.inside and self.location.near_npc(self.dino)
        if near_npc and not self._npc_was_near and not self.dialogue_active:
            self.dialogue_active = True
            self.dialogue_text = self.location.get_next_dialogue()

        if self.dialogue_active:
            distance = self.location.npc_distance(self.dino)
            fade_progress = (
                self.DIALOGUE_FADE_END_DISTANCE - distance
            ) / (self.DIALOGUE_FADE_END_DISTANCE - self.DIALOGUE_FADE_START_DISTANCE)
            self.dialogue_alpha = round(255 * max(0, min(1, fade_progress)))
            if not near_npc and self.dialogue_alpha == 0:
                self.dialogue_active = False
                self.dialogue_text = ""
        else:
            self.dialogue_alpha = 0

        self._npc_was_near = near_npc
