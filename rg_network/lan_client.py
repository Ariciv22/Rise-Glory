from __future__ import annotations

import argparse
import queue
import socket
import threading
import time
from typing import Any

from rg_network.protocol import DEFAULT_PORT, MessageBuffer, encode_message, make_message


class LanClient:
    def __init__(self) -> None:
        self.sock: socket.socket | None = None
        self.player_id: str | None = None
        self.is_host = False
        self.connected = False
        self._events: queue.Queue[dict[str, Any]] = queue.Queue()
        self._send_lock = threading.Lock()
        self._reader: threading.Thread | None = None

    def connect(self, host: str, name: str, port: int = DEFAULT_PORT, timeout: float = 5.0) -> None:
        self.close()
        self.player_id = None
        self.is_host = False
        self._events = queue.Queue()
        sock = socket.create_connection((host, int(port)), timeout=timeout)
        sock.settimeout(None)
        self.sock = sock
        self.connected = True
        self._reader = threading.Thread(target=self._reader_loop, name="rg-lan-reader", daemon=True)
        self._reader.start()
        self.send(make_message("hello", name=(name.strip()[:24] or "Gracz")))

    def send(self, message: dict[str, Any]) -> None:
        sock = self.sock
        if not self.connected or sock is None:
            raise ConnectionError("Klient LAN nie jest polaczony.")
        try:
            with self._send_lock:
                sock.sendall(encode_message(message))
        except OSError as exc:
            self._events.put(make_message("connection_lost", reason=str(exc)))
            self.close()
            raise ConnectionError("Utracono polaczenie z serwerem LAN.") from exc

    def set_ready(self, ready: bool) -> None:
        self.send(make_message("ready", ready=bool(ready)))

    def send_chat(self, text: str) -> None:
        self.send(make_message("chat", text=str(text)[:240]))

    def start_game(self) -> None:
        self.send(make_message("start_game"))

    def ping(self) -> None:
        self.send(make_message("ping", sent_at=time.time()))

    def poll(self, limit: int = 100) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        for _ in range(max(0, int(limit))):
            try:
                event = self._events.get_nowait()
            except queue.Empty:
                break
            event_type = event.get("type")
            if event_type == "welcome":
                self.player_id = str(event.get("player_id"))
                self.is_host = bool(event.get("is_host", False))
            elif event_type == "lobby_state" and self.player_id:
                own_state = next(
                    (player for player in event.get("players", []) if player.get("player_id") == self.player_id),
                    None,
                )
                if own_state is not None:
                    self.is_host = bool(own_state.get("is_host", False))
            events.append(event)
        return events

    def _reader_loop(self) -> None:
        buffer = MessageBuffer()
        try:
            while self.connected and self.sock is not None:
                data = self.sock.recv(4096)
                if not data:
                    break
                for message in buffer.feed(data):
                    self._events.put(message)
        except (OSError, ValueError, UnicodeError) as exc:
            if self.connected:
                self._events.put(make_message("connection_lost", reason=str(exc)))
        finally:
            self.connected = False
            self._events.put(make_message("disconnected"))

    def close(self) -> None:
        self.connected = False
        sock = self.sock
        self.sock = None
        if sock is not None:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                sock.close()
            except OSError:
                pass


def _print_event(event: dict[str, Any]) -> None:
    event_type = event.get("type")
    if event_type == "lobby_state":
        print("\nLOBBY:")
        for player in event.get("players", []):
            host = " HOST" if player.get("is_host") else ""
            ready = "GOTOWY" if player.get("ready") else "czeka"
            print(f"- {player.get('name')} [{ready}]{host}")
        return
    if event_type == "chat":
        print(f"[{event.get('name')}] {event.get('text')}")
        return
    if event_type == "welcome":
        print(f"Polaczono. ID={event.get('player_id')} host={event.get('is_host')}")
        return
    if event_type == "game_start":
        print("\n*** SERWER ROZPOCZAL GRE LAN ***")
        return
    if event_type in {"error", "rejected", "connection_lost"}:
        print(f"{event_type.upper()}: {event.get('reason', '-')}")
        return
    if event_type not in {"player_joined", "player_left", "pong", "disconnected"}:
        print(event)


def main() -> None:
    parser = argparse.ArgumentParser(description="Rise & Glory - testowy klient LAN")
    parser.add_argument("host", help="IPv4 komputera hosta, np. 192.168.1.25")
    parser.add_argument("--name", default=socket.gethostname(), help="Nazwa gracza")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    client = LanClient()
    client.connect(args.host, args.name, args.port)
    print("Komendy: ready, unready, start, say TEKST, ping, quit")
    try:
        while client.connected:
            for event in client.poll():
                _print_event(event)
            try:
                command = input("> ").strip()
            except EOFError:
                break
            if command == "ready":
                client.set_ready(True)
            elif command == "unready":
                client.set_ready(False)
            elif command == "start":
                client.start_game()
            elif command.startswith("say "):
                client.send_chat(command[4:])
            elif command == "ping":
                client.ping()
            elif command in {"quit", "exit"}:
                break
            elif command:
                print("Nieznana komenda.")
            time.sleep(0.05)
    finally:
        client.close()


if __name__ == "__main__":
    main()
