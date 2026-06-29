"""Tests for deferred-commit session helpers."""

from unittest.mock import MagicMock

from src.core.session_commit import commit_or_rollback
from src.core.session_state import is_defer_commit, set_defer_commit


class _FakeSession:
    def __init__(self) -> None:
        self.info: dict = {}
        self.flush_calls = 0
        self.commit_calls = 0
        self.rollback_calls = 0

    def flush(self) -> None:
        self.flush_calls += 1

    def commit(self) -> None:
        self.commit_calls += 1

    def rollback(self) -> None:
        self.rollback_calls += 1


def test_defer_commit_flushes_instead_of_committing():
    session = _FakeSession()
    set_defer_commit(session, defer=True)  # type: ignore[arg-type]
    assert is_defer_commit(session) is True  # type: ignore[arg-type]

    commit_or_rollback(session)  # type: ignore[arg-type]
    assert session.flush_calls == 1
    assert session.commit_calls == 0

    set_defer_commit(session, defer=False)  # type: ignore[arg-type]
    commit_or_rollback(session)  # type: ignore[arg-type]
    assert session.commit_calls == 1


def test_get_transactional_db_commits_and_clears_defer_flag(monkeypatch):
    from src.core.sync_transaction import get_transactional_db

    mock_db = MagicMock()
    mock_db.info = {}

    def fake_session_local():
        return mock_db

    import src.core.sync_transaction as tx_module

    monkeypatch.setattr(tx_module, "SessionLocal", fake_session_local)

    gen = get_transactional_db()
    db = next(gen)
    assert is_defer_commit(db)
    try:
        next(gen)
    except StopIteration:
        pass
    mock_db.commit.assert_called_once()
    mock_db.close.assert_called_once()
