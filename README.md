# ⚡ LANSpeed

> **Lightweight LAN diagnostics and performance testing from the terminal.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python\&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)](#requirements)
[![Protocol](https://img.shields.io/badge/Protocol-TCP-orange)](#how-it-works)

**LANSpeed** is a lightweight, Python-based network diagnostic tool for measuring **TCP latency, download and upload throughput, UDP packet loss, and RTT jitter** between devices on the same local network.

It uses a small **TCP client/server architecture** and focuses on being simple, transparent, portable, and easy to integrate into scripts or other tools.

> 🐍 Built with Python's standard library — no external runtime dependencies are required.

---

## ✨ Features

* 🚀 **TCP client/server architecture**
* 📡 **TCP request/response latency measurement**
* 📊 **Repeated RTT samples, percentiles, and jitter statistics**
* 📉 **UDP packet-loss and RTT-jitter diagnostics**
* ⬇️ **Download throughput testing**
* ⬆️ **Upload throughput testing**
* 🔌 **Explicit TCP message framing**
* ⚙️ **Configurable host, port, duration, chunk size, and timeout**
* 🧾 **JSON output for automation**
* 📦 **PyInstaller-compatible standalone client**
* 🐍 **Python standard library**
* 🪟 **Windows support**
* 🐧 **Linux support**
* 💻 **Simple terminal-based interface**
* 🛡️ **Input and transfer-size validation**
* 🧩 **Modular client, server, protocol, and metrics architecture**

---

## 🧠 How It Works

LANSpeed uses a simple client/server architecture.

The **server** listens for incoming TCP connections, while the **client** connects to the server and performs the requested network measurements.

```text
                    LAN / Local Network

┌─────────────────────────┐
│       LAN Client        │
│                         │
│  • Connect              │
│  • Measure latency      │
│  • Download test        │
│  • Upload test          │
│  • Calculate metrics    │
└────────────┬────────────┘
             │
             │ TCP :8765
             │
             ▼
┌─────────────────────────┐
│       LAN Server        │
│                         │
│  • Accept connections   │
│  • Respond to requests  │
│  • Send test data       │
│  • Receive test data    │
│  • Validate protocol    │
└─────────────────────────┘
```

A complete speed test follows this general flow:

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
  │<───────── DATA ───────────────│
  │<───────── DATA ───────────────│
  │<───────── END ────────────────│
  │                               │
  │───────── UPLOAD ─────────────>│
  │───────── DATA ───────────────>│
  │───────── DATA ───────────────>│
  │───────── END ────────────────>│
  │<───────── DONE ───────────────│
```

LANSpeed is intended primarily for **local networks and authorized testing environments**.

---

## 🔌 TCP Protocol

LANSpeed does not rely on TCP `recv()` calls corresponding to complete application messages.

Instead, application-level messages use explicit framing.

### Control Messages

Control messages use a 4-byte big-endian length prefix followed by the message payload:

```text
┌──────────────┬─────────────────────────┐
│ 4-byte size  │ JSON control message   │
└──────────────┴─────────────────────────┘
```

### Transfer Data

Upload and download data use the same length-prefixed approach:

```text
┌──────────────┬─────────────────────────┐
│ 4-byte size  │ Transfer chunk          │
└──────────────┴─────────────────────────┘
```

A zero-length frame marks the end of a transfer:

```text
┌──────────────┐
│ 0x00000000   │
└──────────────┘
```

This explicit framing allows LANSpeed to correctly handle:

* Partial TCP reads
* Multiple messages received together
* Large transfers
* Transfer boundaries
* Unexpected or malformed input

> **TCP is a byte stream, not a message-oriented protocol.**

---

## 📋 Requirements

LANSpeed requires:

* **Python 3.10 or newer**
* Two devices connected to the same LAN
* Network connectivity between the devices
* Firewall access to the LANSpeed server port

The default server listener is:

```text
0.0.0.0:8765
```

This means the server listens on all available network interfaces on TCP port `8765`.

### Supported Platforms

| Platform                | Status |
| ----------------------- | :----: |
| Windows                 |    ✅   |
| Linux                   |    ✅   |
| macOS                   |   ⚠️   |
| Other Unix-like systems |   ⚠️   |

The core networking code uses Python's standard library and should remain portable, although platform-specific testing may vary.

---

# 📦 Installation

## Clone the Repository

```powershell
git clone https://github.com/ItsWanheda/lanspeed.git
cd lanspeed
```

## Install in Editable Mode

```powershell
py -m pip install -e .
```

## Verify the Installation

```powershell
py -m lan_speed_tester --help
```

You can also run LANSpeed directly from the source tree during development.

---

# 🚀 Quick Start

## 1. Start the Server

On the machine you want to test against:

```powershell
py -m lan_speed_tester server
```

The server should display:

```text
LANSpeed server listening on 0.0.0.0:8765 (TCP + UDP)
Press Ctrl+C to stop.
```

Leave the server running.

---

## 2. Find the Server's LAN IP

The client needs the **LAN IP address of the machine running the server**.

### Windows

Open PowerShell or Command Prompt:

```powershell
ipconfig
```

Look for the active network adapter:

```text
Wireless LAN adapter Wi-Fi:

   IPv4 Address. . . . . . . . . . : 192.168.1.34
```

In this example:

```text
Server: 192.168.1.34
```

### Linux

Run:

```bash
ip addr
```

or:

```bash
hostname -I
```

Look for an address such as:

```text
192.168.1.34
```

### Private LAN Addresses

Common private IPv4 ranges include:

```text
192.168.x.x
10.x.x.x
172.16.x.x - 172.31.x.x
```

Do **not** use:

```text
127.0.0.1
```

when the client and server are running on different machines.

`127.0.0.1` refers to the local machine itself.

---

## 3. Run a Complete Test

From another device on the same LAN:

```powershell
py -m lan_speed_tester test 192.168.1.34
```

Replace `192.168.1.34` with your server's LAN IP.

The test performs:

```text
Latency
   │
   ▼
Download
   │
   ▼
Upload
   │
   ▼
Results
```

---

# 🧪 Individual Diagnostics

## 📡 Repeated TCP Latency

```powershell
py -m lan_speed_tester ping 192.168.1.34 --count 10 --interval 1
```

Collects repeated request/response RTT samples over the LANSpeed TCP connection and reports minimum, average, median, maximum, p95, p99, and jitter.

> **Important:** This is an application-level TCP RTT measurement, not the operating system's ICMP `ping` command.

Use `--count 0` to continue until you press `Ctrl+C`. JSON output is available with `--json`.

---

## 📉 UDP Packet Loss and Jitter

```powershell
py -m lan_speed_tester udp-test 192.168.1.34 --probes 100 --interval 0.02
```

Sends paced UDP probe datagrams and reports sent, received, and lost packets, packet-loss percentage, RTT statistics, and RTT jitter. The server must be running a LANSpeed version that supports the UDP responder.

`--timeout` controls how long the client waits for responses after the final probe. Use `--json` for machine-readable output.

---

## 🚀 TCP Throughput

```powershell
py -m lan_speed_tester test 192.168.1.34 --duration 10
```

The complete TCP test measures request/response latency, download throughput, and upload throughput.

---

# 🧾 JSON Output

LANSpeed supports machine-readable JSON output for automation, scripts, monitoring systems, and data processing.

Run:

```powershell
py -m lan_speed_tester test 192.168.1.34 --json
```

Example structure:

```json
{
  "host": "192.168.1.34",
  "port": 8765,
  "latency": {},
  "download": {},
  "upload": {}
}
```

The exact fields may evolve as the metrics system develops.

JSON output is designed to make LANSpeed easy to integrate into:

* Shell scripts
* Python scripts
* Monitoring systems
* CI environments
* Network diagnostics
* Custom dashboards
* Automated testing

---

# ⚙️ Configuration

LANSpeed provides configurable parameters for network testing.

Depending on the command, these may include:

| Parameter  | Purpose                            |
| ---------- | ---------------------------------- |
| Host       | Server IP address or hostname      |
| Port       | TCP server port                    |
| Duration   | Length of throughput tests         |
| Chunk size | Size of individual transfer chunks |
| Timeout    | Socket communication timeout       |

### Default Port

```text
8765
```

### Default Listener

```text
0.0.0.0:8765
```

Configuration defaults are intentionally conservative and can be adjusted as the project evolves.

---

# 📊 Measurements

LANSpeed separates network communication from metric calculation.

### TCP latency

TCP latency is measured as the elapsed time for a LANSpeed request and its response over an established TCP connection. It is not ICMP echo latency.

### UDP packet loss

```text
Packet loss (%) = (sent probes - received probes) / sent probes × 100
```

### RTT jitter

LANSpeed reports RTT jitter as the **mean absolute difference between consecutive successful RTT samples**, ordered by probe sequence. This is a round-trip variation metric and should not be confused with one-way RTP interarrival jitter.

### Latency statistics

Repeated samples include minimum, maximum, average, median, p95, and p99 values. Percentiles use the nearest-rank method.

### Throughput

```text
Throughput = transferred data / elapsed time
```

Results can be represented in human-readable units or JSON for automation.

The goal is to keep measurement logic independent from the terminal interface and network protocol.

---

# 🛠️ Development

Clone and install the project:

```powershell
py -m pip install -e .
```

Run the test suite:

```powershell
py -m unittest discover -s tests -v
```

If the project test configuration provides pytest support:

```powershell
py -m pytest
```

### Syntax Checks

Check the core modules:

```powershell
py -m py_compile src\lan_speed_tester\protocol.py
py -m py_compile src\lan_speed_tester\client.py
py -m py_compile src\lan_speed_tester\server.py
py -m py_compile src\lan_speed_tester\cli.py
py -m py_compile src\lan_speed_tester\metrics.py
```

### Project Structure

```text
lanspeed/
│
├── src/
│   └── lan_speed_tester/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── client.py
│       ├── server.py
│       ├── protocol.py
│       ├── metrics.py
│       ├── diagnostics.py
│       └── udp.py
│
├── tests/
│   ├── test_cli.py
│   ├── test_package.py
│   ├── test_diagnostics.py
│   └── test_udp.py
│
├── launcher.py
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── SECURITY.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── LICENSE
└── .gitignore
```

---

# 🏗️ Standalone Client

LANSpeed can be packaged as a standalone Windows executable using **PyInstaller**.

The project provides:

```text
launcher.py
```

Build the standalone client:

```powershell
py -m PyInstaller --clean --onefile --name lanspeed-client --paths src launcher.py
```

The resulting executable will be:

```text
dist/
└── lanspeed-client.exe
```

Run it with:

```powershell
.\dist\lanspeed-client.exe test 192.168.1.34
```

The standalone build is useful when running the client on a machine where you do not want to install the complete Python development environment.

---

# 🧯 Troubleshooting

## Connection Refused

If the client cannot connect to the server:

1. Make sure the LANSpeed server is running.
2. Verify the server IP address.
3. Verify that port `8765` is accessible.
4. Check the Windows/Linux firewall.
5. Make sure both machines are on the same LAN.
6. Make sure you are not using `127.0.0.1` from another device.

---

## Timeout

A timeout can indicate:

* Firewall filtering
* Incorrect IP address
* Network isolation
* Server not running
* Unstable network connectivity
* Incorrect port configuration

---

## Client and Server Protocol Errors

Make sure the client and server are running compatible versions of LANSpeed.

Protocol changes should always be tested on **both sides**.

---

## 🌐 Network Isolation

Some Wi-Fi networks prevent connected devices from communicating with each other.

This can occur with:

* Guest Wi-Fi
* Client isolation
* AP isolation
* VLAN segmentation
* Router firewall rules

If two devices can access the Internet but cannot communicate directly, check the router or access-point configuration.

---

# 🗺️ Roadmap

## ✅ v0.1.0 — Core TCP Tester

* [x] Python package and CLI foundation
* [x] TCP client/server architecture and framed protocol
* [x] TCP latency measurement
* [x] Download and upload throughput testing
* [x] JSON-ready result models
* [x] PyInstaller-compatible client entry point

## ✅ v0.2.0 — Network Diagnostics

* [x] UDP echo responder alongside the TCP server
* [x] UDP packet-loss measurement
* [x] UDP RTT and jitter statistics
* [x] Repeated TCP RTT command
* [x] Min, max, average, median, p95, and p99 statistics
* [x] JSON output for TCP test, ping, and UDP test
* [x] Automated tests for statistics and UDP diagnostics

## 🚧 v0.3.0 — Advanced Benchmarking

* [ ] Multi-stream TCP throughput testing
* [ ] Repeated benchmark runs
* [ ] Quick, normal, and intensive test profiles
* [ ] Live transfer progress
* [ ] Aggregate and per-stream throughput reports

## 🚧 v0.4.0 — Reporting & Network Intelligence

* [ ] Persistent local test history
* [ ] Compare historical benchmark runs
* [ ] CSV and expanded JSON export
* [ ] Standalone HTML reports
* [ ] Network interface discovery
* [ ] Platform-aware local IP and interface details

The roadmap is subject to change as LANSpeed develops.

---

# 🔐 Security

LANSpeed is a **network performance testing utility**, not an authentication system or security boundary.

The server accepts network connections and should therefore only be exposed to networks and systems you are authorized to test.

For security guidance and vulnerability reporting, see:

**[🔐 SECURITY.md](SECURITY.md)**

Please only use LANSpeed against systems and networks where you have permission to perform testing.

---

# 🤝 Contributing

Contributions are welcome!

Before submitting changes, please read:

**[🤝 CONTRIBUTING.md](CONTRIBUTING.md)**

For community standards and expected behavior:

**[📜 CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)**

Bug reports, documentation improvements, testing, protocol improvements, performance work, and new features are all welcome.

---

# 📋 Changelog

Development history and notable releases are documented in:

**[📋 CHANGELOG.md](CHANGELOG.md)**

---

# 📄 License

LANSpeed is released under the **MIT License**.

See **[LICENSE](LICENSE)** for the complete license text.

---

<div align="center">

### ⚡ LANSpeed

**Measure your LAN. Understand your network.**

Built with 🐍 Python

</div>
