"""UDP echo service and packet-loss / RTT-jitter diagnostics.

The UDP diagnostic protocol is deliberately independent of the existing
length-prefixed TCP protocol. Each probe is a fixed-size, versioned datagram.
"""

from __future__ import annotations

import select
import socket
import struct
import time
from dataclasses import dataclass
from secrets import token_bytes
from threading import Event, Thread

from .diagnostics import LatencyStatistics

UDP_MAGIC = b"LSUD"
UDP_SESSION_BYTES = 8
UDP_HEADER = struct.Struct("!4s8sI")
MAX_UDP_DATAGRAM_SIZE = 1200

DEFAULT_UDP_PROBE_COUNT = 100
DEFAULT_UDP_INTERVAL_SECONDS = 0.02
DEFAULT_UDP_TIMEOUT_SECONDS = 1.0
MAX_UDP_PROBE_COUNT = 10000


class UDPEchoServer:
    """Small UDP responder used by LANSpeed diagnostic clients."""

    def __init__(self, host: str = "0.0.0.0", port: int = 8765) -> None:
        if not 0 <= port <= 65535:
            raise ValueError("UDP port must be between 0 and 65535")
        self.host = host
        self.port = port
        self._socket: socket.socket | None = None
        self._thread: Thread | None = None
        self._stop_event = Event()

    def start(self) -> tuple[str, int]:
        """Bind the UDP endpoint and start its receive thread."""

        if self._thread is not None and self._thread.is_alive():
            raise RuntimeError("UDP echo server is already running")

        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_socket.bind((self.host, self.port))
            udp_socket.settimeout(0.2)
        except OSError:
            udp_socket.close()
            raise

        self._socket = udp_socket
        self.port = int(udp_socket.getsockname()[1])
        self._stop_event.clear()
        self._thread = Thread(
            target=self._serve,
            name="lanspeed-udp",
            daemon=True,
        )
        self._thread.start()
        return self.host, self.port

    def _serve(self) -> None:
        udp_socket = self._socket
        if udp_socket is None:
            return

        while not self._stop_event.is_set():
            try:
                payload, address = udp_socket.recvfrom(
                    MAX_UDP_DATAGRAM_SIZE + 1
                )
            except socket.timeout:
                continue
            except OSError:
                if self._stop_event.is_set():
                    break
                continue

            if len(payload) != UDP_HEADER.size:
                continue

            try:
                magic, _session, _sequence = UDP_HEADER.unpack(payload)
            except struct.error:
                continue

            if magic != UDP_MAGIC:
                continue

            try:
                udp_socket.sendto(payload, address)
            except OSError:
                if self._stop_event.is_set():
                    break

    def stop(self) -> None:
        """Stop the responder and release its socket."""

        self._stop_event.set()
        udp_socket = self._socket
        self._socket = None

        if udp_socket is not None:
            try:
                udp_socket.close()
            except OSError:
                pass

        thread = self._thread
        self._thread = None
        if thread is not None and thread.is_alive():
            thread.join(timeout=1.0)

    def __enter__(self) -> "UDPEchoServer":
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.stop()


@dataclass(frozen=True, slots=True)
class UDPTestResult:
    """Result of a UDP probe run."""

    host: str
    port: int
    packets_sent: int
    packets_received: int
    packets_lost: int
    packet_loss_percent: float
    latency: LatencyStatistics | None
    duration_seconds: float

    @property
    def jitter_ms(self) -> float | None:
        """Return RTT jitter, or None when no probes were received."""

        return self.latency.jitter_ms if self.latency is not None else None

    def to_dict(self) -> dict:
        """Return a JSON-serializable result."""

        return {
            "host": self.host,
            "port": self.port,
            "protocol": "udp",
            "packets_sent": self.packets_sent,
            "packets_received": self.packets_received,
            "packets_lost": self.packets_lost,
            "packet_loss_percent": round(self.packet_loss_percent, 3),
            "latency": self.latency.to_dict() if self.latency else None,
            "jitter_ms": (
                round(self.jitter_ms, 3)
                if self.jitter_ms is not None
                else None
            ),
            "duration_seconds": round(self.duration_seconds, 3),
        }


