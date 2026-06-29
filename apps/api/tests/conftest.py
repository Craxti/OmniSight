import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import bcrypt
import pytest
import pytest_asyncio
import src.main as main_module
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker
from src.core import database as db_module
from src.core.config import settings
from src.core.database_async import dispose_async_engines
from src.models import (  # noqa: F401
    CI,
    AuditLog,
    CacheEntry,
    CIType,
    GraphLayout,
    IntegrationOutbox,
    RateLimitHit,
    Relation,
    User,
)

from tests.helpers.postgres_db import (
    create_test_engine,
    prepare_clean_test_database,
    reset_database,
    seed_test_database,
    test_database_url,
)


@pytest.fixture(autouse=True)
def _fast_bcrypt_for_tests(monkeypatch):
    real_gensalt = bcrypt.gensalt
    monkeypatch.setattr(bcrypt, "gensalt", lambda rounds=None: real_gensalt(rounds=4))


@pytest.fixture(autouse=True)
def _enable_async_database(monkeypatch):
    monkeypatch.setattr(settings, "database_async_enabled", True)


@pytest.fixture(autouse=True)
def _disable_rate_limit_for_tests():
    settings.rate_limit_enabled = False
    yield
    settings.rate_limit_enabled = True


@pytest.fixture(autouse=True)
def _disable_cache_for_tests():
    settings.cache_enabled = False
    yield
    settings.cache_enabled = True


@pytest.fixture(autouse=True)
def _fresh_test_database(test_engine, request):
    """Truncate and re-seed before each test for isolation across the shared session engine."""
    if request.module and request.module.__name__.endswith("test_nfr_scale"):
        return

    from tests.helpers.async_db import dispose_cached_async_engines

    reset_database(test_engine)
    seed_test_database(test_engine)
    asyncio.run(dispose_async_engines())
    dispose_cached_async_engines()


@pytest.fixture(scope="session")
def test_engine():
    engine = create_test_engine()
    test_url = test_database_url()
    settings.database_url = test_url
    settings.database_read_url = test_url
    prepare_clean_test_database(engine)
    seed_test_database(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def scale_database_seeded(test_engine):
    """Populate omnisight_test with 50k CIs for NFR scale tests."""
    from tests.helpers.scale_seed import ensure_scale_seed

    ensure_scale_seed(test_engine, verbose=True)


@pytest.fixture(scope="session", autouse=True)
def _dispose_async_parity_engines():
    yield
    from tests.helpers.async_db import dispose_cached_async_engines

    dispose_cached_async_engines()


def _bind_test_engine(engine, session_factory):
    db_module.engine = engine
    db_module.SessionLocal = session_factory
    main_module.engine = engine
    main_module.SessionLocal = session_factory


@pytest.fixture()
def admin_user(db_session) -> User:
    return db_session.query(User).filter(User.email == "admin@omnisight.local").first()


@pytest.fixture()
def client(test_engine):
    from src.main import app

    engine = test_engine
    session_factory = sessionmaker(bind=engine)
    _bind_test_engine(engine, session_factory)
    asyncio.run(dispose_async_engines())

    with TestClient(app) as c:
        yield c

    asyncio.run(dispose_async_engines())


@pytest.fixture()
def auth_headers(client: TestClient):
    r = client.post("/api/v1/auth/login", json={"email": "admin@omnisight.local", "password": "admin123"})
    assert r.status_code == 200, r.text
    token = r.json()["session"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def db_session(test_engine) -> Session:
    session = sessionmaker(bind=test_engine)()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest_asyncio.fixture()
async def async_bundle(test_engine):
    from tests.helpers.async_db import async_bundle_for_test_engine

    async with async_bundle_for_test_engine(test_engine) as bundle:
        yield bundle


@pytest_asyncio.fixture()
async def ci_write_service(async_bundle):
    from src.services.async_write.ci import AsyncCiWriteService

    return AsyncCiWriteService(async_bundle)


@pytest_asyncio.fixture()
async def relation_write_service(async_bundle):
    from src.services.async_write.relations import AsyncRelationWriteService

    return AsyncRelationWriteService(async_bundle)


@pytest_asyncio.fixture()
async def ci_import_export_write_service(async_bundle):
    from src.services.async_write.import_export import AsyncCiImportExportWriteService

    return AsyncCiImportExportWriteService(async_bundle)


@pytest_asyncio.fixture()
async def relation_import_export_write_service(async_bundle):
    from src.services.async_write.import_export import AsyncRelationImportExportWriteService

    return AsyncRelationImportExportWriteService(async_bundle)


@pytest_asyncio.fixture()
async def ci_type_write_service(async_bundle):
    from src.services.async_write.ci_types import AsyncCiTypeWriteService

    return AsyncCiTypeWriteService(async_bundle)


@pytest_asyncio.fixture()
async def ci_import_export_read_service(async_bundle):
    from src.services.async_read.import_export import AsyncCiImportExportReadService

    return AsyncCiImportExportReadService(async_bundle)


@pytest_asyncio.fixture()
async def relation_import_export_read_service(async_bundle):
    from src.services.async_read.import_export import AsyncRelationImportExportReadService

    return AsyncRelationImportExportReadService(async_bundle)


@pytest_asyncio.fixture()
async def user_write_service(async_bundle):
    from src.services.async_write.users import AsyncUserWriteService

    return AsyncUserWriteService(async_bundle)
