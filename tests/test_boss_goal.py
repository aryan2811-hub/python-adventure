import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import settings as S
from src.platforms import Platform
from src.enemy import BossEnemy
from src.collectibles import Goal
from src.level import Level
from src.world import World


def arena(boss=None, goal_x=700, score=0):
    enemies = [boss] if boss else []
    lv = Level(platforms=[Platform(0, 400, 1000, 80, "ground")], enemies=enemies,
               spawn=(100, 340), width=1000, name="T", goal=Goal(goal_x, 400))
    w = World(lv, score)
    for _ in range(5):
        w.step(0, False)
    return w


def test_boss_needs_hp_stomps_and_stuns_between_hits():
    b = BossEnemy(500, 320, 400, 800, hp=3)
    assert b.stomp() is False and b.hp == 2 and b.harmless
    assert b.stomp() is False and b.hp == 2  # ignored while stunned
    for _ in range(S.BOSS_STUN):
        b.update()
    assert not b.harmless
    b.stomp()
    for _ in range(S.BOSS_STUN):
        b.update()
    assert b.stomp() is True and not b.alive


def test_boss_speeds_up_as_it_loses_hp():
    b = BossEnemy(500, 320, 100, 900, hp=5)
    x0 = b.rect.x
    b.update()
    slow = abs(b.rect.x - x0)
    b.hp = 1
    x1 = b.pos_x
    b.update()
    assert abs(b.pos_x - x1) > slow


def test_boss_stomp_in_world_scores_and_bounces():
    b = BossEnemy(300, 320, 300, 300, hp=2)
    w = arena(b)
    w.player.respawn_at((320, 240), grace=0)
    w.player.vy = 4
    for _ in range(40):
        w.step(0, False)
        if b.hp < 2:
            break
    assert b.hp == 1 and w.score == S.BOSS_HIT_SCORE and w.player.health == 5 and w.player.vy < 0


def test_stunned_boss_does_not_hurt():
    b = BossEnemy(300, 320, 300, 300)
    w = arena(b)
    b.stun = 50
    w.player.respawn_at((320, 330), grace=0)
    for _ in range(5):
        w.step(0, False)
    assert w.player.health == 5


def test_goal_locked_until_boss_dead():
    b = BossEnemy(300, 320, 300, 300, hp=1)
    w = arena(b, goal_x=150)
    assert w.level.goal.locked
    w.player.respawn_at((150, 300), grace=0)
    for _ in range(20):
        w.step(0, False)
    assert not w.level_complete  # touched goal but locked
    b.stomp()
    for _ in range(3):
        w.step(0, False)
    assert not w.level.goal.locked and w.level_complete


def test_level_complete_adds_bonus_and_freezes_world():
    w = arena(goal_x=150, score=40)
    w.player.respawn_at((150, 300), grace=0)
    for _ in range(20):
        w.step(0, False)
        if w.level_complete:
            break
    assert w.level_complete
    assert w.bonus == S.GOAL_BONUS + S.HEART_BONUS * 5
    assert w.score == 40 + w.bonus
    pos = w.player.rect.copy()
    w.step(1, False)
    assert w.player.rect == pos


def test_reset_restores_boss_goal_and_start_score():
    b = BossEnemy(300, 320, 300, 500, hp=1)
    w = arena(b, goal_x=150, score=40)
    b.stomp()
    w.score = 999
    w.reset()
    assert b.alive and b.hp == 1 and w.level.goal.locked and w.score == 40
