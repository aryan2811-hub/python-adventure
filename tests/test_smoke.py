import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from src.game import Game


def test_game_runs_frames_and_player_lands():
    g = Game()
    g.handle_action("play")
    for _ in range(120):
        g.handle_events()
        g.step(False)
        g.draw()
    assert g.world.player.on_ground
    pygame.quit()
