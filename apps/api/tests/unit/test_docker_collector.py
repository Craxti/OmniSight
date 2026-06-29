"""Unit tests for docker container collector."""

from __future__ import annotations

from unittest.mock import patch

from src.services.autodiscover.discovery.collectors.docker_collector import docker_containers


@patch("src.services.autodiscover.discovery.collectors.docker_collector.run_docker")
def test_docker_containers_parses_ps_output(mock_run_docker):
    mock_run_docker.return_value = (
        "api\tregistry.example/api:1.0\t0.0.0.0:8080->8080/tcp\n",
        None,
    )

    items, err = docker_containers()

    assert err is None
    assert len(items) == 1
    assert items[0]["name"] == "api"
    assert items[0]["entity_type"] == "Application"
    assert items[0]["ports"] == [8080]


@patch("src.services.autodiscover.discovery.collectors.docker_collector.run_docker")
def test_docker_containers_returns_error_when_docker_missing(mock_run_docker):
    mock_run_docker.return_value = (None, "docker: not found")

    items, err = docker_containers()

    assert items is None
    assert err == "docker: not found"
