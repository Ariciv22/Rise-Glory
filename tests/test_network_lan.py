import math
import socket
import time
import unittest

from rg_core.data import HEX_SIZE, TERRAINS
from rg_network.lan_client import LanClient
from rg_network.lan_server import LanLobbyServer


def _free_tcp_port():
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()
    return port


def _collect_until(client, predicate, timeout=3.0):
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


def _latest(events, message_type):
    return next((event for event in reversed(events) if event.get("type") == message_type), None)


def _all_ready(events, count):
    for event in reversed(events):
        if event.get("type") != "lobby_state":
            continue
        players = event.get("players", [])
        return (
            len(players) == count
            and all(player.get("archetype_id") for player in players)
            and all(player.get("ready") for player in players)
        )
    return False


def _find_legal_target(snapshot, player_index):
    token = next(item for item in snapshot["tokens"] if int(item["player_index"]) == int(player_index))
    current = next(item for item in snapshot["tiles"] if int(item["id"]) == int(token["tile_id"]))
    for tile in snapshot["tiles"]:
        if int(tile["id"]) == int(current["id"]):
            continue
        terrain = TERRAINS[tile["terrain_key"]]
        if not terrain["passable"]:
            continue
        distance = math.hypot(float(tile["x"]) - float(current["x"]), float(tile["y"]) - float(current["y"]))
        cost = int(terrain.get("move", 1) or 1)
        if distance <= HEX_SIZE * 1.85 and cost <= int(token["actions"]):
            return int(tile["id"])
    return None


class LanLobbyIntegrationTests(unittest.TestCase):
    def test_two_players_can_start_move_and_change_turn(self):
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

            first.configure_hero(1)
            second.configure_hero(6)
            _collect_until(first, _has_type("lobby_state"))
            _collect_until(second, _has_type("lobby_state"))

            first.set_ready(True)
            second.set_ready(True)
            first_ready = _collect_until(first, lambda events: _all_ready(events, 2))
            second_ready = _collect_until(second, lambda events: _all_ready(events, 2))
            self.assertTrue(_all_ready(first_ready, 2))
            self.assertTrue(_all_ready(second_ready, 2))

            first.start_game()
            first_start_events = _collect_until(first, _has_type("game_start"))
            second_start_events = _collect_until(second, _has_type("game_start"))
            first_start = _latest(first_start_events, "game_start")
            second_start = _latest(second_start_events, "game_start")
            self.assertIsNotNone(first_start)
            self.assertIsNotNone(second_start)
            self.assertEqual(first_start["snapshot"], second_start["snapshot"])
            self.assertEqual(server.player_count, 2)

            snapshot = first_start["snapshot"]
            active_index = int(snapshot["turn"]["active_player_index"])
            active_network_id = snapshot["players"][active_index]["network_player_id"]
            active_client = first if first.player_id == active_network_id else second
            passive_client = second if active_client is first else first
            target_tile_id = _find_legal_target(snapshot, active_index)
            self.assertIsNotNone(target_tile_id)

            active_client.request_move(target_tile_id)
            active_move_events = _collect_until(active_client, _has_type("game_state"))
            passive_move_events = _collect_until(passive_client, _has_type("game_state"))
            active_state = _latest(active_move_events, "game_state")["snapshot"]
            passive_state = _latest(passive_move_events, "game_state")["snapshot"]
            self.assertEqual(active_state, passive_state)
            moved_token = next(item for item in active_state["tokens"] if int(item["player_index"]) == active_index)
            self.assertEqual(int(moved_token["tile_id"]), int(target_tile_id))

            previous_active = int(active_state["turn"]["active_player_index"])
            active_client.end_turn()
            turn_events = _collect_until(passive_client, _has_type("game_state"))
            turn_state = _latest(turn_events, "game_state")["snapshot"]
            self.assertNotEqual(int(turn_state["turn"]["active_player_index"]), previous_active)
        finally:
            first.close()
            second.close()
            server.stop()


if __name__ == "__main__":
    unittest.main()
