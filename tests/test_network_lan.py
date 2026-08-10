import socket
import time
import unittest

from rg_network.lan_client import LanClient
from rg_network.lan_server import LanLobbyServer


def _free_tcp_port():
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()
    return port


def _collect_until(client, predicate, timeout=2.0):
    deadline = time.time() + timeout
    events = []
    while time.time() < deadline:
        events.extend(client.poll())
        if predicate(events):
            return events
        time.sleep(0.02)
    return events


def _has_type(message_type):
    return lambda events: any(event.get("type") == message_type for event in events)


def _all_ready(events, count):
    for event in reversed(events):
        if event.get("type") != "lobby_state":
            continue
        players = event.get("players", [])
        return len(players) == count and all(player.get("ready") for player in players)
    return False


class LanLobbyIntegrationTests(unittest.TestCase):
    def test_two_players_can_ready_and_start(self):
        port = _free_tcp_port()
        server = LanLobbyServer(host="127.0.0.1", port=port)
        first = LanClient()
        second = LanClient()
        try:
            server.start(background=True)
            first.connect("127.0.0.1", "Aldric", port)
            second.connect("127.0.0.1", "Selena", port)

            first_events = _collect_until(first, _has_type("welcome"))
            second_events = _collect_until(second, _has_type("welcome"))
            self.assertTrue(any(event.get("type") == "welcome" for event in first_events))
            self.assertTrue(any(event.get("type") == "welcome" for event in second_events))
            self.assertTrue(first.is_host)
            self.assertFalse(second.is_host)

            first.set_ready(True)
            second.set_ready(True)
            first_ready = _collect_until(first, lambda events: _all_ready(events, 2))
            second_ready = _collect_until(second, lambda events: _all_ready(events, 2))
            self.assertTrue(_all_ready(first_ready, 2))
            self.assertTrue(_all_ready(second_ready, 2))

            first.start_game()
            first_start = _collect_until(first, _has_type("game_start"))
            second_start = _collect_until(second, _has_type("game_start"))
            self.assertTrue(any(event.get("type") == "game_start" for event in first_start))
            self.assertTrue(any(event.get("type") == "game_start" for event in second_start))
            self.assertEqual(server.player_count, 2)
        finally:
            first.close()
            second.close()
            server.stop()


if __name__ == "__main__":
    unittest.main()
