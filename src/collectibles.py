import math
import pygame


class Coin:
    SIZE = 22

    def __init__(self, x, y):
        self.rect = pygame.Rect(0, 0, self.SIZE, self.SIZE)
        self.rect.center = (x, y)
        self.collected = False
        self.t = (x * 0.05) % 6.28

    def update(self):
        self.t += 0.08

    def draw(self, surface, camera_x=0):
        if self.collected:
            return
        cx, cy = self.rect.centerx - camera_x, self.rect.centery + int(3 * math.sin(self.t * 0.7))
        if cx < -20 or cx > 980:
            return
        w = max(3, int(11 * abs(math.cos(self.t))))  # fake "spinning" by squeezing the width
        pygame.draw.ellipse(surface, (200, 150, 20), (cx - w - 1, cy - 12, 2 * w + 2, 24))
        pygame.draw.ellipse(surface, (255, 215, 50), (cx - w, cy - 11, 2 * w, 22))
        if w > 6:
            pygame.draw.ellipse(surface, (255, 240, 150), (cx - w // 2, cy - 7, w // 2, 10))


class Checkpoint:
    def __init__(self, x, ground_y):
        self.rect = pygame.Rect(x, ground_y - 80, 14, 80)
        self.spawn = (x - 9, ground_y - 48)  # where the player reappears (player is 48 tall)
        self.activated = False

    def draw(self, surface, camera_x=0):
        r = self.rect.move(-camera_x, 0)
        if r.right < 0 or r.left > 960:
            return
        pygame.draw.rect(surface, (90, 70, 50), (r.x + 4, r.y, 5, r.h))
        color = (60, 200, 90) if self.activated else (220, 60, 60)
        pygame.draw.polygon(surface, color, [(r.x + 9, r.y + 4), (r.x + 42, r.y + 16), (r.x + 9, r.y + 28)])
        pygame.draw.circle(surface, (240, 200, 60), (r.x + 6, r.y), 5)


class Goal:
    """The finish flag. Locked (grey) until any boss in the level is defeated."""

    def __init__(self, x, ground_y):
        self.rect = pygame.Rect(x, ground_y - 110, 44, 110)
        self.locked = False

    def draw(self, surface, camera_x=0):
        r = self.rect.move(-camera_x, 0)
        if r.right < 0 or r.left > 960:
            return
        pygame.draw.rect(surface, (90, 70, 50), (r.x + 4, r.y, 6, r.h))
        color = (140, 140, 150) if self.locked else (255, 205, 40)
        pygame.draw.polygon(surface, color, [(r.x + 10, r.y + 4), (r.x + 44, r.y + 20), (r.x + 10, r.y + 36)])
        pygame.draw.circle(surface, (240, 200, 60), (r.x + 7, r.y), 6)
        if self.locked:  # little padlock
            pygame.draw.rect(surface, (70, 70, 80), (r.x + 16, r.y + 16, 14, 12), border_radius=2)
            pygame.draw.arc(surface, (70, 70, 80), (r.x + 17, r.y + 8, 12, 12), 0, 3.14, 2)
