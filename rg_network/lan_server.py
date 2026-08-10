from __future__ import annotations

import argparse
import socket
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from rg_network.game_state import NetworkGameSession
from rg_network.protocol import DEFAULT_PORT, PROTOCOL_VERSION, MessageBuffer, encode_message, make_message

MAX_PLAYERS = 6


def get_lan_ipv4() -> str:
    """Zwraca adres IPv4 komputera widoczny zwykle w tej samej sieci LAN."""
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("192.0.2.1", 9))
        address = probe.getsockname()[0]
        if address and not address.startswith("127."):
            return address
    except OSError:
        pass
    finally:
        probe.close()

    try:
        address = socket.gethostbyname(socket.gethostname())
        if address:
            return address
    except OSError:
        pass
    return "127.0.0.1"


@dataclass
class ConnectedPlayer:
    player_id: str
    name: str
    sock: socket.socket
    address: tuple[str, int]
    ready: bool = False
    is_host: bool = False
    archetype_id: int | None = None
    send_lock: threading.Lock = field(default_factory=threading.Lock)

    def public_state(self) -> dict[str, Any]:
        return {
            "player_id": self.player_id,
            "name": self.name,
            "ready": self.ready,
            "is_host": self.is_host,
            "archetype_id": self.archetype_id,
        }


