"""Best-effort local network interface discovery.

Detailed per-interface addresses and link metadata are available when the
optional psutil package is installed. The standard-library fallback reports
interface names and local addresses without guessing which address belongs
to which interface.
"""

from __future__ import annotations

import socket
from typing import Any


def discover_interfaces() -> dict[str, Any]:
    """Return local interface metadata using psutil when available."""
    try:
        import psutil  # type: ignore[import-not-found]
    except ImportError:
        return _standard_library_interfaces()

    interfaces = []
    stats = psutil.net_if_stats()
    addresses = psutil.net_if_addrs()
    for name, entries in addresses.items():
        stat = stats.get(name)
        ip_addresses = []
        mac_address = None
        for entry in entries:
            family_name = getattr(entry.family, "name", str(entry.family))
            if family_name in ("AF_INET", "AF_INET6"):
                ip_addresses.append({
                    "family": family_name,
                    "address": entry.address.split("%", 1)[0],
                    "netmask": entry.netmask,
                    "broadcast": entry.broadcast,
                })
            elif family_name in ("AF_LINK", "AF_PACKET"):
                mac_address = entry.address or None
        interfaces.append({
            "name": name,
            "is_up": bool(stat.isup) if stat else None,
            "mtu": stat.mtu if stat else None,
            "speed_mbps": stat.speed if stat and stat.speed > 0 else None,
            "mac_address": mac_address,
            "addresses": ip_addresses,
        })

    return {
        "source": "psutil",
        "detail_level": "per-interface",
        "interfaces": interfaces,
    }


def _standard_library_interfaces() -> dict[str, Any]:
    names = []
    try:
        names = [
            {"index": index, "name": name}
            for index, name in socket.if_nameindex()
        ]
    except (AttributeError, OSError):
        pass

    addresses = []
    try:
        for info in socket.getaddrinfo(
            socket.gethostname(),
            None,
            type=socket.SOCK_DGRAM,
        ):
            family, _, _, _, sockaddr = info
            address = sockaddr[0].split("%", 1)[0]
            family_name = "IPv6" if family == socket.AF_INET6 else "IPv4"
            item = {"family": family_name, "address": address}
            if item not in addresses:
                addresses.append(item)
    except OSError:
        pass

    return {
        "source": "python-standard-library",
        "detail_level": "best-effort-host-addresses",
        "interfaces": names,
        "host_addresses": addresses,
        "note": (
            "Install the optional 'network' extra for per-interface IP, "
            "MAC, link state, MTU, and link-speed details."
        ),
    }
