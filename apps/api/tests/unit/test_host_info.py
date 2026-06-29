"""Unit tests for local host metadata collection."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.services.autodiscover.discovery.collectors.host_info import host_info


def _path_mock(path_str: str) -> MagicMock:
    mock = MagicMock()
    if path_str == "/etc/hostname":
        mock.read_text.return_value = "real-host\n"
    elif path_str == "/etc/os-release":
        mock.read_text.return_value = 'PRETTY_NAME="Ubuntu 24.04 LTS"\n'
    else:
        mock.read_text.side_effect = OSError()
    return mock


@patch("src.services.autodiscover.discovery.collectors.host_info.Path")
@patch("src.services.autodiscover.discovery.collectors.host_info.subprocess.check_output")
def test_host_info_collects_metadata(mock_check_output, mock_path_cls):
    mock_check_output.side_effect = [
        "app-srv-01\n",
        "192.168.1.10 192.168.1.11\n",
    ]
    mock_path_cls.side_effect = _path_mock

    result = host_info()

    assert result["hostname"] == "app-srv-01"
    assert result["ip"] == "192.168.1.10"
    assert result["os"] == "Ubuntu 24.04 LTS"


@patch("src.services.autodiscover.discovery.collectors.host_info.Path")
@patch("src.services.autodiscover.discovery.collectors.host_info.subprocess.check_output")
def test_host_info_falls_back_when_hostname_is_localhost(mock_check_output, mock_path_cls):
    mock_check_output.side_effect = [
        "localhost\n",
        "10.0.0.2\n",
    ]
    mock_path_cls.side_effect = _path_mock

    result = host_info()

    assert result["hostname"] == "real-host"
    assert result["ip"] == "10.0.0.2"
