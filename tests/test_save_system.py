import json

from src.save_system import DEFAULTS, SaveSystem, default_save_dir, sanitize


def make(tmp_path, **kw):
    return SaveSystem(path=str(tmp_path / "save.json"), **kw)


def test_missing_file_gives_defaults_and_no_warning(tmp_path):
    s = make(tmp_path)
    assert s.data == DEFAULTS
    assert s.warning is None


def test_save_and_load_roundtrip(tmp_path):
    s = make(tmp_path)
    assert s.update_high_score(450) is True
    s.unlock_level(2)
    s.set_audio(True, 0.25, 0.9)
    again = make(tmp_path)
    assert again.high_score == 450
    assert again.unlocked_levels == 2
    assert again.data["muted"] is True
    assert again.data["music_volume"] == 0.25
    assert again.data["sfx_volume"] == 0.9


def test_corrupted_json_is_quarantined_and_defaults_used(tmp_path):
    p = tmp_path / "save.json"
    p.write_text("{ this is not json", encoding="utf-8")
    s = make(tmp_path)
    assert s.data == DEFAULTS
    assert s.warning is not None
    assert (tmp_path / "save.json.corrupt").exists()
    assert not p.exists()
    assert s.save() is True  # a fresh save works afterwards


def test_wrong_top_level_type_uses_defaults(tmp_path):
    (tmp_path / "save.json").write_text("[1, 2, 3]", encoding="utf-8")
    s = make(tmp_path)
    assert s.data == DEFAULTS
    assert s.warning is not None


def test_bad_values_are_cleaned():
    raw = {"high_score": "lots", "unlocked_levels": -5, "muted": "yes",
           "music_volume": 7, "sfx_volume": float("nan"), "extra": 1}
    clean = sanitize(raw)
    assert clean["high_score"] == 0
    assert clean["unlocked_levels"] == 1
    assert clean["muted"] is False
    assert clean["music_volume"] == 1.0
    assert clean["sfx_volume"] == DEFAULTS["sfx_volume"]
    assert "extra" not in clean


def test_booleans_are_not_accepted_as_numbers():
    clean = sanitize({"high_score": True, "unlocked_levels": True, "music_volume": True})
    assert clean["high_score"] == 0
    assert clean["unlocked_levels"] == 1
    assert clean["music_volume"] == DEFAULTS["music_volume"]


def test_unlocked_levels_capped_by_level_count(tmp_path):
    (tmp_path / "save.json").write_text(json.dumps({"unlocked_levels": 99}), encoding="utf-8")
    s = make(tmp_path, level_count=3)
    assert s.unlocked_levels == 3


def test_high_score_only_goes_up(tmp_path):
    s = make(tmp_path)
    assert s.update_high_score(100) is True
    assert s.update_high_score(60) is False
    assert s.update_high_score(100) is False
    assert s.high_score == 100


def test_unlock_never_locks_again_and_respects_count(tmp_path):
    s = make(tmp_path, level_count=3)
    assert s.is_unlocked(0) and not s.is_unlocked(1)
    s.unlock_level(3)
    assert s.unlocked_levels == 3
    assert s.unlock_level(2) is False
    assert s.unlocked_levels == 3
    s.unlock_level(10)
    assert s.unlocked_levels == 3


def test_unwritable_location_does_not_crash(tmp_path):
    blocker = tmp_path / "afile"
    blocker.write_text("x")
    s = SaveSystem(path=str(blocker / "save.json"))
    assert s.save() is False
    assert s.warning is not None


def test_default_folder_name():
    assert default_save_dir().endswith("PythonAdventure")