def run_udp_probe_test(
    host: str,
    port: int = 8765,
    probe_count: int = DEFAULT_UDP_PROBE_COUNT,
    interval_seconds: float = DEFAULT_UDP_INTERVAL_SECONDS,
    timeout_seconds: float = DEFAULT_UDP_TIMEOUT_SECONDS,
) -> UDPTestResult:
    """Send paced UDP probes and calculate loss, RTT statistics, and jitter.

    Jitter is the mean absolute difference between consecutive successful
    RTT measurements ordered by probe sequence number. This is an RTT
    variation metric, not one-way RTP jitter.
    """

    if not host:
        raise ValueError("host is required")
    if not 1 <= port <= 65535:
        raise ValueError("port must be between 1 and 65535")
    if not 1 <= probe_count <= MAX_UDP_PROBE_COUNT:
        raise ValueError(
            f"probe_count must be between 1 and {MAX_UDP_PROBE_COUNT}"
        )
    if not 0 < interval_seconds <= 10:
        raise ValueError("interval_seconds must be greater than 0 and at most 10")
    if not 0.05 <= timeout_seconds <= 30:
        raise ValueError("timeout_seconds must be between 0.05 and 30")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((host, port))
    sock.setblocking(False)

    session = token_bytes(UDP_SESSION_BYTES)
    sent_at: dict[int, float] = {}
    received_rtt: dict[int, float] = {}
    started_at = time.perf_counter()
    next_send_at = started_at
    final_deadline: float | None = None
    sequence = 0

    try:
        while sequence < probe_count or (
            final_deadline is not None
            and time.perf_counter() < final_deadline
        ):
            now = time.perf_counter()

            if sequence < probe_count and now >= next_send_at:
                payload = UDP_HEADER.pack(UDP_MAGIC, session, sequence)
                sock.send(payload)
                sent_at[sequence] = time.perf_counter()
                sequence += 1

                if sequence == probe_count:
                    final_deadline = sent_at[sequence - 1] + timeout_seconds
                else:
                    next_send_at = sent_at[sequence - 1] + interval_seconds
                continue

            if sequence < probe_count:
                wake_at = next_send_at
            else:
                wake_at = final_deadline

            if wake_at is None:
                break

            wait_seconds = max(0.0, min(0.05, wake_at - now))
            readable, _, _ = select.select([sock], [], [], wait_seconds)

            if not readable:
                continue

            while True:
                try:
                    payload = sock.recv(MAX_UDP_DATAGRAM_SIZE + 1)
                except BlockingIOError:
                    break

                if len(payload) != UDP_HEADER.size:
                    continue

                try:
                    magic, response_session, response_sequence = (
                        UDP_HEADER.unpack(payload)
                    )
                except struct.error:
                    continue

                if (
                    magic != UDP_MAGIC
                    or response_session != session
                    or response_sequence not in sent_at
                    or response_sequence in received_rtt
                ):
                    continue

                received_at = time.perf_counter()
                rtt_ms = (received_at - sent_at[response_sequence]) * 1000.0
                if rtt_ms <= timeout_seconds * 1000.0:
                    received_rtt[response_sequence] = rtt_ms

    finally:
        sock.close()

    ordered_samples = [
        received_rtt[index]
        for index in sorted(received_rtt)
    ]
    packets_received = len(ordered_samples)
    packets_lost = probe_count - packets_received

    return UDPTestResult(
        host=host,
        port=port,
        packets_sent=probe_count,
        packets_received=packets_received,
        packets_lost=packets_lost,
        packet_loss_percent=(packets_lost / probe_count) * 100.0,
        latency=(
            LatencyStatistics.from_samples(ordered_samples)
            if ordered_samples
            else None
        ),
        duration_seconds=time.perf_counter() - started_at,
    )
