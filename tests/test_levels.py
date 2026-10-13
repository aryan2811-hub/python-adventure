import copy
import json
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pytest
from src import settings as S
from src.level_loader import parse_level, load_level, LevelError
from src.level_manager import LevelManager

LEVELS_DIR = os.path.join(ROOT, "levels")

VALID = {
    "name": "T", "width": 1200, "spawn": [50, 400], "ground": [[0, 1200]],
    "platforms": [{"type": "stone", "x": 100, "y": 380, "w": 100, "h": 24}],
    "enemies": [{"type": "walker", "x": 300, "y": 448, "xmin": 300, "xmax": 500}],
    "coins": [{"x": 200, "y": 300, "n": 3}], "checkpoints": [400], "goal": {"x": 1100},
}


def bad(**changes):
    d = copy.deepcopy(VALID)
    d.update(changes)
    return d


def test_valid_data_loads():
    lv = parse_level(VALID)
    assert lv.name == "T" and len(lv.coins) == 3 and lv.goal is not None


@pytest.mark.parametrize("data", [
    [],                                              # not an object
    bad(name=""),                                    # empty name
    bad(width=500),                                  # narrower than screen
    bad(spawn=[1]),                                  # bad spawn
    bad(ground=[]),                                  # no ground
    bad(ground=[[0, 5000]]),                         # ground outside level
    bad(platforms=[{"type": "lava", "x": 0, "y": 0, "w": 1, "h": 1}]),
    bad(platforms=[{"type": "stone", "x": 0, "y": 0, "w": 0, "h": 1}]),
    bad(enemies=[{"type": "walker", "x": 1, "y": 1, "xmin": 9, "xmax": 2}]),
    bad(enemies=[{"type": "dragon", "x": 1, "y": 1}]),
    bad(coins=[{"x": 10, "y": 10, "n": 0}]),
    bad(checkpoints=["a"]),
    bad(goal={"x": 99999}),
    bad(goal=None),
])
def test_bad_data_raises_clear_error(data):
    with pytest.raises(LevelError):
        parse_level(data)


def test_missing_and_corrupt_files(tmp_path):
    with pytest.raises(LevelError):
        load_level(tmp_path / "nope.json")
    broken = tmp_path / "level_1.json"
    broken.write_text("{ not json")
    with pytest.raises(LevelError):
        load_level(broken)


def test_manager_finds_levels_in_numeric_order(tmp_path):
    for n in (10, 2, 1):
        (tmp_path / f"level_{n}.json").write_text(json.dumps(VALID))
    m = LevelManager(str(tmp_path))
    assert [os.path.basename(p) for p in m.paths] == ["level_1.json", "level_2.json", "level_10.json"]
    with pytest.raises(LevelError):
        LevelManager(str(tmp_path / "empty"))


def test_three_shipped_levels_exist_and_load():
    m = LevelManager(LEVELS_DIR)
    assert m.count >= 3
    for i in range(m.count):
        lv = m.load(i)
        assert lv.goal and lv.checkpoints and lv.coins and lv.enemies


def test_only_last_level_has_boss():
    m = LevelManager(LEVELS_DIR)
    flags = [m.load(i).has_boss for i in range(m.count)]
    assert flags[-1] and not any(flags[:-1])


# ---- Reachability: a rough static check, NOT a proof. It assumes only a single jump
# (about 215 px far, about 134 px high, measured with the real Player physics) and a platform's full swing range if it moves.
def _surfaces(data):
    out = [(x, x + w, S.GROUND_Y) for x, w in data["ground"]]
    for p in data.get("platforms", []):
        reach = abs(p.get("ax", 0))
        out.append((p["x"] - reach, p["x"] + p["w"] + reach, p["y"]))
    return out


def _reachable(data, max_gap=215, max_rise=130):
    surf = _surfaces(data)
    start = next(i for i, (a, b, t) in enumerate(surf) if t == S.GROUND_Y and a <= data["spawn"][0] <= b)
    goal = next(i for i, (a, b, t) in enumerate(surf) if t == S.GROUND_Y and a <= data["goal"]["x"] <= b)
    seen, todo = {start}, [start]
    while todo:
        a = surf[todo.pop()]
        for j, b in enumerate(surf):
            if j in seen:
                continue
            gap = max(0, b[0] - a[1], a[0] - b[1])
            if gap <= max_gap and a[2] - b[2] <= max_rise:
                seen.add(j)
                todo.append(j)
    return goal in seen


@pytest.mark.parametrize("n", [1, 2, 3])
def test_goal_reachable_with_single_jumps(n):
    with open(os.path.join(LEVELS_DIR, f"level_{n}.json")) as f:
        data = json.load(f)
    assert _reachable(data)


def test_reachability_check_detects_impossible_gap():
    d = copy.deepcopy(VALID)
    d["ground"] = [[0, 400], [900, 300]]
    d["platforms"] = []
    d["goal"] = {"x": 1000}
    assert not _reachable(d)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_checkpoints_stand_on_ground_and_things_are_inside_level(n):
    with open(os.path.join(LEVELS_DIR, f"level_{n}.json")) as f:
        d = json.load(f)
    spans = [(x, x + w) for x, w in d["ground"]]
    for cx in d["checkpoints"]:
        assert any(a <= cx <= b - 14 for a, b in spans), cx
    for e in d["enemies"]:
        assert 0 <= e["x"] <= d["width"]
    assert 0 <= d["goal"]["x"] <= d["width"] - 44
    assert any(a <= d["goal"]["x"] and d["goal"]["x"] + 44 <= b for a, b in spans)
