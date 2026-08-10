from __future__ import annotations

import copy
import socket
from typing import Any

import pygame

from rg_core.data import BG, GOLD, HERO_ARCHETYPES, MUTED, PANEL, TEXT, ZOOM_STEP
from rg_core.setup import GameHeroToken
from rg_engine.world import register_players
from rg_network.lan_client import LanClient
from rg_network.lan_server import LanLobbyServer, get_lan_ipv4
from rg_network.protocol import DEFAULT_PORT
from rg_ui import over_ui, ui_rects
from rg_ui.common import Button, draw_panel, wrap
from rg_ui.hud import draw_game_ui
from rg_ui.tooltip import draw_location_tooltip
from rg_world.map import Camera, Tile


class _LanView:
    def __init__(self) -> None:
        self.mode = "menu"
        self.name = socket.gethostname()[:24] or "Gracz"
        self.host_ip = ""
        self.active_field: str | None = None
        self.status = ""
        self.server: LanLobbyServer | None = None
        self.client: LanClient | None = None
        self.server_address = ""
        self.lobby: dict[str, Any] = {"players": [], "max_players": 6}
        self.selected_archetype_id: int | None = None
        self.local_ready = False
        self.snapshot: dict[str, Any] | None = None
        self.players: list[dict[str, Any]] = []
        self.tiles: list[Tile] = []
        self.tokens: list[GameHeroToken] = []
        self.active_player_index = 0
        self.local_player_index = -1
        self.selected_tile: Tile | None = None
        self.camera = Camera()
        self.dragging = False
        self.drag_moved = False
        self.drag_start = (0, 0)
        self.last_mouse = (0, 0)

    def cleanup(self) -> None:
        if self.client is not None:
            self.client.close()
            self.client = None
        if self.server is not None:
            self.server.stop()
            self.server = None

    def own_lobby_state(self) -> dict[str, Any] | None:
        if self.client is None or not self.client.player_id:
            return None
        return next(
            (item for item in self.lobby.get("players", []) if item.get("player_id") == self.client.player_id),
            None,
        )

    def sync_own_lobby_flags(self) -> None:
        own = self.own_lobby_state()
        if own is None:
            return
        self.selected_archetype_id = own.get("archetype_id")
        self.local_ready = bool(own.get("ready", False))

    def connect_as_host(self) -> None:
        self.cleanup()
        self.server = LanLobbyServer(port=DEFAULT_PORT, max_players=6)
        self.server.start(background=True)
        address = get_lan_ipv4()
        self.server_address = f"{address}:{DEFAULT_PORT}"
        self.client = LanClient()
        try:
            self.client.connect(address, self.name, DEFAULT_PORT)
        except OSError:
            self.client.connect("127.0.0.1", self.name, DEFAULT_PORT)
        self.mode = "lobby"
        self.status = f"Lobby utworzone. Podaj innym graczom adres {self.server_address}."

    def connect_to_host(self) -> None:
        host = self.host_ip.strip()
        if not host:
            self.status = "Wpisz adres IPv4 komputera hosta."
            return
        self.cleanup()
        self.client = LanClient()
        self.client.connect(host, self.name, DEFAULT_PORT)
        self.server_address = f"{host}:{DEFAULT_PORT}"
        self.mode = "lobby"
        self.status = "Polaczono z hostem LAN."

    def apply_snapshot(self, snapshot: dict[str, Any], center_camera: bool = False) -> None:
        if not snapshot:
            return
        previous_selected_id = getattr(self.selected_tile, "id", None)
        self.snapshot = copy.deepcopy(snapshot)
        self.players = [copy.deepcopy(entry.get("hero", {})) for entry in snapshot.get("players", [])]
        register_players(self.players)

        self.tiles = []
        tiles_by_id: dict[int, Tile] = {}
        for row in snapshot.get("tiles", []):
            tile = Tile(
                int(row["id"]),
                int(row["q"]),
                int(row["r"]),
                float(row["x"]),
                float(row["y"]),
                str(row["terrain_key"]),
            )
            tile.location = copy.deepcopy(row.get("location"))
            tile.adventure = copy.deepcopy(row.get("adventure"))
            self.tiles.append(tile)
            tiles_by_id[tile.id] = tile

        self.tokens = []
        for token_row in snapshot.get("tokens", []):
            player_index = int(token_row["player_index"])
            hero = self.players[player_index]
            tile = tiles_by_id[int(token_row["tile_id"])]
            token = GameHeroToken(hero, tile)
            token.actions = int(token_row.get("actions", 0))
            token.start_tile = tiles_by_id.get(int(token_row.get("start_tile_id", tile.id)), tile)
            self.tokens.append(token)

        turn = snapshot.get("turn", {})
        self.active_player_index = int(turn.get("active_player_index", 0) or 0)
        self.local_player_index = -1
        if self.client is not None and self.client.player_id:
            for index, entry in enumerate(snapshot.get("players", [])):
                if entry.get("network_player_id") == self.client.player_id:
                    self.local_player_index = index
                    break

        self.selected_tile = tiles_by_id.get(int(previous_selected_id)) if previous_selected_id else None
        if center_camera and self.tiles:
            self.camera.center_on_tiles(self.tiles)
        elif self.tokens and 0 <= self.active_player_index < len(self.tokens):
            self.camera.center_on_tile(self.tokens[self.active_player_index].tile)

    def process_network(self) -> None:
        client = self.client
        if client is None:
            return
        for event in client.poll():
            event_type = event.get("type")
            if event_type == "lobby_state":
                self.lobby = event
                self.sync_own_lobby_flags()
            elif event_type == "game_start":
                self.apply_snapshot(event.get("snapshot", {}), center_camera=True)
                self.mode = "game"
                self.status = "Partia LAN rozpoczeta. Serwer kontroluje ruch i kolejnosc tur."
            elif event_type == "game_state":
                old_active = self.active_player_index
                self.apply_snapshot(event.get("snapshot", {}), center_camera=False)
                if self.active_player_index != old_active and self.tokens:
                    self.camera.center_on_tile(self.tokens[self.active_player_index].tile)
            elif event_type in {"error", "rejected", "connection_lost"}:
                self.status = str(event.get("reason") or "Blad polaczenia LAN.")
            elif event_type == "disconnected" and self.mode != "menu":
                self.status = "Rozlaczono z serwerem LAN."


