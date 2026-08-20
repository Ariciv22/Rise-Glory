from __future__ import annotations

import pygame

_ORIGINAL_SYSFONT = pygame.font.SysFont
_INSTALLED = False

# Naglowki moga korzystac z bardziej dekoracyjnego Cinzel, jesli uzytkownik
# posiada go w systemie. Mniejsze teksty preferuja czytelniejsze kroje
# klasyczne pasujace do fantasy / starego pergaminu.
_TITLE_FAMILIES = (
    "Cinzel",
    "Palatino Linotype",
    "Book Antiqua",
    "Georgia",
    "Times New Roman",
)
_BODY_FAMILIES = (
    "Palatino Linotype",
    "Book Antiqua",
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
    # Starsze wersje Pygame nie obsluguja argumentu constructor.
    if constructor is None:
        return _ORIGINAL_SYSFONT(name, size, bold=bold, italic=italic)
    try:
        return _ORIGINAL_SYSFONT(name, size, bold=bold, italic=italic, constructor=constructor)
    except TypeError:
        return _ORIGINAL_SYSFONT(name, size, bold=bold, italic=italic)


def _themed_sysfont(name, size, bold=False, italic=False, constructor=None):
    if not _is_plain_ui_font(name):
        return _original_sysfont(name, size, bold, italic, constructor)

    families = _TITLE_FAMILIES if int(size) >= 28 else _BODY_FAMILIES
    path = _find_font_path(families, bold=bold, italic=italic)
    if path:
        try:
            font_constructor = constructor or pygame.font.Font
            font = font_constructor(path, size)
            # Gdy system nie ma osobnego pliku bold/italic, pygame moze
            # zasymulowac styl bez zmiany wybranego kroju.
            if bold:
                font.set_bold(True)
            if italic:
                font.set_italic(True)
            return font
        except (TypeError, OSError, pygame.error):
            pass

    # Ostateczny fallback nadal jest serifowy, zamiast wracac do Ariala.
    return _original_sysfont("georgia", size, bold, italic, constructor)


def install_font_theme():
    """Globalnie zamienia zwykle fonty sans-serif UI na fantasy-serif."""
    global _INSTALLED
    if _INSTALLED:
        return False
    pygame.font.SysFont = _themed_sysfont
    _INSTALLED = True
    return True
