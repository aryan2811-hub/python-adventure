import pygame
from src import settings as S
from src.player import Player


class World:
    """All gameplay rules for one level, with no drawing. This makes it easy to test.

    Every frame, step() fills self.events with short names such as "coin" or "hurt".
    The Game reads them to play sounds and save progress. World itself knows nothing about sound.
    Possible events: jump, coin, checkpoint, stomp, hurt, goal, game_over.
    """

    def __init__(self, level, score=0):
        self.level = level
        self.start_score = score
        self.events = []
        self.reset()

    def reset(self):
        lv = self.level
        self.player = Player(*lv.spawn)
        self.spawn = lv.spawn
        for e in lv.enemies:
            e.reset()
        for p in lv.platforms:
            p.reset()
        for c in lv.coins:
            c.collected = False
        for cp in lv.checkpoints:
            cp.activated = False
        self.score = self.start_score
        self.coins_collected = 0
        self.bonus = 0
        self.game_over = False
        self.level_complete = False
        self.respawned = False
        self.events = []
        self._update_goal_lock()

    def _update_goal_lock(self):
        if self.level.goal is not None:
            self.level.goal.locked = any(e.is_boss and e.alive for e in self.level.enemies)

    def step(self, move, jump):
        self.respawned = False
        self.events = []
        if self.game_over or self.level_complete:
            return
        lv, pl = self.level, self.player
        for p in lv.platforms:
            p.update(pl.rect)
        for e in lv.enemies:
            if e.alive:
                e.update()
        for c in lv.coins:
            c.update()

        will_jump = bool(jump) and pl.jumps_left > 0  # same rule Player.update uses
        prev_bottom = pl.rect.bottom
        pl.update(move, jump, lv.platforms)
        if will_jump:
            self.events.append("jump")
        if pl.rect.left < 0 or pl.rect.right > lv.width:
            pl.rect.clamp_ip(pygame.Rect(0, -10000, lv.width, 20000))
            pl.pos_x = float(pl.rect.x)

        self._collect_coins()
        self._check_checkpoints()
        self._check_enemies(prev_bottom)
        self._update_goal_lock()
        self._check_goal()
        if pl.rect.top > S.FALL_LIMIT:
            self._fell_into_pit()
        if pl.health <= 0:
            self.game_over = True
            self.events = [e for e in self.events if e != "hurt"]  # the game-over sound is enough
            self.events.append("game_over")

    def _collect_coins(self):
        for c in self.level.coins:
            if not c.collected and self.player.rect.colliderect(c.rect):
                c.collected = True
                self.coins_collected += 1
                self.score += S.COIN_SCORE
                self.events.append("coin")

    def _check_checkpoints(self):
        for cp in self.level.checkpoints:
            if not cp.activated and self.player.rect.colliderect(cp.rect):
                cp.activated = True
                self.spawn = cp.spawn
                self.events.append("checkpoint")

    def _check_enemies(self, prev_bottom):
        pl = self.player
        for e in self.level.enemies:
            if not e.alive or e.harmless or not pl.rect.colliderect(e.hit_rect):
                continue
            stomping = pl.vy > 0 and prev_bottom <= e.hit_rect.top + 10
            if stomping:
                if e.stomp():
                    self.score += e.score_value
                elif e.is_boss:
                    self.score += S.BOSS_HIT_SCORE
                pl.bounce()
                self.events.append("stomp")
            else:
                if pl.hurt():
                    self.events.append("hurt")

    def _check_goal(self):
        goal = self.level.goal
        if goal is not None and not goal.locked and self.player.rect.colliderect(goal.rect):
            self.bonus = S.GOAL_BONUS + S.HEART_BONUS * self.player.health
            self.score += self.bonus
            self.level_complete = True
            self.events.append("goal")

    def _fell_into_pit(self):
        # Falling always costs a heart, even right after being hit.
        self.player.health = max(0, self.player.health - 1)
        if self.player.health > 0:
            self.player.respawn_at(self.spawn)
            self.respawned = True
            self.events.append("hurt")