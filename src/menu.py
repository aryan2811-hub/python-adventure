import pygame
from src import settings as S

BTN_W, BTN_H, GAP = 340, 52, 14
COL_BTN = (50, 70, 110)
COL_SEL = (90, 140, 220)
COL_OFF = (60, 60, 70)
COL_TEXT = (255, 255, 255)
COL_TEXT_OFF = (140, 140, 150)
COL_TITLE = (255, 215, 0)
COL_HINT = (190, 225, 255)

INSTRUCTION_LINES = [
    "A / Left Arrow : move left",
    "D / Right Arrow : move right",
    "Space : jump (press twice for a double jump)",
    "Jump on enemies to defeat them",
    "Collect coins and reach the flag",
    "Esc : pause or go back",
    "M : sound on / off",
    "R : restart after game over",
    "Enter : confirm",
]


def _make_veil(alpha):
    veil = pygame.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pygame.SRCALPHA)
    veil.fill((10, 15, 30, alpha))
    return veil


def _draw_centered(screen, font, text, color, y):
    img = font.render(text, True, color)
    screen.blit(img, img.get_rect(center=(S.SCREEN_WIDTH // 2, y)))


class Menu:
    """A vertical list of buttons. handle_event() returns an action name or None."""

    def __init__(self, title, items, disabled=(), back_action=None):
        pygame.font.init()
        self.title = title
        self.items = list(items)  # (label, action) pairs
        self.disabled = set(disabled)  # indexes that cannot be chosen
        self.back_action = back_action  # what Esc does (None = nothing)
        self.title_font = pygame.font.Font(None, 76)
        self.font = pygame.font.Font(None, 38)
        self.veil = _make_veil(150)
        total = len(self.items) * (BTN_H + GAP) - GAP
        top = max(150, (S.SCREEN_HEIGHT - total) // 2 + 40)
        left = (S.SCREEN_WIDTH - BTN_W) // 2
        self.title_y = top - 70
        self.rects = [
            pygame.Rect(left, top + i * (BTN_H + GAP), BTN_W, BTN_H)
            for i in range(len(self.items))
        ]
        self.selected = 0
        for i in range(len(self.items)):
            if i not in self.disabled:
                self.selected = i
                break

    def _move(self, step):
        n = len(self.items)
        i = self.selected
        for _ in range(n):
            i = (i + step) % n
            if i not in self.disabled:
                self.selected = i
                return

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._move(-1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._move(1)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.selected not in self.disabled:
                    return self.items[self.selected][1]
            elif event.key == pygame.K_ESCAPE:
                return self.back_action
        elif event.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self.rects):
                if r.collidepoint(event.pos) and i not in self.disabled:
                    self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self.rects):
                if r.collidepoint(event.pos) and i not in self.disabled:
                    self.selected = i
                    return self.items[i][1]
        return None

    def draw(self, screen, veil=True):
        if veil:
            screen.blit(self.veil, (0, 0))
        _draw_centered(screen, self.title_font, self.title, COL_TITLE, self.title_y)
        for i, (label, _action) in enumerate(self.items):
            off = i in self.disabled
            color = COL_OFF if off else (COL_SEL if i == self.selected else COL_BTN)
            pygame.draw.rect(screen, color, self.rects[i], border_radius=12)
            pygame.draw.rect(screen, (255, 255, 255), self.rects[i], 2, border_radius=12)
            text_color = COL_TEXT_OFF if off else COL_TEXT
            img = self.font.render(label, True, text_color)
            screen.blit(img, img.get_rect(center=self.rects[i].center))


class InfoScreen:
    """A page of text. Enter, Esc or a mouse click returns "back"."""

    def __init__(self, title, lines):
        pygame.font.init()
        self.title = title
        self.lines = list(lines)
        self.title_font = pygame.font.Font(None, 76)
        self.font = pygame.font.Font(None, 34)
        self.small_font = pygame.font.Font(None, 28)
        self.veil = _make_veil(210)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (
            pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE
        ):
            return "back"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return "back"
        return None

    def draw(self, screen, veil=True):
        if veil:
            screen.blit(self.veil, (0, 0))
        _draw_centered(screen, self.title_font, self.title, COL_TITLE, 80)
        for i, line in enumerate(self.lines):
            _draw_centered(screen, self.font, line, COL_TEXT, 150 + i * 36)
        _draw_centered(screen, self.small_font, "Press Enter or Esc to go back",
                       COL_HINT, S.SCREEN_HEIGHT - 40)


class SettingsScreen:
    """Music volume, effects volume, sound on/off, Back.

    handle_event() returns "changed" when a value changed, "back" to leave, else None.
    The Game reads .music, .sfx and .muted afterwards.
    """

    ROWS = 4  # 0 music, 1 effects, 2 sound on/off, 3 back

    def __init__(self, music=0.5, sfx=0.7, muted=False):
        pygame.font.init()
        self.music = round(music, 1)
        self.sfx = round(sfx, 1)
        self.muted = bool(muted)
        self.selected = 0
        self.title_font = pygame.font.Font(None, 76)
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)
        self.veil = _make_veil(190)

    def row_rect(self, i):
        cx = S.SCREEN_WIDTH // 2
        return pygame.Rect(cx - 280, 200 + i * 70, 560, 52)

    def bar_rect(self, i):
        r = self.row_rect(i)
        return pygame.Rect(S.SCREEN_WIDTH // 2 - 20, r.y + 20, 200, 12)

    def _set(self, row, value):
        value = round(min(1.0, max(0.0, value)), 1)
        name = "music" if row == 0 else "sfx"
        if value == getattr(self, name):
            return None
        setattr(self, name, value)
        return "changed"

    def _toggle(self):
        self.muted = not self.muted
        return "changed"

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            k = event.key
            if k in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % self.ROWS
            elif k in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % self.ROWS
            elif k in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
                step = -0.1 if k in (pygame.K_LEFT, pygame.K_a) else 0.1
                if self.selected in (0, 1):
                    current = self.music if self.selected == 0 else self.sfx
                    return self._set(self.selected, current + step)
                if self.selected == 2:
                    return self._toggle()
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.selected == 2:
                    return self._toggle()
                if self.selected == 3:
                    return "back"
            elif k == pygame.K_ESCAPE:
                return "back"
        elif event.type == pygame.MOUSEMOTION:
            for i in range(self.ROWS):
                if self.row_rect(i).collidepoint(event.pos):
                    self.selected = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i in range(self.ROWS):
                if not self.row_rect(i).collidepoint(event.pos):
                    continue
                self.selected = i
                if i in (0, 1):
                    bar = self.bar_rect(i)
                    if bar.inflate(0, 20).collidepoint(event.pos):
                        return self._set(i, (event.pos[0] - bar.x) / bar.w)
                elif i == 2:
                    return self._toggle()
                else:
                    return "back"
        return None

    def draw(self, screen, veil=True):
        if veil:
            screen.blit(self.veil, (0, 0))
        _draw_centered(screen, self.title_font, "Settings", COL_TITLE, 100)
        for i in range(self.ROWS):
            r = self.row_rect(i)
            color = COL_SEL if i == self.selected else COL_BTN
            pygame.draw.rect(screen, color, r, border_radius=12)
            pygame.draw.rect(screen, (255, 255, 255), r, 2, border_radius=12)
            if i == 3:
                img = self.font.render("Back", True, COL_TEXT)
                screen.blit(img, img.get_rect(center=r.center))
                continue
            label = ("Music", "Effects", "Sound")[i]
            img = self.font.render(label, True, COL_TEXT)
            screen.blit(img, (r.x + 20, r.centery - img.get_height() // 2))
            if i == 2:
                state = "Off" if self.muted else "On"
                img = self.font.render(state, True, COL_TEXT)
                screen.blit(img, (self.bar_rect(i).x, r.centery - img.get_height() // 2))
            else:
                value = self.music if i == 0 else self.sfx
                bar = self.bar_rect(i)
                pygame.draw.rect(screen, (30, 40, 70), bar, border_radius=6)
                fill = pygame.Rect(bar.x, bar.y, int(bar.w * value), bar.h)
                pygame.draw.rect(screen, (255, 215, 0), fill, border_radius=6)
                pct = self.small_font.render(f"{int(round(value * 100))}%", True, COL_TEXT)
                screen.blit(pct, (bar.right + 14, r.centery - pct.get_height() // 2))
        _draw_centered(screen, self.small_font, "Arrows or mouse to change, Esc to go back",
                       COL_HINT, S.SCREEN_HEIGHT - 40)


def main_menu():
    return Menu("Python Adventure", [
        ("Play", "play"),
        ("Level Select", "levels"),
        ("Instructions", "instructions"),
        ("Settings", "settings"),
        ("Quit", "quit"),
    ])


def pause_menu():
    return Menu("Paused", [
        ("Resume", "resume"),
        ("Restart", "restart"),
        ("Settings", "settings"),
        ("Main Menu", "main"),
    ], back_action="resume")


def level_select_menu(count, unlocked):
    """Levels above `unlocked` (a 1-based count) are shown greyed out and cannot be chosen."""
    items = []
    disabled = set()
    for i in range(count):
        if i + 1 > unlocked:
            items.append((f"Level {i + 1}  (locked)", f"level:{i}"))
            disabled.add(i)
        else:
            items.append((f"Level {i + 1}", f"level:{i}"))
    items.append(("Back", "back"))
    return Menu("Select Level", items, disabled=disabled, back_action="back")


def instructions_screen():
    return InfoScreen("How to Play", INSTRUCTION_LINES)