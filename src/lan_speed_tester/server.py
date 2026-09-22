"""
LAN Speed Tester server.

Implements the LANSpeed TCP protocol with:

    - framed JSON control messages
    - framed download data
    - framed upload data

Protocol:
    Control:
        [4-byte big-endian length][JSON]

    Transfer:
        [4-byte big-endian chunk length][chunk]
        ...
        [4-byte zero length]  <- end of transfer
"""

from __future__ import annotations

import socket
import threading
from typing import Optional

from .protocol import (
    COMMAND_DOWNLOAD,
    COMMAND_HELLO,
    COMMAND_LATENCY,
    COMMAND_QUIT,
    COMMAND_UPLOAD,
    MAX_TRANSFER_CHUNK,
    ProtocolError,
    RESPONSE_DONE,
    RESPONSE_ERROR,
    RESPONSE_OK,
    RESPONSE_READY,
    recv_control,
    recv_exact,
    send_control,
)


DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8765
DEFAULT_CHUNK_SIZE = 1024 * 1024
SOCKET_TIMEOUT = 30.0


class LANSpeedServer:
    """LAN Speed Tester TCP server."""

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> None:
        if not 1 <= port <= 65535:
            raise ValueError("port must be between 1 and 65535")

        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        if chunk_size > MAX_TRANSFER_CHUNK:
            raise ValueError("chunk_size is too large")

        self.host = host
        self.port = port
        self.chunk_size = chunk_size

        self._server_socket: Optional[socket.socket] = None
        self._running = False

    def start(self) -> None:
        """Start accepting client connections."""

        server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1,
        )

        server_socket.bind((self.host, self.port))
        server_socket.listen(16)
        server_socket.settimeout(1.0)

        self._server_socket = server_socket
        self._running = True

        print(
            f"LANSpeed server listening on "
            f"{self.host}:{self.port}"
        )
        print("Press Ctrl+C to stop.")

        try:
            while self._running:
                try:
                    conn, address = server_socket.accept()
                except socket.timeout:
                    continue
                except OSError:
                    if self._running:
                        raise
                    break

                thread = threading.Thread(
                    target=self.handle_client,
                    args=(conn, address),
                    daemon=True,
                )

                thread.start()

        except KeyboardInterrupt:
            print("\nStopping server...")

        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the server."""

        self._running = False

        server_socket = self._server_socket
        self._server_socket = None

        if server_socket is not None:
            try:
                server_socket.close()
            except OSError:
                pass

    def handle_client(
        self,
        conn: socket.socket,
        address,
    ) -> None:
        """Handle one client connection."""

        peer = address

        print(f"[+] Client connected: {peer}")

        conn.settimeout(SOCKET_TIMEOUT)

        try:
            while True:
                message = recv_control(conn)

                print(
                    f"[{peer}] "
                    f"{message.command} "
                    f"{message.data}"
                )

                if message.command == COMMAND_HELLO:
                    self.handle_hello(conn)

                elif message.command == COMMAND_LATENCY:
                    self.handle_latency(conn)

                elif message.command == COMMAND_DOWNLOAD:
                    self.handle_download(
                        conn,
                        message.data,
                    )

                elif message.command == COMMAND_UPLOAD:
                    self.handle_upload(
                        conn,
                        message.data,
                    )

                elif message.command == COMMAND_QUIT:
                    send_control(
                        conn,
                        RESPONSE_OK,
                    )
                    break

                else:
                    send_control(
                        conn,
                        RESPONSE_ERROR,
                        {
                            "message": (
                                f"Unknown command: "
                                f"{message.command}"
                            )
                        },
                    )

        except (ConnectionError, socket.timeout):
            pass

        except (OSError, ProtocolError) as exc:
            print(
                f"[!] Connection error from "
                f"{peer}: {exc}"
            )

        finally:
            try:
                conn.close()
            except OSError:
                pass

            print(f"[-] Connection closed: {peer}")

    @staticmethod
    def handle_hello(
        conn: socket.socket,
    ) -> None:
        """Handle HELLO."""

        send_control(
            conn,
            RESPONSE_OK,
            {
                "type": "hello",
            },
        )

    @staticmethod
    def handle_latency(
        conn: socket.socket,
    ) -> None:
        """Handle latency request."""

        send_control(
            conn,
            RESPONSE_OK,
            {
                "type": "latency",
            },
        )

    def handle_download(
        self,
        conn: socket.socket,
        data: dict,
    ) -> None:
        """Send framed download data."""

        duration = float(
            data.get("duration", 0)
        )

        chunk_size = int(
            data.get(
                "chunk_size",
                self.chunk_size,
            )
        )

        if duration <= 0:
            raise ProtocolError(
                "Invalid download duration"
            )

        if not 0 < chunk_size <= MAX_TRANSFER_CHUNK:
            raise ProtocolError(
                "Invalid download chunk size"
            )

        send_control(
            conn,
            RESPONSE_READY,
            {
                "type": "download",
                "chunk_size": chunk_size,
            },
        )

        payload = b"\x00" * chunk_size

        import time

        start = time.perf_counter()

        while (
            time.perf_counter() - start
            < duration
        ):
            conn.sendall(
                len(payload).to_bytes(
                    4,
                    byteorder="big",
                    signed=False,
                )
            )

            conn.sendall(payload)

        # End-of-transfer marker.
        conn.sendall(
            (0).to_bytes(
                4,
                byteorder="big",
                signed=False,
            )
        )

    def handle_upload(
        self,
        conn: socket.socket,
        data: dict,
    ) -> None:
        """
        Receive framed upload data.

        Each chunk is:

            [4-byte length][data]

        The transfer ends with:

            [4-byte zero]

        After the zero marker the client sends
        the normal framed DONE control message.
        """

        duration = float(
            data.get("duration", 0)
        )

        if duration <= 0:
            raise ProtocolError(
                "Invalid upload duration"
            )

        send_control(
            conn,
            RESPONSE_READY,
            {
                "type": "upload",
            },
        )

        total_bytes = 0

        while True:
            raw_size = recv_exact(
                conn,
                4,
            )

            chunk_size = int.from_bytes(
                raw_size,
                byteorder="big",
                signed=False,
            )

            # Zero-length chunk terminates
            # the raw upload stream.
            if chunk_size == 0:
                break

            if chunk_size > MAX_TRANSFER_CHUNK:
                raise ProtocolError(
                    "Client sent an oversized upload chunk"
                )

            chunk = recv_exact(
                conn,
                chunk_size,
            )

            total_bytes += len(chunk)

        # The raw upload stream is finished.
        #
        # NOW read the framed DONE control message.
        done_message = recv_control(conn)

        if done_message.command != RESPONSE_DONE:
            raise ProtocolError(
                "Expected DONE after upload"
            )

        client_bytes = done_message.data.get(
            "bytes"
        )

        if client_bytes is not None:
            try:
                client_bytes = int(client_bytes)
            except (TypeError, ValueError):
                client_bytes = None

        print(
            f"Upload complete: "
            f"{total_bytes:,} bytes"
        )

        send_control(
            conn,
            RESPONSE_DONE,
            {
                "type": "upload",
                "bytes": total_bytes,
            },
        )


def run_server(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
) -> None:
    """Run the LANSpeed server."""

    server = LANSpeedServer(
        host=host,
        port=port,
    )

    server.start()