"""Warstwa sieciowa Rise & Glory.

Pierwszy etap obsluguje lobby i wspolna rozgrywke w lokalnej sieci LAN.
Transport oraz autorytatywny stan gry sa oddzielone od Pygame, aby ten sam
model klient-serwer mozna bylo pozniej wystawic przez Internet.
"""

from rg_network.game_state import NetworkGameSession
from rg_network.lan_client import LanClient
from rg_network.lan_server import LanLobbyServer, get_lan_ipv4
from rg_network.protocol import DEFAULT_PORT, PROTOCOL_VERSION

__all__ = [
    "DEFAULT_PORT",
    "PROTOCOL_VERSION",
    "LanClient",
    "LanLobbyServer",
    "NetworkGameSession",
    "get_lan_ipv4",
]
