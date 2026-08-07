from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

_REGISTERED_PLAYERS: list[dict] = []
_FORCED_WORLD_LEVEL: int | None = None


def register_players(players: Iterable[dict] | None) -> None:
    global _REGISTERED_PLAYERS
    _REGISTERED_PLAYERS = list(players or [])


def registered_players() -> list[dict]:
    """Zwraca graczy bieżącej rozgrywki z zachowaniem referencji do ich stanu."""
    return list(_REGISTERED_PLAYERS)


def set_forced_world_level(level: int | None) -> int | None:
    """Opcjonalny override poziomu świata używany przez narzędzia programisty."""
    global _FORCED_WORLD_LEVEL
    if level is None:
        _FORCED_WORLD_LEVEL = None
        return None
    _FORCED_WORLD_LEVEL = max(1, min(4, int(level)))
    return _FORCED_WORLD_LEVEL


def clear_forced_world_level() -> None:
    set_forced_world_level(None)


def forced_world_level() -> int | None:
    return _FORCED_WORLD_LEVEL


def world_level_from_legend(legend: int) -> int:
    value = max(0, int(legend or 0))
    if value >= 30:
        return 4
    if value >= 20:
        return 3
    if value >= 10:
        return 2
    return 1


def current_world_level(players: Iterable[dict] | None = None) -> int:
    if _FORCED_WORLD_LEVEL is not None:
        return _FORCED_WORLD_LEVEL
    source = list(_REGISTERED_PLAYERS if players is None else players)
    leader_legend = max((int(player.get("legend", 0) or 0) for player in source), default=0)
    return world_level_from_legend(leader_legend)


def scaled_enemy_hp(base_hp: int, world_level: int | None = None, legendary: bool = False) -> int:
    base = max(1, int(base_hp or 1))
    if legendary:
        return base + 10
    level = max(1, min(4, int(world_level or current_world_level())))
    return base + level * 2


def defeat_gold_loss(world_level: int | None = None) -> int:
    return max(1, min(4, int(world_level or current_world_level())))


@dataclass
class WorldState:
    level: int = 1
    leader_legend: int = 0

    @classmethod
    def from_players(cls, players: Iterable[dict]) -> "WorldState":
        source = list(players)
        leader = max((int(player.get("legend", 0) or 0) for player in source), default=0)
        return cls(level=current_world_level(source), leader_legend=leader)
