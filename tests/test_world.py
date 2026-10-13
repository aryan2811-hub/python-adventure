import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from src import settings as S
from src.platforms import Platform
from src.enemy import WalkingEnemy, FlyingEnemy
from src.collectibles import Coin, Checkpoint
from src.level import Level
from src.world import World


def make_world(enemies=(), coins=(), checkpoints=()):
    lv = Level(
        platforms=[Platform(0, 400, 400, 60, "ground"), Platform(600, 400, 600, 60, "ground")],
        enemies=list(enemies), coins=list(coins), checkpoints=list(checkpoints),
        spawn=(300, 340), width=1200,
    )
    w = World(lv)
    for _ in range(5):
        w.step(0, False)
    return w


def place(w, x, y=340):
    w.player.respawn_at((x, y), grace=0)


def test_start_with_five_hearts():
    w = make_world()
    assert w.player.health == 5 == S.MAX_HEALTH


def test_coin_collected_once_and_scores():
    w = make_world(coins=[Coin(66, 370)])
    place(w, 50)
    for _ in range(3):
        w.step(0, False)
    assert w.coins_collected == 1
    assert w.score == S.COIN_SCORE
    w.step(0, False)
    assert w.score == S.COIN_SCORE  # not collected twice


def test_enemy_side_hit_costs_exactly_one_heart():
    walker = WalkingEnemy(80, 368, 80, 80, speed=0)
    w = make_world(enemies=[walker])
    place(w, 60)
    for _ in range(3):
        w.step(0, False)
    assert w.player.health == 4


def test_no_repeated_damage_while_invulnerable():
    walker = WalkingEnemy(60, 368, 60, 60, speed=0)
    w = make_world(enemies=[walker])
    place(w, 60)
    for _ in range(S.INVULN_FRAMES - 10):
        w.step(0, False)
    assert w.player.health == 4


def test_stomp_kills_enemy_and_bounces():
    walker = WalkingEnemy(60, 368, 60, 60, speed=0)
    w = make_world(enemies=[walker])
    pl = w.player
    pl.respawn_at((60, 300), grace=0)
    pl.vy = 4
    w.score = 0
    for _ in range(40):
        w.step(0, False)
        if not walker.alive:
            break
    assert not walker.alive
    assert w.score == S.ENEMY_SCORE
    assert pl.health == 5
    assert pl.vy < 0


def test_flying_enemy_hurts():
    flyer = FlyingEnemy(66, 360, ax=0, ay=0)
    w = make_world(enemies=[flyer])
    place(w, 50)
    w.step(0, False)
    assert w.player.health == 4


def test_checkpoint_activates_and_sets_spawn():
    cp = Checkpoint(100, 400)
    w = make_world(checkpoints=[cp])
    w.player.respawn_at((95, 340), grace=0)
    w.step(0, False)
    assert cp.activated
    assert w.spawn == cp.spawn


def test_pit_fall_costs_heart_and_respawns_at_checkpoint():
    cp = Checkpoint(100, 400)
    w = make_world(checkpoints=[cp])
    w.player.respawn_at((95, 340), grace=0)
    w.step(0, False)
    w.player.respawn_at((450, 300), grace=0)  # over the gap between the two ground pieces
    for _ in range(200):
        w.step(0, False)
        if w.respawned:
            break
    assert w.respawned
    assert w.player.health == 4
    assert w.player.rect.topleft == (round(cp.spawn[0]), round(cp.spawn[1]))
    assert not w.game_over


def test_game_over_when_health_reaches_zero_and_reset():
    w = make_world()
    w.player.health = 1
    w.player.respawn_at((450, 300), grace=0)
    for _ in range(200):
        w.step(0, False)
        if w.game_over:
            break
    assert w.game_over
    before = w.player.rect.copy()
    w.step(1, False)
    assert w.player.rect == before  # frozen while game over
    w.score = 99
    w.reset()
    assert not w.game_over and w.player.health == 5 and w.score == 0


def test_dead_enemy_stays_dead_until_reset():
    walker = WalkingEnemy(60, 368, 60, 60, speed=0)
    w = make_world(enemies=[walker])
    walker.alive = False
    place(w, 60)
    w.step(0, False)
    assert w.player.health == 5
    w.reset()
    assert walker.alive
