"""Stale nazwy dziewieciu generowanych lokacji swiata."""

import unicodedata


LOCATION_NAMES = {
    "city": {
        1: "Lirion",
        2: "Valdren",
        3: "Eryndor",
    },
    "village": {
        1: "Elarin",
        2: "Norven",
        3: "Thalwen",
    },
    "castle": {
        1: "Artium",
        2: "Vargard",
        3: "Durnhal",
    },
}

# Stare techniczne nazwy oraz poprzednie robocze nazwy pozostaja aliasami.
# Jest to potrzebne m.in. dla questow i stanow gry zapisanych przed zmiana nazw.
LEGACY_LOCATION_ALIASES = {
    "Miasto 1": "Lirion",
    "Miasto 2": "Valdren",
    "Miasto 3": "Eryndor",
    "Wies 1": "Elarin",
    "Wies 2": "Norven",
    "Wies 3": "Thalwen",
    "Wieś 1": "Elarin",
    "Wieś 2": "Norven",
    "Wieś 3": "Thalwen",
    "Brzeziny": "Elarin",
    "Kamienny Bród": "Norven",
    "Wilcza Dolina": "Thalwen",
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
    nazw wlasnych stare definicje i save'y nadal musza wskazywac ten sam punkt.
    Adapter traktuje stare i nowe nazwy jako te same lokacje oraz aktualizuje
    runtime questa o studni, aby gracz widzial juz nazwe Elarin.
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

    # Kanoniczne nazwy tez rejestrujemy jawnie, aby porownania byly stabilne.
    for names in LOCATION_NAMES.values():
        for canonical in names.values():
            canonical_key = _simple_normalize(canonical)
            aliases[canonical_key] = canonical_key

    def normalize_with_location_aliases(value):
        normalized = original_normalize(value)
        return aliases.get(normalized, normalized)

    quest_engine._normalize = normalize_with_location_aliases

    # Quest nr 13 wskazywal pierwotnie techniczna nazwe "Wies 1", a przez
    # krotki czas robocza nazwe "Brzeziny". Obie wersje pozostaja zgodne,
    # natomiast w UI pokazujemy juz finalna nazwe Elarin.
    definition = getattr(quest_engine, "_QUESTS", {}).get("spor_o_studnie")
    if isinstance(definition, dict):
        definition["required_location"] = "Elarin"
        definition["objective"] = "Udaj się do wsi Elarin i rozwiąż spór o studnię."
        old_village_one_names = {
            _simple_normalize("Wies 1"),
            _simple_normalize("Wieś 1"),
            _simple_normalize("Brzeziny"),
            _simple_normalize("Elarin"),
        }
        for stage in definition.get("stages", []) or []:
            if isinstance(stage, dict):
                required = stage.get("required_location")
                if _simple_normalize(required) in old_village_one_names:
                    stage["required_location"] = "Elarin"

    quest_engine._rise_glory_location_names_installed = True
