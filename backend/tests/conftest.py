"""Pytest configuration — sets up an in-memory test database for every test."""

# Import all models so Base.metadata is fully populated before create_all runs.
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import app.models.character  # noqa: F401
import app.models.chat  # noqa: F401
import app.models.location  # noqa: F401
import app.models.organization  # noqa: F401
import app.models.relationship  # noqa: F401
import app.models.timeline  # noqa: F401
import app.models.universe  # noqa: F401
import app.models.world_object  # noqa: F401
import app.models.world_rule  # noqa: F401
from app.database.base import Base
from app.database.session import get_db

# Use an in-memory SQLite database so tests are fully isolated.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
async def test_engine():
    """Create a fresh engine + schema for every test function."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine):
    """Yield a session bound to the test engine."""
    factory = async_sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    async with factory() as session:
        yield session


@pytest.fixture(scope="function")
async def client(test_engine):
    """Provide an HTTPX async client that uses the test database."""
    from app.main import app

    factory = async_sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    async def override_get_db():
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
