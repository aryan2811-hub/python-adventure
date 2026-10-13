from dataclasses import dataclass, field
from src import settings as S


@dataclass
class Level:
    platforms: list = field(default_factory=list)
    enemies: list = field(default_factory=list)
    coins: list = field(default_factory=list)
    checkpoints: list = field(default_factory=list)
    spawn: tuple = S.PLAYER_SPAWN
    width: int = S.LEVEL_WIDTH
    name: str = ""
    goal: object = None

    @property
    def has_boss(self):
        return any(e.is_boss for e in self.enemies)
