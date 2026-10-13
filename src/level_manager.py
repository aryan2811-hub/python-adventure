import glob
import os
import re
from src.paths import resource_path
from src.level_loader import load_level, LevelError


class LevelManager:
    """Finds levels/level_1.json, level_2.json, ... in order. Add a file and it appears."""

    def __init__(self, levels_dir=None):
        self.levels_dir = levels_dir or resource_path("levels")
        found = glob.glob(os.path.join(self.levels_dir, "level_*.json"))
        keyed = []
        for path in found:
            m = re.search(r"level_(\d+)\.json$", path)
            if m:
                keyed.append((int(m.group(1)), path))
        self.paths = [p for _, p in sorted(keyed)]
        if not self.paths:
            raise LevelError(f"No level files found in {self.levels_dir}")

    @property
    def count(self):
        return len(self.paths)

    def load(self, index):
        return load_level(self.paths[index])
