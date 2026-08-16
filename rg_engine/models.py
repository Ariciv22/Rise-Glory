from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ItemDefinition:
    item_id: str
    name: str
    category: str
    slot: str | None = None
    quality: str = "zwykla"
    price: int = 0
    description: str = ""
    hit_bonus: int = 0
    damage_bonus: int = 0
    armor_class: int = 0
    stat_bonus: dict[str, int] = field(default_factory=dict)
    effects: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EnemyDefinition:
    enemy_id: str
    name: str
    base_hp: int
    armor_class: int
    attack_bonus: int = 0
    wounds: int = 1
    image: str = ""
    can_escape: bool = True
    scale_with_world: bool = True
    legendary: bool = False
    escape: dict[str, Any] = field(default_factory=dict)
    rewards: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class QuestOption:
    option_id: str
    label: str
    option_type: str = "test"
    stat: str | None = None
    threshold: int | None = None
    materials: dict[str, int] = field(default_factory=dict)
    gold_cost: int = 0
    item_cost: str | None = None
    enemy_id: str | None = None
    on_success: str = "next"
    on_failure: str = "retry"
    failure_enemy_id: str | None = None
    action_cost: int = 1
    text: str = ""
    requires: dict[str, Any] = field(default_factory=dict)
    consumes: dict[str, Any] = field(default_factory=dict)
    visible_if: dict[str, Any] = field(default_factory=dict)
    disabled_if: dict[str, Any] = field(default_factory=dict)
    disabled_reason: str = ""
    success_effects: tuple[dict[str, Any], ...] = ()
    failure_effects: tuple[dict[str, Any], ...] = ()
    success_paragraph: str | None = None
    failure_paragraph: str | None = None
    nat20_paragraph: str | None = None
    nat1_paragraph: str | None = None
    combat_defeat: str = "quest_failure"
    combat_victory: str = "success"

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["type"] = result.pop("option_type")
        return result


@dataclass(frozen=True)
class QuestStage:
    number: int
    title: str
    text: str
    options: tuple[QuestOption, ...]
    required_location: str | None = None
    image: str | None = None
    required_hex: str | None = None
    point_of_no_return: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "number": self.number,
            "title": self.title,
            "text": self.text,
            "options": [option.to_dict() for option in self.options],
            "required_location": self.required_location,
            "required_hex": self.required_hex,
            "image": self.image,
            "point_of_no_return": self.point_of_no_return,
        }


@dataclass(frozen=True)
class QuestExpansionDefinition:
    expansion_id: str
    quest_id: str
    title: str
    text: str
    paragraph: str | None = None
    image: str = ""
    ending_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class QuestDefinition:
    quest_id: str
    name: str
    deck: str
    description: str
    objective: str
    required_location: str
    stages: tuple[QuestStage, ...]
    reward: dict[str, Any]
    world_level_min: int = 1
    image: str = ""
    board_text: str = ""
    unique: bool = False
    shared: bool = False
    sellable: bool = True
    tradeable: bool = True
    abandonable: bool = True
    quest_number: int = 0
    world_level: int | None = None
    length: str = "Krótki"
    reward_hint: str = ""
    time_limit: dict[str, Any] = field(default_factory=dict)
    markers: tuple[dict[str, Any], ...] = ()
    flags_on_complete: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.quest_id,
            "name": self.name,
            "deck": self.deck or "Questy",
            "description": self.description,
            "objective": self.objective,
            "required_location": self.required_location,
            "world_level_min": self.world_level_min,
            "world_level": self.world_level if self.world_level is not None else self.world_level_min,
            "quest_number": self.quest_number,
            "length": self.length,
            "reward_hint": self.reward_hint,
            "time_limit": dict(self.time_limit),
            "markers": [dict(marker) for marker in self.markers],
            "flags_on_complete": dict(self.flags_on_complete),
            "stages": [stage.to_dict() for stage in self.stages],
            "reward": dict(self.reward),
            "image": self.image,
            "board_text": self.board_text or self.description,
            "unique": self.unique,
            "shared": self.shared,
            "sellable": self.sellable,
            "tradeable": self.tradeable,
            "abandonable": self.abandonable,
        }


@dataclass
class RuntimeGameState:
    current_map: str = "rosette9"
    players: list[dict[str, Any]] = field(default_factory=list)
    active_player_index: int = 0
    round_number: int = 1
    council_cycle: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
