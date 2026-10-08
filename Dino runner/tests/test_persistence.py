import sqlite3
import tempfile
import unittest
from pathlib import Path

from backend.game import Game
from backend.persistence import SaveRepository


class SaveRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        database_path = Path(self.temp_dir.name) / "game.sqlite3"
        self.repository = SaveRepository(database_path)

    def test_save_and_restore_game_state_and_inventory(self):
        game = Game()
        game.start_location()
        game.dino.x = 630
        game.dino.y = 94
        game.dino.velocity = 2.5
        game.dino.jumping = True
        game.hp = 75
        game.location.enter()
        game.location.dialogue_manager.dialogue_index = 2
        game.inventory.add("berry", amount=4, max_stack=20)

        saved_at = self.repository.save(game)
        restored_game = Game()

        self.assertTrue(self.repository.load(restored_game))
        self.assertTrue(saved_at)
        self.assertEqual(restored_game.dino.x, 630)
        self.assertEqual(restored_game.dino.y, 94)
        self.assertEqual(restored_game.dino.velocity, 2.5)
        self.assertTrue(restored_game.dino.jumping)
        self.assertEqual(restored_game.hp, 75)
        self.assertTrue(restored_game.location.inside)
        self.assertEqual(restored_game.location.dialogue_manager.dialogue_index, 2)
        self.assertEqual(restored_game.inventory.count("berry"), 4)
        self.assertEqual(restored_game.inventory.get_items()[0].max_stack, 20)
        self.assertEqual(restored_game.state, "location")

    def test_save_overwrites_previous_inventory_items(self):
        game = Game()
        game.start_location()
        game.inventory.add("berry", amount=2)
        self.repository.save(game)

        game.inventory.clear()
        game.inventory.add("shell", amount=1)
        self.repository.save(game)
        restored_game = Game()

        self.assertTrue(self.repository.load(restored_game))
        self.assertEqual(restored_game.inventory.count("berry"), 0)
        self.assertEqual(restored_game.inventory.count("shell"), 1)

    def test_load_returns_false_when_no_save_exists(self):
        self.assertFalse(self.repository.load(Game()))

    def test_save_is_rejected_outside_gameplay(self):
        with self.assertRaises(ValueError):
            self.repository.save(Game())

    def test_database_schema_is_versioned_and_normalized(self):
        connection = sqlite3.connect(self.repository.database.path)
        try:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
        finally:
            connection.close()

        self.assertEqual(version, 1)
        self.assertTrue({"save_slots", "inventory_items"}.issubset(tables))


if __name__ == "__main__":
    unittest.main()
