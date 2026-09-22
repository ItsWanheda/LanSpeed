# 🤝 Contributing to LANSpeed

Thank you for your interest in contributing to **LANSpeed**! ❤️

LANSpeed is an open-source LAN network performance testing tool built around a lightweight **TCP client/server architecture**. The project focuses on making network testing **simple, reliable, transparent, and easy to understand**.

Whether you're fixing a bug, improving the protocol, writing tests, or simply improving the documentation — every contribution is welcome.

### Ways You Can Contribute

* 🐛 **Bug fixes**
* ✨ **New features**
* 🔌 **Protocol improvements**
* ⚡ **Performance optimizations**
* 🧪 **Tests and reliability improvements**
* 📚 **Documentation**
* 🛠️ **Build and packaging improvements**
* 🔄 **CI/CD improvements**
* 💡 **Ideas and technical discussions**

---

## 🧭 Before You Start

For significant architectural or behavioral changes, please consider opening an issue first.

This gives us a chance to discuss:

* The problem being solved
* The proposed approach
* Compatibility implications
* Possible alternatives
* Whether the change fits LANSpeed's direction

For smaller changes, opening an issue beforehand is usually unnecessary.

Examples include:

* Documentation fixes
* Typo corrections
* Minor improvements
* Obvious bug fixes
* Small test additions

> 💡 **When in doubt, open an issue.** A short discussion can save a lot of unnecessary work.

---

# 🛠️ Development Setup

LANSpeed is written in **Python** and keeps its core networking implementation lightweight by relying primarily on the Python standard library.

## 1. Clone the Repository

```bash
git clone https://github.com/ItsWanheda/lanspeed.git
cd lanspeed
```

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

## 3. Activate the Environment

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
source .venv/bin/activate
```

## 4. Install the Project

If supported by the current project configuration:

```bash
python -m pip install -e .
```

Upgrade packaging tools when necessary:

```bash
python -m pip install --upgrade pip
```

---

# 📁 Project Structure

LANSpeed follows a `src/` package layout:

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
│       └── metrics.py
│
├── tests/
│   ├── test_cli.py
│   └── test_package.py
│
├── launcher.py
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── SECURITY.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
└── LICENSE
```

### Core Components

| Component     | Responsibility                            |
| :------------ | :---------------------------------------- |
| `client.py`   | Client-side network testing and transfers |
| `server.py`   | TCP server and request handling           |
| `protocol.py` | Message framing and protocol operations   |
| `metrics.py`  | Performance and throughput calculations   |
| `cli.py`      | Command-line interface                    |
| `__main__.py` | `python -m lan_speed_tester` entry point  |
| `launcher.py` | PyInstaller executable entry point        |
| `tests/`      | Automated project tests                   |

---

# 🌿 Creating a Branch

Avoid working directly on `main`.

Create a dedicated branch for your change.

### ✨ Feature

```bash
git checkout -b feature/my-feature
```

### 🐛 Bug Fix

```bash
git checkout -b fix/my-bug
```

### 📚 Documentation

```bash
git checkout -b docs/improve-documentation
```

### ⚡ Performance

```bash
git checkout -b perf/improve-throughput
```

Choose a short, descriptive branch name that explains the purpose of the work.

---

# 🔧 Making Changes

Keep each change **focused and intentional**.

A good pull request should ideally solve one problem or introduce one clearly defined improvement.

### Prefer

* Small, understandable changes
* Clear function and variable names
* Minimal unrelated modifications
* Reusable logic
* Explicit error handling
* Tests for changed behavior

### Avoid

* Unrelated refactoring
* Large formatting-only changes
* Temporary debugging code
* Unnecessary dependencies
* Breaking existing behavior without discussion

> 🎯 **Simple code is a feature.** LANSpeed should remain easy to read, debug, test, and maintain.

---

# 🧪 Testing

Before opening a pull request, run the relevant checks locally.

## Syntax Checks

For example:

```bash
python -m py_compile src/lan_speed_tester/protocol.py
python -m py_compile src/lan_speed_tester/client.py
python -m py_compile src/lan_speed_tester/server.py
```

## Test Suite

If the project test suite is available:

```bash
python -m pytest
```

Or, when using the standard-library test runner:

```bash
python -m unittest discover -s tests -v
```

## Package Check

Verify that the package can be imported:

```bash
python -c "import lan_speed_tester; print('Import OK')"
```

## CLI Check

Verify that the CLI starts correctly:

```bash
python -m lan_speed_tester --help
```

---

# 🌐 Network & Integration Testing

Changes involving networking should be tested with **both the client and server**.

