import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")  # no real window needed for tests

import pygame

from src.game import Game
from src.save_system import SaveSystem


def press(g, k):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=k))
    g.handle_events()


def test_game_starts_on_main_menu():
    g = Game()
    assert g.state == "menu"
    assert g.ui is not None


def test_play_action_starts_the_game():
    g = Game()
    g.handle_action("play")
    assert g.state == "playing"
    assert g.ui is None


def test_enter_on_main_menu_starts_the_game():
    g = Game()
    press(g, pygame.K_RETURN)
    assert g.state == "playing"


def test_escape_pauses_and_resume_continues():
    g = Game()
    g.handle_action("play")
    press(g, pygame.K_ESCAPE)
    assert g.state == "paused"
    assert g.running is True
    g.handle_action("resume")
    assert g.state == "playing"
    assert g.ui is None


def test_world_is_frozen_while_paused():
    g = Game()
    g.handle_action("play")
    press(g, pygame.K_ESCAPE)
    before = g.world.player.rect.copy()
    for _ in range(5):
        g.step(False)
    assert g.world.player.rect == before


def test_level_select_loads_that_level():
    g = Game()
    g.handle_action("level:1")
    assert g.level_index == 1
    assert g.state == "playing"


def test_settings_change_is_saved():
    g = Game()
    g.handle_action("settings")
    g.ui.music = 0.3
    g.handle_action("changed")
    assert SaveSystem(path=g.save.path).data["music_volume"] == 0.3


def test_settings_back_returns_to_pause_menu():
    g = Game()
    g.handle_action("play")
    press(g, pygame.K_ESCAPE)
    g.handle_action("settings")
    assert g.state == "settings"
    g.handle_action("back")
    assert g.state == "paused"


def test_quit_action_stops_the_game():
    g = Game()
    g.handle_action("quit")
    assert g.running is False


def test_escape_on_main_menu_does_nothing():
    g = Game()
    press(g, pygame.K_ESCAPE)
    assert g.running is True
    assert g.state == "menu"