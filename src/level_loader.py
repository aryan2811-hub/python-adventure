"""Turns a level JSON file into game objects, and refuses broken data with a clear message."""
import json
from src import settings as S
from src.level import Level
from src.platforms import Platform, MovingPlatform, BreakablePlatform
from src.enemy import WalkingEnemy, FlyingEnemy, BossEnemy
from src.collectibles import Coin, Checkpoint, Goal


class LevelError(Exception):
    pass


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def parse_level(data, source="level"):
    def err(msg):
        raise LevelError(f"{source}: {msg}")

    def need(obj, key, where, check=_num, what="a number"):
        if not isinstance(obj, dict) or key not in obj:
            err(f"{where} is missing '{key}'")
        if not check(obj[key]):
            err(f"{where}: '{key}' must be {what}")
        return obj[key]

    if not isinstance(data, dict):
        err("top level must be a JSON object")
    name = need(data, "name", "level", lambda v: isinstance(v, str) and v, "a non-empty string")
    width = need(data, "width", "level")
    if width < S.SCREEN_WIDTH:
        err(f"width must be at least {S.SCREEN_WIDTH}")

    spawn = data.get("spawn")
    if not (isinstance(spawn, list) and len(spawn) == 2 and all(_num(v) for v in spawn)):
        err("'spawn' must be [x, y]")
    if not 0 <= spawn[0] <= width:
        err("spawn x is outside the level")

    ground = data.get("ground")
    if not isinstance(ground, list) or not ground:
        err("'ground' must be a non-empty list of [x, width]")
    platforms = []
    for i, g in enumerate(ground):
        if not (isinstance(g, list) and len(g) == 2 and all(_num(v) for v in g)):
            err(f"ground[{i}] must be [x, width]")
        x, w = g
        if w <= 0 or x < 0 or x + w > width:
            err(f"ground[{i}] is outside the level or has no width")
        platforms.append(Platform(x, S.GROUND_Y, w, S.SCREEN_HEIGHT - S.GROUND_Y + 20, "ground"))

    for i, p in enumerate(data.get("platforms", [])):
        where = f"platforms[{i}]"
        kind = need(p, "type", where, lambda v: v in ("stone", "moving", "breakable"), "stone, moving or breakable")
        x, y = need(p, "x", where), need(p, "y", where)
        w, h = need(p, "w", where), need(p, "h", where)
        if w <= 0 or h <= 0:
            err(f"{where} must have positive w and h")
        if kind == "stone":
            platforms.append(Platform(x, y, w, h))
        elif kind == "breakable":
            platforms.append(BreakablePlatform(x, y, w, h))
        else:
            ax, ay, speed = p.get("ax", 0), p.get("ay", 0), p.get("speed", 0.025)
            if not (_num(ax) and _num(ay) and _num(speed)):
                err(f"{where}: ax, ay and speed must be numbers")
            platforms.append(MovingPlatform(x, y, w, h, ax=ax, ay=ay, speed=speed))

    enemies = []
    for i, e in enumerate(data.get("enemies", [])):
        where = f"enemies[{i}]"
        kind = need(e, "type", where, lambda v: v in ("walker", "flyer", "boss"), "walker, flyer or boss")
        x, y = need(e, "x", where), need(e, "y", where)
        if not 0 <= x <= width:
            err(f"{where} is outside the level")
        if kind in ("walker", "boss"):
            xmin, xmax = need(e, "xmin", where), need(e, "xmax", where)
            if xmin > xmax:
                err(f"{where}: xmin must not be greater than xmax")
            if kind == "walker":
                enemies.append(WalkingEnemy(x, y, xmin, xmax, e.get("speed", 1.5)))
            else:
                hp = e.get("hp", S.BOSS_HP)
                if not isinstance(hp, int) or hp < 1:
                    err(f"{where}: hp must be a whole number of at least 1")
                enemies.append(BossEnemy(x, y, xmin, xmax, hp))
        else:
            ax, ay = e.get("ax", 60), e.get("ay", 30)
            if not (_num(ax) and _num(ay)):
                err(f"{where}: ax and ay must be numbers")
            enemies.append(FlyingEnemy(x, y, ax, ay))

    coins = []
    for i, c in enumerate(data.get("coins", [])):
        where = f"coins[{i}]"
        x, y = need(c, "x", where), need(c, "y", where)
        n, gap = c.get("n", 1), c.get("gap", 38)
        if not isinstance(n, int) or not 1 <= n <= 50 or not _num(gap):
            err(f"{where}: n must be a whole number from 1 to 50")
        if not 0 <= x <= width:
            err(f"{where} is outside the level")
        coins += [Coin(x + k * gap, y) for k in range(n)]

    checkpoints = []
    for i, x in enumerate(data.get("checkpoints", [])):
        if not _num(x) or not 0 <= x <= width:
            err(f"checkpoints[{i}] must be an x position inside the level")
        checkpoints.append(Checkpoint(x, S.GROUND_Y))

    goal_x = need(data.get("goal"), "x", "goal") if isinstance(data.get("goal"), dict) else err("'goal' must be {\"x\": number}")
    if not 0 <= goal_x <= width - 44:
        err("goal is outside the level")

    return Level(platforms, enemies, coins, checkpoints, tuple(spawn), int(width), name, Goal(goal_x, S.GROUND_Y))


def load_level(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise LevelError(f"{path}: file not found")
    except json.JSONDecodeError as exc:
        raise LevelError(f"{path}: not valid JSON ({exc})")
    return parse_level(data, source=str(path))