A typical LANSpeed flow looks like:

```text
                    LAN
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌───────────────┐         ┌───────────────┐
│     Client    │◄───────►│     Server    │
│               │   TCP   │               │
│  latency      │         │  protocol     │
│  download     │         │  transfers    │
│  upload       │         │  validation   │
└───────────────┘         └───────────────┘
```

For protocol-related changes, verify at minimum:

* Successful connection
* Handshake behavior
* Latency measurement
* Download transfers
* Upload transfers
* Transfer completion
* Invalid input handling
* Connection failures
* Clean connection shutdown

Where practical, test across the operating systems supported by the project.

---

# 🔌 Protocol Testing

Protocol changes require additional care because LANSpeed communicates over TCP between separate processes and potentially different machines.

When modifying the protocol:

1. Update both client and server behavior.
2. Document the change.
3. Consider protocol-version compatibility.
4. Validate message lengths before processing.
5. Test malformed messages.
6. Test unexpected message sequences.
7. Test partial TCP reads.
8. Test both successful and failed transfers.
9. Verify that connections close cleanly after protocol errors.

---

## ⚠️ TCP Is a Byte Stream

Never assume that a single `recv()` call represents one complete message.

TCP provides a **byte stream**, not message boundaries.

For example, one `recv()` may return:

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

LANSpeed therefore relies on **explicit message framing** to determine where protocol messages and transfer chunks begin and end.

Any protocol implementation must correctly handle:

* Partial reads
* Multiple messages in one read
* Unexpected message boundaries
* Zero-length frames
* Oversized messages
* Invalid lengths
* Connection termination

> 🧠 If your protocol code assumes `recv()` returns exactly what was requested, it probably needs another look.

---

# 🛡️ Safe Network Testing

LANSpeed should only be used on systems and networks where you have permission to perform testing.

When developing or testing the project:

* Prefer a controlled LAN environment.
* Use systems you own or are authorized to test.
* Avoid exposing development servers to the public Internet.
* Test malformed input safely.
* Verify oversized messages are rejected.
* Verify invalid protocol sequences are handled safely.
* Confirm resources are released after failed connections.

Do not use LANSpeed to disrupt networks or systems without authorization.

For security-related concerns, see [`SECURITY.md`](SECURITY.md).

---

# 📊 Performance Changes

LANSpeed is a network performance testing tool, so performance-related changes should be measured rather than assumed.

When modifying performance-sensitive code, consider documenting:

* Test environment
* Client/server hardware
* Operating system
* Python version
* Network connection
* Transfer size
* Test duration
* Before/after results

For example:

```text
Environment:
- Client: Windows
- Server: Linux
- Network: Gigabit Ethernet
- Python: 3.x

Result:
- Before:  ~720 Mbps
- After:   ~910 Mbps
```

> 📈 Reproducible measurements are more useful than “this feels faster.”

---

# 🔀 Pull Requests

Before opening a pull request, make sure you have:

* [ ] Tested the changes locally
* [ ] Run the relevant test suite
* [ ] Reviewed the final diff
* [ ] Removed debugging code
* [ ] Removed temporary files
* [ ] Checked for accidentally committed secrets
* [ ] Updated documentation where necessary
* [ ] Updated the changelog when appropriate
* [ ] Used a clear commit message

A good pull request should explain:

### What changed?

Describe the implementation.

### Why?

Explain the problem or motivation.

### How was it tested?

List the tests, commands, or environments used.

### Compatibility

Mention any:

* Protocol changes
* CLI changes
* Configuration changes
* Python version considerations
* Backward-compatibility concerns

---

# 📝 Commit Messages

LANSpeed uses a simple Conventional Commits-style format:

```text
type(scope): description
```

### Examples

```text
feat(client): add configurable transfer duration
fix(protocol): validate control message size
fix(client): handle framed upload transfers
fix(server): reject invalid transfer chunks
perf(metrics): reduce throughput calculation overhead
test(protocol): add malformed frame tests
docs: improve contributing guide
build: add PyInstaller launcher
ci: add Python test matrix
```

## Common Types

| Type       | Purpose                    |
| :--------- | :------------------------- |
| `feat`     | New functionality          |
| `fix`      | Bug fix                    |
| `docs`     | Documentation              |
| `refactor` | Code restructuring         |
| `test`     | Tests                      |
| `perf`     | Performance improvements   |
| `build`    | Build or packaging changes |
| `ci`       | Continuous integration     |
| `chore`    | Maintenance                |

Keep commit messages:

