from backend.game import Game


def test_game_starts_with_full_hp():
    game = Game()
    assert game.hp == 100


def test_take_damage_reduces_hp_and_keeps_minimum_zero():
    game = Game()
    game.take_damage(35)
    assert game.hp == 65

    game.hit_cooldown = 0
    game.take_damage(100)
    assert game.hp == 0
    assert game.state == "game_over"
