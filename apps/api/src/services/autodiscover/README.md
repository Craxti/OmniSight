# Autodiscover module

Auto-discovery pipeline: scan hosts, infer CI/relations, review draft mapping, apply to inventory.

## Layout

```
services/autodiscover/
├── discovery/          # Collectors + inference (SSH, Docker, K8s, systemd)
├── connectors/         # External sync connector registry
├── runtime/            # Async orchestration (scan, apply, auto-sync, seed)
├── apply_ci.py         # Map entity → CI row
├── scope.py            # Scan scope resolution
├── serializers.py      # API response helpers
└── …

services/async_read/autodiscover.py   # HTTP read adapter
services/async_write/autodiscover.py  # HTTP write adapter
services/domain/autodiscover.py       # Shared list/summary builders
```

## Flow

```
POST /scan → runtime/scan → discovery/collectors → inference
GET  /runs/{id} → draft CIs + proposed relations
POST /runs/{id}/apply → runtime/apply_run → apply_ci + relations + audit
```

## When extending

1. Add collector logic under `discovery/collectors/`.
2. Add async orchestration under `runtime/` — not a separate top-level package.
3. Multi-step apply uses transactional write pool (`get_transactional_autodiscover_write_port`).

## Testing

- Unit: `tests/unit/test_autodiscover_*.py`, collector tests
- Integration: `tests/test_autodiscover.py`
