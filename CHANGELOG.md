# 📋 Changelog

All notable changes to **LANSpeed** are documented in this file.

The format is inspired by [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and LANSpeed follows **Semantic Versioning** where practical.

---

## [0.4.0] — 2026-11-13

> 🗂️ **Reporting & Network Intelligence**

This release adds local result history, benchmark comparisons, report exports, and network interface discovery.

### ✨ Added

#### 🗃️ Persistent Test History
* Automatically save successful TCP speed tests, repeated TCP latency checks, UDP diagnostics, and multi-stream benchmark suites.
* Store structured result payloads in a local SQLite database at `~/.lanspeed/history.sqlite3`.
* Add commands to list recent results and compare two saved entries.
* Support an alternate database path for history operations.

#### 📊 Reporting & Export
* Export the complete history to JSON with the original structured result payloads.
* Export history to CSV for spreadsheet tools and further analysis.
* Generate a standalone HTML report that can be opened locally in a browser.
* Compare download and upload throughput with absolute and percentage changes.

#### 🖧 Network Interface Discovery
* Add a local interface discovery command with JSON output.
* Use Python standard-library discovery as a dependency-free fallback.
* Add an optional `network` extra using psutil for per-interface IP addresses, MAC addresses, link state, MTU, and link speed when exposed by the operating system.
* Clearly distinguish per-interface details from best-effort host address discovery.

#### 🧪 Testing
* Add tests for SQLite persistence, result comparison, JSON/CSV/HTML export, HTML escaping, CLI arguments, and interface discovery.

### 🔧 Changed

* Bump runtime and package metadata to `0.4.0`.
* Expand README usage examples and mark the 0.4.0 roadmap milestone complete.

### 🔒 Compatibility Notes

* Existing TCP and UDP test protocols are unchanged.
* History is stored locally on the client machine and is not synchronized between devices.
* The standard-library interface fallback does not claim to map each discovered host address to a specific interface.
* Detailed per-interface metadata requires installing the optional `network` extra.
* No database service or mandatory third-party runtime dependency is introduced.

---

## [0.3.0] — 2026-11-12

> 🧵 **Advanced Benchmarking**

This release adds concurrent TCP throughput benchmarking, repeatable test suites, configurable workload profiles, and live terminal progress. The existing TCP and UDP diagnostic commands remain available.

### ✨ Added

#### 🧵 Multi-Stream TCP Benchmarking
* Run multiple independent TCP client connections concurrently.
* Measure download streams concurrently, followed by upload streams concurrently.
* Preserve per-stream transfer metrics alongside aggregate throughput.
* Calculate aggregate throughput using total transferred bytes divided by the wall-clock duration of each transfer phase.
* Establish stream connections before transfer timing begins.

#### 🔁 Repeated Benchmark Runs
* Run a benchmark multiple times using the `--repeat` option.
* Report individual run throughput.
* Calculate minimum, maximum, average, and median throughput across runs.
* Include all per-run and per-stream results in JSON output.

#### 🎚️ Benchmark Profiles
* `quick`: 2 streams, 1 run, 2 seconds per direction.
* `normal`: 4 streams, 3 runs, 5 seconds per direction.
* `intensive`: 8 streams, 5 runs, 10 seconds per direction.
* Allow stream count, repeat count, duration, and chunk size to override profile defaults.

#### 📈 Live Progress
* Display transfer progress for the existing single-stream `test` command.
* Display run, direction, stream, elapsed percentage, and transferred bytes during multi-stream benchmarks.
* Keep JSON output free from terminal progress messages.

#### 🧪 Testing
* Add integration coverage for concurrent streams against a local LANSpeed server.
* Verify per-stream byte totals match aggregate transferred bytes.
* Verify repeated runs, profile ordering, validation, JSON serialization, and progress callbacks.

### 🔧 Changed

* Expose the existing client transfer progress callback through the `run_speed_test` convenience API.
* Add the `benchmark` CLI command and update the README roadmap and usage guide.
* Bump package metadata and runtime version to `0.3.0`.

### 🔒 Compatibility Notes

* Existing `server`, `test`, `ping`, and `udp-test` commands are retained.
* The TCP wire protocol and UDP diagnostic datagram format are unchanged.
* Multi-stream benchmarking opens multiple simultaneous TCP connections to the LANSpeed server. Choose stream counts appropriate for the server and network capacity.
* Benchmark figures represent throughput observed by the LANSpeed client/server pair; they are not a promise of Internet speed or a substitute for testing the path to an external destination.

---

## [0.2.0] — 2026-11-12

> 📡 **Network Diagnostics**

This release extends LANSpeed beyond its initial TCP throughput test with UDP diagnostics and repeatable latency measurements. The existing framed TCP control and transfer protocol remains unchanged.

### ✨ Added

#### 📉 UDP Diagnostics
* UDP echo responder started alongside the existing TCP server.
* UDP probe command with configurable probe count, interval, and response timeout.
* Sent, received, lost, and packet-loss percentage metrics.
* UDP RTT minimum, maximum, average, median, p95, and p99 statistics.
* RTT jitter calculated as the mean absolute difference between consecutive successful RTT samples.

#### 📡 Repeated TCP Latency
* New `ping` command for repeated LANSpeed request/response RTT samples.
* Continuous mode with `--count 0` and graceful Ctrl+C handling.
* Latency summary statistics and jitter.
* Explicit distinction between LANSpeed TCP RTT and ICMP echo ping.

#### 🧾 Output and Testing
* JSON output for the complete TCP test, repeated TCP ping, and UDP diagnostics.
* Automated tests for latency statistics, jitter calculations, CLI arguments, and the local UDP responder.

### 🔧 Changed

* The server now starts the TCP service and UDP diagnostic responder on the same numeric port using their separate transport protocols.
* Project metadata and documentation now require Python 3.10 or newer, matching language features already used by the codebase.
* Updated CLI tests to match the actual default TCP port and test duration.

### 🛠️ Fixed

* Implemented the previously documented `test --json` option.
* Removed outdated README examples for individual download/upload CLI commands that were not implemented.
* Expanded project structure and roadmap documentation for the upcoming 0.3.0 and 0.4.0 releases.

### 🔒 Compatibility Notes

* The existing TCP message framing and command flow are unchanged.
* UDP diagnostics require both client and server to run v0.2.0 or newer.
* The `ping` command measures LANSpeed TCP request/response RTT; it does not send ICMP echo packets.

---

## [0.1.0] — 2026-09-22

> 🎉 **Initial public release**

The first development release of LANSpeed establishes the project's core architecture, command-line interface, TCP communication layer, and documentation foundation.

This release focuses on creating a clean foundation for future LAN performance testing features.

### ✨ Added

#### 🏗️ Project Foundation

* Initial LANSpeed project structure.
* Python package configuration.
* `src/`-based package layout.
* Standard-library-first architecture.
* Initial MIT license.
* Initial `.gitignore`.
* Initial project documentation.

#### 🖥️ Command-Line Interface

* Initial CLI entry point.
* Command structure for LANSpeed operations.
* Server command foundation.
* Test command foundation.
* Command-line argument handling groundwork.
* Foundation for future individual latency, upload, and download commands.

#### 🌐 Client / Server Architecture

* Initial TCP client/server architecture.
* Dedicated LANSpeed server implementation.
* Dedicated LANSpeed client implementation.
* Configurable server host and port.
* Connection handling foundation.
* Basic client/server lifecycle management.

#### 🔌 Network Protocol

* Initial LANSpeed TCP protocol.
* Protocol versioning foundation.
* Structured control-message communication.
* JSON-based control messages.
* Explicit message framing using length prefixes.
* Protocol response handling.
* Basic protocol validation.
* Foundation for reliable client/server communication over TCP.

#### ⚡ Network Testing Foundation

* Latency measurement foundation.
* Download throughput testing foundation.
* Upload throughput testing foundation.
* Transfer chunk handling.
* Configurable transfer chunk size.
* Configurable test duration.
* Foundation for collecting and reporting network performance metrics.

#### 📊 Metrics

* Initial network performance metrics module.
* Foundation for throughput calculations.
* Foundation for latency measurements.
* Separation of network measurements from protocol and CLI logic.

#### 📦 Packaging

* PyInstaller-compatible application entry point.
* Root-level `launcher.py` for executable builds.
* Foundation for standalone LANSpeed client distribution.
* Support for building a single-file Windows executable.

#### 📚 Documentation

* Initial `README.md`.
* Installation instructions.
* Quick-start documentation.
* LAN IP discovery instructions.
* Usage examples.
* Architecture overview.
* JSON output documentation.
* Development instructions.
* Initial roadmap.

#### 🛡️ Security & Community

* Initial `SECURITY.md`.
* Security vulnerability reporting guidance.
* Authorized-testing guidelines.
* Initial `CODE_OF_CONDUCT.md`.
* Initial `CONTRIBUTING.md`.
* Contribution workflow documentation.
* Development and protocol-testing guidelines.

#### 🧪 Development & Testing

* Initial test structure.
* Python syntax validation workflow.
* Client/server protocol testing foundation.
* Development environment documentation.
* Foundation for automated testing and future CI improvements.

---

### 🔧 Technical Details

The initial release establishes a framed TCP communication model between LANSpeed clients and servers.

Control messages use a length-prefixed structure:

```text
┌──────────────┬─────────────────────┐
│ 4-byte size  │ JSON control data   │
└──────────────┴─────────────────────┘
```

Transfer data uses explicit framing to prevent TCP stream-boundary issues:

```text
┌──────────────┬─────────────────────┐
│ 4-byte size  │ Transfer chunk      │
└──────────────┴─────────────────────┘
```

A zero-length transfer frame marks the end of a data stream.

This design provides a clear foundation for reliable upload and download transfers without relying on individual TCP `recv()` calls to correspond to complete application messages.

---

### 🧭 Initial Test Flow

The initial architecture supports the following general workflow:

```text
Client                         Server
  │                               │
  │────────── HELLO ─────────────>│
  │<───────── OK ─────────────────│
  │                               │
  │──────── LATENCY ─────────────>│
  │<───────── OK ─────────────────│
  │                               │
  │──────── DOWNLOAD ────────────>│
  │<───────── READY ──────────────│
  │<──────── DATA ────────────────│
  │<──────── DATA ────────────────│
  │<──────── END ─────────────────│
  │                               │
  │───────── UPLOAD ─────────────>│
  │<───────── READY ──────────────│
  │────────── DATA ──────────────>│
  │────────── DATA ──────────────>│
  │────────── END ───────────────>│
  │<───────── DONE ───────────────│
  │                               │
```

The protocol is designed to keep control messages and transfer data clearly separated.

---

### 📁 Initial Project Components

The initial release establishes the following core components:

```text
src/
└── lan_speed_tester/
    ├── __main__.py      # Package entry point
    ├── cli.py           # Command-line interface
    ├── client.py        # Client implementation
    ├── server.py        # Server implementation
    ├── protocol.py      # TCP protocol and framing
    └── metrics.py       # Network performance metrics

launcher.py              # PyInstaller entry point
```

---

### 🚧 Known Limitations

This release is an early foundation and does not yet provide every planned LANSpeed feature.

The following areas remain under development:

* UDP packet-loss testing.
* Jitter measurement.
* Multi-stream throughput testing.
* Network interface discovery.
* Historical test results.
* Advanced terminal output.
* CSV export.
* Expanded automated test coverage.
* Additional platform-specific packaging.
* More extensive protocol compatibility handling.

---

### 🔮 Next Steps

Future releases are expected to build on this foundation with improvements such as:

* More comprehensive latency statistics.
* More accurate throughput measurement.
* Rich terminal reporting.
* JSON and CSV result export.
* UDP testing.
* Packet-loss measurement.
* Jitter analysis.
* Multi-connection throughput testing.
* Better error reporting.
* Expanded automated tests.
* Improved standalone distribution.

---

## Versioning

LANSpeed uses version numbers in the following format:

```text
MAJOR.MINOR.PATCH
```

Where:

* **MAJOR** — Breaking changes.
* **MINOR** — New backward-compatible functionality.
* **PATCH** — Backward-compatible fixes and improvements.

---

## Unreleased

Changes made after `v0.1.0` and before the next release will be documented here.

### Added

*No unreleased changes yet.*

### Changed

*No unreleased changes yet.*

### Fixed

*No unreleased fixes yet.*

---

[0.1.0]: https://github.com/ItsWanheda/lanspeed/releases/tag/v0.1.0

[0.2.0]: https://github.com/ItsWanheda/lanspeed/releases/tag/v0.2.0

[0.3.0]: https://github.com/ItsWanheda/lanspeed/releases/tag/v0.3.0

[0.4.0]: https://github.com/ItsWanheda/lanspeed/releases/tag/v0.4.0
