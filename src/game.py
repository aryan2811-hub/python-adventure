import asyncio
import os
import pygame
from src import settings as S
from src.audio import Audio
from src.camera import Camera
from src.background import Background
from src.level_manager import LevelManager
from src.menu import (
    SettingsScreen, instructions_screen, level_select_menu, main_menu, pause_menu,
)
from src.particles import ParticleSystem
from src.save_system import SaveSystem
from src.ui import HUD
from src.world import World

# World event name -> sound name. Event names not listed here are used as the sound name.
SOUND_FOR_EVENT = {"goal": "victory"}

# World event -> particle burst: (color, count, speed, life in frames, where on the player)
EFFECTS = {
    "jump": ((235, 235, 235), 5, 1.5, 18, "feet"),
    "coin": ((255, 215, 0), 12, 3.5, 30, "center"),
    "stomp": ((255, 255, 255), 14, 3.0, 28, "feet"),
    "hurt": ((255, 80, 80), 14, 3.5, 30, "center"),
    "checkpoint": ((120, 255, 160), 16, 3.0, 40, "center"),
}
CONFETTI = [(255, 215, 0), (255, 80, 80), (90, 170, 255), (120, 255, 160)]

# States where a menu screen (self.ui) is shown on top of the frozen game.
MENU_STATES = ("menu", "levels", "instructions", "settings", "paused")


