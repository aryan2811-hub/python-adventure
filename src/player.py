import pygame
from src import settings as S


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, S.PLAYER_W, S.PLAYER_H)
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.jumps_left = S.MAX_JUMPS
        self.facing = 1
        self.standing_on = None
        self.health = S.MAX_HEALTH
        self.invuln = 0

    def hurt(self, amount=1):
        """Remove hearts unless recently hit. Returns True if damage was applied."""
        if self.invuln > 0 or self.health <= 0:
            return False
        self.health = max(0, self.health - amount)
        self.invuln = S.INVULN_FRAMES
        self.vy = S.HURT_BOUNCE
        return True

    def bounce(self, speed=None):
        self.vy = S.STOMP_BOUNCE if speed is None else speed
        self.jumps_left = max(self.jumps_left, 1)

    def respawn_at(self, pos, grace=S.RESPAWN_GRACE):
        self.pos_x, self.pos_y = float(pos[0]), float(pos[1])
        self.rect.topleft = (round(self.pos_x), round(self.pos_y))
        self.vx = self.vy = 0.0
        self.standing_on = None
        self.jumps_left = S.MAX_JUMPS
        self.invuln = max(self.invuln, grace)

    def update(self, move_dir, jump_pressed, platforms):
        """move_dir: -1, 0 or 1. jump_pressed: True only on the frame the key goes down."""
        platforms = [p for p in platforms if p.solid]
        if self.invuln > 0:
            self.invuln -= 1

        # Ride a moving platform: move with it before doing anything else.
        if self.standing_on is not None and self.standing_on.solid:
            self.pos_x += self.standing_on.dx
            self.pos_y += self.standing_on.dy

        self.vx = move_dir * S.MOVE_SPEED
        if move_dir:
            self.facing = move_dir

        if jump_pressed and self.jumps_left > 0:
            self.vy = S.JUMP_SPEED
            self.jumps_left -= 1
            self.on_ground = False

        self.vy = min(self.vy + S.GRAVITY, S.MAX_FALL_SPEED)

        # Move on X first, fix overlaps, then Y. This stops the player sticking to walls.
        self.pos_x += self.vx
        self.rect.x = round(self.pos_x)
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vx > 0:
                    self.rect.right = p.rect.left
                elif self.vx < 0:
                    self.rect.left = p.rect.right
                self.pos_x = float(self.rect.x)

        self.pos_y += self.vy
        self.rect.y = round(self.pos_y)
        self.on_ground = False
        self.standing_on = None
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vy > 0:
                    self.rect.bottom = p.rect.top
                    self.on_ground = True
                    self.standing_on = p
                    self.jumps_left = S.MAX_JUMPS
                elif self.vy < 0:
                    self.rect.top = p.rect.bottom
                self.vy = 0.0
                self.pos_y = float(self.rect.y)

        if self.standing_on is not None:
            self.standing_on.on_stand()

    def draw(self, surface, camera_x=0):
        if self.invuln > 0 and (self.invuln // 4) % 2:
            return  # blink while invulnerable
        r = self.rect.move(-camera_x, 0)
        pygame.draw.rect(surface, S.PLAYER_COLOR, r, border_radius=8)
        eye_x = r.centerx + (6 if self.facing > 0 else -6)
        pygame.draw.circle(surface, (255, 255, 255), (eye_x, r.y + 14), 6)
        pygame.draw.circle(surface, (20, 20, 20), (eye_x + self.facing * 2, r.y + 14), 3)
