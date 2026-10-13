import pytest


@pytest.fixture(autouse=True)
def isolate_user_data(tmp_path, monkeypatch):
    """Tests must never touch the real save file or play real sound."""
    monkeypatch.setattr("src.save_system.default_save_dir", lambda: str(tmp_path / "userdata"))
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")