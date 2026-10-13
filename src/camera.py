from src import settings as S


class Camera:
    """Follows a target smoothly and never scrolls outside the level."""

    def __init__(self, level_width, smoothing=0.12):
        self.level_width = level_width
        self.smoothing = smoothing
        self.x = 0.0

    def max_x(self):
        return max(0, self.level_width - S.SCREEN_WIDTH)

    def snap_to(self, target_rect):
        self.x = self._clamp(target_rect.centerx - S.SCREEN_WIDTH / 2)

    def update(self, target_rect):
        goal = target_rect.centerx - S.SCREEN_WIDTH / 2
        self.x += (goal - self.x) * self.smoothing
        self.x = self._clamp(self.x)

    def _clamp(self, value):
        return min(max(value, 0), self.max_x())

    @property
    def offset(self):
        return int(round(self.x))
