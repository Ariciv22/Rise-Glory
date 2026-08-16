from __future__ import annotations

_INSTALLED = False


def _tick_player(player: dict, clock: str) -> None:
    from rg_engine.quests import tick_quest_time

    for quest in list(player.get("active_quests", []) or []):
        if quest.get("status") != "active":
            continue
        tick_quest_time(player, quest, clock)


def install_quest_time_bridge() -> None:
    """Podpina jawne limity czasu Questów do realnego zegara partii.

    Instalator powinien być uruchomiony przed warstwami UI blokującymi
    zakończenie tury. Dzięki temu kliknięcie zakończenia tury przy otwartym
    modalu nie przesuwa czasu Questa.
    """
    global _INSTALLED
    if _INSTALLED:
        return

    from rg_engine import turns as turns_module
    from rg_engine.world import registered_players

    original_end_turn = turns_module.TurnManager.end_turn

    def end_turn_with_quest_time(self, tokens):
        current_index = self.active_player_index
        result = original_end_turn(self, tokens)
        players = registered_players()

        if 0 <= current_index < len(players):
            _tick_player(players[current_index], "own_turn")

        if result.get("round_completed"):
            for player in list(players):
                _tick_player(player, "round")

        if result.get("council_due"):
            for player in list(players):
                _tick_player(player, "council")
                _tick_player(player, "until_next_council")

        return result

    turns_module.TurnManager.end_turn = end_turn_with_quest_time
    _INSTALLED = True