class LanLobbyServer:
    """Serwer LAN lobby i pierwszego autorytatywnego vertical slice Rise & Glory."""

    def __init__(self, host: str = "0.0.0.0", port: int = DEFAULT_PORT, max_players: int = MAX_PLAYERS) -> None:
        self.host = host
        self.port = int(port)
        self.max_players = max(1, min(MAX_PLAYERS, int(max_players)))
        self._server_socket: socket.socket | None = None
        self._players: dict[str, ConnectedPlayer] = {}
        self._lock = threading.RLock()
        self._running = threading.Event()
        self._accept_thread: threading.Thread | None = None
        self._started_at = time.time()
        self._game: NetworkGameSession | None = None

    @property
    def running(self) -> bool:
        return self._running.is_set()

    @property
    def player_count(self) -> int:
        with self._lock:
            return len(self._players)

    @property
    def game_started(self) -> bool:
        return self._game is not None

    def start(self, background: bool = True) -> None:
        if self.running:
            return
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(self.max_players + 2)
        server.settimeout(0.5)
        self._server_socket = server
        self._running.set()
        if background:
            self._accept_thread = threading.Thread(target=self._accept_loop, name="rg-lan-accept", daemon=True)
            self._accept_thread.start()
        else:
            self._accept_loop()

    def stop(self) -> None:
        self._running.clear()
        server = self._server_socket
        self._server_socket = None
        if server is not None:
            try:
                server.close()
            except OSError:
                pass
        with self._lock:
            players = list(self._players.values())
            self._players.clear()
            self._game = None
        for player in players:
            try:
                player.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                player.sock.close()
            except OSError:
                pass

    def _accept_loop(self) -> None:
        while self.running:
            server = self._server_socket
            if server is None:
                break
            try:
                client_socket, address = server.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            client_socket.settimeout(30.0)
            thread = threading.Thread(
                target=self._client_loop,
                args=(client_socket, address),
                name=f"rg-lan-client-{address[0]}-{address[1]}",
                daemon=True,
            )
            thread.start()

    def _send_socket(self, sock: socket.socket, message: dict[str, Any], lock: threading.Lock | None = None) -> bool:
        try:
            if lock is None:
                sock.sendall(encode_message(message))
            else:
                with lock:
                    sock.sendall(encode_message(message))
            return True
        except OSError:
            return False

    def _send_player(self, player: ConnectedPlayer, message: dict[str, Any]) -> bool:
        return self._send_socket(player.sock, message, player.send_lock)

    def _broadcast(self, message: dict[str, Any], exclude_player_id: str | None = None) -> None:
        with self._lock:
            players = list(self._players.values())
        stale: list[str] = []
        for player in players:
            if exclude_player_id and player.player_id == exclude_player_id:
                continue
            if not self._send_player(player, message):
                stale.append(player.player_id)
        for player_id in stale:
            self._remove_player(player_id)

    def _lobby_state(self) -> dict[str, Any]:
        with self._lock:
            players = [player.public_state() for player in self._players.values()]
        return make_message(
            "lobby_state",
            players=players,
            max_players=self.max_players,
            server_uptime=int(time.time() - self._started_at),
            game_started=self.game_started,
        )

    def _broadcast_lobby(self) -> None:
        self._broadcast(self._lobby_state())

    def _broadcast_game_state(self) -> None:
        game = self._game
        if game is not None:
            self._broadcast(make_message("game_state", snapshot=game.snapshot()))

    def _remove_player(self, player_id: str) -> None:
        with self._lock:
            player = self._players.pop(player_id, None)
            if player is None:
                return
            was_host = player.is_host
            remaining = list(self._players.values())
            if was_host and remaining:
                remaining[0].is_host = True
        try:
            player.sock.close()
        except OSError:
            pass
        self._broadcast(make_message("player_left", player_id=player_id, name=player.name))
        self._broadcast_lobby()

    def _register_player(self, sock: socket.socket, address: tuple[str, int], hello: dict[str, Any]) -> ConnectedPlayer | None:
        if int(hello.get("protocol", 0) or 0) != PROTOCOL_VERSION:
            self._send_socket(sock, make_message("rejected", reason="Niezgodna wersja protokolu multiplayer."))
            return None
        name = str(hello.get("name", "")).strip()[:24] or "Gracz"
        with self._lock:
            if self._game is not None:
                self._send_socket(sock, make_message("rejected", reason="Partia juz sie rozpoczęla."))
                return None
            if len(self._players) >= self.max_players:
                self._send_socket(sock, make_message("rejected", reason="Lobby jest pelne."))
                return None
            player_id = uuid.uuid4().hex[:10]
            player = ConnectedPlayer(
                player_id=player_id,
                name=name,
                sock=sock,
                address=address,
                is_host=not self._players,
            )
            self._players[player_id] = player
        self._send_player(
            player,
            make_message(
                "welcome",
                player_id=player.player_id,
                is_host=player.is_host,
                server_port=self.port,
                max_players=self.max_players,
            ),
        )
        self._broadcast(make_message("player_joined", player=player.public_state()))
        self._broadcast_lobby()
        return player

    def _start_game(self, player: ConnectedPlayer) -> None:
        with self._lock:
            players = list(self._players.values())
        if not player.is_host:
            self._send_player(player, make_message("error", reason="Tylko host moze rozpoczac gre."))
            return
        if len(players) < 2:
            self._send_player(player, make_message("error", reason="Do gry LAN potrzeba co najmniej 2 graczy."))
            return
        if not all(entry.archetype_id for entry in players):
            self._send_player(player, make_message("error", reason="Kazdy gracz musi wybrac bohatera."))
            return
        if not all(entry.ready for entry in players):
            self._send_player(player, make_message("error", reason="Wszyscy gracze musza byc gotowi."))
            return
        try:
            game = NetworkGameSession([entry.public_state() for entry in players])
        except ValueError as exc:
            self._send_player(player, make_message("error", reason=str(exc)))
            return
        with self._lock:
            self._game = game
        self._broadcast(
            make_message(
                "game_start",
                snapshot=game.snapshot(),
            )
        )

    def _handle_message(self, player: ConnectedPlayer, message: dict[str, Any]) -> None:
        message_type = str(message.get("type", ""))

        if message_type == "configure_hero":
            if self._game is not None:
                self._send_player(player, make_message("error", reason="Partia juz sie rozpoczela."))
                return
            archetype_id = int(message.get("archetype_id", 0) or 0)
            if archetype_id not in range(1, 7):
                self._send_player(player, make_message("error", reason="Nieprawidlowy archetyp bohatera."))
                return
            player.archetype_id = archetype_id
            player.ready = False
            self._broadcast_lobby()
            return

        if message_type == "ready":
            if self._game is not None:
                self._send_player(player, make_message("error", reason="Partia juz sie rozpoczela."))
                return
            wants_ready = bool(message.get("ready", False))
            if wants_ready and not player.archetype_id:
                self._send_player(player, make_message("error", reason="Najpierw wybierz bohatera."))
                return
            player.ready = wants_ready
            self._broadcast_lobby()
            return

        if message_type == "chat":
            text = str(message.get("text", "")).strip()[:240]
            if text:
                self._broadcast(make_message("chat", player_id=player.player_id, name=player.name, text=text))
            return

        if message_type == "start_game":
            self._start_game(player)
            return

        if message_type == "move_request":
            game = self._game
            if game is None:
                self._send_player(player, make_message("error", reason="Partia nie zostala jeszcze uruchomiona."))
                return
            success, reason = game.move(player.player_id, int(message.get("target_tile_id", 0) or 0))
            if not success:
                self._send_player(player, make_message("error", reason=reason))
                return
            self._broadcast_game_state()
            return

        if message_type == "end_turn_request":
            game = self._game
            if game is None:
                self._send_player(player, make_message("error", reason="Partia nie zostala jeszcze uruchomiona."))
                return
            success, reason = game.end_turn(player.player_id)
            if not success:
                self._send_player(player, make_message("error", reason=reason))
                return
            self._broadcast_game_state()
            return

        if message_type == "request_game_state":
            game = self._game
            if game is not None:
                self._send_player(player, make_message("game_state", snapshot=game.snapshot()))
            return

        if message_type == "ping":
            self._send_player(player, make_message("pong", sent_at=message.get("sent_at")))
            return

        self._send_player(player, make_message("error", reason=f"Nieznany typ wiadomosci: {message_type or '-'}"))

    def _client_loop(self, sock: socket.socket, address: tuple[str, int]) -> None:
        buffer = MessageBuffer()
        player: ConnectedPlayer | None = None
        try:
            while self.running:
                data = sock.recv(4096)
                if not data:
                    break
                messages = buffer.feed(data)
                for message in messages:
                    if player is None:
                        if str(message.get("type", "")) != "hello":
                            self._send_socket(sock, make_message("rejected", reason="Najpierw wymagane jest HELLO."))
                            return
                        player = self._register_player(sock, address, message)
                        if player is None:
                            return
                        sock.settimeout(None)
                    else:
                        self._handle_message(player, message)
        except (OSError, ValueError, UnicodeError):
            pass
        finally:
            if player is not None:
                self._remove_player(player.player_id)
            else:
                try:
                    sock.close()
                except OSError:
                    pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Rise & Glory - serwer LAN")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port TCP, domyslnie {DEFAULT_PORT}")
    parser.add_argument("--max-players", type=int, default=MAX_PLAYERS, choices=range(2, MAX_PLAYERS + 1))
    args = parser.parse_args()

    server = LanLobbyServer(port=args.port, max_players=args.max_players)
    server.start(background=True)
    print("Rise & Glory - LAN server")
    print(f"Adres dla graczy: {get_lan_ipv4()}:{args.port}")
    print(f"Maksymalnie graczy: {args.max_players}")
    print("CTRL+C konczy serwer.")
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nZamykanie serwera...")
    finally:
        server.stop()


if __name__ == "__main__":
    main()
