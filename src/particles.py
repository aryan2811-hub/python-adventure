import math
import random

import pygame


def _offset(cam):
    """The camera offset may be a single number (x only) or an (x, y) pair."""
    if isinstance(cam, (tuple, list)):
        return cam[0], cam[1]
    return cam, 0


class Particle:
    def __init__(self, x, y, vx, vy, color, size, life, gravity):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        self.gravity = gravity

    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, screen, ox, oy):
        shrink = self.life / self.max_life  # particles get smaller as they fade
        radius = max(1, int(self.size * shrink))
        pygame.draw.circle(screen, self.color, (int(self.x - ox), int(self.y - oy)), radius)


class ParticleSystem:
    MAX_PARTICLES = 300  # keeps the game fast even if many bursts happen at once

    def __init__(self):
        self.items = []

    def burst(self, x, y, color, count=10, speed=3.0, gravity=0.15, life=30, size=4):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            v = random.uniform(0.3, 1.0) * speed
            vx = math.cos(angle) * v
            vy = math.sin(angle) * v - speed * 0.4  # slight upward push
            self.items.append(
                Particle(x, y, vx, vy, color, size, random.randint(max(1, life // 2), life), gravity)
            )
        if len(self.items) > self.MAX_PARTICLES:
            self.items = self.items[-self.MAX_PARTICLES:]

    def update(self):
        for p in self.items:
            p.update()
        self.items = [p for p in self.items if p.life > 0]

    def draw(self, screen, cam):
        ox, oy = _offset(cam)
        for p in self.items:
            p.draw(screen, ox, oy)

    def clear(self):
        self.items = []