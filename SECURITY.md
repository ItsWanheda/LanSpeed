# 🔐 Security Policy

LANSpeed is a lightweight network performance testing tool designed for use on trusted and authorized networks.

We take security issues seriously and appreciate responsible vulnerability research and disclosure.

---

## 📦 Supported Versions

Security fixes are generally provided for the latest stable release and the current development branch.

| Version            | Supported |
| :----------------- | :-------: |
| Latest release     |     ✅     |
| Development branch |     ✅     |
| Older releases     |     ❌     |

Because LANSpeed is actively developed, users are encouraged to keep their installation up to date.

---

## 🚨 Reporting a Vulnerability

If you discover a potential security vulnerability in LANSpeed, **please do not open a public GitHub issue containing sensitive technical details.**

Instead, report the vulnerability privately through:

* GitHub's private vulnerability reporting feature, if enabled
* The project's designated security contact

### Please Include

When possible, include:

* **Vulnerability description** — What is the issue?
* **Affected version** — Which version or commit is affected?
* **Reproduction steps** — How can the issue be reproduced?
* **Proof of concept** — Include one if it is safe to share.
* **Potential impact** — What could an attacker or malicious client accomplish?
* **Suggested mitigation** — If you have an idea for a fix, include it.

Providing clear reproduction steps and technical details helps the issue get investigated more quickly.

---

## ⏱️ Responsible Disclosure

Please allow reasonable time for the vulnerability to be investigated and addressed before publicly disclosing it.

During this period, please avoid publishing:

* Exploit code for an unpatched vulnerability
* Detailed attack instructions
* Sensitive information obtained during testing
* Information that could unnecessarily put LANSpeed users at risk

We will make a reasonable effort to acknowledge and investigate valid security reports.

---

## 🛡️ Security Considerations

LANSpeed is intended for **authorized network performance testing**.

The server listens for TCP connections and accepts protocol commands from connected clients. Because of this, users should take appropriate precautions when running the server.

### Recommended Practices

* Run LANSpeed only on trusted networks.
* Use firewall rules to restrict access to trusted hosts where appropriate.
* Avoid exposing the LANSpeed server directly to the public Internet.
* Only test systems and networks you are authorized to access.
* Keep LANSpeed updated.
* Do not run the server with unnecessary system privileges.
* Review configuration before running LANSpeed on an unfamiliar network.

> **LANSpeed is a network testing utility, not a security boundary, authentication system, or secure remote-access service.**

---

## 🎯 Security Scope

Security reports may involve issues such as:

### Protocol & Network Security

* Malformed control messages
* Protocol parsing vulnerabilities
* Invalid or unexpected commands
* Unexpected TCP behavior
* Oversized transfer messages
* Improper message framing

### Resource & Availability

* Denial-of-service conditions
* Memory exhaustion
* Excessive CPU consumption
* Unbounded network resource consumption
* Connection exhaustion

### Application Security

* Unsafe file or process behavior
* Unexpected command execution
* Input validation issues
* Error-handling vulnerabilities

### Distribution & Dependencies

* Packaging vulnerabilities
* PyInstaller-related issues
* Dependency vulnerabi
