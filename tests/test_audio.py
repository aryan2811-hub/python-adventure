import os

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")  # no real speakers needed for tests

from src import audio as A


def test_effects_exist_and_are_not_silent():
    effects = A.build_effects()
    for name in ("jump", "coin", "hurt", "stomp", "victory", "game_over", "checkpoint", "click"):
        assert name in effects, name
        assert len(effects[name]) > 0
        assert max(abs(v) for v in effects[name]) > 1000, f"{name} is silent"


def test_samples_stay_inside_16_bit_range():
    for samples in list(A.build_effects().values()) + [A.build_music()]:
        assert -32768 <= min(samples) and max(samples) <= 32767


def test_music_is_eight_seconds_long():
    music = A.build_music()
    assert len(music) == int(8 * A.SAMPLE_RATE)


def test_overlay_clamps_instead_of_wrapping():
    loud = A.make_tone(440, 440, 0.05, 1.0, "square")
    mixed = A.overlay(loud, loud, 1.0)
    assert max(mixed) == 32767 and min(mixed) == -32767


def test_clamp01():
    assert A.clamp01(5) == 1.0
    assert A.clamp01(-1) == 0.0
    assert A.clamp01("bad") == 0.0
    assert A.clamp01(float("nan")) == 0.0
    assert A.clamp01(0.3) == 0.3


def test_audio_object_never_crashes():
    a = A.Audio()  # works with or without a sound device
    for name in ("jump", "coin", "hurt", "stomp", "victory", "game_over", "nope"):
        a.play(name)
    a.start_music()
    a.pause_music()
    a.resume_music()
    a.stop_music()


def test_mute_and_volume_controls():
    a = A.Audio(muted=False, music_volume=0.5, sfx_volume=0.7)
    assert a.toggle_mute() is True
    assert a.toggle_mute() is False
    a.set_music_volume(9)
    a.set_sfx_volume(-3)
    assert a.music_volume == 1.0 and a.sfx_volume == 0.0
    a.apply_settings({"muted": True, "music_volume": 0.2, "sfx_volume": 0.4})
    assert a.settings() == {"muted": True, "music_volume": 0.2, "sfx_volume": 0.4}