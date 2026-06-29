"""Tests for IP address validation."""

import pytest
from src.core.ip_validation import is_valid_ip_address


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
        "10.0.0.1",
        "192.168.1.255",
        "0.0.0.0",
        "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
        "::1",
        "[::1]",
    ],
)
def test_valid_ip_addresses(value: str) -> None:
    assert is_valid_ip_address(value) is True


@pytest.mark.parametrize(
    "value",
    [
        "999.1.1.1",
        "10.0.0",
        "not-an-ip",
        "gggg::1",
    ],
)
def test_invalid_ip_addresses(value: str) -> None:
    assert is_valid_ip_address(value) is False
