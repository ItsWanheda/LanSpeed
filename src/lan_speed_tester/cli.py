"""Command-line interface for LANSpeed."""

from __future__ import annotations

import argparse
import json
import sys
import threading
import time

from . import __version__
from .benchmark import BENCHMARK_PROFILES, run_benchmark_suite
from .client import (
    DEFAULT_PORT,
    ClientConfig,
    LANSpeedClient,
    run_speed_test,
)
from .diagnostics import LatencyStatistics
from .metrics import format_bytes, format_mbps, format_mbs
from .server import run_server
from .udp import (
    DEFAULT_UDP_INTERVAL_SECONDS,
    DEFAULT_UDP_PROBE_COUNT,
    DEFAULT_UDP_TIMEOUT_SECONDS,
    run_udp_probe_test,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the LANSpeed command-line parser."""

    parser = argparse.ArgumentParser(
        prog="lanspeed",
        description="LANSpeed - Local Network Diagnostics and Performance Tester",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the installed LANSpeed version and exit.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    server_parser = subparsers.add_parser(
        "server",
        help="Start the LANSpeed TCP and UDP services.",
    )
    server_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Address to bind to (default: 0.0.0.0).",
    )
    server_parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"TCP and UDP port (default: {DEFAULT_PORT}).",
    )

    test_parser = subparsers.add_parser(
        "test",
        help="Run a complete single-stream TCP speed test.",
    )
    test_parser.add_argument(
        "host",
        help="LANSpeed server IP address or hostname.",
    )
    test_parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    test_parser.add_argument(
        "--duration",
        type=float,
        default=10.0,
        help="Duration of each transfer test in seconds (default: 10).",
    )
    test_parser.add_argument(
        "--chunk-size",
        type=int,
        default=1024 * 1024,
        help="Transfer chunk size in bytes (default: 1048576).",
    )
    test_parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Socket timeout in seconds (default: 5).",
    )
    test_parser.add_argument(
        "--json",
        action="store_true",
        help="Print the result as JSON.",
    )

    ping_parser = subparsers.add_parser(
        "ping",
        help="Run repeated LANSpeed TCP RTT measurements (not ICMP ping).",
    )
    ping_parser.add_argument("host", help="LANSpeed server IP address or hostname.")
    ping_parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    ping_parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of samples; use 0 to continue until Ctrl+C (default: 10).",
    )
    ping_parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Target interval between samples in seconds (default: 1).",
    )
    ping_parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Socket timeout in seconds (default: 5).",
    )
    ping_parser.add_argument(
        "--json",
        action="store_true",
        help="Print the summary as JSON.",
    )

    udp_parser = subparsers.add_parser(
        "udp-test",
        help="Measure UDP packet loss, RTT statistics, and RTT jitter.",
    )
    udp_parser.add_argument("host", help="LANSpeed server IP address or hostname.")
    udp_parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    udp_parser.add_argument(
        "--probes",
        type=int,
        default=DEFAULT_UDP_PROBE_COUNT,
        help=f"Number of UDP probes (default: {DEFAULT_UDP_PROBE_COUNT}).",
    )
    udp_parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_UDP_INTERVAL_SECONDS,
        help="Delay between probes in seconds (default: 0.02).",
    )
    udp_parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_UDP_TIMEOUT_SECONDS,
        help="Response timeout in seconds (default: 1).",
    )
    udp_parser.add_argument(
        "--json",
        action="store_true",
        help="Print the result as JSON.",
    )

    benchmark_parser = subparsers.add_parser(
        "benchmark",
        help="Run a repeated multi-stream TCP throughput benchmark.",
    )
    benchmark_parser.add_argument(
        "host",
        help="LANSpeed server IP address or hostname.",
    )
    benchmark_parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    benchmark_parser.add_argument(
        "--profile",
        choices=tuple(BENCHMARK_PROFILES),
        default="normal",
        help="Preset settings (default: normal). Explicit options override the profile.",
    )
    benchmark_parser.add_argument(
        "--streams",
        type=int,
        default=None,
        help="Concurrent TCP streams (profile default when omitted).",
    )
    benchmark_parser.add_argument(
        "--repeat",
        type=int,
        default=None,
        help="Number of benchmark runs (profile default when omitted).",
    )
    benchmark_parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Seconds per download/upload phase (profile default when omitted).",
    )
    benchmark_parser.add_argument(
        "--chunk-size",
        type=int,
        default=None,
        help="Transfer chunk size in bytes (profile default when omitted).",
    )
    benchmark_parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Socket timeout in seconds (default: 5).",
    )
    benchmark_parser.add_argument(
        "--json",
        action="store_true",
        help="Print all runs and aggregate summaries as JSON.",
    )

    return parser


def run_server_command(args: argparse.Namespace) -> int:
    """Run the TCP and UDP server command."""

    try:
        run_server(host=args.host, port=args.port)
    except (OSError, ValueError) as exc:
        print(f"Error: could not start server: {exc}", file=sys.stderr)
        return 1

    return 0


def _single_progress_callback(duration: float):
    """Build a throttled, thread-safe transfer progress reporter."""

    lock = threading.Lock()
    last_update = 0.0

    def report(direction: str, total_bytes: int, elapsed: float) -> None:
        nonlocal last_update

        now = time.monotonic()
        with lock:
            if now - last_update < 0.15 and elapsed < duration:
                return
            last_update = now
            percent = min(100.0, max(0.0, elapsed / duration * 100.0))
            sys.stdout.write(
                f"\r{direction.title():8} {percent:5.1f}% "
                f"| {format_bytes(total_bytes)} transferred"
            )
            sys.stdout.flush()

    return report


def run_test_command(args: argparse.Namespace) -> int:
    """Run a complete single-stream TCP speed test."""

    try:
        if not args.json:
            print(f"LANSpeed test: {args.host}:{args.port}")
            print(f"Duration per direction: {args.duration:.1f}s")

        result = run_speed_test(
            host=args.host,
            port=args.port,
            duration=args.duration,
            chunk_size=args.chunk_size,
            timeout=args.timeout,
            progress_callback=(
                None if args.json else _single_progress_callback(args.duration)
            ),
        )
    except KeyboardInterrupt:
        print("\nTest cancelled.")
        return 130
    except (ConnectionError, OSError, ValueError, RuntimeError) as exc:
        print(f"\nError: {exc}", file=sys.stderr)
        return 1

    if not args.json:
        print()

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        return 0

    print()
    print("Results")
    print("-" * 40)

    if result.latency is not None:
        print(f"Latency:  {result.latency.latency_ms:.2f} ms")
    if result.download is not None:
        print(
            f"Download: {format_mbps(result.download.throughput_mbps)} "
            f"({format_mbs(result.download.throughput_mbs)})"
        )
    if result.upload is not None:
        print(
            f"Upload:   {format_mbps(result.upload.throughput_mbps)} "
            f"({format_mbs(result.upload.throughput_mbs)})"
        )

    print("-" * 40)
    return 0


def run_ping_command(args: argparse.Namespace) -> int:
    """Collect repeated TCP request/response latency samples."""

    if args.count < 0:
        print("Error: --count must be zero or greater.", file=sys.stderr)
        return 2
    if args.interval <= 0:
        print("Error: --interval must be greater than zero.", file=sys.stderr)
        return 2
    if args.timeout <= 0:
        print("Error: --timeout must be greater than zero.", file=sys.stderr)
        return 2

    config = ClientConfig(
        host=args.host,
        port=args.port,
        duration=1.0,
        chunk_size=1024,
        timeout=args.timeout,
    )
    samples: list[float] = []
    interrupted = False

    try:
        with LANSpeedClient(config) as client:
            while args.count == 0 or len(samples) < args.count:
                sample_started = time.perf_counter()
                measurement = client.measure_latency()
                samples.append(measurement.latency_ms)

                if not args.json:
                    print(
                        f"Reply from {args.host}: "
                        f"TCP RTT={measurement.latency_ms:.2f} ms"
                    )

                if args.count != 0 and len(samples) >= args.count:
                    break

                remaining = args.interval - (
                    time.perf_counter() - sample_started
                )
                if remaining > 0:
                    time.sleep(remaining)

    except KeyboardInterrupt:
        interrupted = True
    except (ConnectionError, OSError, ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not samples:
        print("No latency samples were collected.", file=sys.stderr)
        return 130 if interrupted else 1

    statistics = LatencyStatistics.from_samples(samples)
    result = {
        "host": args.host,
        "port": args.port,
        "protocol": "tcp",
        "measurement": "LANSpeed request-response RTT (not ICMP)",
        "latency": statistics.to_dict(),
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print()
        print("TCP Latency Statistics")
        print("-" * 40)
        print(f"Samples:  {statistics.sample_count}")
        print(f"Minimum:  {statistics.min_ms:.2f} ms")
        print(f"Average:  {statistics.average_ms:.2f} ms")
        print(f"Median:   {statistics.median_ms:.2f} ms")
        print(f"Maximum:  {statistics.max_ms:.2f} ms")
        print(f"95th %:   {statistics.p95_ms:.2f} ms")
        print(f"99th %:   {statistics.p99_ms:.2f} ms")
        print(f"Jitter:   {statistics.jitter_ms:.2f} ms")

    return 130 if interrupted else 0


def run_udp_test_command(args: argparse.Namespace) -> int:
    """Run UDP packet-loss and jitter diagnostics."""

    try:
        result = run_udp_probe_test(
            host=args.host,
            port=args.port,
            probe_count=args.probes,
            interval_seconds=args.interval,
            timeout_seconds=args.timeout,
        )
    except (OSError, ValueError) as exc:
        print(f"Error: UDP test failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        return 0

    print()
    print("UDP Diagnostics")
    print("=" * 40)
    print(f"Server:       {args.host}:{args.port}")
    print(f"Packets sent: {result.packets_sent}")
    print(f"Received:     {result.packets_received}")
    print(f"Lost:         {result.packets_lost}")
    print(f"Packet loss:  {result.packet_loss_percent:.2f}%")

    if result.latency is None:
        print("Latency:      no valid UDP responses")
        print("Jitter:       unavailable")
    else:
        stats = result.latency
        print(f"Minimum RTT:  {stats.min_ms:.2f} ms")
        print(f"Average RTT:  {stats.average_ms:.2f} ms")
        print(f"Median RTT:   {stats.median_ms:.2f} ms")
        print(f"Maximum RTT:  {stats.max_ms:.2f} ms")
        print(f"95th % RTT:   {stats.p95_ms:.2f} ms")
        print(f"99th % RTT:   {stats.p99_ms:.2f} ms")
        print(f"Jitter:       {stats.jitter_ms:.2f} ms")

    print("-" * 40)
    return 0


def _benchmark_progress_callback(duration: float, stream_count: int):
    """Build a throttled progress reporter for multi-stream benchmark runs."""

    lock = threading.Lock()
    last_update = 0.0

    def report(
        run_number: int,
        run_count: int,
        direction: str,
        stream_id: int,
        total_bytes: int,
        elapsed: float,
    ) -> None:
        nonlocal last_update

        now = time.monotonic()
        with lock:
            if now - last_update < 0.15 and elapsed < duration:
                return
            last_update = now
            percent = min(100.0, max(0.0, elapsed / duration * 100.0))
            sys.stdout.write(
                f"\rRun {run_number}/{run_count} | "
                f"{direction.title():8} | Stream {stream_id}/{stream_count} "
                f"| {percent:5.1f}% | {format_bytes(total_bytes)}"
            )
            sys.stdout.flush()

    return report


def run_benchmark_command(args: argparse.Namespace) -> int:
    """Run repeated multi-stream TCP throughput benchmarks."""

    preset = BENCHMARK_PROFILES[args.profile]
    streams = preset.streams if args.streams is None else args.streams
    duration = (
        preset.duration_seconds
        if args.duration is None
        else args.duration
    )
    repeats = preset.repeats if args.repeat is None else args.repeat

    try:
        if not args.json:
            print(f"LANSpeed benchmark: {args.host}:{args.port}")
            print(
                f"Profile: {args.profile} | Streams: {streams} | "
                f"Runs: {repeats} | Duration/direction: {duration:.1f}s"
            )

        result = run_benchmark_suite(
            host=args.host,
            port=args.port,
            profile=args.profile,
            stream_count=args.streams,
            repeat_count=args.repeat,
            duration_seconds=args.duration,
            chunk_size=args.chunk_size,
            timeout=args.timeout,
            progress_callback=(
                None
                if args.json
                else _benchmark_progress_callback(duration, streams)
            ),
        )
    except KeyboardInterrupt:
        print("\nBenchmark cancelled.")
        return 130
    except (ConnectionError, OSError, ValueError, RuntimeError) as exc:
        print(f"\nError: benchmark failed: {exc}", file=sys.stderr)
        return 1

    if not args.json:
        print()

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        return 0

    payload = result.to_dict()
    summary = payload["summary"]

    print()
    print("Benchmark Summary")
    print("=" * 72)
    print(
        "Download: "
        f"avg {summary['download']['average_mbps']:.2f} Mbps | "
        f"median {summary['download']['median_mbps']:.2f} Mbps | "
        f"min {summary['download']['min_mbps']:.2f} Mbps | "
        f"max {summary['download']['max_mbps']:.2f} Mbps"
    )
    print(
        "Upload:   "
        f"avg {summary['upload']['average_mbps']:.2f} Mbps | "
        f"median {summary['upload']['median_mbps']:.2f} Mbps | "
        f"min {summary['upload']['min_mbps']:.2f} Mbps | "
        f"max {summary['upload']['max_mbps']:.2f} Mbps"
    )

    print()
    print("Individual Runs")
    for index, run in enumerate(result.runs, start=1):
        print(
            f"Run {index}: "
            f"Download {run.download.throughput_mbps:.2f} Mbps | "
            f"Upload {run.upload.throughput_mbps:.2f} Mbps"
        )

    if result.runs:
        print()
        print(f"Per-stream results (run {len(result.runs)}):")
        for stream in result.runs[-1].streams:
            print(
                f"Stream {stream.stream_id}: "
                f"Download {stream.download.throughput_mbps:.2f} Mbps | "
                f"Upload {stream.upload.throughput_mbps:.2f} Mbps"
            )

    print("=" * 72)
    return 0


def main() -> int:
    """CLI entry point."""

    parser = build_parser()
    args = parser.parse_args()

    if args.command == "server":
        return run_server_command(args)
    if args.command == "test":
        return run_test_command(args)
    if args.command == "ping":
        return run_ping_command(args)
    if args.command == "udp-test":
        return run_udp_test_command(args)
    if args.command == "benchmark":
        return run_benchmark_command(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
