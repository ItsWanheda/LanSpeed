# 📋 Changelog

All notable changes to **LANSpeed** are documented in this file.

The format is inspired by [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and LANSpeed follows **Semantic Versioning** where practical.

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
