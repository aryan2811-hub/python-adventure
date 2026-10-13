import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")  # no real window needed for tests

import pygame
import pytest

from src.audio import Audio
from src.game import Game
from src.level_manager import LevelManager
from src.save_system import SaveSystem

BAD_SAVES = [
    "",  # empty file
    "{not json",  # broken JSON
    "[]",  # valid JSON, wrong shape
    "null",
    '"just text"',
    '{"high_score": "abc"}',  # wrong type
    '{"high_score": -5, "unlocked_levels": 999}',  # out-of-range numbers
    '{"unlocked_levels": 0}',
]


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


@pytest.mark.parametrize("content", BAD_SAVES)
def test_bad_save_file_does_not_crash_and_gives_sane_values(tmp_path, content):
    path = str(tmp_path / "userdata" / "save.json")
    write(path, content)
    s = SaveSystem(path=path, level_count=3)
    assert s.high_score >= 0
    assert 1 <= s.unlocked_levels <= 3


def test_missing_save_file_starts_fresh(tmp_path):
    path = str(tmp_path / "does_not_exist_yet" / "save.json")
    s = SaveSystem(path=path, level_count=3)
    assert s.high_score == 0
    assert s.unlocked_levels == 1


def test_game_starts_even_if_the_save_file_is_garbage():
    first = Game()
    write(first.save.path, "{this is not json")
    again = Game()
    assert again.save.high_score == 0
    assert again.state == "menu"


def test_unknown_sound_name_is_ignored():
    Audio().play("not_a_real_sound")


def test_audio_survives_having_no_sound_device(monkeypatch):
    def no_device(*args, **kwargs):
        raise pygame.error("no audio device")

    pygame.mixer.quit()
    monkeypatch.setattr(pygame.mixer, "init", no_device)
    a = Audio()
    assert a.enabled is False
    a.play("jump")
    a.start_music()
    a.toggle_mute()
    a.apply_settings({"muted": False, "music_volume": 0.5, "sfx_volume": 0.7})


def test_every_level_loads_and_looks_sane():
    manager = LevelManager()
    assert manager.count >= 3
    for i in range(manager.count):
        level = manager.load(i)
        assert level.width > 0
        assert len(level.platforms) > 0
        assert 0 <= level.spawn[0] <= level.width