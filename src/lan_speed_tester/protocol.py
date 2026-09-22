"""
TCP protocol used by LAN Speed Tester.

The protocol is intentionally simple and dependency-free.

Control messages:
    [4-byte big-endian payload length]
    [JSON payload]

Client -> Server:
    HELLO
    LATENCY
    DOWNLOAD
    UPLOAD
    QUIT
    DONE

Server -> Client:
    OK
    READY
    DONE
    ERROR

Transfer framing:

DOWNLOAD:
    [4-byte chunk length]
    [chunk data]
    ...
    [4-byte zero]

UPLOAD:
    [4-byte chunk length]
    [chunk data]
    ...
    [4-byte zero]
    DONE control message
"""

from __future__ import annotations

import json
import socket
import struct
from dataclasses import dataclass
from typing import Any


PROTOCOL_VERSION = 1

COMMAND_HELLO = "HELLO"
COMMAND_LATENCY = "LATENCY"
COMMAND_DOWNLOAD = "DOWNLOAD"
COMMAND_UPLOAD = "UPLOAD"
COMMAND_QUIT = "QUIT"

RESPONSE_OK = "OK"
RESPONSE_ERROR = "ERROR"
RESPONSE_READY = "READY"
RESPONSE_DONE = "DONE"

HEADER_SIZE = 4
MAX_CONTROL_MESSAGE = 64 * 1024
MAX_TRANSFER_CHUNK = 16 * 1024 * 1024


class ProtocolError(Exception):
    """Raised when a protocol operation fails."""


@dataclass(slots=True)
class ControlMessage:
    """A JSON control message."""

    command: str
    data: dict[str, Any]

    def encode(self) -> bytes:
        """Encode the message into a length-prefixed payload."""

        payload = json.dumps(
            {
                "version": PROTOCOL_VERSION,
                "command": self.command,
                "data": self.data,
            },
            separators=(",", ":"),
        ).encode("utf-8")

        if len(payload) > MAX_CONTROL_MESSAGE:
            raise ProtocolError(
                "Control message is too large"
            )

        return struct.pack(
            "!I",
            len(payload),
        ) + payload

    @classmethod
    def decode(
        cls,
        payload: bytes,
    ) -> "ControlMessage":
        """Decode a JSON control message."""

        try:
            message = json.loads(
                payload.decode("utf-8")
            )
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:
            raise ProtocolError(
                "Invalid control message"
            ) from exc

        if not isinstance(message, dict):
            raise ProtocolError(
                "Control message must be an object"
            )

        version = message.get("version")

        if version != PROTOCOL_VERSION:
            raise ProtocolError(
                f"Unsupported protocol version: {version}"
            )

        command = message.get("command")
        data = message.get("data", {})

        if not isinstance(command, str):
            raise ProtocolError(
                "Missing or invalid command"
            )

        if not isinstance(data, dict):
            raise ProtocolError(
                "Message data must be an object"
            )

        return cls(
            command=command,
            data=data,
        )


def recv_exact(
    sock: socket.socket,
    size: int,
) -> bytes:
    """
    Receive exactly `size` bytes from a socket.

    Raises:
        ConnectionError:
            If the peer closes the connection.
    """

    if size < 0:
        raise ValueError(
            "size must not be negative"
        )

    if size == 0:
        return b""

    chunks = bytearray()

    while len(chunks) < size:
        chunk = sock.recv(
            size - len(chunks)
        )

        if not chunk:
            raise ConnectionError(
                "Connection closed while receiving data"
            )

        chunks.extend(chunk)

    return bytes(chunks)


def send_control(
    sock: socket.socket,
    command: str,
    data: dict[str, Any] | None = None,
) -> None:
    """Send a control message."""

    message = ControlMessage(
        command=command,
        data=data or {},
    )

    sock.sendall(
        message.encode()
    )


def recv_control(
    sock: socket.socket,
) -> ControlMessage:
    """Receive a control message."""

    raw_size = recv_exact(
        sock,
        HEADER_SIZE,
    )

    message_size = struct.unpack(
        "!I",
        raw_size,
    )[0]

    if message_size <= 0:
        raise ProtocolError(
            "Invalid control message size"
        )

    if message_size > MAX_CONTROL_MESSAGE:
        raise ProtocolError(
            "Control message is too large"
        )

    payload = recv_exact(
        sock,
        message_size,
    )

    return ControlMessage.decode(
        payload
    )


def expect_response(
    sock: socket.socket,
    expected: str | tuple[str, ...],
) -> ControlMessage:
    """
    Receive a response and ensure
    its command matches.
    """

    message = recv_control(sock)

    expected_commands = (
        (expected,)
        if isinstance(expected, str)
        else expected
    )

    if message.command not in expected_commands:
        raise ProtocolError(
            f"Expected {expected_commands}, "
            f"received {message.command}"
        )

    return message


def send_hello(
    sock: socket.socket,
    client_name: str = "lan-speed-tester",
) -> ControlMessage:
    """Perform the protocol handshake."""

    send_control(
        sock,
        COMMAND_HELLO,
        {
            "client": client_name,
            "protocol_version": PROTOCOL_VERSION,
        },
    )

    return expect_response(
        sock,
        RESPONSE_OK,
    )


def send_quit(
    sock: socket.socket,
) -> None:
    """Tell the server that the client is disconnecting."""

    try:
        send_control(
            sock,
            COMMAND_QUIT,
        )
    except (
        ConnectionError,
        OSError,
    ):
        # Connection may already be closed.
        pass


def send_latency_request(
    sock: socket.socket,
) -> None:
    """Request a latency measurement."""

    send_control(
        sock,
        COMMAND_LATENCY,
    )


def send_download_request(
    sock: socket.socket,
    duration_seconds: float,
    chunk_size: int,
) -> None:
    """Request a download stream."""

    if duration_seconds <= 0:
        raise ValueError(
            "duration_seconds must be greater than zero"
        )

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than zero"
        )

    if chunk_size > MAX_TRANSFER_CHUNK:
        raise ValueError(
            "chunk_size is too large"
        )

    send_control(
        sock,
        COMMAND_DOWNLOAD,
        {
            "duration": duration_seconds,
            "chunk_size": chunk_size,
        },
    )


def send_upload_request(
    sock: socket.socket,
    duration_seconds: float,
    chunk_size: int,
) -> None:
    """Request an upload receiver."""

    if duration_seconds <= 0:
        raise ValueError(
            "duration_seconds must be greater than zero"
        )

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than zero"
        )

    if chunk_size > MAX_TRANSFER_CHUNK:
        raise ValueError(
            "chunk_size is too large"
        )

    send_control(
        sock,
        COMMAND_UPLOAD,
        {
            "duration": duration_seconds,
            "chunk_size": chunk_size,
        },
    )


def send_transfer_done(
    sock: socket.socket,
    bytes_transferred: int,
) -> None:
    """Send the client-side upload completion message."""

    if bytes_transferred < 0:
        raise ValueError(
            "bytes_transferred must not be negative"
        )

    send_control(
        sock,
        RESPONSE_DONE,
        {
            "bytes": bytes_transferred,
        },
    )