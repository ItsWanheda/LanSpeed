"""Statistical helpers for network diagnostics.

Latency jitter is reported as the mean absolute difference between
consecutive RTT samples, in the order in which probes were measured.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, isfinite
from statistics import mean, median
from typing import Iterable


def calculate_jitter_ms(samples: Iterable[float]) -> float:
    """Return mean absolute variation between consecutive RTT samples."""

    values = tuple(float(sample) for sample in samples)

    if any(not isfinite(value) or value < 0 for value in values):
        raise ValueError("latency samples must be finite and non-negative")

    if len(values) < 2:
        return 0.0

    differences = (
        abs(current - previous)
        for previous, current in zip(values, values[1:])
    )
    return mean(differences)


def _nearest_rank_percentile(values: tuple[float, ...], percentile: float) -> float:
    """Calculate a percentile using the nearest-rank method."""

    rank = max(1, ceil((percentile / 100.0) * len(values)))
    return values[min(rank - 1, len(values) - 1)]


@dataclass(frozen=True, slots=True)
class LatencyStatistics:
    """Descriptive statistics for a sequence of RTT measurements."""

    sample_count: int
    min_ms: float
    max_ms: float
    average_ms: float
    median_ms: float
    p95_ms: float
    p99_ms: float
    jitter_ms: float

    @classmethod
    def from_samples(cls, samples: Iterable[float]) -> "LatencyStatistics":
        """Build latency statistics from non-negative millisecond samples."""

        values = tuple(float(sample) for sample in samples)

        if not values:
            raise ValueError("at least one latency sample is required")

        if any(not isfinite(value) or value < 0 for value in values):
            raise ValueError("latency samples must be finite and non-negative")

        ordered = tuple(sorted(values))

        return cls(
            sample_count=len(values),
            min_ms=ordered[0],
            max_ms=ordered[-1],
            average_ms=mean(values),
            median_ms=median(values),
            p95_ms=_nearest_rank_percentile(ordered, 95),
            p99_ms=_nearest_rank_percentile(ordered, 99),
            jitter_ms=calculate_jitter_ms(values),
        )

    def to_dict(self) -> dict[str, int | float]:
        """Return a JSON-serializable representation."""

        return {
            "sample_count": self.sample_count,
            "min_ms": round(self.min_ms, 3),
            "max_ms": round(self.max_ms, 3),
            "average_ms": round(self.average_ms, 3),
            "median_ms": round(self.median_ms, 3),
            "p95_ms": round(self.p95_ms, 3),
            "p99_ms": round(self.p99_ms, 3),
            "jitter_ms": round(self.jitter_ms, 3),
        }
