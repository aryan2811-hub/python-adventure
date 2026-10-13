import math
import pygame
from src import settings as S


class Platform:
    """A solid stone rectangle. Subclasses add movement or breaking."""

    def __init__(self, x, y, w, h, kind="stone"):
        self.rect = pygame.Rect(x, y, w, h)
        self.kind = kind
        self.solid = True
        self.dx = 0  # how far it moved this frame (used to carry the player)
        self.dy = 0

    def update(self, player_rect=None):
        pass

    def on_stand(self):
        """Called every frame the player is standing on this platform."""

    def reset(self):
        pass

    def draw(self, surface, camera_x=0):
        if not self.solid:
            return
        r = self.rect.move(-camera_x, 0)
        if r.right < 0 or r.left > S.SCREEN_WIDTH:
            return
        pygame.draw.rect(surface, S.STONE_COLOR, r, border_radius=6)
        pygame.draw.rect(surface, S.STONE_EDGE, r, width=3, border_radius=6)
        pygame.draw.rect(surface, S.GRASS_COLOR, (r.x, r.y, r.w, 8), border_radius=4)


class MovingPlatform(Platform):
    """Slides back and forth (ax = horizontal range, ay = vertical range)."""

    def __init__(self, x, y, w, h, ax=0, ay=0, speed=0.025):
        super().__init__(x, y, w, h, "moving")
        self.ox, self.oy = x, y
        self.ax, self.ay = ax, ay
        self.speed = speed
        self.phase = 0.0

    def reset(self):
        self.phase = 0.0
        self.rect.topleft = (self.ox, self.oy)
        self.dx = self.dy = 0

    def update(self, player_rect=None):
        old_x, old_y = self.rect.x, self.rect.y
        self.phase += self.speed
        self.rect.x = round(self.ox + self.ax * math.sin(self.phase))
        self.rect.y = round(self.oy + self.ay * math.sin(self.phase))
        self.dx = self.rect.x - old_x
        self.dy = self.rect.y - old_y

    def draw(self, surface, camera_x=0):
        super().draw(surface, camera_x)
        r = self.rect.move(-camera_x, 0)
        pygame.draw.rect(surface, (230, 190, 60), (r.x + 6, r.centery - 3, r.w - 12, 6), border_radius=3)


class BreakablePlatform(Platform):
    """Cracks when stood on, disappears, then comes back."""

    BREAK_DELAY = 40
    RESPAWN_DELAY = 180

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, "breakable")
        self.timer = 0
        self.triggered = False

    def on_stand(self):
        if self.solid:
            self.triggered = True

    def reset(self):
        self.solid = True
        self.timer = 0
        self.triggered = False

    def update(self, player_rect=None):
        if self.triggered and self.solid:
            self.timer += 1
            if self.timer >= self.BREAK_DELAY:
                self.solid = False
                self.timer = 0
                self.triggered = False
        elif not self.solid:
            self.timer += 1
            blocked = player_rect is not None and self.rect.colliderect(player_rect)
            if self.timer >= self.RESPAWN_DELAY and not blocked:
                self.solid = True
                self.timer = 0

    def draw(self, surface, camera_x=0):
        if not self.solid:
            return
        r = self.rect.move(-camera_x, 0)
        shake = 2 if self.triggered and (self.timer // 3) % 2 else 0
        r.x += shake
        pygame.draw.rect(surface, (170, 140, 110), r, border_radius=6)
        pygame.draw.rect(surface, (120, 95, 70), r, width=3, border_radius=6)
        for cx in range(r.x + 14, r.right - 8, 24):
            pygame.draw.line(surface, (120, 95, 70), (cx, r.y + 4), (cx - 6, r.bottom - 4), 2)
