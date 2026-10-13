import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from src import settings as S
from src.camera import Camera


def test_camera_clamps_left():
    c = Camera(3200)
    c.snap_to(pygame.Rect(0, 0, 32, 48))
    assert c.x == 0


def test_camera_clamps_right():
    c = Camera(3200)
    c.snap_to(pygame.Rect(3190, 0, 32, 48))
    assert c.x == 3200 - S.SCREEN_WIDTH


def test_camera_follows_smoothly():
    c = Camera(3200)
    target = pygame.Rect(1500, 0, 32, 48)
    c.update(target)
    first = c.x
    assert 0 < first < 1500 - S.SCREEN_WIDTH / 2  # moved, but not all the way
    for _ in range(200):
        c.update(target)
    assert abs(c.x - (target.centerx - S.SCREEN_WIDTH / 2)) < 1


def test_camera_never_leaves_level():
    c = Camera(3200)
    for x in (-500, 0, 1600, 3200, 9999):
        for _ in range(50):
            c.update(pygame.Rect(x, 0, 32, 48))
        assert 0 <= c.x <= 3200 - S.SCREEN_WIDTH
