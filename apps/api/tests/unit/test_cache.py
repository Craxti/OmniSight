from src.core.cache import cache_backend, cache_get, cache_invalidate_prefix, cache_set, cache_stats, cached
from src.core.config import settings


def test_cache_roundtrip_memory(monkeypatch):
    monkeypatch.setattr(settings, "cache_enabled", True)
    monkeypatch.setattr(settings, "redis_url", "")
    cache_set("unit:test", {"ok": True}, ttl=60)
    assert cache_get("unit:test") == {"ok": True}
    cache_invalidate_prefix("unit:")
    assert cache_get("unit:test") is None


def test_memory_cache_expires(monkeypatch):
    import src.core.cache as cache_mod

    monkeypatch.setattr(settings, "cache_enabled", True)
    monkeypatch.setattr(settings, "redis_url", "")
    cache_mod._store.clear()
    cache_mod._memory_set("unit:expired", {"gone": True}, ttl=-1)
    assert cache_mod._memory_get("unit:expired") is None
    assert "unit:expired" not in cache_mod._store


def test_cached_decorator_uses_memory(monkeypatch):
    import src.core.cache as cache_mod

    monkeypatch.setattr(settings, "cache_enabled", True)
    monkeypatch.setattr(settings, "redis_url", "")
    cache_mod._store.clear()
    calls = {"n": 0}

    @cached(ttl=60, key_fn=lambda value: f"unit:decorator:{value}")
    def expensive(value: int) -> int:
        calls["n"] += 1
        return value * 2

    assert expensive(3) == 6
    assert expensive(3) == 6
    assert calls["n"] == 1


def test_cache_disabled_skips_storage(monkeypatch):
    monkeypatch.setattr(settings, "cache_enabled", False)
    cache_set("unit:disabled", {"ok": True}, ttl=60)
    assert cache_get("unit:disabled") is None
    assert cache_backend() == "disabled"


def test_pydantic_serialize_roundtrip(monkeypatch):
    import src.core.cache as cache_mod
    from pydantic import BaseModel

    class SampleModel(BaseModel):
        label: str

    monkeypatch.setattr(settings, "cache_enabled", True)
    monkeypatch.setattr(settings, "redis_url", "")
    cache_mod._store.clear()
    model = SampleModel(label="cached")
    cache_mod._memory_set("unit:pydantic", model, ttl=60)
    restored = cache_mod._memory_get("unit:pydantic")
    assert restored.label == "cached"


def test_postgres_cache_invalidate_prefix(monkeypatch):
    from src.core.cache import _postgres_invalidate_prefix_db, _postgres_set_db

    stored: dict[str, dict[str, float | str]] = {}

    class FakeRow:
        def __init__(self, key: str, value_blob: str, expires_at: float):
            self.key = key
            self.value_blob = value_blob
            self.expires_at = expires_at

    class FakeQuery:
        def __init__(self, model):
            self._model = model

        def filter(self, *_args, **_kwargs):
            return self

        def delete(self, **_kwargs):
            for key in list(stored):
                if key.startswith("unit:"):
                    stored.pop(key)
            return len(stored)

    class FakeSession:
        def get(self, _model, key):
            row = stored.get(key)
            if not row:
                return None
            return FakeRow(key, str(row["blob"]), float(row["expires_at"]))

        def add(self, row):
            stored[row.key] = {"blob": row.value_blob, "expires_at": row.expires_at}

        def query(self, model):
            return FakeQuery(model)

        def commit(self):
            pass

    fake = FakeSession()
    _postgres_set_db(fake, "unit:keep", {"ok": True}, ttl=120)
    _postgres_set_db(fake, "unit:drop", {"ok": True}, ttl=120)
    _postgres_invalidate_prefix_db(fake, "unit:")
    assert stored == {}


def test_cache_stats_reports_backend(monkeypatch):
    monkeypatch.setattr(settings, "cache_enabled", True)
    stats = cache_stats()
    assert stats["backend"] in ("memory", "postgres", "disabled")
    assert "enabled" in stats
    assert cache_backend() in ("memory", "postgres", "disabled")


def test_postgres_cache_uses_utc_expiry(monkeypatch):
    from datetime import UTC, datetime, timedelta

    from src.core.cache import _postgres_get_db, _postgres_set_db, _utc_timestamp

    stored: dict[str, dict[str, float | str]] = {}

    class FakeRow:
        def __init__(self, key: str, value_blob: str, expires_at: float):
            self.key = key
            self.value_blob = value_blob
            self.expires_at = expires_at

    class FakeSession:
        def get(self, _model, key):
            row = stored.get(key)
            if not row:
                return None
            return FakeRow(key, str(row["blob"]), float(row["expires_at"]))

        def delete(self, row):
            stored.pop(row.key, None)

        def add(self, row):
            stored[row.key] = {"blob": row.value_blob, "expires_at": row.expires_at}

        def commit(self):
            pass

    fake = FakeSession()
    _postgres_set_db(fake, "unit:utc", {"ok": True}, ttl=120)
    assert stored["unit:utc"]["expires_at"] > _utc_timestamp()

    stored["unit:utc"]["expires_at"] = (datetime.now(UTC) - timedelta(seconds=1)).timestamp()
    assert _postgres_get_db(fake, "unit:utc") is None
