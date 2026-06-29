"""Unit tests for Kubernetes collectors (mocked kubectl)."""

from __future__ import annotations

import json
from unittest.mock import patch

from src.services.autodiscover.discovery.collectors.kubernetes_collector import (
    kubernetes_services,
    kubernetes_workloads,
)

POD_JSON = {
    "items": [
        {
            "metadata": {"name": "api-pod", "namespace": "prod", "labels": {"app": "api"}},
            "status": {"phase": "Running", "podIP": "10.42.0.5"},
            "spec": {
                "containers": [
                    {"name": "api", "image": "registry.example/api:1.0", "env": [{"name": "PORT", "value": "8080"}]},
                ],
            },
        },
    ],
}

SVC_JSON = {
    "items": [
        {
            "metadata": {"name": "postgres", "namespace": "prod"},
            "spec": {"clusterIP": "10.43.0.8"},
        },
    ],
}


@patch("src.services.autodiscover.discovery.collectors.kubernetes_collector.run_cmd")
def test_kubernetes_workloads_parses_running_pods(mock_run_cmd):
    mock_run_cmd.return_value = (json.dumps(POD_JSON), None)

    items, err = kubernetes_workloads()

    assert err is None
    assert len(items) == 1
    assert items[0]["name"] == "api"
    assert items[0]["k8s_namespace"] == "prod"
    assert items[0]["entity_type"] == "Application"


@patch("src.services.autodiscover.discovery.collectors.kubernetes_collector.run_cmd")
def test_kubernetes_workloads_returns_error_when_kubectl_missing(mock_run_cmd):
    mock_run_cmd.return_value = (None, "kubectl not found")

    items, err = kubernetes_workloads()

    assert items is None
    assert err == "kubectl not found"


@patch("src.services.autodiscover.discovery.collectors.kubernetes_collector.run_cmd")
def test_kubernetes_services_builds_index(mock_run_cmd):
    mock_run_cmd.return_value = (json.dumps(SVC_JSON), None)

    index, services = kubernetes_services()

    assert len(services) == 1
    assert services[0]["entity_type"] == "Database"
    assert index["postgres"] == "prod/postgres"
