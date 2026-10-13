from src import settings as S
from src.collectibles import Checkpoint, Coin, Goal
from src.enemy import WalkingEnemy
from src.level import Level
from src.platforms import Platform
from src.world import World


def make_world():
    """A flat level with just ground. The player is dropped in and left to land first."""
    ground = Platform(0, S.GROUND_Y, 3000, 80, "ground")
    level = Level(platforms=[ground], width=3000, name="test", spawn=(100, 400))
    w = World(level)
    for _ in range(60):
        w.step(0, False)
    assert w.player.on_ground
    return w


def test_events_are_empty_when_nothing_happens():
    w = make_world()
    w.step(0, False)
    assert w.events == []


def test_jump_event_and_no_event_when_out_of_jumps():
    w = make_world()
    w.step(0, True)
    assert "jump" in w.events
    for _ in range(S.MAX_JUMPS - 1):
        w.step(0, True)
    w.step(0, True)  # no jumps left in the air
    assert "jump" not in w.events


def test_coin_event_and_score():
    w = make_world()
    w.level.coins.append(Coin(*w.player.rect.center))
    w.step(0, False)
    assert "coin" in w.events
    assert w.score == S.COIN_SCORE
    w.step(0, False)
    assert "coin" not in w.events  # events are cleared every frame


def test_checkpoint_event_only_once():
    w = make_world()
    w.level.checkpoints.append(Checkpoint(w.player.rect.x + 10, S.GROUND_Y))
    w.step(0, False)
    assert "checkpoint" in w.events
    w.step(0, False)
    assert "checkpoint" not in w.events


def test_hurt_event_when_touching_enemy_from_the_side():
    w = make_world()
    x = w.player.rect.x + 10
    w.level.enemies.append(WalkingEnemy(x, S.GROUND_Y - 32, x, x))
    w.step(0, False)
    assert "hurt" in w.events
    assert w.player.health == S.MAX_HEALTH - 1


def test_stomp_event_when_landing_on_enemy():
    w = make_world()
    enemy = WalkingEnemy(400, S.GROUND_Y - 32, 400, 400)
    w.level.enemies.append(enemy)
    w.player.respawn_at((404, 380))
    found = False
    for _ in range(60):
        w.step(0, False)
        if "stomp" in w.events:
            found = True
            break
    assert found
    assert not enemy.alive
    assert w.score >= S.ENEMY_SCORE


def test_goal_event_and_level_complete():
    w = make_world()
    w.level.goal = Goal(w.player.rect.x + 10, S.GROUND_Y)
    w.step(0, False)
    assert "goal" in w.events
    assert w.level_complete
    w.step(0, False)
    assert w.events == []  # nothing more happens after the level is complete


def test_pit_fall_gives_hurt_event_and_respawn():
    w = make_world()
    w.player.respawn_at((100, S.FALL_LIMIT + 50))
    w.step(0, False)
    assert "hurt" in w.events
    assert w.respawned
    assert w.player.health == S.MAX_HEALTH - 1


def test_last_heart_gives_game_over_event_not_hurt():
    w = make_world()
    w.player.health = 1
    x = w.player.rect.x + 10
    w.level.enemies.append(WalkingEnemy(x, S.GROUND_Y - 32, x, x))
    w.step(0, False)
    assert w.game_over
    assert "game_over" in w.events
    assert "hurt" not in w.events
    w.step(0, False)
    assert w.events == []