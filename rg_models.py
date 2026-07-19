from __future__ import annotations

from collections.abc import Iterator, MutableMapping
from copy import deepcopy
from dataclasses import dataclass, field, fields
from typing import Any


class MappingModel(MutableMapping[str, Any]):
    """Model domenowy z tymczasowa zgodnoscia ze slownikowym UI."""

    def _field_names(self) -> tuple[str, ...]:
        return tuple(item.name for item in fields(self) if not item.name.startswith("_"))

    def _extra_values(self) -> dict[str, Any]:
        return self.__dict__.setdefault("_extra", {})

    def __getitem__(self, key: str) -> Any:
        if key in self._field_names():
            return getattr(self, key)
        extra = self._extra_values()
        if key in extra:
            return extra[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self._field_names():
            setattr(self, key, value)
        else:
            self._extra_values()[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self._field_names():
            raise KeyError(f"Nie mozna usunac wymaganego pola modelu: {key}")
        del self._extra_values()[key]

    def __iter__(self) -> Iterator[str]:
        yield from self._field_names()
        yield from self._extra_values()

    def __len__(self) -> int:
        return len(self._field_names()) + len(self._extra_values())

    def clone(self):
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return {key: _plain_value(self[key]) for key in self}


def _plain_value(value: Any) -> Any:
    if isinstance(value, MappingModel):
        return value.to_dict()
    if isinstance(value, dict):
        return {key: _plain_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_plain_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_plain_value(item) for item in value)
    return value


@dataclass
class HeroArchetype(MappingModel):
    id: int
    name: str
    color: tuple[int, int, int]
    stats: dict[str, int]
    basic_item: str
    class_item: str
    role: str


@dataclass
class ItemDefinition(MappingModel):
    id: str
    name: str
    category: str
    price: int
    description: str
    effects: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class HelperDefinition(MappingModel):
    id: str
    name: str
    price: int
    description: str
    effect_text: str = ""
    stat_bonus: dict[str, int] = field(default_factory=dict)


@dataclass
class QuestDefinition(MappingModel):
    id: str
    name: str
    deck: str
    description: str
    level: int = 1
    stages: list[dict[str, Any]] = field(default_factory=list)
    reward: dict[str, Any] = field(default_factory=dict)


@dataclass
class QuestInstance(MappingModel):
    id: str
    name: str
    deck: str
    description: str
    level: int = 1
    stages: list[dict[str, Any]] = field(default_factory=list)
    reward: dict[str, Any] = field(default_factory=dict)
    current_stage: int = 0
    failures: int = 0
    status: str = "active"

    @classmethod
    def from_definition(cls, definition: QuestDefinition) -> "QuestInstance":
        return cls(
            id=definition.id,
            name=definition.name,
            deck=definition.deck,
            description=definition.description,
            level=definition.level,
            stages=deepcopy(definition.stages),
            reward=deepcopy(definition.reward),
        )


@dataclass
class LocationState(MappingModel):
    kind: str
    type_name: str
    name: str
    symbol: str
    color: tuple[int, int, int]
    number: int = 0
    background: str = ""
    shop_layout: list[str] = field(default_factory=list)
    shop_offers: list[ItemDefinition] = field(default_factory=list)
    helper_offers: list[HelperDefinition] = field(default_factory=list)
    quest_offers: list[QuestDefinition] = field(default_factory=list)
    offers_ready: bool = False

    @classmethod
    def from_mapping(cls, data: MutableMapping[str, Any]) -> "LocationState":
        return cls(
            kind=str(data.get("kind", "city")),
            type_name=str(data.get("type_name", "Lokacja")),
            name=str(data.get("name", "Lokacja")),
            symbol=str(data.get("symbol", "L")),
            color=tuple(data.get("color", (180, 180, 180))),
            number=int(data.get("number", 0)),
            background=str(data.get("background", "")),
            shop_layout=list(data.get("shop_layout", [])),
            shop_offers=list(data.get("shop_offers", [])),
            helper_offers=list(data.get("helper_offers", [])),
            quest_offers=list(data.get("quest_offers", [])),
            offers_ready=bool(data.get("offers_ready", False)),
        )


@dataclass
class Hero(MappingModel):
    archetype_id: int
    archetype_name: str
    archetype_color: tuple[int, int, int]
    stats: dict[str, int]
    name: str
    player_number: int
    player_color: tuple[int, int, int]
    color: tuple[int, int, int]
    basic_item: str
    class_item: str
    role: str
    gold: int = 5
    wounds: int = 0
    legend: int = 0
    food: list[str] = field(default_factory=list)
    goods: list[str] = field(default_factory=list)
    inventory: list[ItemDefinition] = field(default_factory=list)
    helpers: list[HelperDefinition] = field(default_factory=list)
    active_quests: list[QuestInstance] = field(default_factory=list)
    custom_stats: bool = False
