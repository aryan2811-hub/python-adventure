import math
import pygame
from src import settings as S


class Enemy:
    is_boss = False
    score_value = S.ENEMY_SCORE

    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.alive = True
        self.t = 0.0

    @property
    def harmless(self):
        return False

    def stomp(self):
        """Called when the player lands on top. Returns True if the enemy died."""
        self.alive = False
        return True

    def reset(self):
        self.alive = True

    @property
    def hit_rect(self):
        """Slightly smaller than the sprite so near-misses feel fair."""
        return self.rect.inflate(-8, -6)

    def update(self):
        self.t += 0.1


class WalkingEnemy(Enemy):
    """Patrols left and right between xmin and xmax (rect.x values)."""

    def __init__(self, x, y, xmin, xmax, speed=1.5):
        super().__init__(x, y, 38, 32)
        self.xmin, self.xmax = xmin, xmax
        self.speed = speed
        self.dir = 1
        self.pos_x = float(x)

    def update(self):
        super().update()
        self.pos_x += self.dir * self.speed
        if self.pos_x >= self.xmax:
            self.pos_x, self.dir = float(self.xmax), -1
        elif self.pos_x <= self.xmin:
            self.pos_x, self.dir = float(self.xmin), 1
        self.rect.x = round(self.pos_x)

    def draw(self, surface, camera_x=0):
        r = self.rect.move(-camera_x, 0)
        if r.right < 0 or r.left > 960:
            return
        squash = int(2 * math.sin(self.t * 2))
        body = pygame.Rect(r.x, r.y + 4 - squash, r.w, r.h - 4 + squash)
        pygame.draw.ellipse(surface, (140, 70, 170), body)
        pygame.draw.ellipse(surface, (95, 45, 125), body, 3)
        step = int(4 * math.sin(self.t * 2))
        pygame.draw.ellipse(surface, (60, 30, 80), (r.x + 4 + step, r.bottom - 7, 12, 7))
        pygame.draw.ellipse(surface, (60, 30, 80), (r.right - 16 - step, r.bottom - 7, 12, 7))
        for ex in (r.x + 9, r.x + 24):
            pygame.draw.circle(surface, (255, 255, 255), (ex + 3, r.y + 14), 5)
            pygame.draw.circle(surface, (20, 20, 20), (ex + 3 + self.dir * 2, r.y + 15), 2)


class FlyingEnemy(Enemy):
    """Floats in a wave around (x, y). ax / ay = how far it swings."""

    def __init__(self, x, y, ax=60, ay=30):
        super().__init__(0, 0, 40, 28)
        self.ox, self.oy = x, y
        self.ax, self.ay = ax, ay
        self.phase = 0.0
        self.rect.center = (x, y)

    def update(self):
        super().update()
        self.phase += 0.035
        self.rect.centerx = round(self.ox + self.ax * math.sin(self.phase))
        self.rect.centery = round(self.oy + self.ay * math.sin(self.phase * 2))

    def draw(self, surface, camera_x=0):
        r = self.rect.move(-camera_x, 0)
        if r.right < 0 or r.left > 960:
            return
        flap = int(10 * math.sin(self.t * 3))
        cx, cy = r.center
        for side in (-1, 1):
            pts = [(cx + side * 6, cy), (cx + side * 26, cy - 6 - flap), (cx + side * 22, cy + 6)]
            pygame.draw.polygon(surface, (90, 50, 110), pts)
        pygame.draw.ellipse(surface, (210, 70, 70), (cx - 13, cy - 11, 26, 24))
        pygame.draw.ellipse(surface, (150, 40, 40), (cx - 13, cy - 11, 26, 24), 3)
        pygame.draw.circle(surface, (255, 255, 255), (cx - 5, cy - 3), 4)
        pygame.draw.circle(surface, (255, 255, 255), (cx + 5, cy - 3), 4)
        pygame.draw.circle(surface, (20, 20, 20), (cx - 5, cy - 2), 2)
        pygame.draw.circle(surface, (20, 20, 20), (cx + 5, cy - 2), 2)


