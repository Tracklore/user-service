import sys
from pathlib import Path

# Add the shared-libs directory to the Python path
shared_libs_path = Path(__file__).resolve().parent.parent / "shared_libs"
sys.path.append(str(shared_libs_path))

import pytest
import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db, engine
from app.core.settings import settings
from httpx import AsyncClient
import httpx
import os

# Use a test database URL
# For testing, we'll use SQLite for simplicity
# If DATABASE_URL is not set, default to an in-memory SQLite database
TEST_DATABASE_URL = settings.database_url or "sqlite+aiosqlite:///./test.db"

# Create a new asynchronous engine for testing
test_engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def client():
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create a new session for the test
    session = TestingSessionLocal()
    try:
        async def override_get_db():
            yield session
        
        # Override the get_db dependency
        app.dependency_overrides[get_db] = override_get_db
        
        transport = httpx.ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
        
        # Remove the override after the test
        app.dependency_overrides.clear()
    finally:
        await session.close()
    
    # Drop tables after the test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)