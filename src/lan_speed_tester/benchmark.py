"""Advanced TCP benchmarking: concurrent streams, repeat runs, and profiles."""

from __future__ import annotations

import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Callable

from .client import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_PORT,
    DEFAULT_SOCKET_TIMEOUT,
    ClientConfig,
    LANSpeedClient,
)
from .metrics import TransferMetrics


MAX_BENCHMARK_STREAMS = 32
MAX_BENCHMARK_REPEATS = 100


@dataclass(frozen=True, slots=True)
class BenchmarkProfile:
    """Preset benchmark settings."""

    name: str
    streams: int
    repeats: int
    duration_seconds: float
    chunk_size: int


BENCHMARK_PROFILES: dict[str, BenchmarkProfile] = {
    "quick": BenchmarkProfile(
        name="quick",
        streams=2,
        repeats=1,
        duration_seconds=2.0,
        chunk_size=256 * 1024,
    ),
    "normal": BenchmarkProfile(
        name="normal",
        streams=4,
        repeats=3,
        duration_seconds=5.0,
        chunk_size=1024 * 1024,
    ),
    "intensive": BenchmarkProfile(
        name="intensive",
        streams=8,
        repeats=5,
        duration_seconds=10.0,
        chunk_size=1024 * 1024,
    ),
)


ProgressCallback = Callable[[str, int, int, float], None]
SuiteProgressCallback = Callable[[int, int, str, int, int, float], None]


