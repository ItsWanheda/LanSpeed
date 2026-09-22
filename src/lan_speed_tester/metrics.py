"""
Performance metrics for LAN Speed Tester.

This module contains small, dependency-free helpers for measuring and
presenting network performance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


BITS_PER_BYTE = 8
BYTES_PER_KB = 1024
BYTES_PER_MB = 1024 * 1024
BYTES_PER_GB = 1024 * 1024 * 1024


def bytes_to_bits(value: int | float) -> float:
    """Convert bytes to bits."""
    return value * BITS_PER_BYTE


def bits_to_mbps(bits: int | float) -> float:
    """Convert bits per second to megabits per second."""
    return bits / 1_000_000


def bytes_per_second_to_mbps(value: int | float) -> float:
    """Convert bytes per second to megabits per second."""
    return bits_to_mbps(bytes_to_bits(value))


def bytes_per_second_to_mbs(value: int | float) -> float:
    """Convert bytes per second to megabytes per second."""
    return value / 1_000_000


def calculate_throughput(
    transferred_bytes: int,
    elapsed_seconds: float,
) -> float:
    """
    Calculate throughput in megabits per second.

    Args:
        transferred_bytes: Number of bytes transferred.
        elapsed_seconds: Duration of the transfer.

    Returns:
        Throughput in Mbps.

    Raises:
        ValueError: If elapsed_seconds is zero or negative.
    """
    if elapsed_seconds <= 0:
        raise ValueError("elapsed_seconds must be greater than zero")

    return bytes_per_second_to_mbps(
        transferred_bytes / elapsed_seconds
    )


def calculate_latency_ms(elapsed_seconds: float) -> float:
    """
    Convert seconds to milliseconds.
    """
    return elapsed_seconds * 1000.0


def format_mbps(value: float, decimals: int = 2) -> str:
    """Format a Mbps value."""
    return f"{value:.{decimals}f} Mbps"


def format_mbs(value: float, decimals: int = 2) -> str:
    """Format a MB/s value."""
    return f"{value:.{decimals}f} MB/s"


def format_bytes(value: int | float) -> str:
    """
    Format a byte count using human-readable units.
    """
    value = float(value)

    if value >= BYTES_PER_GB:
        return f"{value / BYTES_PER_GB:.2f} GB"

    if value >= BYTES_PER_MB:
        return f"{value / BYTES_PER_MB:.2f} MB"

    if value >= BYTES_PER_KB:
        return f"{value / BYTES_PER_KB:.2f} KB"

    return f"{int(value)} B"


@dataclass(slots=True)
class TransferMetrics:
    """
    Metrics collected for one transfer direction.
    """

    direction: str
    bytes_transferred: int
    elapsed_seconds: float
    throughput_mbps: float
    throughput_mbs: float

    @classmethod
    def from_transfer(
        cls,
        direction: str,
        bytes_transferred: int,
        elapsed_seconds: float,
    ) -> "TransferMetrics":
        """Build metrics from transfer counters."""
        if elapsed_seconds <= 0:
            raise ValueError("elapsed_seconds must be greater than zero")

        bytes_per_second = bytes_transferred / elapsed_seconds

        return cls(
            direction=direction,
            bytes_transferred=bytes_transferred,
            elapsed_seconds=elapsed_seconds,
            throughput_mbps=bytes_per_second_to_mbps(
                bytes_per_second
            ),
            throughput_mbs=bytes_per_second_to_mbs(
                bytes_per_second
            ),
        )

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return {
            "direction": self.direction,
            "bytes_transferred": self.bytes_transferred,
            "elapsed_seconds": round(self.elapsed_seconds, 6),
            "throughput_mbps": round(self.throughput_mbps, 3),
            "throughput_mbs": round(self.throughput_mbs, 3),
        }


@dataclass(slots=True)
class LatencyMetrics:
    """Metrics for TCP connection latency."""

    elapsed_seconds: float
    latency_ms: float

    @classmethod
    def from_seconds(cls, elapsed_seconds: float) -> "LatencyMetrics":
        """Create latency metrics from seconds."""
        return cls(
            elapsed_seconds=elapsed_seconds,
            latency_ms=calculate_latency_ms(elapsed_seconds),
        )

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return {
            "elapsed_seconds": round(self.elapsed_seconds, 6),
            "latency_ms": round(self.latency_ms, 3),
        }


@dataclass(slots=True)
class SpeedTestResult:
    """
    Complete result of a two-way LAN speed test.
    """

    host: str
    port: int
    duration_seconds: float

    latency: Optional[LatencyMetrics] = None
    download: Optional[TransferMetrics] = None
    upload: Optional[TransferMetrics] = None

    def to_dict(self) -> dict:
        """Return a JSON-serializable result."""
        return {
            "host": self.host,
            "port": self.port,
            "duration_seconds": self.duration_seconds,
            "latency": (
                self.latency.to_dict()
                if self.latency is not None
                else None
            ),
            "download": (
                self.download.to_dict()
                if self.download is not None
                else None
            ),
            "upload": (
                self.upload.to_dict()
                if self.upload is not None
                else None
            ),
        }