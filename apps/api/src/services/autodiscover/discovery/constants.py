"""Shared constants and regexes for host discovery."""

from __future__ import annotations

import re

APP_SUFFIXES = ("-main-api", "-main", "-api", "-service", "-app", "-worker", "-web")
DB_SUFFIXES = ("-db", "-database", "-postgres", "-mongo", "-redis", "-mysql")

URL_HOST_RE = re.compile(
    r"(?:jdbc:[^:/]+://|(?:postgres|mysql|mongodb|redis|amqp|kafka)(?:\+[^:]+)?://|https?://)([^:/?#,]+)",
    re.IGNORECASE,
)
HOST_ENV_KEY_RE = re.compile(
    r"^(?:[A-Z0-9_]*(?:HOST|HOSTNAME|ADDR|SERVER|BROKER|BOOTSTRAP|ENDPOINT|URI|URL))$",
    re.IGNORECASE,
)
TCP_LINE_RE = re.compile(
    r"(\d{1,3}(?:\.\d{1,3}){3}|\[[\da-f:]+\]|[\da-f:]+):(\d+)\s+"
    r"(\d{1,3}(?:\.\d{1,3}){3}|\[[\da-f:]+\]|[\da-f:]+):(\d+)",
    re.IGNORECASE,
)
TCP_PROC_RE = re.compile(r'users:\(\("([^"]+)"', re.IGNORECASE)
EVIDENCE_CONFIDENCE = {
    "env": 0.96,
    "tcp": 0.94,
    "compose": 0.93,
    "compose_file": 0.92,
    "k8s_service": 0.91,
    "infra": 0.9,
    "docker_network": 0.78,
    "name": 0.72,
}
SKIP_HOSTS = frozenset({"localhost", "127.0.0.1", "0.0.0.0", "::1"})

SKIP_DOCKER_NETWORKS = frozenset({"bridge", "host", "none"})
COMPOSE_FILENAMES = (
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "docker-compose.override.yml",
)
COMPOSE_SEARCH_ROOTS = ("/opt", "/srv", "/home", "/var/www", "/etc/docker/compose")