class BossEnemy(Enemy):
    """Big patrolling boss. Stomp it hp times. It gets faster and is stunned after each hit."""

    is_boss = True
    score_value = S.BOSS_SCORE

    def __init__(self, x, y, xmin, xmax, hp=S.BOSS_HP):
        super().__init__(x, y, 80, 80)
        self.xmin, self.xmax = xmin, xmax
        self.max_hp = hp
        self.hp = hp
        self.stun = 0
        self.dir = -1
        self.pos_x = float(x)

    @property
    def harmless(self):
        return self.stun > 0

    @property
    def hit_rect(self):
        return self.rect.inflate(-10, -8)

    def reset(self):
        self.alive = True
        self.hp = self.max_hp
        self.stun = 0
        self.dir = -1
        self.pos_x = float(self.xmin + (self.xmax - self.xmin) // 2)
        self.rect.x = round(self.pos_x)

    def stomp(self):
        if self.stun > 0:
            return False
        self.hp -= 1
        if self.hp <= 0:
            self.alive = False
            return True
        self.stun = S.BOSS_STUN
        return False

    def update(self):
        super().update()
        if self.stun > 0:
            self.stun -= 1
            return
        speed = 2.0 + 0.6 * (self.max_hp - self.hp)
        self.pos_x += self.dir * speed
        if self.pos_x >= self.xmax:
            self.pos_x, self.dir = float(self.xmax), -1
        elif self.pos_x <= self.xmin:
            self.pos_x, self.dir = float(self.xmin), 1
        self.rect.x = round(self.pos_x)

    def draw(self, surface, camera_x=0):
        r = self.rect.move(-camera_x, 0)
        if r.right < 0 or r.left > 960:
            return
        if self.stun > 0 and (self.stun // 4) % 2:
            return  # flash when hit
        bob = int(3 * math.sin(self.t * 2))
        body = pygame.Rect(r.x, r.y + 10 + bob, r.w, r.h - 10 - bob)
        pygame.draw.ellipse(surface, (60, 140, 70), body)
        pygame.draw.ellipse(surface, (35, 95, 45), body, 4)
        for hx in (r.x + 8, r.right - 22):  # horns
            pygame.draw.polygon(surface, (235, 225, 190), [(hx, r.y + 22 + bob), (hx + 7, r.y - 2 + bob), (hx + 14, r.y + 22 + bob)])
        for ex in (r.x + 20, r.x + 48):  # angry eyes
            pygame.draw.circle(surface, (255, 255, 255), (ex + 6, r.y + 36 + bob), 8)
            pygame.draw.circle(surface, (200, 20, 20), (ex + 6 + self.dir * 3, r.y + 37 + bob), 4)
            pygame.draw.line(surface, (20, 50, 25), (ex - 3, r.y + 25 + bob), (ex + 14, r.y + 30 + bob), 4)
        pygame.draw.rect(surface, (30, 60, 35), (r.x + 22, r.y + 56 + bob, 36, 7), border_radius=3)
        step = int(5 * math.sin(self.t * 2))
        pygame.draw.ellipse(surface, (35, 95, 45), (r.x + 8 + step, r.bottom - 9, 24, 9))
        pygame.draw.ellipse(surface, (35, 95, 45), (r.right - 32 - step, r.bottom - 9, 24, 9))
        # health bar
        bar_w = 100
        bx, by = r.centerx - bar_w // 2, r.y - 18
        pygame.draw.rect(surface, (40, 40, 50), (bx - 2, by - 2, bar_w + 4, 12), border_radius=3)
        seg = bar_w / self.max_hp
        for i in range(self.hp):
            pygame.draw.rect(surface, (230, 60, 60), (bx + i * seg + 1, by, seg - 2, 8))
