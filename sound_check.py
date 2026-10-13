"""Quick listening test. Run from the project folder:  python audio_test.py"""
import pygame
from src.audio import Audio

pygame.init()
audio = Audio()
if not audio.enabled:
    print("Audio is OFF (no sound device found). The game will still run silently.")
    raise SystemExit(1)

for name in ("jump", "coin", "hurt", "stomp", "checkpoint", "click", "victory", "game_over"):
    print("Playing:", name)
    audio.play(name)
    pygame.time.wait(1000)

print("Music for 8 seconds (one full loop)...")
audio.start_music()
pygame.time.wait(8000)
print("Muted for 2 seconds (music should go silent)...")
audio.toggle_mute()
pygame.time.wait(2000)
print("Unmuted (music should come back)...")
audio.toggle_mute()
pygame.time.wait(2500)
audio.stop_music()
print("Done.")