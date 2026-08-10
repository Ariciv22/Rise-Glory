"""Warstwa sieciowa Rise & Glory.

Pierwszy etap obsluguje lobby w lokalnej sieci LAN. Kod nie zalezy od Pygame,
dzieki czemu ten sam transport bedzie mozna pozniej wykorzystac przez Internet.
"""

from rg_network.lan_client import LanClient
from rg_network.lan_server import LanLobbyServer, get_lan_ipv4
from rg_network.protocol import DEFAULT_PORT, PROTOCOL_VERSION

__all__ = [
    "DEFAULT_PORT",
    "PROTOCOL_VERSION",
    "LanClient",
    "LanLobbyServer",
    "get_lan_ipv4",
]
