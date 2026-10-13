import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")  # no real window needed for tests

import pygame

from src.game import Game
from src.save_system import SaveSystem


def test_goal_event_saves_high_score_and_unlocks_next_level():
    g = Game()
    g.world.score = 500
    g.play_events(["goal"])
    again = SaveSystem(path=g.save.path, level_count=g.manager.count)
    assert again.high_score == 500
    assert again.unlocked_levels == 2


def test_game_over_event_keeps_the_higher_score():
    g = Game()
    g.world.score = 300
    g.play_events(["game_over"])
    g.world.score = 100
    g.play_events(["game_over"])
    assert g.save.high_score == 300


def test_m_key_toggles_mute_and_saves_it():
    g = Game()
    assert g.audio.muted is False
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m))
    g.handle_events()
    assert g.audio.muted is True
    assert SaveSystem(path=g.save.path).data["muted"] is True


def test_unknown_events_are_ignored():
    g = Game()
    g.play_events(["not_a_real_event"])
    assert g.save.high_score == 0