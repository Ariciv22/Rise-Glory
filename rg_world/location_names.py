"""Stale nazwy dziewieciu generowanych lokacji swiata."""

import unicodedata


LOCATION_NAMES = {
    "city": {
        1: "Lirion",
        2: "Valdren",
        3: "Eryndor",
    },
    "village": {
        1: "Brzeziny",
        2: "Kamienny Bród",
        3: "Wilcza Dolina",
    },
    "castle": {
        1: "Artium",
        2: "Vargard",
        3: "Durnhal",
    },
}

# Stare techniczne nazwy pozostaja aliasami. Jest to potrzebne m.in. dla
# istniejacych questow i stanow gry zapisanych przed nadaniem nazw wlasnych.
LEGACY_LOCATION_ALIASES = {
    "Miasto 1": "Lirion",
    "Miasto 2": "Valdren",
    "Miasto 3": "Eryndor",
    "Wies 1": "Brzeziny",
    "Wies 2": "Kamienny Bród",
    "Wies 3": "Wilcza Dolina",
    "Wieś 1": "Brzeziny",
    "Wieś 2": "Kamienny Bród",
    "Wieś 3": "Wilcza Dolina",
    "Zamek 1": "Artium",
    "Zamek 2": "Vargard",
    "Zamek 3": "Durnhal",
}


def location_name(kind, number, fallback=None):
    """Zwraca kanoniczna nazwe lokacji dla typu i numeru 1..3."""
    try:
        number = int(number)
    except (TypeError, ValueError):
        return fallback
    return LOCATION_NAMES.get(str(kind), {}).get(number, fallback)


def _simple_normalize(value):
    text = unicodedata.normalize("NFKD", str(value or ""))
    ascii_text = text.encode("ascii", "ignore").decode("ascii").lower()
    return "".join(character for character in ascii_text if character.isalnum())


def install_quest_location_name_compatibility():
    """Utrzymuje zgodnosc questow zapisanych ze starymi nazwami lokacji.

    Questy porownuja wymagane miejsce po znormalizowanej nazwie. Po zmianie
    np. ``Wies 1`` na ``Brzeziny`` stare definicje przestalyby pasowac. Ten
    adapter traktuje stare i nowe nazwy jako ten sam punkt oraz aktualizuje
    zarejestrowany quest o studni, aby gracz widzial juz nowa nazwe.
    """
    try:
        from rg_engine import quests as quest_engine
    except ImportError:
        return

    if getattr(quest_engine, "_rise_glory_location_names_installed", False):
        return

    original_normalize = quest_engine._normalize
    aliases = {}
    for legacy, canonical in LEGACY_LOCATION_ALIASES.items():
        canonical_key = _simple_normalize(canonical)
        aliases[_simple_normalize(legacy)] = canonical_key
        aliases[canonical_key] = canonical_key

    def normalize_with_location_aliases(value):
        normalized = original_normalize(value)
        return aliases.get(normalized, normalized)

    quest_engine._normalize = normalize_with_location_aliases

    # Quest nr 13 wskazywal dotad techniczna nazwe "Wies 1". Rejestr questow
    # jest juz gotowy w chwili instalacji, wiec aktualizujemy jego wersje runtime.
    definition = getattr(quest_engine, "_QUESTS", {}).get("spor_o_studnie")
    if isinstance(definition, dict):
        definition["required_location"] = "Brzeziny"
        definition["objective"] = "Udaj się do Brzezin i rozwiąż spór o studnię."
        for stage in definition.get("stages", []) or []:
            if isinstance(stage, dict):
                required = stage.get("required_location")
                if _simple_normalize(required) in {"wies1", "wies1"}:
                    stage["required_location"] = "Brzeziny"

    quest_engine._rise_glory_location_names_installed = True
