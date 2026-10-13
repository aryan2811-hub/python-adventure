import pygame
from src import settings as S


def draw_heart(surface, x, y, size, filled=True):
    r = size // 4
    color = (230, 50, 70) if filled else (70, 70, 80)
    pygame.draw.circle(surface, color, (x + r, y + r), r)
    pygame.draw.circle(surface, color, (x + 3 * r, y + r), r)
    pygame.draw.polygon(surface, color, [(x, y + r + 1), (x + 4 * r, y + r + 1), (x + 2 * r, y + 4 * r)])
    if filled:
        pygame.draw.circle(surface, (255, 150, 160), (x + r - 2, y + r - 2), max(2, r // 3))


class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 40)
        self.big = pygame.font.Font(None, 96)

    def _text(self, surface, text, pos, font=None, color=(255, 255, 255), center=False):
        font = font or self.font
        shadow = font.render(text, True, (30, 30, 40))
        img = font.render(text, True, color)
        rect = img.get_rect(center=pos) if center else img.get_rect(topleft=pos)
        surface.blit(shadow, rect.move(2, 2))
        surface.blit(img, rect)

    def _veil(self, surface, alpha=150):
        veil = pygame.Surface((S.SCREEN_WIDTH, S.SCREEN_HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 0, alpha))
        surface.blit(veil, (0, 0))

    def draw(self, surface, world, title=""):
        for i in range(S.MAX_HEALTH):
            draw_heart(surface, 16 + i * 38, 14, 32, filled=i < world.player.health)
        self._text(surface, f"Score: {world.score}", (S.SCREEN_WIDTH - 200, 16))
        self._text(surface, f"Coins: {world.coins_collected}", (S.SCREEN_WIDTH - 200, 46), color=(255, 225, 90))
        if title:
            self._text(surface, title, (S.SCREEN_WIDTH // 2, 28), center=True)
        cx = S.SCREEN_WIDTH // 2
        if world.game_over:
            self._veil(surface)
            self._text(surface, "GAME OVER", (cx, 220), self.big, (255, 90, 90), center=True)
            self._text(surface, f"Score: {world.score}", (cx, 290), center=True)
            self._text(surface, "Press R to try this level again", (cx, 340), center=True)

    def draw_level_complete(self, surface, world, name, is_last):
        self._veil(surface)
        cx = S.SCREEN_WIDTH // 2
        self._text(surface, "LEVEL COMPLETE!", (cx, 160), self.big, (255, 215, 60), center=True)
        self._text(surface, name, (cx, 225), center=True)
        self._text(surface, f"Coins collected: {world.coins_collected}", (cx, 280), center=True)
        self._text(surface, f"Level bonus: +{world.bonus}", (cx, 320), center=True)
        self._text(surface, f"Total score: {world.score}", (cx, 370), color=(255, 225, 90), center=True)
        self._text(surface, "Press ENTER to continue", (cx, 440), center=True)

    def draw_victory(self, surface, world):
        self._veil(surface, 170)
        cx = S.SCREEN_WIDTH // 2
        self._text(surface, "YOU WIN!", (cx, 150), self.big, (255, 215, 60), center=True)
        self._text(surface, "You defeated the boss and finished every level.", (cx, 225), center=True)
        self._text(surface, f"Final score: {world.score}", (cx, 285), color=(255, 225, 90), center=True)
        self._text(surface, "Press ENTER or R to play again", (cx, 380), center=True)
