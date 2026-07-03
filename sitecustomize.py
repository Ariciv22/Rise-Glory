"""Runtime UI extension for deck panel.

This keeps main.py clean and extends game_ui without adding more code there yet.
Python loads sitecustomize automatically before main.py imports game_ui.
"""

from pathlib import Path

try:
    import pygame
    import game_ui
except Exception:  # pragma: no cover
    pygame = None
    game_ui = None


if pygame is not None and game_ui is not None:
    ROOT_DIR = Path(__file__).resolve().parent
    DECK_GRAPHICS_DIRS = [
        ROOT_DIR / "Grafiki" / "talie kart",
        ROOT_DIR / "Grafiki" / "grafiki UI",
    ]

    DECKS = [
        {"name": "Przygody", "keys": ("przygody", "deck_przygody", "adventures")},
        {"name": "Technologia", "keys": ("nauka", "technologia", "deck_technologia", "technology")},
        {"name": "Polityki i Intrygi", "keys": ("polityki_intrygi", "polityki_i_intrygi", "polityki intrygi", "deck_polityki_i_intrygi")},
        {"name": "Ekonomia", "keys": ("ekonomia", "deck_ekonomia", "economy")},
        {"name": "Doradcy i Emisariusze", "keys": ("doradcy_emisariusze", "doradcy_i_emisariusze", "doradcy emisariusze", "deck_doradcy_i_emisariusze")},
        {"name": "Talia Osobista", "keys": ("talia_osobista", "deck_talia_osobista", "personal_deck")},
    ]

    game_ui.DECKS = DECKS
    original_load_ui_panel_graphics = game_ui.load_ui_panel_graphics

    def _find_image(*names):
        for directory in DECK_GRAPHICS_DIRS:
            for name in names:
                for ext in ["", ".png", ".jpg", ".jpeg", ".webp"]:
                    path = directory / f"{name}{ext}"
                    if path.exists():
                        return path
        return None

    def _load_deck_images():
        images = {}
        for deck in DECKS:
            path = _find_image(*deck["keys"])
            if path:
                image = pygame.image.load(str(path)).convert_alpha()
                images[deck["name"]] = game_ui.crop_to_visible(game_ui.remove_checker_background(image))
            else:
                images[deck["name"]] = None
        return images

    def patched_load_ui_panel_graphics():
        graphics = original_load_ui_panel_graphics()
        graphics["decks"] = _load_deck_images()
        return graphics

    def _blit_fit_center(screen, image, rect):
        iw, ih = image.get_size()
        if iw <= 0 or ih <= 0 or rect.width <= 0 or rect.height <= 0:
            return
        scale = min(rect.width / iw, rect.height / ih)
        size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
        scaled = pygame.transform.smoothscale(image, size)
        screen.blit(scaled, (rect.x + (rect.width - size[0]) // 2, rect.y + (rect.height - size[1]) // 2))

    def _draw_fallback_deck(screen, font, rect, name):
        pygame.draw.rect(screen, (38, 30, 22), rect, border_radius=8)
        pygame.draw.rect(screen, (128, 92, 48), rect, 2, border_radius=8)
        words = name.split()
        lines = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if font.size(candidate)[0] <= rect.width - 16:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        y = rect.centery - (len(lines) * 20) // 2
        for line in lines:
            label = font.render(line, True, game_ui.TEXT_COLOR)
            screen.blit(label, label.get_rect(center=(rect.centerx, y + 10)))
            y += 20

    def _draw_deck_slot(screen, font, slot, deck_name, image):
        pygame.draw.rect(screen, (18, 15, 12), slot, border_radius=8)
        pygame.draw.rect(screen, game_ui.GOLD_BORDER, slot, 1, border_radius=8)
        inner = slot.inflate(-10, -10)
        if image:
            _blit_fit_center(screen, image, inner)
        else:
            _draw_fallback_deck(screen, font, inner, deck_name)

    def patched_draw_cards_panel(screen, font, small_font, mouse_pos, ui_state, ui_graphics):
        _, sh = screen.get_size()
        buttons = []
        x = 0 if ui_state.cards_open else -game_ui.LEFT_CARDS_WIDTH + game_ui.PANEL_HANDLE
        y = game_ui.PLAYER_TOPBAR_HEIGHT + game_ui.LEFT_SCORE_HEIGHT + game_ui.PANEL_GAP * 2 + 24
        panel_h = max(220, sh - y)
        panel = pygame.Rect(x, y, game_ui.LEFT_CARDS_WIDTH, panel_h)
        game_ui.draw_image_panel(screen, panel, ui_graphics.get("panel1"), fill_alpha=25)
        handle = pygame.Rect(x + game_ui.LEFT_CARDS_WIDTH - game_ui.PANEL_HANDLE, y + 14, game_ui.PANEL_HANDLE, 54)
        game_ui.draw_arrow_handle(screen, handle, "left" if ui_state.cards_open else "right", mouse_pos)
        buttons.append(game_ui.Button("", "toggle_cards", handle))

        if ui_state.cards_open:
            old_clip = screen.get_clip()
            screen.set_clip(panel.inflate(-46, -36))
            screen.blit(font.render("Talie kart", True, game_ui.TEXT_COLOR), (x + 52, y + 30))
            deck_images = ui_graphics.get("decks", {})
            content_x = x + 28
            content_top = y + 72
            content_w = game_ui.LEFT_CARDS_WIDTH - 66
            content_h = panel.bottom - content_top - 28
            gap = 8
            slot_h = max(46, min(92, (content_h - gap * (len(DECKS) - 1)) // len(DECKS)))
            py = content_top
            for deck in DECKS:
                slot = pygame.Rect(content_x, py, content_w, slot_h)
                _draw_deck_slot(screen, small_font, slot, deck["name"], deck_images.get(deck["name"]))
                buttons.append(game_ui.Button("", f"deck:{deck['name']}", slot))
                py += slot_h + gap
            screen.set_clip(old_clip)
        return buttons, [panel]

    game_ui.load_ui_panel_graphics = patched_load_ui_panel_graphics
    game_ui.draw_cards_panel = patched_draw_cards_panel
