import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")  # no real window needed for tests

import pygame

from src.game import Game
from src.particles import ParticleSystem


def test_burst_adds_the_requested_number_of_particles():
    ps = ParticleSystem()
    ps.burst(100, 100, (255, 0, 0), count=10)
    assert len(ps.items) == 10


def test_particles_expire_after_their_life():
    ps = ParticleSystem()
    ps.burst(100, 100, (255, 0, 0), count=10, life=10)
    for _ in range(10):
        ps.update()
    assert ps.items == []


def test_clear_removes_everything():
    ps = ParticleSystem()
    ps.burst(0, 0, (255, 255, 255), count=5)
    ps.clear()
    assert ps.items == []


def test_draw_works_with_a_number_camera_offset():
    ps = ParticleSystem()
    ps.burst(50, 50, (255, 0, 0), count=5)
    ps.draw(pygame.Surface((200, 200)), 20)


def test_draw_works_with_a_tuple_camera_offset():
    ps = ParticleSystem()
    ps.burst(50, 50, (255, 0, 0), count=5)
    ps.draw(pygame.Surface((200, 200)), (20, 0))


def test_game_coin_event_creates_particles():
    g = Game()
    assert g.particles.items == []
    g.spawn_effects(["coin"])
    assert len(g.particles.items) > 0


def test_game_unknown_event_creates_no_particles():
    g = Game()
    g.spawn_effects(["not_a_real_event"])
    assert g.particles.items == []