import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base
from database.postgres import Database
from main import app

DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
pytest_plugins = ('pytest_asyncio',)


class MockedDatabase(Database):
    def __init__(self, *args, **kwargs):
        self.engine = engine
        self.session_class = TestingSessionLocal


@pytest_asyncio.fixture(scope="session")
async def db_gen():
    db = MockedDatabase(dict())
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield db
    finally:
        async with db.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session")
async def db_session(db_gen):
    async with db_gen.get_session() as session:
        yield session


@pytest.fixture(scope="session")
def test_client(db_gen):
    def override_get_db():
        return db_gen

    app.dependency_overrides[Database.get_instance] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