class Game:
    def __init__(self):
        pygame.init()
        # SCALED lets fullscreen stretch the game to the monitor without distortion.
        flags = 0 if os.environ.get("SDL_VIDEODRIVER") == "dummy" else pygame.SCALED
        self.screen = pygame.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), flags)
        pygame.display.set_caption(S.TITLE)
        self.fullscreen = False
        self.clock = pygame.time.Clock()
        self.background = Background()
        self.hud = HUD()
        self.small_font = pygame.font.Font(None, 26)
        self.manager = LevelManager()
        self.save = SaveSystem(level_count=self.manager.count)
        self.audio = Audio()
        self.audio.apply_settings(self.save.data)
        self.audio.start_music()
        self.particles = ParticleSystem()
        self.was_on_ground = True
        self.running = True
        # playing | level_complete | victory | paused | menu | levels | instructions | settings
        # (game over lives inside World)
        self.state = "playing"
        self.resume_state = "playing"  # where Resume goes back to
        self.settings_from = "menu"  # which menu Settings was opened from
        self.ui = None  # the menu screen currently shown, if any
        self.fade = 0
        self.start_level(0, 0)
        self.open_main_menu()

    # ----- menus -----

    def open_main_menu(self):
        self.state = "menu"
        self.ui = main_menu()

    def open_pause(self):
        self.resume_state = self.state
        self.state = "paused"
        self.ui = pause_menu()

    def show_hud(self):
        """The HUD is for the game itself, so it is hidden on the start-up menus."""
        if self.state in ("menu", "levels", "instructions"):
            return False
        if self.state == "settings" and self.settings_from != "paused":
            return False
        return True

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        try:
            pygame.display.toggle_fullscreen()
        except pygame.error:
            pass  # some systems cannot switch; the game keeps running in a window

    def handle_action(self, action):
        """Does what a menu asked for. Menus return short action names."""
        if action is None:
            return
        if action == "play":
            self.start_level(0, 0)
        elif action == "levels":
            self.state = "levels"
            self.ui = level_select_menu(self.manager.count, self.save.unlocked_levels)
        elif action == "instructions":
            self.state = "instructions"
            self.ui = instructions_screen()
        elif action == "settings":
            self.settings_from = self.state
            s = self.audio.settings()
            self.state = "settings"
            self.ui = SettingsScreen(s["music_volume"], s["sfx_volume"], s["muted"])
        elif action == "changed":
            self.apply_audio(self.ui.music, self.ui.sfx, self.ui.muted)
        elif action == "resume":
            self.ui = None
            self.state = self.resume_state
        elif action == "restart":
            self.start_level(self.level_index, self.world.start_score)
        elif action == "main":
            self.open_main_menu()
        elif action == "back":
            if self.state == "settings" and self.settings_from == "paused":
                self.state = "paused"
                self.ui = pause_menu()
            else:
                self.open_main_menu()
        elif action == "quit":
            self.running = False
        elif action.startswith("level:"):
            self.start_level(int(action.split(":")[1]), 0)

    def apply_audio(self, music, sfx, muted):
        self.audio.apply_settings({"muted": muted, "music_volume": music, "sfx_volume": sfx})
        self.save.set_audio(muted, music, sfx)

    # ----- levels -----

    def start_level(self, index, score):
        self.level_index = index
        self.world = World(self.manager.load(index), score)
        self.camera = Camera(self.world.level.width)
        self.camera.snap_to(self.world.player.rect)
        self.particles.clear()
        self.was_on_ground = True
        self.state = "playing"
        self.ui = None
        self.fade = S.FADE_FRAMES

    def restart_game(self):
        self.start_level(0, 0)

    def toggle_mute(self):
        self.audio.toggle_mute()
        s = self.audio.settings()
        self.save.set_audio(s["muted"], s["music_volume"], s["sfx_volume"])

    def play_events(self, events):
        """Turns what happened in the World this frame into sounds and saved progress."""
        for ev in dict.fromkeys(events):  # same event twice in one frame -> play once
            self.audio.play(SOUND_FOR_EVENT.get(ev, ev))
            if ev == "goal":
                self.save.unlock_level(self.level_index + 2)  # level numbers start at 1
                self.save.update_high_score(self.world.score)
            elif ev == "game_over":
                self.save.update_high_score(self.world.score)

    def spawn_effects(self, events):
        """Small particle bursts for what happened in the World this frame."""
        r = self.world.player.rect
        for ev in dict.fromkeys(events):
            if ev == "goal":
                for color in CONFETTI:
                    self.particles.burst(r.centerx, r.top, color, count=10, speed=5.0, life=60)
            elif ev in EFFECTS:
                color, count, speed, life, where = EFFECTS[ev]
                y = r.bottom if where == "feet" else r.centery
                self.particles.burst(r.centerx, y, color, count=count, speed=speed, life=life)

    # ----- input -----

    def handle_events(self):
        """Returns True if a jump key was pressed this frame."""
        jump = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self.toggle_fullscreen()
                continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m and self.state != "settings":
                self.toggle_mute()
                continue
            if self.ui is not None:  # a menu is open: it gets all the input
                self.handle_action(self.ui.handle_event(event))
                continue
            if event.type != pygame.KEYDOWN:
                continue
            k = event.key
            if k == pygame.K_ESCAPE:
                self.open_pause()
            elif k == pygame.K_SPACE:
                jump = True
            elif k == pygame.K_r:
                if self.world.game_over:
                    self.world.reset()
                    self.camera.snap_to(self.world.player.rect)
                    self.fade = S.FADE_FRAMES
                elif self.state == "victory":
                    self.restart_game()
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.state == "level_complete":
                    self.start_level(self.level_index + 1, self.world.score)
                elif self.state == "victory":
                    self.restart_game()
        return jump

    # ----- update and draw -----

    def step(self, jump):
        if self.fade > 0:
            self.fade -= 1
        if self.state == "playing":
            keys = pygame.key.get_pressed()
            move = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
            self.world.step(move, jump)
            self.play_events(self.world.events)
            self.spawn_effects(self.world.events)
            on_ground = self.world.player.on_ground
            if on_ground and not self.was_on_ground:  # just landed: a little dust
                r = self.world.player.rect
                self.particles.burst(r.centerx, r.bottom, (220, 220, 220), count=4,
                                     speed=1.2, gravity=0.05, life=14, size=3)
            self.was_on_ground = on_ground
            if self.world.respawned:
                self.camera.snap_to(self.world.player.rect)
            if self.world.level_complete:
                last = self.level_index >= self.manager.count - 1
                self.state = "victory" if last else "level_complete"
        if self.state not in MENU_STATES:
            self.particles.update()
        self.camera.update(self.world.player.rect)

    def draw(self):
        cam = self.camera.offset
        lv = self.world.level
        self.background.draw(self.screen, cam)
        for cp in lv.checkpoints:
            cp.draw(self.screen, cam)
        if lv.goal:
            lv.goal.draw(self.screen, cam)
        for p in lv.platforms:
            p.draw(self.screen, cam)
        for c in lv.coins:
            c.draw(self.screen, cam)
        for e in lv.enemies:
            if e.alive:
                e.draw(self.screen, cam)
        self.world.player.draw(self.screen, cam)
        self.particles.draw(self.screen, cam)
        if self.show_hud():
            title = f"Level {self.level_index + 1}: {lv.name}"
            self.hud.draw(self.screen, self.world, title)
            self.hud._text(self.screen, f"Best: {self.save.high_score}", (S.SCREEN_WIDTH - 200, 76), color=(190, 225, 255))
            if not self.audio.enabled:
                hint = "No sound device"
            else:
                hint = "M: sound off" if self.audio.muted else "M: sound on"
            self.hud._text(self.screen, hint, (16, S.SCREEN_HEIGHT - 28), self.small_font)
        if self.state == "level_complete":
            self.hud.draw_level_complete(self.screen, self.world, lv.name, False)
        elif self.state == "victory":
            self.hud.draw_victory(self.screen, self.world)
        if self.ui is not None:
            self.ui.draw(self.screen)
        if self.fade > 0:
            veil = pygame.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT))
            veil.set_alpha(int(255 * self.fade / S.FADE_FRAMES))
            self.screen.blit(veil, (0, 0))
        pygame.display.flip()

    async def run(self):
        # async + sleep(0) is what lets pygbag run this in a browser later.
        while self.running:
            jump = self.handle_events()
            self.step(jump)
            self.draw()
            self.clock.tick(S.FPS)
            await asyncio.sleep(0)
        pygame.quit()