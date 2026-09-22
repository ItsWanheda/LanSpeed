# 🤝 Contributing to LANSpeed

Thank you for your interest in contributing to **LANSpeed**!

LANSpeed is an open-source LAN network speed testing tool focused on **simple, reliable, and transparent network performance testing**.

Contributions are welcome, including:

* 🐛 Bug fixes
* 🔌 Protocol improvements
* 📚 Documentation
* 🧪 Testing
* ⚡ Performance improvements
* ✨ New features

---

## 🚀 Before You Start

Before making a large or architectural change, consider opening an issue to discuss the idea first.

For small changes such as:

* Documentation updates
* Typo fixes
* Minor improvements
* Obvious bug fixes

opening an issue beforehand is usually not necessary.

---

## 🛠️ Development Setup

LANSpeed uses **Python** and the **standard library** for its core networking functionality.

### 1. Clone the Repository

```bash
git clone https://github.com/ItsWanheda/lanspeed.git
cd lanspeed
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### 4. Install the Project

If supported by the current project configuration:

```bash
python -m pip install -e .
```

---

## 📁 Project Structure

The main source code is located under `src/`:

```text
src/
└── lan_speed_tester/
    ├── client.py
    ├── server.py
    ├── protocol.py
    ├── metrics.py
    ├── cli.py
    └── __main__.py
```

The PyInstaller entry point is:

```text
launcher.py
```

---

## 🔧 Making Changes

Create a dedicated branch for your change.

### Feature

```bash
git checkout -b feature/my-change
```

### Bug Fix

```bash
git checkout -b fix/my-bug
```

Keep changes focused.

Avoid mixing unrelated refactoring with bug fixes unless the refactoring is necessary for the change.

---

## 🧪 Testing

Before submitting a pull request, run the relevant checks.

### Syntax Checks

```bash
python -m py_compile src/lan_speed_tester/protocol.py
python -m py_compile src/lan_speed_tester/client.py
python -m py_compile src/lan_speed_tester/server.py
```

### Project Tests

If the test suite is available:

```bash
python -m pytest
```

### Network Protocol Testing

For network or protocol changes, test **both sides of the connection**.

A typical LANSpeed test flow is:

```text
┌──────────────┐
│    Server    │
└──────┬───────┘
       │
       ▼
     HELLO
       │
       ▼
    LATENCY
       │
       ▼
   DOWNLOAD
       │
       ▼
     UPLOAD
       │
       ▼
      DONE
```

Protocol changes should be tested with both the client and server using the same protocol version.

---

## 🌐 Network Testing

LANSpeed should only be used on networks and systems where you have permission to perform testing.

When testing protocol changes:

* Use a controlled LAN environment where possible.
* Test malformed input where appropriate.
* Verify that oversized messages are rejected safely.
* Verify that connections close cleanly after protocol errors.
* Avoid exposing development servers to the public Internet.
* Test both valid and invalid protocol sequences.

---

## 🔀 Pull Requests

Before opening a pull request:

* Make sure your branch is up to date.
* Run the relevant tests.
* Review your changes.
* Remove debugging code.
* Make sure sensitive information is not committed.
* Write a clear pull request description.

A good pull request should explain:

* **What changed**
* **Why it changed**
* **How it was tested**
* **Any compatibility considerations**

For protocol or networking changes, include details about the environments used for testing when relevant.

---

## 📝 Commit Messages

Use clear and descriptive commit messages.

LANSpeed follows a conventional format:

```text
type(scope): description
```

### Examples

```text
fix(protocol): validate control message size
fix(client): handle framed upload transfers
fix(server): reject invalid transfer chunks
docs: improve contributing guide
build: add PyInstaller launcher
```

### Common Types

| Type       | Purpose                    |
| ---------- | -------------------------- |
| `feat`     | New functionality          |
| `fix`      | Bug fix                    |
| `docs`     | Documentation              |
| `refactor` | Code restructuring         |
| `test`     | Tests                      |
| `build`    | Build or packaging changes |
| `ci`       | Continuous integration     |
| `perf`     | Performance improvements   |
| `chore`    | Maintenance                |

Keep commit messages concise and focused on the actual change.

---

## 💻 Code Style

When contributing code, prefer:

* Clear and descriptive names
* Small, focused functions
* Explicit error handling
* Type hints where useful
* Standard-library solutions where practical
* Comments that explain **why** something is necessary

Avoid unnecessary complexity.

LANSpeed should remain **easy to understand, test, maintain, and extend**.

---

## 🔌 Protocol Changes

Protocol changes require additional care because LANSpeed communicates over TCP between separate processes and machines.

If you modify the TCP protocol:

1. Update both the client and server.
2. Document the protocol change.
3. Consider protocol-version compatibility.
4. Test partial TCP reads and writes.
5. Validate message and transfer lengths before processing them.
6. Test malformed and unexpected input.
7. Test both successful and failed transfers.

### ⚠️ Important TCP Rule

Never assume that one `recv()` call contains one complete message.

TCP is a **byte stream**, not a message-oriented protocol.

For example, a single `recv()` may contain:

```text
[partial message]
```

or:

```text
[message A][message B]
```

or:

```text
[partial A][remaining A][partial B]
```

Protocol implementations should therefore use explicit framing and reliably handle partial reads.

---

## 📚 Documentation

Documentation improvements are always welcome.

Useful contributions include:

* README improvements
* Installation instructions
* Troubleshooting guides
* Usage examples
* Architecture documentation
* Protocol documentation
* Security documentation

If a code change affects user-facing behavior, update the relevant documentation when appropriate.

---

## 🐛 Reporting Issues

When reporting a bug, include as much useful information as possible.

Please provide:

* **Operating system**
* **Python version**
* **LANSpeed version or commit**
* **Client/server configuration**
* **Steps to reproduce**
* **Expected behavior**
* **Actual behavior**
* **Relevant logs or traceback**

For networking issues, also include relevant information about the test environment when useful, such as whether the client and server were running on Windows or Linux.

### 🔐 Remove Sensitive Information

Before posting an issue, remove:

* Passwords
* API tokens
* Private keys
* Credentials
* Private or sensitive IP addresses
* Other confidential information

Do not commit secrets or sensitive configuration files to the repository.

---

## 🛡️ Security Issues

Please **do not publicly disclose sensitive vulnerability details** in a GitHub issue.

For security vulnerabilities, follow the reporting process described in [`SECURITY.md`](SECURITY.md).

---

## ❤️ Thank You

Every contribution helps make LANSpeed more reliable, maintainable, and useful.

Whether you're fixing a typo, improving the protocol, adding tests, or working on a larger feature — thank you for contributing to LANSpeed! 🚀
