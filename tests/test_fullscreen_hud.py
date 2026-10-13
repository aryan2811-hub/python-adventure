import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")  # no real window needed for tests

import pygame

from src.game import Game


def press(g, k):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=k))
    g.handle_events()


def test_f11_toggles_the_fullscreen_flag():
    g = Game()
    assert g.fullscreen is False
    press(g, pygame.K_F11)
    assert g.fullscreen is True
    press(g, pygame.K_F11)
    assert g.fullscreen is False


def test_f11_does_not_change_the_screen_you_are_on():
    g = Game()
    assert g.state == "menu"
    press(g, pygame.K_F11)
    assert g.state == "menu"
    assert g.running is True


def test_hud_is_hidden_on_the_start_up_menus():
    g = Game()
    assert g.show_hud() is False
    g.handle_action("levels")
    assert g.show_hud() is False
    g.handle_action("back")
    g.handle_action("instructions")
    assert g.show_hud() is False
    g.handle_action("back")
    g.handle_action("settings")
    assert g.show_hud() is False


def test_hud_is_shown_while_playing_and_paused():
    g = Game()
    g.handle_action("play")
    assert g.show_hud() is True
    g.open_pause()
    assert g.show_hud() is True
    g.handle_action("settings")
    assert g.show_hud() is True


def test_every_screen_draws_without_error():
    g = Game()
    g.draw()
    for action in ("levels", "back", "instructions", "back", "settings", "back", "play"):
        g.handle_action(action)
        g.draw()
    g.open_pause()
    g.draw()