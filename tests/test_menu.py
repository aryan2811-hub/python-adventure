import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")  # no real window needed for tests

import pygame

from src import settings as S
from src.menu import (
    InfoScreen, Menu, SettingsScreen,
    instructions_screen, level_select_menu, main_menu, pause_menu,
)


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


def click(pos):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1)


def test_enter_picks_first_item():
    m = main_menu()
    assert m.handle_event(key(pygame.K_RETURN)) == "play"


def test_down_then_enter():
    m = main_menu()
    m.handle_event(key(pygame.K_DOWN))
    assert m.handle_event(key(pygame.K_RETURN)) == "levels"


def test_up_wraps_to_last():
    m = main_menu()
    m.handle_event(key(pygame.K_UP))
    assert m.handle_event(key(pygame.K_RETURN)) == "quit"


def test_locked_levels_are_skipped():
    m = level_select_menu(3, 1)
    assert m.selected == 0
    m.handle_event(key(pygame.K_DOWN))
    assert m.handle_event(key(pygame.K_RETURN)) == "back"


def test_mouse_click_returns_action():
    m = main_menu()
    assert m.handle_event(click(m.rects[3].center)) == "settings"


def test_click_on_locked_level_does_nothing():
    m = level_select_menu(3, 1)
    assert m.handle_event(click(m.rects[2].center)) is None


def test_escape_uses_back_action():
    assert pause_menu().handle_event(key(pygame.K_ESCAPE)) == "resume"
    assert main_menu().handle_event(key(pygame.K_ESCAPE)) is None


def test_mouse_hover_selects():
    m = main_menu()
    pos = m.rects[2].center
    m.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=pos, rel=(0, 0), buttons=(0, 0, 0)))
    assert m.selected == 2


def test_level_select_action_names():
    m = level_select_menu(3, 3)
    assert m.items[1][1] == "level:1"
    assert m.disabled == set()


def test_settings_arrows_change_volume():
    s = SettingsScreen(0.5, 0.7, False)
    assert s.handle_event(key(pygame.K_RIGHT)) == "changed"
    assert s.music == 0.6
    s.handle_event(key(pygame.K_DOWN))
    assert s.handle_event(key(pygame.K_LEFT)) == "changed"
    assert s.sfx == 0.6


def test_settings_volume_is_clamped():
    s = SettingsScreen(1.0, 0.0, False)
    assert s.handle_event(key(pygame.K_RIGHT)) is None
    assert s.music == 1.0
    s.handle_event(key(pygame.K_DOWN))
    assert s.handle_event(key(pygame.K_LEFT)) is None
    assert s.sfx == 0.0


def test_settings_mute_toggle():
    s = SettingsScreen(0.5, 0.7, False)
    s.handle_event(key(pygame.K_DOWN))
    s.handle_event(key(pygame.K_DOWN))
    assert s.handle_event(key(pygame.K_RETURN)) == "changed"
    assert s.muted is True


def test_settings_slider_click():
    s = SettingsScreen(0.2, 0.7, False)
    bar = s.bar_rect(0)
    assert s.handle_event(click((bar.x + bar.w // 2, bar.centery))) == "changed"
    assert s.music == 0.5


def test_settings_escape_goes_back():
    assert SettingsScreen().handle_event(key(pygame.K_ESCAPE)) == "back"


def test_info_screen_goes_back():
    assert instructions_screen().handle_event(key(pygame.K_RETURN)) == "back"
    assert InfoScreen("t", ["a"]).handle_event(click((10, 10))) == "back"


def test_everything_draws():
    surface = pygame.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT))
    for screen in (main_menu(), pause_menu(), level_select_menu(3, 2),
                   instructions_screen(), SettingsScreen()):
        screen.draw(surface)
        screen.draw(surface, veil=False)