@dataclass(frozen=True, slots=True)
class StreamBenchmarkResult:
    """Download and upload measurements for one TCP stream."""

    stream_id: int
    download: TransferMetrics
    upload: TransferMetrics

    def to_dict(self) -> dict:
        return {
            "stream_id": self.stream_id,
            "download": self.download.to_dict(),
            "upload": self.upload.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class MultiStreamBenchmarkResult:
    """Aggregate and per-stream results from one benchmark run."""

    host: str
    port: int
    stream_count: int
    duration_seconds: float
    download: TransferMetrics
    upload: TransferMetrics
    streams: tuple[StreamBenchmarkResult, ...]
    elapsed_seconds: float

    def to_dict(self) -> dict:
        return {
            "host": self.host,
            "port": self.port,
            "stream_count": self.stream_count,
            "duration_seconds": self.duration_seconds,
            "elapsed_seconds": round(self.elapsed_seconds, 3),
            "download": self.download.to_dict(),
            "upload": self.upload.to_dict(),
            "streams": [stream.to_dict() for stream in self.streams],
        }


@dataclass(frozen=True, slots=True)
class BenchmarkSuiteResult:
    """A sequence of benchmark runs and their throughput summary."""

    host: str
    port: int
    profile: str
    repeat_count: int
    stream_count: int
    duration_seconds: float
    runs: tuple[MultiStreamBenchmarkResult, ...]

    @staticmethod
    def _summary(values: list[float]) -> dict[str, float]:
        return {
            "min_mbps": round(min(values), 3),
            "max_mbps": round(max(values), 3),
            "average_mbps": round(statistics.mean(values), 3),
            "median_mbps": round(statistics.median(values), 3),
        }

    def to_dict(self) -> dict:
        download_values = [
            run.download.throughput_mbps for run in self.runs
        ]
        upload_values = [
            run.upload.throughput_mbps for run in self.runs
        ]

        return {
            "host": self.host,
            "port": self.port,
            "profile": self.profile,
            "repeat_count": self.repeat_count,
            "stream_count": self.stream_count,
            "duration_seconds": self.duration_seconds,
            "summary": {
                "download": self._summary(download_values),
                "upload": self._summary(upload_values),
            },
            "runs": [
                {
                    "run_number": index,
                    **run.to_dict(),
                }
                for index, run in enumerate(self.runs, start=1)
            ],
        }


def _run_transfer_phase(
    clients: list[LANSpeedClient],
    direction: str,
    duration_seconds: float,
    progress_callback: ProgressCallback | None,
) -> tuple[tuple[TransferMetrics, ...], float]:
    """Run one transfer direction concurrently across all connected clients."""

    method_name = "download" if direction == "download" else "upload"
    phase_started = time.perf_counter()

    def run_one(stream_index: int) -> TransferMetrics:
        client = clients[stream_index]

        def report(total_bytes: int, elapsed_seconds: float) -> None:
            if progress_callback is not None:
                progress_callback(
                    direction,
                    stream_index + 1,
                    total_bytes,
                    elapsed_seconds,
                )

        method = getattr(client, method_name)
        return method(
            duration=duration_seconds,
            progress_callback=report,
        )

    with ThreadPoolExecutor(
        max_workers=len(clients),
        thread_name_prefix=f"lanspeed-{direction}",
    ) as executor:
        futures = [
            executor.submit(run_one, index)
            for index in range(len(clients))
        ]
        results = tuple(future.result() for future in futures)

    phase_elapsed = max(time.perf_counter() - phase_started, 1e-9)
    return results, phase_elapsed


def run_multi_stream_benchmark(
    host: str,
    port: int = DEFAULT_PORT,
    stream_count: int = 4,
    duration_seconds: float = 5.0,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    timeout: float = DEFAULT_SOCKET_TIMEOUT,
    progress_callback: ProgressCallback | None = None,
) -> MultiStreamBenchmarkResult:
    """Run concurrent download and upload phases using independent TCP sockets.

    All client connections are established before throughput timing begins.
    Download streams run concurrently first, followed by concurrent upload
    streams over the same set of client connections.
    """

    if not host:
        raise ValueError("host is required")
    if not 1 <= stream_count <= MAX_BENCHMARK_STREAMS:
        raise ValueError(
            f"stream_count must be between 1 and {MAX_BENCHMARK_STREAMS}"
        )
    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be greater than zero")

    config = ClientConfig(
        host=host,
        port=port,
        duration=duration_seconds,
        chunk_size=chunk_size,
        timeout=timeout,
    )

    clients = [
        LANSpeedClient(config)
        for _ in range(stream_count)
    ]
    benchmark_started = time.perf_counter()

    try:
        # Establish connections concurrently, outside throughput timing.
        with ThreadPoolExecutor(
            max_workers=stream_count,
            thread_name_prefix="lanspeed-connect",
        ) as executor:
            futures = [
                executor.submit(client.connect)
                for client in clients
            ]
            for future in futures:
                future.result()

        download_results, download_elapsed = _run_transfer_phase(
            clients,
            "download",
            duration_seconds,
            progress_callback,
        )
        upload_results, upload_elapsed = _run_transfer_phase(
            clients,
            "upload",
            duration_seconds,
            progress_callback,
        )
    finally:
        for client in clients:
            client.close()

    total_download_bytes = sum(
        result.bytes_transferred for result in download_results
    )
    total_upload_bytes = sum(
        result.bytes_transferred for result in upload_results
    )

    streams = tuple(
        StreamBenchmarkResult(
            stream_id=index + 1,
            download=download_results[index],
            upload=upload_results[index],
        )
        for index in range(stream_count)
    )

    return MultiStreamBenchmarkResult(
        host=host,
        port=port,
        stream_count=stream_count,
        duration_seconds=duration_seconds,
        download=TransferMetrics.from_transfer(
            direction="download",
            bytes_transferred=total_download_bytes,
            elapsed_seconds=download_elapsed,
        ),
        upload=TransferMetrics.from_transfer(
            direction="upload",
            bytes_transferred=total_upload_bytes,
            elapsed_seconds=upload_elapsed,
        ),
        streams=streams,
        elapsed_seconds=time.perf_counter() - benchmark_started,
    )


def run_benchmark_suite(
    host: str,
    port: int = DEFAULT_PORT,
    profile: str = "normal",
    stream_count: int | None = None,
    repeat_count: int | None = None,
    duration_seconds: float | None = None,
    chunk_size: int | None = None,
    timeout: float = DEFAULT_SOCKET_TIMEOUT,
    progress_callback: SuiteProgressCallback | None = None,
) -> BenchmarkSuiteResult:
    """Run repeated multi-stream benchmarks using a named profile as defaults."""

    if profile not in BENCHMARK_PROFILES:
        raise ValueError(
            f"Unknown benchmark profile: {profile}. "
            f"Choose from: {', '.join(BENCHMARK_PROFILES)}"
        )

    preset = BENCHMARK_PROFILES[profile]
    streams = preset.streams if stream_count is None else stream_count
    repeats = preset.repeats if repeat_count is None else repeat_count
    duration = (
        preset.duration_seconds
        if duration_seconds is None
        else duration_seconds
    )
    selected_chunk_size = (
        preset.chunk_size
        if chunk_size is None
        else chunk_size
    )

    if not 1 <= streams <= MAX_BENCHMARK_STREAMS:
        raise ValueError(
            f"stream_count must be between 1 and {MAX_BENCHMARK_STREAMS}"
        )
    if not 1 <= repeats <= MAX_BENCHMARK_REPEATS:
        raise ValueError(
            f"repeat_count must be between 1 and {MAX_BENCHMARK_REPEATS}"
        )
    if duration <= 0:
        raise ValueError("duration_seconds must be greater than zero")
    if timeout <= 0:
        raise ValueError("timeout must be greater than zero")

    runs: list[MultiStreamBenchmarkResult] = []

    for run_index in range(1, repeats + 1):
        def report(
            direction: str,
            stream_id: int,
            total_bytes: int,
            elapsed_seconds: float,
        ) -> None:
            if progress_callback is not None:
                progress_callback(
                    run_index,
                    repeats,
                    direction,
                    stream_id,
                    total_bytes,
                    elapsed_seconds,
                )

        runs.append(
            run_multi_stream_benchmark(
                host=host,
                port=port,
                stream_count=streams,
                duration_seconds=duration,
                chunk_size=selected_chunk_size,
                timeout=timeout,
                progress_callback=report,
            )
        )

    return BenchmarkSuiteResult(
        host=host,
        port=port,
        profile=profile,
        repeat_count=repeats,
        stream_count=streams,
        duration_seconds=duration,
        runs=tuple(runs),
    )
