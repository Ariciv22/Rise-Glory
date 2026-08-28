"""Aktywne efekty specjalnych nagrod questowych.

Modul nie zalezy od pygame ani od UI. Interfejs moze wywolac te funkcje
bezposrednio na obiektach pionka i heksow mapy.
"""

from __future__ import annotations

from typing import Any, Iterable

from rg_content.quest_runtime_ext import (
    mark_miniature_house_used,
    miniature_house_available,
    use_bran_bonus,
)


def _axial_distance(a: Any, b: Any) -> int:
    """Odleglosc heksowa dla wspolrzednych axial q/r."""
    dq = int(getattr(b, "q", 0)) - int(getattr(a, "q", 0))
    dr = int(getattr(b, "r", 0)) - int(getattr(a, "r", 0))
    return (abs(dq) + abs(dr) + abs(dq + dr)) // 2


def nearest_place_tiles(token: Any, tiles: Iterable[Any]) -> list[Any]:
    """Zwraca wszystkie najblizsze Miejsca; remis pozostawia wybor graczowi."""
    current = getattr(token, "tile", None)
    if current is None:
        return []

    candidates = [
        tile
        for tile in tiles or []
        if tile is not current and isinstance(getattr(tile, "location", None), dict)
    ]
    if not candidates:
        return []

    distances = [(_axial_distance(current, tile), tile) for tile in candidates]
    best = min(distance for distance, _tile in distances)
    return [tile for distance, tile in distances if distance == best]


def miniature_house_targets(player: dict[str, Any], token: Any, tiles: Iterable[Any], round_number: int) -> list[dict[str, Any]]:
    """Dane celow do UI Miniaturowego Wedrownego Domu."""
    if not miniature_house_available(player, round_number):
        return []
    result = []
    for tile in nearest_place_tiles(token, tiles):
        location = getattr(tile, "location", {}) or {}
        result.append(
            {
                "tile_id": int(getattr(tile, "id", -1)),
                "name": str(location.get("name") or "Miejsce"),
                "kind": str(location.get("kind") or "place"),
                "q": int(getattr(tile, "q", 0)),
                "r": int(getattr(tile, "r", 0)),
            }
        )
    return result


def teleport_with_miniature_house(
    player: dict[str, Any],
    token: Any,
    tiles: Iterable[Any],
    round_number: int,
    *,
    target_tile_id: int | None = None,
) -> tuple[bool, str]:
    """Teleportuje pionek raz na runde do najblizszego Miejsca.

    Gdy kilka Miejsc jest w tej samej minimalnej odleglosci, funkcja nie
    wybiera za gracza. UI powinno najpierw pokazac `miniature_house_targets`
    i ponownie wywolac funkcje z `target_tile_id`.
    """
    if not miniature_house_available(player, round_number):
        return False, "Miniaturowy Wedrowny Dom zostal juz uzyty w tej rundzie albo gracz go nie posiada."

    nearest = nearest_place_tiles(token, tiles)
    if not nearest:
        return False, "Na mapie nie ma dostepnego Miejsca, do ktorego mozna sie przeniesc."

    target = None
    if target_tile_id is not None:
        target = next((tile for tile in nearest if int(getattr(tile, "id", -1)) == int(target_tile_id)), None)
        if target is None:
            return False, "Wybrane Miejsce nie jest jednym z najblizszych celow."
    elif len(nearest) == 1:
        target = nearest[0]
    else:
        names = [str((getattr(tile, "location", {}) or {}).get("name") or "Miejsce") for tile in nearest]
        return False, "Kilka Miejsc jest tak samo blisko. Wybierz cel: " + ", ".join(names) + "."

    token.tile = target
    player["_token_ref"] = token
    mark_miniature_house_used(player, round_number)
    location = getattr(target, "location", {}) or {}
    return True, f"Miniaturowy Wedrowny Dom przenosi bohatera do: {location.get('name', 'Miejsce')}."


def bran_roll_bonus(player: dict[str, Any], round_number: int) -> tuple[bool, int, str]:
    """Zuzywa jedno z dwoch uzyc Brana w rundzie i zwraca bonus do rzutu."""
    bonus = use_bran_bonus(player, round_number)
    if bonus <= 0:
        return False, 0, "Bran nie moze juz pomoc w tej rundzie albo nie jest Pomocnikiem gracza."
    return True, bonus, "Bran: +1 do wybranego rzutu."
