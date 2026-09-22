# ⚡ LANSpeed

> **Lightweight LAN throughput & latency testing from the terminal.**

LANSpeed is a lightweight, Python-based network diagnostic tool for measuring **latency, download throughput, and upload throughput** between devices on the same local network.

Built with simplicity in mind, LANSpeed uses a small TCP client/server architecture and requires **no external runtime dependencies**.

---

## ✨ Features

* 🚀 **TCP client/server architecture**
* 📡 **LAN latency measurement**
* ⬇️ **Download throughput testing**
* ⬆️ **Upload throughput testing**
* ⚙️ **Configurable host, port, duration, and chunk size**
* 🧾 **JSON output for automation**
* 🐍 **Python standard library**
* 🪟 **Windows friendly**
* 🐧 **Linux friendly**
* 🔌 **Simple terminal-based interface**
* 📦 **PyInstaller-compatible standalone client**

---

## 🧠 How It Works

LANSpeed uses a client/server model:

```text
┌──────────────────────┐             ┌──────────────────────┐
│      LAN Client      │             │      LAN Server      │
│                      │             │                      │
│  Measure latency     │ ──────────► │  Respond             │
│                      │             │                      │
│  Download test       │ ◄────────── │  Send test data      │
│                      │             │                      │
│  Upload test         │ ──────────► │  Receive test data    │
│                      │             │                      │
└──────────────────────┘             └──────────────────────┘
```

The server listens for connections while the client performs the requested network tests.

LANSpeed is intended for **local networks and authorized testing environments**.

---

## 📋 Requirements

* **Python 3.9+**
* Two devices connected to the same LAN
* Network connectivity between the devices
* Firewall access to the LANSpeed server port

By default, LANSpeed uses:

```text
0.0.0.0:8765
```

---

## 📦 Installation

Clone the repository:

```powershell
git clone https://github.com/ItsWanheda/lanspeed.git
cd lanspeed
```

Install LANSpeed in editable mode:

```powershell
py -m pip install -e .
```

Verify the installation:

```powershell
py -m lan_speed_tester --help
```

You can also run LANSpeed directly from the source tree.

---

# 🚀 Quick Start

## 1. Start the Server

On the device you want to test against:

```powershell
py -m lan_speed_tester server
```

You should see:

```text
LANSpeed server listening on 0.0.0.0:8765
Press Ctrl+C to stop.
```

---

# 2.🌐 Find Your LAN IP Address

Before running a LANSpeed test, you need the **local IP address of the machine running the server**.

## Windows

Open PowerShell or Command Prompt:

```powershell
ipconfig
```

Look for the network adapter you are currently using and find:

```text
IPv4 Address
```

For example:

```text
Wireless LAN adapter Wi-Fi:

   IPv4 Address. . . . . . . . . . : 192.168.1.34
```

In this example, the server's LAN IP address is:

```text
192.168.1.34
```

You would then run the test from another device:

```powershell
py -m lan_speed_tester test 192.168.1.34
```

> **Tip:** Ignore `127.0.0.1` — that's the loopback address and is only used to communicate with the same machine.

## Linux

Open a terminal and run:

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

Then use that address from the client:

```bash
python -m lan_speed_tester test 192.168.1.34
```

## Which IP Should I Use?

Use the IPv4 address belonging to the network interface that connects both devices to the **same LAN**.

Common private LAN addresses include:

```text
192.168.x.x
10.x.x.x
172.16.x.x - 172.31.x.x
```

For example:

```text
Server
192.168.1.34
    │
    │ LAN
    │
    ▼
Client
192.168.1.38
```

The client should connect to:

```text
192.168.1.34
```

Do **not** use:

```text
127.0.0.1
```

when the client and server are on different devices.

---

## 3. Run a Speed Test

From another device on the same LAN:

```powershell
py -m lan_speed_tester test 192.168.1.10
```

Replace:

```text
192.168.1.10
```

with the LAN IP address of your server.

A complete test includes:

```text
Latency
   ↓
Download
   ↓
Upload
   ↓
Results
```

---

# 🧪 Individual Tests

LANSpeed also supports running individual measurements.

### Latency

```powershell
py -m lan_speed_tester ping 192.168.1.10
```

### Download

```powershell
py -m lan_speed_tester download 192.168.1.10
```

### Upload

```powershell
py -m lan_speed_tester upload 192.168.1.10
```

---

# 🧾 JSON Output

Use `--json` when integrating LANSpeed with scripts, monitoring tools, or other automation:

```powershell
py -m lan_speed_tester test 192.168.1.10 --json
```

Example:

```json
{
  "host": "192.168.1.10",
  "port": 8765,
  "latency": {},
  "download": {},
  "upload": {}
}
```

The JSON interface is intended to make LANSpeed easy to integrate into other tools and workflows.

---

# ⚙️ Configuration

LANSpeed supports configurable testing parameters such as:

* Server host
* Server port
* Test duration
* Transfer chunk size
* Socket timeout

The default server port is:

```text
8765
```

---

# 🛠️ Development

Clone the repository and install it in editable mode:

```powershell
py -m pip install -e .
```

Run the test suite:

```powershell
py -m unittest discover -s tests -v
```

Run basic syntax checks:

```powershell
py -m py_compile src\lan_speed_tester\protocol.py
py -m py_compile src\lan_speed_tester\client.py
py -m py_compile src\lan_speed_tester\server.py
```

---

## 🏗️ Building the Standalone Client

LANSpeed can be packaged as a standalone Windows executable using PyInstaller.

The project includes:

```text
launcher.py
```

Build the client:

```powershell
py -m PyInstaller --clean --onefile --name lanspeed-client --paths src launcher.py
```

The resulting executable will be placed in:

```text
dist/lanspeed-client.exe
```

Run it with:

```powershell
.\lanspeed-client.exe test 192.168.1.10
```

---

# 🗺️ Roadmap

### Core

* [x] Project foundation
* [x] TCP client/server architecture
* [x] TCP latency measurement
* [x] Download throughput testing
* [x] Upload throughput testing
* [x] Framed TCP transfer protocol
* [x] Configurable test duration
* [x] JSON output

### Planned

* [ ] Rich terminal output
* [ ] JSON/CSV export improvements
* [ ] UDP packet-loss testing
* [ ] Jitter measurement
* [ ] Multi-stream throughput
* [ ] Network interface discovery
* [ ] Historical test results
* [ ] More detailed network statistics
* [ ] Automated test reporting

---

# 🔐 Security

LANSpeed is a network testing utility, **not an authentication or security boundary**.

For security information and responsible vulnerability reporting, see:

**[SECURITY.md](SECURITY.md)**

Only run LANSpeed against networks and systems you are authorized to test.

---

# 🤝 Contributing

Contributions are welcome.

Before submitting a pull request, please read:

**[CONTRIBUTING.md](CONTRIBUTING.md)**

For community standards, see:

**[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)**

---

# 📄 License

LANSpeed is released under the **MIT License**.

See [LICENSE](LICENSE) for the full license text.

---

<div align="center">

**LANSpeed**

*Measure your LAN. Understand your network.*

Made with 🐍 Python

</div>
