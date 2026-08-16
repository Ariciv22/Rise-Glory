from __future__ import annotations

import copy
from typing import Any

_PARAGRAPHS: dict[str, dict[str, Any]] = {}


def register_quest_paragraph(paragraph_id: str, text: str, *, title: str = "", quest_id: str = "") -> dict[str, Any]:
    paragraph_id = str(paragraph_id).strip()
    if not paragraph_id:
        raise ValueError("Akapit Księgi Questów wymaga identyfikatora.")
    entry = {
        "id": paragraph_id,
        "title": str(title or ""),
        "text": str(text or ""),
        "quest_id": str(quest_id or ""),
    }
    _PARAGRAPHS[paragraph_id] = entry
    return copy.deepcopy(entry)


def quest_paragraph(paragraph_id: str) -> dict[str, Any] | None:
    entry = _PARAGRAPHS.get(str(paragraph_id))
    return copy.deepcopy(entry) if entry else None


def all_quest_paragraphs() -> list[dict[str, Any]]:
    return [copy.deepcopy(value) for value in _PARAGRAPHS.values()]


# Pierwsze akapity testowe. Numer akapitu jest niezależny od numeru Questa.
register_quest_paragraph(
    "130A",
    "Po długiej rozmowie obie rodziny zgadzają się podzielić dostęp do studni. Starsi wyznaczają kolejność czerpania wody, a napięcie powoli opada.",
    title="Ugoda przy studni",
    quest_id="spor_o_studnie",
)
register_quest_paragraph(
    "130Z",
    "Rozmowa zamienia się w serię oskarżeń. Nikt nie chce ustąpić, a każda kolejna próba porozumienia będzie trudniejsza.",
    title="Rozmowy załamują się",
    quest_id="spor_o_studnie",
)
register_quest_paragraph(
    "131A",
    "Wskazany przez bohatera winny ustępuje pod presją. Spór cichnie, choć jedna z rodzin zapamiętuje sposób, w jaki wymuszono rozwiązanie.",
    title="Wymuszone rozstrzygnięcie",
    quest_id="spor_o_studnie",
)
register_quest_paragraph(
    "131Z",
    "Próba manipulacji zostaje zauważona. Rodziny zaczynają podejrzewać także bohatera i dalsze rozmowy stają się trudniejsze.",
    title="Intryga odkryta",
    quest_id="spor_o_studnie",
)
