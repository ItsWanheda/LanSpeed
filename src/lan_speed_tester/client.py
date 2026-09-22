"""
LAN Speed Tester client.

Connects to a LAN Speed Tester server and measures:

    - TCP connection latency
    - Download throughput
    - Upload throughput

The implementation uses only Python's standard library.
"""

from __future__ import annotations

import socket
import time
from dataclasses import dataclass
from typing import Callable, Optional

from .metrics import (
    LatencyMetrics,
    SpeedTestResult,
    TransferMetrics,
)

from .protocol import (
    COMMAND_LATENCY,
    MAX_TRANSFER_CHUNK,
    RESPONSE_DONE,
    RESPONSE_OK,
    RESPONSE_READY,
    ProtocolError,
    expect_response,
    recv_exact,
    send_download_request,
    send_hello,
    send_latency_request,
    send_quit,
    send_transfer_done,
    send_upload_request,
)


DEFAULT_PORT = 8765
DEFAULT_DURATION = 10.0
DEFAULT_CHUNK_SIZE = 1024 * 1024
DEFAULT_SOCKET_TIMEOUT = 5.0


class ClientConfig:
    """Configuration for the LAN speed test client."""

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        duration: float = DEFAULT_DURATION,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        timeout: float = DEFAULT_SOCKET_TIMEOUT,
    ) -> None:
        self.host = host
        self.port = port
        self.duration = duration
        self.chunk_size = chunk_size
        self.timeout = timeout

    def validate(self) -> None:
        """Validate client configuration."""

        if not self.host:
            raise ValueError(
                "host is required"
            )

        if not 1 <= self.port <= 65535:
            raise ValueError(
                "port must be between 1 and 65535"
            )

        if self.duration <= 0:
            raise ValueError(
                "duration must be greater than zero"
            )

        if self.chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero"
            )

        if self.chunk_size > MAX_TRANSFER_CHUNK:
            raise ValueError(
                "chunk_size is too large"
            )

        if self.timeout <= 0:
            raise ValueError(
                "timeout must be greater than zero"
            )


