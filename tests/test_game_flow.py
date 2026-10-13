import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from src.game import Game


def press(key):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))


def test_full_flow_through_all_levels_to_victory_and_restart():
    g = Game()
    g.handle_action("play")
    n = g.manager.count
    assert g.level_index == 0 and g.state == "playing"
    carried = 0
    for i in range(n):
        assert g.level_index == i
        g.world.player.respawn_at((g.world.level.goal.rect.x, 300), grace=0)
        for e in g.world.level.enemies:
            if e.is_boss:
                e.alive = False  # skip the boss fight here: the boss is tested in test_boss_goal.py
        for _ in range(60):
            g.handle_events(); g.step(False); g.draw()
            if g.state != "playing":
                break
        assert g.world.level_complete
        carried = g.world.score
        if i < n - 1:
            assert g.state == "level_complete"
            press(pygame.K_RETURN)
            g.handle_events()
            assert g.level_index == i + 1 and g.world.score == carried and g.state == "playing"
        else:
            assert g.state == "victory"
            g.draw()
    press(pygame.K_RETURN)
    g.handle_events()
    assert g.level_index == 0 and g.world.score == 0 and g.state == "playing"
    pygame.quit()


def test_game_over_restarts_same_level_with_level_start_score():
    g = Game()
    g.handle_action("play")
    g.start_level(1, 120)
    g.world.score = 500
    g.world.player.health = 0
    g.world.step(0, False)
    g.step(False)
    assert g.world.game_over
    press(pygame.K_r)
    g.handle_events()
    assert not g.world.game_over and g.level_index == 1 and g.world.score == 120
    assert g.world.player.health == 5
    pygame.quit()
