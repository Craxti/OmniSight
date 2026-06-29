"""Shared domain read logic: serializers, response builders, query orchestration.

Not a sync I/O layer — these modules are transport-agnostic helpers used by
``services/async_read/*`` adapters and occasionally by handlers/write services.
Import submodules directly (``from src.services.domain.search import ...``).
"""
