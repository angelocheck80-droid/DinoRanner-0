from datetime import datetime, timezone

from backend.constants import SCREEN_WIDTH
from backend.persistence.database import Database


class SaveRepository:
    DEFAULT_SLOT = "main"

    def __init__(self, database_path=None):
        self.database = Database(database_path)

    def has_save(self, slot_name=DEFAULT_SLOT):
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT 1 FROM save_slots WHERE slot_name = ?", (slot_name,)
            ).fetchone()
        return row is not None

    def save(self, game, slot_name=DEFAULT_SLOT):
        if game.state != "location":
            raise ValueError("Game can only be saved while playing a location")

        saved_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        save_values = (
            slot_name,
            game.location.location_id,
            game.dino.x,
            game.dino.y,
            game.dino.velocity,
            int(game.dino.jumping),
            int(game.location.inside),
            game.hp,
            game.inventory.max_slots,
            game.location.dialogue_manager.dialogue_index,
            saved_at,
        )
        item_values = [
            (slot_name, item.name, item.quantity, item.max_stack)
            for item in game.inventory.get_items()
        ]

        with self.database.connection() as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO save_slots (
                        slot_name, location_id, player_x, player_y,
                        player_velocity, player_jumping, location_inside, hp,
                        inventory_capacity, dialogue_index, saved_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(slot_name) DO UPDATE SET
                        location_id = excluded.location_id,
                        player_x = excluded.player_x,
                        player_y = excluded.player_y,
                        player_velocity = excluded.player_velocity,
                        player_jumping = excluded.player_jumping,
                        location_inside = excluded.location_inside,
                        hp = excluded.hp,
                        inventory_capacity = excluded.inventory_capacity,
                        dialogue_index = excluded.dialogue_index,
                        saved_at = excluded.saved_at
                    """,
                    save_values,
                )
                connection.execute(
                    "DELETE FROM inventory_items WHERE slot_name = ?",
                    (slot_name,),
                )
                connection.executemany(
                    """
                    INSERT INTO inventory_items (
                        slot_name, item_name, quantity, max_stack
                    ) VALUES (?, ?, ?, ?)
                    """,
                    item_values,
                )

        return saved_at

    def load(self, game, slot_name=DEFAULT_SLOT):
        with self.database.connection() as connection:
            save_row = connection.execute(
                "SELECT * FROM save_slots WHERE slot_name = ?", (slot_name,)
            ).fetchone()
            if save_row is None:
                return False
            item_rows = connection.execute(
                """
                SELECT item_name, quantity, max_stack
                FROM inventory_items
                WHERE slot_name = ?
                ORDER BY item_name
                """,
                (slot_name,),
            ).fetchall()

        if save_row["location_id"] != game.location.location_id:
            return False
        if len(item_rows) > save_row["inventory_capacity"]:
            raise ValueError("Save contains more items than the inventory can hold")
        if any(item["quantity"] > item["max_stack"] for item in item_rows):
            raise ValueError("Save contains an item quantity above its stack limit")

        game.dino.x = save_row["player_x"]
        game.dino.y = save_row["player_y"]
        game.dino.velocity = save_row["player_velocity"]
        game.dino.jumping = bool(save_row["player_jumping"])
        game.dino.direction = 0
        game.dino.animation_timer = 0
        game.location.inside = bool(save_row["location_inside"])
        game.location.dialogue_manager.dialogue_index = (
            save_row["dialogue_index"]
            % max(len(game.location.dialogue_manager.dialogues), 1)
        )
        game.camera_x = max(0, game.dino.x - SCREEN_WIDTH // 2)
        game.hp = save_row["hp"]
        game.state = "location"
        game.dialogue_active = False
        game.dialogue_text = ""
        game.dialogue_alpha = 0
        game.inventory.max_slots = save_row["inventory_capacity"]
        game.inventory.clear()
        for item in item_rows:
            game.inventory.add(
                item["item_name"], item["quantity"], item["max_stack"]
            )
        game._npc_was_near = (
            not game.location.inside and game.location.near_npc(game.dino)
        )
        return True
