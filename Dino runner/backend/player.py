from backend.constants import DINO_SIZE, GROUND_Y, GRAVITY, JUMP_FORCE, MOVE_SPEED


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = DINO_SIZE
        self.velocity = 0
        self.jumping = False
        self.direction = 0
        self.animation_timer = 0
        self.form = "dino"

    def toggle_form(self):
        self.form = "dragon_human" if self.form == "dino" else "dino"

    def jump(self):
        if not self.jumping:
            self.velocity = -JUMP_FORCE
            self.jumping = True

    def update(self, direction=0):
        self.direction = direction
        if direction:
            self.x += direction * MOVE_SPEED
            self.x = max(0, self.x)

        self.animation_timer = (self.animation_timer + 1) % 20
        if self.jumping:
            self.y += self.velocity
            self.velocity += GRAVITY
            ground_y = GROUND_Y - self.size
            if self.y >= ground_y:
                self.y = ground_y
                self.jumping = False
                self.velocity = 0

