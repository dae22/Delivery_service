import asyncio
import os
import pathlib

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from alembic import command
from alembic.config import Config
from delivery import database
from delivery.main import app as fastapi_app

load_dotenv()

DATABASE_URL = os.getenv("DB_URL_TEST")
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def alembic_config():
    cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    return cfg


@pytest_asyncio.fixture(scope="session")
async def migrations(alembic_config):
    command.upgrade(alembic_config, "head")
    yield
    # подумать про очистку БД здесь


@pytest_asyncio.fixture(scope="session")
async def engine(migrations):
    engine = create_async_engine(DATABASE_URL, future=True)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session, monkeypatch):
    async def override_get_db():
        yield db_session

    monkeypatch.setattr(database, "get_db", override_get_db)

    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    fastapi_app.dependency_overrides.clear()
