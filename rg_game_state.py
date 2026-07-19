from dataclasses import dataclass, field
from typing import Any

from rg_data import STATE_MENU


@dataclass
class GameSession:
    state: str = STATE_MENU
    current_map: str = "rosette9"
    player_count: int = 1
    config_player_index: int = 0
    player_name: str = ""
    name_input_active: bool = False
    selected_archetype: Any = None
    custom_stats: dict[str, int] = field(default_factory=dict)
    players: list[Any] = field(default_factory=list)
    tiles: list[Any] = field(default_factory=list)
    tokens: list[Any] = field(default_factory=list)
    initiative: dict | None = None
    turn_manager: Any = None
    active_player_index: int = 0
    selected_tile: Any = None
    selected_token: Any = None
    current_city: Any = None
    selected_city_place: str | None = None
    location_message: str = ""
    intro_index: int = 0
    start_intro_index: int = 0
    start_intro_started_at: int = 0

    def reset_player_configuration(self, stats):
        self.player_name = ""
        self.name_input_active = True
        self.selected_archetype = None
        self.custom_stats = dict(stats)

    def clear_location_context(self):
        self.current_city = None
        self.selected_city_place = None
        self.location_message = ""
