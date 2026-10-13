import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from src.player import Player
from src.platforms import Platform, MovingPlatform, BreakablePlatform


def run(player, plats, frames):
    for _ in range(frames):
        for p in plats:
            p.update(player.rect)
        player.update(0, False, plats)


def test_moving_platform_carries_player():
    mp = MovingPlatform(100, 400, 200, 20, ax=100, speed=0.05)
    p = Player(150, 300)
    run(p, [mp], 30)
    assert p.standing_on is mp
    start = p.rect.centerx - mp.rect.centerx
    run(p, [mp], 60)
    assert p.standing_on is mp
    assert abs((p.rect.centerx - mp.rect.centerx) - start) <= 2  # stays put relative to platform


def test_vertical_moving_platform_keeps_player_on_top():
    mp = MovingPlatform(100, 400, 200, 20, ay=60, speed=0.05)
    p = Player(150, 300)
    run(p, [mp], 200)
    assert p.on_ground and p.rect.bottom == mp.rect.top


def test_breakable_platform_breaks_and_returns():
    bp = BreakablePlatform(100, 400, 200, 20)
    p = Player(150, 300)
    run(p, [bp], 30)
    assert bp.solid
    run(p, [bp], BreakablePlatform.BREAK_DELAY + 5)
    assert not bp.solid
    away = Player(2000, 0)
    for _ in range(BreakablePlatform.RESPAWN_DELAY + 2):
        bp.update(away.rect)
    assert bp.solid


def test_player_falls_through_broken_platform():
    bp = BreakablePlatform(100, 400, 200, 20)
    p = Player(150, 300)
    run(p, [bp], BreakablePlatform.BREAK_DELAY + 40)
    assert p.rect.top > 400


def test_breakable_waits_if_player_overlaps():
    bp = BreakablePlatform(100, 400, 200, 20)
    bp.solid = False
    blocker = pygame.Rect(150, 395, 32, 48)
    for _ in range(BreakablePlatform.RESPAWN_DELAY + 20):
        bp.update(blocker)
    assert not bp.solid
