import pytest
import pytest_asyncio
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db
from app.core.settings import settings
from httpx import AsyncClient
import httpx
import os

# Use a test database URL
# For testing, we'll use SQLite for simplicity
# If DATABASE_URL is not set, default to an in-memory SQLite database
TEST_DATABASE_URL = settings.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite") or "sqlite:///./test.db"

# Create a new synchronous engine for testing
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def client():
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create a new session for the test
    session = TestingSessionLocal()
    try:
        def override_get_db():
            yield session
        
        # Override the get_db dependency
        app.dependency_overrides[get_db] = override_get_db
        
        transport = httpx.ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
        
        # Remove the override after the test
        app.dependency_overrides.clear()
    finally:
        session.close()
    
    # Drop tables after the test
    Base.metadata.drop_all(bind=test_engine)