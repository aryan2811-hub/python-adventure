import math
import random
import pygame
from src import settings as S


def _hill_layer(width, base_y, amp, periods, color, phase=0.0):
    """A seamless (tileable) hill silhouette: whole number of sine periods."""
    surf = pygame.Surface((width, S.SCREEN_HEIGHT), pygame.SRCALPHA)
    pts = [(0, S.SCREEN_HEIGHT)]
    for x in range(0, width + 1, 8):
        a = 2 * math.pi * periods * x / width + phase
        y = base_y - amp * (0.5 + 0.35 * math.sin(a) + 0.15 * math.sin(2.3 * a + 1))
        pts.append((x, y))
    pts.append((width, S.SCREEN_HEIGHT))
    pygame.draw.polygon(surf, color, pts)
    return surf


def _cloud_layer(width, seed=7):
    surf = pygame.Surface((width, 260), pygame.SRCALPHA)
    rng = random.Random(seed)
    for _ in range(7):
        cx, cy = rng.randint(0, width), rng.randint(30, 200)
        for dx, dy, r in ((-30, 6, 26), (0, -6, 34), (32, 4, 28), (60, 10, 20)):
            pygame.draw.circle(surf, S.CLOUD_COLOR, (cx + dx, cy + dy), r)
    return surf


class Background:
    """Sky + clouds + two hill layers, each scrolling at its own speed (parallax)."""

    def __init__(self):
        self.sky = pygame.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT))
        for y in range(S.SCREEN_HEIGHT):
            t = y / S.SCREEN_HEIGHT
            c = tuple(int(a + (b - a) * t) for a, b in zip(S.SKY_TOP, S.SKY_BOTTOM))
            pygame.draw.line(self.sky, c, (0, y), (S.SCREEN_WIDTH, y))
        w = S.SCREEN_WIDTH * 2
        self.clouds = _cloud_layer(w)
        self.far = _hill_layer(w, 390, 140, 3, S.HILL_FAR)
        self.near = _hill_layer(w, 450, 90, 5, S.HILL_NEAR, 1.0)
        # (surface, parallax factor, y position)
        self.layers = [(self.clouds, 0.15, 10), (self.far, 0.3, 0), (self.near, 0.55, 0)]
        self.time = 0

    def draw(self, surface, camera_x):
        self.time += 1
        surface.blit(self.sky, (0, 0))
        for img, factor, y in self.layers:
            w = img.get_width()
            drift = self.time * 0.2 if img is self.clouds else 0
            off = int(camera_x * factor + drift) % w
            surface.blit(img, (-off, y))
            surface.blit(img, (w - off, y))
