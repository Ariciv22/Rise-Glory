import rg_engine.quests as quests
import rg_world
import rg_world.generation as generation
from rg_engine.quest_world_bridge import install_quest_world_bridge


def test_failed_world_attempt_does_not_drain_quest_reservations(monkeypatch):
    attempts = []

    def fake_try_generate_world(map_key, rng):
        _ = (map_key, rng)
        attempts.append(set(quests._RESERVED_OFFERS))
        if len(attempts) == 1:
            quests._RESERVED_OFFERS.add("leaked-from-failed-attempt")
            return None
        return ["generated-world"]

    monkeypatch.setattr(generation, "_try_generate_world", fake_try_generate_world)
    quests._RESERVED_OFFERS.add("stale-from-previous-world")

    install_quest_world_bridge()
    result = rg_world.generate_world("test-map")

    assert result == ["generated-world"]
    assert attempts == [set(), set()]
