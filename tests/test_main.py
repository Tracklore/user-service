import pytest
import pytest_asyncio
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test that the service is running"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data