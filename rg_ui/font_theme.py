from __future__ import annotations

from pathlib import Path

import pygame


_ORIGINAL_SYSFONT = pygame.font.SysFont
_INSTALLED = False
ROOT_DIR = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT_DIR / "Grafiki" / "fonty"

# Docelowo fonty trzymamy jako asset gry. Loader jest juz gotowy na pliki,
# dzieki czemu po dodaniu ich do Grafiki/fonty wyglad bedzie identyczny na
# kazdym komputerze, niezaleznie od fontow zainstalowanych w Windowsie.
_TITLE_FONT_FILES = (
    "Cinzel-SemiBold.ttf",
    "Cinzel-Bold.ttf",
    "Cinzel-Regular.ttf",
)
_BODY_FONT_FILES = (
    "CormorantGaramond-SemiBold.ttf",
    "CormorantGaramond-Regular.ttf",
    "Cinzel-Regular.ttf",
)

# Dopoki lokalnych assetow fontow nie ma, wybieramy zdecydowanie bardziej
# fantasy/ksiazkowe kroje dostepne na typowej instalacji Windows. Gabriola
# sluzy jako dekoracyjny font naglowkow, a Garamond/Goudy jako czytelny tekst.
_TITLE_FAMILIES = (
    "Cinzel Decorative",
    "Cinzel",
    "Gabriola",
    "Castellar",
    "Goudy Old Style",
    "Garamond",
    "Palatino Linotype",
    "Book Antiqua",
    "Georgia",
)
_BODY_FAMILIES = (
    "Garamond",
    "Goudy Old Style",
    "Palatino Linotype",
    "Book Antiqua",
    "Constantia",
    "Georgia",
    "Times New Roman",
)


def _normalized_family_name(value) -> str:
    return "".join(character for character in str(value or "").lower() if character.isalnum())


def _is_plain_ui_font(name) -> bool:
    if isinstance(name, (list, tuple)):
        return any(_is_plain_ui_font(value) for value in name)
    normalized = _normalized_family_name(name)
    return normalized in {
        "arial",
        "helvetica",
        "sans",
        "sansserif",
        "dejavusans",
        "liberationsans",
    }


def _asset_font_path(filenames):
    for filename in filenames:
        path = FONT_DIR / filename
        if path.is_file():
            return str(path)
    return None


def _find_font_path(families, bold=False, italic=False):
    for family in families:
        try:
            path = pygame.font.match_font(family, bold=bold, italic=italic)
        except (AttributeError, pygame.error):
            path = None
        if path:
            return path
    return None


def _original_sysfont(name, size, bold=False, italic=False, constructor=None):
    if constructor is None:
        return _ORIGINAL_SYSFONT(name, size, bold=bold, italic=italic)
    try:
        return _ORIGINAL_SYSFONT(name, size, bold=bold, italic=italic, constructor=constructor)
    except TypeError:
        return _ORIGINAL_SYSFONT(name, size, bold=bold, italic=italic)


def _font_from_path(path, size, bold=False, italic=False, constructor=None):
    if not path:
        return None
    try:
        font_constructor = constructor or pygame.font.Font
        font = font_constructor(path, size)
        if bold:
            font.set_bold(True)
        if italic:
            font.set_italic(True)
        return font
    except (TypeError, OSError, pygame.error):
        return None


def _themed_sysfont(name, size, bold=False, italic=False, constructor=None):
    if not _is_plain_ui_font(name):
        return _original_sysfont(name, size, bold, italic, constructor)

    is_title = int(size) >= 26
    asset_files = _TITLE_FONT_FILES if is_title else _BODY_FONT_FILES
    system_families = _TITLE_FAMILIES if is_title else _BODY_FAMILIES

    # 1. Wlasny asset gry - najwyzszy priorytet.
    font = _font_from_path(
        _asset_font_path(asset_files),
        size,
        bold=bold,
        italic=italic,
        constructor=constructor,
    )
    if font is not None:
        return font

    # 2. Fantasy/serif z systemu operacyjnego.
    font = _font_from_path(
        _find_font_path(system_families, bold=bold, italic=italic),
        size,
        bold=bold,
        italic=italic,
        constructor=constructor,
    )
    if font is not None:
        return font

    # 3. Ostateczny fallback nadal serifowy - nigdy nie wracamy do Ariala.
    return _original_sysfont("georgia", size, bold, italic, constructor)


def install_font_theme():
    """Globalnie zamienia techniczne fonty sans-serif UI na motyw Rise & Glory."""
    global _INSTALLED
    if _INSTALLED:
        return False
    pygame.font.SysFont = _themed_sysfont
    _INSTALLED = True
    return True
