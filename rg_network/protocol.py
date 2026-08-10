from __future__ import annotations

import json
from typing import Any

PROTOCOL_VERSION = 1
DEFAULT_PORT = 27840
MAX_MESSAGE_BYTES = 64 * 1024


def make_message(message_type: str, **payload: Any) -> dict[str, Any]:
    return {
        "type": str(message_type),
        "protocol": PROTOCOL_VERSION,
        **payload,
    }


def encode_message(message: dict[str, Any]) -> bytes:
    raw = json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(raw) > MAX_MESSAGE_BYTES:
        raise ValueError("Wiadomosc sieciowa jest zbyt duza.")
    return raw + b"\n"


class MessageBuffer:
    """Dekoder wiadomosci JSON rozdzielonych znakiem nowej linii."""

    def __init__(self) -> None:
        self._buffer = bytearray()

    def feed(self, data: bytes) -> list[dict[str, Any]]:
        if data:
            self._buffer.extend(data)
        if len(self._buffer) > MAX_MESSAGE_BYTES * 4:
            raise ValueError("Bufor sieciowy przekroczyl dozwolony rozmiar.")

        messages: list[dict[str, Any]] = []
        while True:
            newline_index = self._buffer.find(b"\n")
            if newline_index < 0:
                break
            raw = bytes(self._buffer[:newline_index])
            del self._buffer[: newline_index + 1]
            if not raw:
                continue
            if len(raw) > MAX_MESSAGE_BYTES:
                raise ValueError("Wiadomosc sieciowa jest zbyt duza.")
            decoded = json.loads(raw.decode("utf-8"))
            if not isinstance(decoded, dict):
                raise ValueError("Wiadomosc sieciowa musi byc obiektem JSON.")
            messages.append(decoded)
        return messages