* Concise
* Specific
* Written in the imperative style where practical
* Focused on the actual change

---

# 🧹 Code Quality

When contributing code, prefer:

* Clear and descriptive names
* Small, focused functions
* Explicit error handling
* Type hints where they improve clarity
* Predictable control flow
* Standard-library solutions where practical
* Minimal dependencies
* Comments that explain **why**, not obvious **what**

Avoid introducing complexity unless it provides a clear benefit.

LANSpeed should remain:

> **Simple enough to understand. Reliable enough to trust. Flexible enough to extend.**

---

# 📚 Documentation

Documentation improvements are always welcome. 📖

Useful contributions include:

* README improvements
* Installation instructions
* Usage examples
* Troubleshooting guides
* Architecture documentation
* Protocol documentation
* API or implementation notes
* Security documentation
* Configuration documentation

If a code change affects user-facing behavior, update the relevant documentation whenever appropriate.

---

# 🐛 Reporting Bugs

When reporting a bug, provide enough information to reproduce it.

Please include:

* **Operating system**
* **Python version**
* **LANSpeed version or commit**
* **Client configuration**
* **Server configuration**
* **Steps to reproduce**
* **Expected behavior**
* **Actual behavior**
* **Relevant logs**
* **Tracebacks**, if available

For networking issues, also include relevant test-environment details such as:

* Client operating system
* Server operating system
* Connection type
* Approximate network topology
* Relevant configuration

You do **not** need to expose sensitive network information.

---

## 🔐 Remove Sensitive Information

Before opening an issue or pull request, make sure you have removed:

* Passwords
* API tokens
* Private keys
* Credentials
* Authentication data
* Sensitive configuration
* Private network information that should not be disclosed

Never commit secrets to the repository.

---

# 🛡️ Security Vulnerabilities

Please **do not publicly disclose sensitive vulnerability details through GitHub Issues or pull requests**.

If you believe you have discovered a security vulnerability, follow the reporting process described in [`SECURITY.md`](SECURITY.md).

Security reports should contain enough technical information to reproduce and investigate the issue while avoiding unnecessary public disclosure.

---

# 📦 Build & Packaging

LANSpeed can also be packaged as a standalone executable using PyInstaller.

The project uses:

```text
launcher.py
```

as the executable entry point.

When modifying packaging or build behavior:

* Verify the source package still works.
* Test the generated executable.
* Check imports and bundled modules.
* Test the executable on the intended platform.
* Avoid committing generated build artifacts unless explicitly required.

For example:

```bash
python -m PyInstaller --clean --onefile --name lanspeed-client --paths src launcher.py
```

Generated files should normally remain outside version control according to `.gitignore`.

---

# 🔄 Keeping Your Branch Updated

Before opening or updating a pull request, synchronize your branch with `main` when appropriate.

For example:

```bash
git fetch origin
git rebase origin/main
```

Resolve conflicts carefully and run the relevant tests again afterward.

If you're unsure about rebasing, using a merge is also acceptable:

```bash
git fetch origin
git merge origin/main
```

---

# 🤝 Code Review

Pull requests may be reviewed for:

* Correctness
* Reliability
* Readability
* Test coverage
* Performance
* Security
* Protocol compatibility
* Documentation
* Long-term maintainability

Review feedback is intended to improve the project, not the person submitting the contribution.

Please keep discussions technical, constructive, and respectful.

---

# 🌱 First-Time Contributors

New to open source? You're welcome here. ❤️

Good starting points include:

* Fixing documentation
* Improving examples
* Adding tests
* Fixing small bugs
* Improving error messages
* Improving CLI usability
* Adding troubleshooting information

If an issue is marked as beginner-friendly or documentation-related, it may be a good place to start.

You don't need to know everything about networking before contributing.

---

# 📋 Contribution Checklist

Before submitting your contribution:

```text
[ ] I created a focused branch
[ ] I understand the change I'm making
[ ] I tested the affected functionality
[ ] I ran the relevant test suite
[ ] I reviewed my git diff
[ ] I removed debugging code
[ ] I did not commit secrets
[ ] I updated documentation if necessary
[ ] I considered compatibility implications
[ ] My commit messages are clear
[ ] My pull request explains what, why, and how
```

---

# ❤️ Thank You

Every contribution helps make LANSpeed more **reliable, maintainable, and useful**.

Whether you're fixing a typo, improving the TCP protocol, adding tests, optimizing performance, improving the CLI, or building a larger feature — thank you for helping make LANSpeed better.

**Happy hacking. 🚀**

---

> **LANSpeed is built in the open, one packet at a time.** ⚡
