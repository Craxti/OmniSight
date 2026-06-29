"""IP address format validation (IPv4 and IPv6)."""

from __future__ import annotations

import ipaddress


def is_valid_ip_address(value: str) -> bool:
    """Return True for empty/whitespace (optional field) or a valid IP literal."""
    text = value.strip()
    if not text:
        return True
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]
    try:
        ipaddress.ip_address(text)
    except ValueError:
        return False
    return True


def require_valid_ip_address(value: str, *, field: str = "ip") -> None:
    if not is_valid_ip_address(value):
        raise ValueError(f"Invalid {field} address: {value}")
