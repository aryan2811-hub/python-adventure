"""Local save file: high score, unlocked levels and sound settings.

The file lives in the player's own app-data folder, because the folder the
game is installed in is often read-only. A missing or broken save file never
stops the game: we simply fall back to the defaults.
"""
import json
import os
import sys

APP_NAME = "PythonAdventure"
SAVE_FILE_NAME = "save.json"
SAVE_VERSION = 1
MAX_SCORE = 1_000_000_000

DEFAULTS = {
    "high_score": 0,
    "unlocked_levels": 1,
    "muted": False,
    "music_volume": 0.5,
    "sfx_volume": 0.7,
}


def default_save_dir():
    """Windows: %APPDATA%\\PythonAdventure   macOS: ~/Library/Application Support   Linux: ~/.local/share"""
    home = os.path.expanduser("~")
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.join(home, "AppData", "Roaming")
    elif sys.platform == "darwin":
        base = os.path.join(home, "Library", "Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.join(home, ".local", "share")
    return os.path.join(base, APP_NAME)


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _is_number(v):
    # "v == v" is False only for NaN, which we also refuse.
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v


def _volume(v, default):
    if not _is_number(v):
        return default
    return min(1.0, max(0.0, float(v)))


def sanitize(raw, level_count=None):
    """Takes whatever was in the file and returns a safe, complete settings dict."""
    data = dict(DEFAULTS)
    if not isinstance(raw, dict):
        return data
    score = raw.get("high_score")
    if _is_int(score) and score >= 0:
        data["high_score"] = min(score, MAX_SCORE)
    unlocked = raw.get("unlocked_levels")
    if _is_int(unlocked):
        data["unlocked_levels"] = max(1, unlocked)
    if level_count:
        data["unlocked_levels"] = min(data["unlocked_levels"], level_count)
    if isinstance(raw.get("muted"), bool):
        data["muted"] = raw["muted"]
    data["music_volume"] = _volume(raw.get("music_volume"), DEFAULTS["music_volume"])
    data["sfx_volume"] = _volume(raw.get("sfx_volume"), DEFAULTS["sfx_volume"])
    return data


class SaveSystem:
    def __init__(self, path=None, level_count=None):
        self.path = path or os.path.join(default_save_dir(), SAVE_FILE_NAME)
        self.level_count = level_count
        self.data = dict(DEFAULTS)
        self.warning = None  # a short message if something went wrong (shown in the console)
        self.load()

    # ---- reading ----
    def load(self):
        self.warning = None
        self.data = dict(DEFAULTS)
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except FileNotFoundError:
            return self.data  # first run: no save yet, that is normal
        except ValueError as exc:  # broken JSON or bad text encoding
            self._quarantine(f"save file is damaged ({exc})")
            return self.data
        except OSError as exc:
            self._warn(f"could not read save file ({exc}); using defaults")
            return self.data
        if not isinstance(raw, dict):
            self._quarantine("save file has the wrong format")
            return self.data
        self.data = sanitize(raw, self.level_count)
        return self.data

    def _quarantine(self, reason):
        """Keep the broken file as save.json.corrupt so nothing is lost, then start fresh."""
        try:
            os.replace(self.path, self.path + ".corrupt")
            self._warn(f"{reason}; moved to {self.path}.corrupt and started a new save")
        except OSError:
            self._warn(f"{reason}; using defaults")

    def _warn(self, message):
        self.warning = message
        print(f"[save] {message}", file=sys.stderr)

    # ---- writing ----
    def save(self):
        """Writes the file safely (temp file, then rename). Returns True on success, never raises."""
        payload = dict(self.data)
        payload["version"] = SAVE_VERSION
        tmp = self.path + ".tmp"
        try:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            os.replace(tmp, self.path)
            return True
        except OSError as exc:
            self._warn(f"could not save progress ({exc}); the game will keep running")
            return False

    # ---- helpers the game will call ----
    @property
    def high_score(self):
        return self.data["high_score"]

    @property
    def unlocked_levels(self):
        return self.data["unlocked_levels"]

    def is_unlocked(self, level_index):
        """level_index starts at 0, like the LevelManager."""
        return level_index < self.data["unlocked_levels"]

    def update_high_score(self, score):
        """Returns True if this is a new record."""
        if _is_int(score) and score > self.data["high_score"]:
            self.data["high_score"] = min(score, MAX_SCORE)
            self.save()
            return True
        return False

    def unlock_level(self, level_number):
        """level_number starts at 1 (level 2 unlocked = 2). Never locks levels again."""
        if not _is_int(level_number):
            return False
        target = max(self.data["unlocked_levels"], level_number)
        if self.level_count:
            target = min(target, self.level_count)
        if target != self.data["unlocked_levels"]:
            self.data["unlocked_levels"] = target
            self.save()
            return True
        return False

    def set_audio(self, muted, music_volume, sfx_volume):
        self.data["muted"] = muted if isinstance(muted, bool) else DEFAULTS["muted"]
        self.data["music_volume"] = _volume(music_volume, DEFAULTS["music_volume"])
        self.data["sfx_volume"] = _volume(sfx_volume, DEFAULTS["sfx_volume"])
        self.save()

    def reset(self):
        self.data = dict(DEFAULTS)
        self.save()
