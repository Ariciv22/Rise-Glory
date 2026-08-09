from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

_REGISTERED_PLAYERS: list[dict] = []
_FORCED_WORLD_LEVEL: int | None = None
_WORLD_LEVEL = 1
_WORLD_LEVEL_CHANGES: list[tuple[int, int]] = []


def register_players(players: Iterable[dict] | None) -> None:
    global _REGISTERED_PLAYERS
    _REGISTERED_PLAYERS = list(players or [])


def registered_players() -> list[dict]:
    """Zwraca graczy bieżącej rozgrywki z zachowaniem referencji do ich stanu."""
    return list(_REGISTERED_PLAYERS)


def reset_world_progression(level: int = 1) -> int:
    """Rozpoczyna nową partię od wskazanego Poziomu Świata."""
    global _WORLD_LEVEL, _WORLD_LEVEL_CHANGES
    _WORLD_LEVEL = max(1, min(4, int(level or 1)))
    _WORLD_LEVEL_CHANGES = []
    return _WORLD_LEVEL


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
    """Ranga bohatera wynikająca wyłącznie z jego Punktów Legendy."""
    value = max(0, int(legend or 0))
    if value >= 30:
        return 4
    if value >= 20:
        return 3
    if value >= 10:
        return 2
    return 1


def player_legend_level(player: dict) -> int:
    return world_level_from_legend(int(player.get("legend", 0) or 0))


def leader_legend(players: Iterable[dict] | None = None) -> int:
    source = list(_REGISTERED_PLAYERS if players is None else players)
    return max((int(player.get("legend", 0) or 0) for player in source), default=0)


def required_ready_players(player_count: int) -> int:
    """Do awansu gotowa musi być co najmniej połowa wszystkich graczy, w górę."""
    count = max(0, int(player_count or 0))
    return int(math.ceil(count / 2)) if count else 0


def ready_player_count(players: Iterable[dict] | None = None, level: int | None = None) -> int:
    source = list(_REGISTERED_PLAYERS if players is None else players)
    target = max(1, min(4, int(_WORLD_LEVEL if level is None else level)))
    return sum(1 for player in source if player_legend_level(player) >= target)


def can_advance_world_level(players: Iterable[dict] | None = None, level: int | None = None) -> bool:
    """Sprawdza warunki przejścia z bieżącego poziomu na dokładnie kolejny."""
    source = list(_REGISTERED_PLAYERS if players is None else players)
    current = max(1, min(4, int(_WORLD_LEVEL if level is None else level)))
    if current >= 4 or not source:
        return False

    next_level = current + 1
    leader_level = world_level_from_legend(leader_legend(source))
    if leader_level < next_level:
        return False

    required = required_ready_players(len(source))
    return ready_player_count(source, current) >= required


def update_world_level(players: Iterable[dict] | None = None) -> int:
    """Natychmiast awansuje świat, gdy kolejne progi są spełnione.

    Każdy krok jest rozpatrywany osobno, więc świat nigdy nie pomija poziomu.
    Przejście 2 -> 3 wymaga już gotowości połowy graczy na poziomie 2 itd.
    """
    global _WORLD_LEVEL
    if _FORCED_WORLD_LEVEL is not None:
        return _FORCED_WORLD_LEVEL

    source = list(_REGISTERED_PLAYERS if players is None else players)
    while can_advance_world_level(source, _WORLD_LEVEL):
        previous = _WORLD_LEVEL
        _WORLD_LEVEL += 1
        _WORLD_LEVEL_CHANGES.append((previous, _WORLD_LEVEL))
    return _WORLD_LEVEL


def consume_world_level_changes() -> list[tuple[int, int]]:
    """Zwraca nierozpatrzone awanse dla UI i czyści kolejkę komunikatów."""
    global _WORLD_LEVEL_CHANGES
    changes = list(_WORLD_LEVEL_CHANGES)
    _WORLD_LEVEL_CHANGES = []
    return changes


def current_world_level(players: Iterable[dict] | None = None) -> int:
    if _FORCED_WORLD_LEVEL is not None:
        return _FORCED_WORLD_LEVEL
    return update_world_level(players)


def quest_difficulty_from_legend_gap(player: dict, world_level: int | None = None) -> int:
    """+2 do testu questa za każdy poziom, o który bohater wyprzedza świat."""
    level = current_world_level() if world_level is None else max(1, min(4, int(world_level)))
    gap = max(0, player_legend_level(player) - level)
    return gap * 2


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
    ready_players: int = 0
    required_players: int = 0

    @classmethod
    def from_players(cls, players: Iterable[dict]) -> "WorldState":
        source = list(players)
        level = current_world_level(source)
        return cls(
            level=level,
            leader_legend=leader_legend(source),
            ready_players=ready_player_count(source, level),
            required_players=required_ready_players(len(source)),
        )
