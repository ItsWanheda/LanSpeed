"""
Command-line interface for LAN Speed Tester.
"""

from __future__ import annotations

import argparse
import sys

from .client import DEFAULT_PORT, run_speed_test
from .metrics import format_mbps, format_mbs
from .server import run_server


def build_parser() -> argparse.ArgumentParser:
    """Build the LANSpeed command-line parser."""
    parser = argparse.ArgumentParser(
        prog="lanspeed",
        description="LANSpeed - Local Network Speed Tester",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # ---------------------------------------------------------
    # SERVER
    # ---------------------------------------------------------
    server_parser = subparsers.add_parser(
        "server",
        help="Start the LANSpeed server.",
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
        help=f"TCP port (default: {DEFAULT_PORT}).",
    )

    # ---------------------------------------------------------
    # TEST
    # ---------------------------------------------------------
    test_parser = subparsers.add_parser(
        "test",
        help="Run a LAN speed test against a server.",
    )

    test_parser.add_argument(
        "host",
        help="LANSpeed server IP address or hostname.",
    )

    test_parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"TCP port (default: {DEFAULT_PORT}).",
    )

    test_parser.add_argument(
        "--duration",
        type=float,
        default=10.0,
        help="Test duration in seconds (default: 10).",
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

    return parser


def run_server_command(args: argparse.Namespace) -> int:
    """Run the server command."""
    try:
        run_server(
            host=args.host,
            port=args.port,
        )

    except OSError as exc:
        print(
            f"Error: could not start server: {exc}",
            file=sys.stderr,
        )
        return 1

    return 0


def run_test_command(args: argparse.Namespace) -> int:
    """Run a LAN speed test."""
    try:
        print()
        print("LANSpeed")
        print("=" * 40)
        print(f"Server:   {args.host}:{args.port}")
        print(f"Duration: {args.duration:.1f}s")
        print()

        print("Connecting...")
        print()

        result = run_speed_test(
            host=args.host,
            port=args.port,
            duration=args.duration,
            chunk_size=args.chunk_size,
            timeout=args.timeout,
        )

    except KeyboardInterrupt:
        print("\nTest cancelled.")
        return 130

    except (
        ConnectionError,
        OSError,
        ValueError,
        RuntimeError,
    ) as exc:
        print(
            f"\nError: {exc}",
            file=sys.stderr,
        )
        return 1

    print("Results")
    print("-" * 40)

    if result.latency is not None:
        print(
            f"Latency:  "
            f"{result.latency.latency_ms:.2f} ms"
        )

    if result.download is not None:
        print(
            f"Download: "
            f"{format_mbps(result.download.throughput_mbps)} "
            f"({format_mbs(result.download.throughput_mbs)})"
        )

    if result.upload is not None:
        print(
            f"Upload:   "
            f"{format_mbps(result.upload.throughput_mbps)} "
            f"({format_mbs(result.upload.throughput_mbs)})"
        )

    print("-" * 40)

    return 0


def main() -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "server":
        return run_server_command(args)

    if args.command == "test":
        return run_test_command(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())