def _centered_button(text: str, action: str, y: int, width: int = 420, height: int = 58) -> Button:
    sw = pygame.display.get_surface().get_width()
    return Button(text, action, (sw // 2 - width // 2, y, width, height))


def _draw_title(screen, title_font, font, title: str, subtitle: str) -> None:
    screen.fill(BG)
    title_label = title_font.render(title, True, TEXT)
    screen.blit(title_label, title_label.get_rect(center=(screen.get_width() // 2, 95)))
    subtitle_label = font.render(subtitle, True, MUTED)
    screen.blit(subtitle_label, subtitle_label.get_rect(center=(screen.get_width() // 2, 140)))


def _draw_text_field(screen, font, small_font, rect: pygame.Rect, label: str, value: str, active: bool, placeholder: str) -> None:
    screen.blit(small_font.render(label, True, MUTED), (rect.x, rect.y - 25))
    pygame.draw.rect(screen, (32, 35, 38), rect, border_radius=9)
    pygame.draw.rect(screen, GOLD if active else (100, 90, 70), rect, 2, border_radius=9)
    shown = value if value else placeholder
    color = TEXT if value else MUTED
    screen.blit(font.render(shown, True, color), (rect.x + 16, rect.y + 14))


def _draw_setup(screen, title_font, font, small_font, mouse, view: _LanView, joining: bool):
    title = "Dolacz do gry LAN" if joining else "Utworz gre LAN"
    subtitle = "Komputery musza znajdowac sie w tej samej sieci LAN / Wi-Fi"
    _draw_title(screen, title_font, font, title, subtitle)
    width = 520
    x = screen.get_width() // 2 - width // 2
    name_rect = pygame.Rect(x, 230, width, 56)
    _draw_text_field(screen, font, small_font, name_rect, "Imie bohatera", view.name, view.active_field == "name", "Wpisz imie")
    fields = {"name": name_rect}
    y = 340
    if joining:
        host_rect = pygame.Rect(x, 340, width, 56)
        _draw_text_field(screen, font, small_font, host_rect, "IPv4 hosta", view.host_ip, view.active_field == "host", "np. 192.168.1.25")
        fields["host"] = host_rect
        y = 440
    action = "lan_connect" if joining else "lan_create"
    button = _centered_button("Polacz" if joining else "Utworz lobby", action, y)
    back = _centered_button("Powrot", "lan_back", y + 76, 260, 50)
    for item in [button, back]:
        item.draw(screen, font, mouse)
    if view.status:
        lines = wrap(small_font, view.status, 720)
        for index, line in enumerate(lines[:3]):
            label = small_font.render(line, True, (235, 170, 95))
            screen.blit(label, label.get_rect(center=(screen.get_width() // 2, y + 155 + index * 22)))
    return [button, back], fields


def _hero_name(archetype_id: int | None) -> str:
    archetype = next((item for item in HERO_ARCHETYPES if item["id"] == archetype_id), None)
    return archetype["name"] if archetype else "Nie wybrano"


def _draw_lobby(screen, title_font, font, small_font, mouse, view: _LanView):
    _draw_title(screen, title_font, font, "Lobby LAN", f"Serwer: {view.server_address}")
    buttons: list[Button] = []

    left = pygame.Rect(60, 185, min(560, screen.get_width() // 2 - 90), screen.get_height() - 250)
    right = pygame.Rect(left.right + 35, 185, screen.get_width() - left.right - 95, screen.get_height() - 250)
    draw_panel(screen, left, GOLD)
    draw_panel(screen, right, GOLD)

    lobby_players = list(view.lobby.get("players", []))
    screen.blit(font.render(f"Gracze {len(lobby_players)}/{view.lobby.get('max_players', 6)}", True, TEXT), (left.x + 22, left.y + 20))
    y = left.y + 62
    for index, player in enumerate(lobby_players):
        row = pygame.Rect(left.x + 18, y, left.width - 36, 62)
        pygame.draw.rect(screen, (29, 28, 25), row, border_radius=9)
        pygame.draw.rect(screen, GOLD, row, 1, border_radius=9)
        host = " HOST" if player.get("is_host") else ""
        ready = "GOTOWY" if player.get("ready") else "OCZEKUJE"
        name = f"{index + 1}. {player.get('name', 'Gracz')}{host}"
        screen.blit(font.render(name, True, TEXT), (row.x + 12, row.y + 8))
        details = f"{_hero_name(player.get('archetype_id'))} | {ready}"
        screen.blit(small_font.render(details, True, MUTED if not player.get("ready") else (165, 220, 150)), (row.x + 12, row.y + 35))
        y += 70

    screen.blit(font.render("Wybierz bohatera", True, TEXT), (right.x + 22, right.y + 20))
    card_w = max(180, (right.width - 66) // 2)
    card_h = 78
    start_y = right.y + 62
    for index, hero in enumerate(HERO_ARCHETYPES):
        col = index % 2
        row = index // 2
        rect = pygame.Rect(right.x + 20 + col * (card_w + 16), start_y + row * (card_h + 12), card_w, card_h)
        selected = hero["id"] == view.selected_archetype_id
        pygame.draw.rect(screen, (47, 42, 34) if selected else PANEL, rect, border_radius=10)
        pygame.draw.rect(screen, hero["color"] if selected else GOLD, rect, 3 if selected else 1, border_radius=10)
        screen.blit(font.render(hero["name"], True, TEXT), (rect.x + 14, rect.y + 11))
        stat = max(hero["stats"], key=hero["stats"].get)
        screen.blit(small_font.render(f"Glowna cecha: {stat} {hero['stats'][stat]}", True, MUTED), (rect.x + 14, rect.y + 43))
        buttons.append(Button("", f"lan_hero:{hero['id']}", rect))

    controls_y = right.bottom - 78
    ready_text = "Cofnij gotowosc" if view.local_ready else "Gotowy"
    ready = Button(ready_text, "lan_ready", (right.x + 20, controls_y, 190, 48))
    ready.draw(screen, font, mouse)
    buttons.append(ready)

    if view.client is not None and view.client.is_host:
        start = Button("Rozpocznij gre", "lan_start", (right.x + 230, controls_y, 210, 48))
        start.draw(screen, font, mouse)
        buttons.append(start)

    leave = Button("Opuść lobby", "lan_leave", (left.x + 20, left.bottom - 60, 190, 42))
    leave.draw(screen, small_font, mouse)
    buttons.append(leave)

    if view.status:
        message = small_font.render(view.status[:110], True, (235, 170, 95))
        screen.blit(message, (60, screen.get_height() - 45))
    return buttons


def _render_game(screen, font, small_font, token_font, textures, mouse, view: _LanView):
    hovered = None
    rects = ui_rects(screen)
    if not view.dragging and not over_ui(mouse, rects):
        for tile in view.tiles:
            if tile.contains(mouse, view.camera):
                hovered = tile
                break

    screen.fill(BG)
    is_local_turn = view.local_player_index == view.active_player_index
    active_token = view.tokens[view.active_player_index] if view.tokens else None
    for tile in view.tiles:
        valid = bool(is_local_turn and active_token and active_token.can_move_to(tile))
        tile.draw(
            screen,
            textures,
            view.camera,
            token_font,
            hovered=(tile == hovered),
            selected=(tile == view.selected_tile),
            valid_move=valid,
        )
    for index, token in enumerate(view.tokens):
        token.draw(screen, view.camera, token_font, selected=(index == view.active_player_index))

    if not view.players or not view.tokens:
        return [], hovered
    active_hero = view.players[view.active_player_index]
    turn = (view.snapshot or {}).get("turn", {})
    buttons = draw_game_ui(
        screen,
        font,
        small_font,
        active_hero,
        active_token,
        view.selected_tile,
        str((view.snapshot or {}).get("current_map", "rosette9")),
        view.active_player_index,
        view.players,
        view.tokens,
        int(turn.get("round_number", 1) or 1),
        int(turn.get("council_cycle", 1) or 1),
    )
    draw_location_tooltip(screen, font, small_font, hovered, mouse)

    banner_text = "TWOJA TURA" if is_local_turn else f"Tura: {active_hero.get('name', 'Gracz')}"
    banner = pygame.Rect(screen.get_width() // 2 - 130, 14, 260, 38)
    pygame.draw.rect(screen, (18, 16, 13), banner, border_radius=9)
    pygame.draw.rect(screen, GOLD, banner, 2, border_radius=9)
    label = small_font.render(f"LAN | {banner_text}", True, TEXT)
    screen.blit(label, label.get_rect(center=banner.center))

    if turn.get("council_due"):
        notice = "Osiagnieto moment Rady. Synchronizacja Rady bedzie kolejnym etapem LAN."
        status = small_font.render(notice, True, (235, 170, 95))
        screen.blit(status, status.get_rect(center=(screen.get_width() // 2, screen.get_height() - 18)))
    elif view.status:
        status = small_font.render(view.status[:120], True, MUTED)
        screen.blit(status, status.get_rect(center=(screen.get_width() // 2, screen.get_height() - 18)))
    return buttons, hovered


def run_lan_mode(screen, title_font, font, small_font, token_font, textures) -> None:
    """Blokujacy podtryb Pygame: lobby LAN + wspolna mapa + ruch i koniec tury."""
    view = _LanView()
    clock = pygame.time.Clock()
    running = True
    buttons: list[Button] = []
    fields: dict[str, pygame.Rect] = {}
    game_buttons: list[Button] = []
    pygame.key.start_text_input()

    try:
        while running:
            mouse = pygame.mouse.get_pos()
            view.process_network()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if view.mode in {"menu", "game"}:
                            running = False
                        elif view.mode == "lobby":
                            view.cleanup()
                            view.mode = "menu"
                            view.status = ""
                        else:
                            view.mode = "menu"
                            view.active_field = None
                        continue
                    if view.mode in {"host_setup", "join_setup"} and view.active_field:
                        if event.key == pygame.K_BACKSPACE:
                            if view.active_field == "name":
                                view.name = view.name[:-1]
                            elif view.active_field == "host":
                                view.host_ip = view.host_ip[:-1]
                        elif event.key == pygame.K_RETURN:
                            view.active_field = None
                    elif view.mode == "game" and event.key == pygame.K_SPACE and view.tokens:
                        view.camera.center_on_tile(view.tokens[view.active_player_index].tile)
                elif event.type == pygame.TEXTINPUT and view.mode in {"host_setup", "join_setup"} and view.active_field:
                    if view.active_field == "name":
                        view.name = (view.name + event.text)[:24]
                    elif view.active_field == "host":
                        allowed = "".join(ch for ch in event.text if ch.isdigit() or ch == ".")
                        view.host_ip = (view.host_ip + allowed)[:15]
                elif event.type == pygame.MOUSEWHEEL and view.mode == "game" and not over_ui(mouse, ui_rects(screen)):
                    view.camera.zoom_at(mouse, ZOOM_STEP if event.y > 0 else 1 / ZOOM_STEP)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if view.mode in {"host_setup", "join_setup"}:
                        view.active_field = next((name for name, rect in fields.items() if rect.collidepoint(event.pos)), None)
                    elif view.mode == "game" and not over_ui(event.pos, ui_rects(screen)):
                        view.dragging = True
                        view.drag_moved = False
                        view.drag_start = event.pos
                        view.last_mouse = event.pos
                elif event.type == pygame.MOUSEMOTION and view.mode == "game" and view.dragging:
                    dx = event.pos[0] - view.last_mouse[0]
                    dy = event.pos[1] - view.last_mouse[1]
                    if abs(event.pos[0] - view.drag_start[0]) > 4 or abs(event.pos[1] - view.drag_start[1]) > 4:
                        view.drag_moved = True
                    view.camera.move(dx, dy)
                    view.last_mouse = event.pos
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    view.dragging = False
                    if view.mode == "menu":
                        for button in buttons:
                            if not button.clicked(event.pos):
                                continue
                            if button.action == "lan_host":
                                view.mode = "host_setup"
                                view.active_field = "name"
                            elif button.action == "lan_join":
                                view.mode = "join_setup"
                                view.active_field = "host"
                            elif button.action == "lan_exit":
                                running = False
                            break
                    elif view.mode in {"host_setup", "join_setup"}:
                        for button in buttons:
                            if not button.clicked(event.pos):
                                continue
                            try:
                                if button.action == "lan_create":
                                    view.connect_as_host()
                                elif button.action == "lan_connect":
                                    view.connect_to_host()
                                elif button.action == "lan_back":
                                    view.mode = "menu"
                                    view.active_field = None
                            except OSError as exc:
                                view.status = f"Nie udalo sie polaczyc: {exc}"
                            break
                    elif view.mode == "lobby":
                        for button in buttons:
                            if not button.clicked(event.pos):
                                continue
                            action = str(button.action)
                            client = view.client
                            if client is None:
                                break
                            try:
                                if action.startswith("lan_hero:"):
                                    client.configure_hero(int(action.split(":", 1)[1]))
                                elif action == "lan_ready":
                                    client.set_ready(not view.local_ready)
                                elif action == "lan_start":
                                    client.start_game()
                                elif action == "lan_leave":
                                    view.cleanup()
                                    view.mode = "menu"
                                    view.status = ""
                            except (ConnectionError, OSError) as exc:
                                view.status = str(exc)
                            break
                    elif view.mode == "game":
                        clicked_button = False
                        for button in game_buttons:
                            if button.clicked(event.pos):
                                clicked_button = True
                                if button.action == "end_turn":
                                    if view.local_player_index == view.active_player_index and view.client is not None:
                                        try:
                                            view.client.end_turn()
                                        except ConnectionError as exc:
                                            view.status = str(exc)
                                    else:
                                        view.status = "Nie mozesz zakonczyc tury innego gracza."
                                break
                        if not clicked_button and not view.drag_moved and not over_ui(event.pos, ui_rects(screen)):
                            for tile in view.tiles:
                                if not tile.contains(event.pos, view.camera):
                                    continue
                                view.selected_tile = tile
                                if view.local_player_index == view.active_player_index and view.client is not None:
                                    active_token = view.tokens[view.active_player_index]
                                    if active_token.can_move_to(tile):
                                        try:
                                            view.client.request_move(tile.id)
                                        except ConnectionError as exc:
                                            view.status = str(exc)
                                break

            if view.mode == "menu":
                _draw_title(screen, title_font, font, "Multiplayer LAN", "Jedna siec lokalna, do 6 graczy")
                buttons = [
                    _centered_button("Utworz gre LAN", "lan_host", 280),
                    _centered_button("Dolacz do gry LAN", "lan_join", 360),
                    _centered_button("Powrot", "lan_exit", 455, 260, 50),
                ]
                for button in buttons:
                    button.draw(screen, font, mouse)
                fields = {}
                game_buttons = []
            elif view.mode == "host_setup":
                buttons, fields = _draw_setup(screen, title_font, font, small_font, mouse, view, joining=False)
                game_buttons = []
            elif view.mode == "join_setup":
                buttons, fields = _draw_setup(screen, title_font, font, small_font, mouse, view, joining=True)
                game_buttons = []
            elif view.mode == "lobby":
                buttons = _draw_lobby(screen, title_font, font, small_font, mouse, view)
                fields = {}
                game_buttons = []
            elif view.mode == "game":
                buttons = []
                fields = {}
                game_buttons, _ = _render_game(screen, font, small_font, token_font, textures, mouse, view)

            pygame.display.flip()
            clock.tick(60)
    finally:
        pygame.key.stop_text_input()
        view.cleanup()