class LANSpeedClient:
    """Client for the LAN Speed Tester TCP server."""

    def __init__(
        self,
        config: ClientConfig,
    ) -> None:
        config.validate()

        self.config = config
        self._socket: Optional[
            socket.socket
        ] = None

    def connect(self) -> None:
        """Connect and perform handshake."""

        if self._socket is not None:
            return

        sock = socket.create_connection(
            (
                self.config.host,
                self.config.port,
            ),
            timeout=self.config.timeout,
        )

        try:
            sock.settimeout(
                self.config.timeout
            )

            send_hello(sock)

            self._socket = sock

        except Exception:
            sock.close()
            raise

    def close(self) -> None:
        """Close the client connection."""

        sock = self._socket
        self._socket = None

        if sock is None:
            return

        try:
            send_quit(sock)
        except (
            ConnectionError,
            OSError,
        ):
            pass
        finally:
            sock.close()

    def __enter__(
        self,
    ) -> "LANSpeedClient":
        self.connect()
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        self.close()

    @property
    def socket(self) -> socket.socket:
        """Return the active socket."""

        if self._socket is None:
            raise ConnectionError(
                "Client is not connected"
            )

        return self._socket

    def measure_latency(self) -> LatencyMetrics:
        sock = self.socket
        sock.settimeout(self.config.timeout)

        start = time.perf_counter()

        send_latency_request(sock)

        response = expect_response(
            sock,
            RESPONSE_OK,
        )

        elapsed = (
            time.perf_counter() - start
        )

        if response.data.get("type") not in (
            None,
            "latency",
        ):
            raise ProtocolError(
                "Unexpected latency response"
            )

        return LatencyMetrics.from_seconds(
            elapsed
        )

    def download(
        self,
        duration: Optional[float] = None,
        progress_callback: Optional[
            Callable[[int, float], None]
        ] = None,
    ) -> TransferMetrics:
        """Download data from the LAN server."""

        sock = self.socket

        duration = (
            self.config.duration
            if duration is None
            else duration
        )

        if duration <= 0:
            raise ValueError(
                "duration must be greater than zero"
            )

        send_download_request(
            sock,
            duration,
            self.config.chunk_size,
        )

        response = expect_response(
            sock,
            RESPONSE_READY,
        )

        if response.data.get("type") not in (
            None,
            "download",
        ):
            raise ProtocolError(
                "Unexpected download response"
            )

        total_bytes = 0

        start = time.perf_counter()

        while True:
            header = recv_exact(
                sock,
                4,
            )

            chunk_size = int.from_bytes(
                header,
                byteorder="big",
                signed=False,
            )

            if chunk_size == 0:
                break

            if chunk_size > MAX_TRANSFER_CHUNK:
                raise ProtocolError(
                    "Server sent an oversized "
                    "download chunk"
                )

            data = recv_exact(
                sock,
                chunk_size,
            )

            total_bytes += len(data)

            elapsed = (
                time.perf_counter()
                - start
            )

            if progress_callback is not None:
                progress_callback(
                    total_bytes,
                    elapsed,
                )

        elapsed = (
            time.perf_counter() - start
        )

        if elapsed <= 0:
            elapsed = 1e-9

        return TransferMetrics.from_transfer(
            direction="download",
            bytes_transferred=total_bytes,
            elapsed_seconds=elapsed,
        )

    def upload(
        self,
        duration: Optional[float] = None,
        progress_callback: Optional[
            Callable[[int, float], None]
        ] = None,
    ) -> TransferMetrics:
        """
        Upload generated data.

        Upload chunks are length-prefixed so the
        server can distinguish transfer data from
        control messages.
        """

        sock = self.socket

        duration = (
            self.config.duration
            if duration is None
            else duration
        )

        if duration <= 0:
            raise ValueError(
                "duration must be greater than zero"
            )

        send_upload_request(
            sock,
            duration,
            self.config.chunk_size,
        )

        response = expect_response(
            sock,
            RESPONSE_READY,
        )

        if response.data.get("type") not in (
            None,
            "upload",
        ):
            raise ProtocolError(
                "Unexpected upload response"
            )

        payload = (
            b"\x00"
            * self.config.chunk_size
        )

        total_bytes = 0

        start = time.perf_counter()

        sock.settimeout(
            max(
                self.config.timeout,
                duration
                + self.config.timeout,
            )
        )

        while True:
            elapsed = (
                time.perf_counter()
                - start
            )

            if elapsed >= duration:
                break

            chunk_size = len(payload)

            sock.sendall(
                chunk_size.to_bytes(
                    4,
                    byteorder="big",
                    signed=False,
                )
            )

            sock.sendall(payload)

            total_bytes += chunk_size

            elapsed = (
                time.perf_counter()
                - start
            )

            if progress_callback is not None:
                progress_callback(
                    total_bytes,
                    elapsed,
                )

        # Zero-length chunk marks the end
        # of the raw upload stream.
        sock.sendall(
            (0).to_bytes(
                4,
                byteorder="big",
                signed=False,
            )
        )

        # Now send the control-level DONE.
        send_transfer_done(
            sock,
            total_bytes,
        )

        response = expect_response(
            sock,
            RESPONSE_DONE,
        )

        elapsed = (
            time.perf_counter()
            - start
        )

        if elapsed <= 0:
            elapsed = 1e-9

        server_bytes = response.data.get(
            "bytes"
        )

        if server_bytes is not None:
            try:
                server_bytes = int(
                    server_bytes
                )
            except (
                TypeError,
                ValueError,
            ):
                server_bytes = None

        _ = server_bytes

        return TransferMetrics.from_transfer(
            direction="upload",
            bytes_transferred=total_bytes,
            elapsed_seconds=elapsed,
        )

    def run(
        self,
        duration: Optional[float] = None,
        progress_callback: Optional[
            Callable[[str, int, float], None]
        ] = None,
    ) -> SpeedTestResult:
        """Run the complete speed test."""

        duration = (
            self.config.duration
            if duration is None
            else duration
        )

        if duration <= 0:
            raise ValueError(
                "duration must be greater than zero"
            )

        if self._socket is None:
            self.connect()

        latency = self.measure_latency()

        def transfer_progress(
            direction: str,
            bytes_transferred: int,
            elapsed_seconds: float,
        ) -> None:
            if progress_callback is not None:
                progress_callback(
                    direction,
                    bytes_transferred,
                    elapsed_seconds,
                )

        download = self.download(
            duration=duration,
            progress_callback=(
                lambda total, elapsed:
                transfer_progress(
                    "download",
                    total,
                    elapsed,
                )
            ),
        )

        upload = self.upload(
            duration=duration,
            progress_callback=(
                lambda total, elapsed:
                transfer_progress(
                    "upload",
                    total,
                    elapsed,
                )
            ),
        )

        return SpeedTestResult(
            host=self.config.host,
            port=self.config.port,
            duration_seconds=duration,
            latency=latency,
            download=download,
            upload=upload,
        )


def run_speed_test(
    host: str,
    port: int = DEFAULT_PORT,
    duration: float = DEFAULT_DURATION,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    timeout: float = DEFAULT_SOCKET_TIMEOUT,
) -> SpeedTestResult:
    """Convenience function for a complete speed test."""

    config = ClientConfig(
        host=host,
        port=port,
        duration=duration,
        chunk_size=chunk_size,
        timeout=timeout,
    )

    with LANSpeedClient(config) as client:
        return client.run()