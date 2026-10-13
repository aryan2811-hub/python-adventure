import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from src import settings as S
from src.player import Player
from src.platforms import Platform


def ground():
    return [Platform(0, 400, 2000, 60, "ground")]


def settle(player, platforms, frames=60):
    for _ in range(frames):
        player.update(0, False, platforms)


def test_gravity_pulls_player_down():
    p = Player(100, 0)
    start = p.rect.y
    p.update(0, False, [])
    p.update(0, False, [])
    assert p.rect.y > start


def test_player_lands_on_ground():
    p = Player(100, 0)
    plats = ground()
    settle(p, plats)
    assert p.on_ground
    assert p.rect.bottom == 400
    assert p.vy == 0


def test_fall_speed_is_capped():
    p = Player(100, -5000)
    for _ in range(200):
        p.update(0, False, [])
    assert p.vy <= S.MAX_FALL_SPEED


def test_move_right_and_left():
    p = Player(100, 0)
    plats = ground()
    settle(p, plats)
    x = p.rect.x
    p.update(1, False, plats)
    assert p.rect.x == x + S.MOVE_SPEED
    p.update(-1, False, plats)
    p.update(-1, False, plats)
    assert p.rect.x < x


def test_jump_leaves_ground():
    p = Player(100, 0)
    plats = ground()
    settle(p, plats)
    p.update(0, True, plats)
    assert p.vy < 0
    assert not p.on_ground


def test_double_jump_allowed_but_not_triple():
    p = Player(100, 0)
    plats = ground()
    settle(p, plats)
    p.update(0, True, plats)
    p.update(0, True, plats)
    assert p.jumps_left == 0
    vy_before = p.vy
    p.update(0, True, plats)
    assert p.vy > vy_before - 1  # third press did not give a new jump impulse


def test_jumps_reset_on_landing():
    p = Player(100, 0)
    plats = ground()
    settle(p, plats)
    p.update(0, True, plats)
    settle(p, plats, 120)
    assert p.jumps_left == S.MAX_JUMPS


def test_wall_blocks_horizontal_movement():
    p = Player(100, 0)
    plats = ground() + [Platform(200, 300, 40, 100, "wall")]
    settle(p, plats)
    for _ in range(100):
        p.update(1, False, plats)
    assert p.rect.right <= 200


def test_head_bump_stops_upward_movement():
    p = Player(100, 340)  # spawn already under the ceiling
    plats = ground() + [Platform(60, 280, 120, 20, "ceiling")]
    settle(p, plats)
    p.update(0, True, plats)
    highest = p.rect.top
    for _ in range(30):
        p.update(0, False, plats)
        highest = min(highest, p.rect.top)
    assert highest >= 300  # head stopped under the ceiling (its bottom is at y=300)


def test_player_never_ends_inside_platform():
    p = Player(100, 0)
    plats = ground() + [Platform(250, 330, 100, 20)]
    settle(p, plats)
    for i in range(300):
        p.update(1 if i % 40 < 25 else -1, i % 30 == 0, plats)
        for pl in plats:
            assert not p.rect.colliderect(pl.rect)


def test_hurt_only_once_during_invulnerability():
    p = Player(0, 0)
    assert p.hurt() is True
    assert p.hurt() is False
    assert p.health == S.MAX_HEALTH - 1
    for _ in range(S.INVULN_FRAMES):
        p.update(0, False, [])
    assert p.hurt() is True
    assert p.health == S.MAX_HEALTH - 2
