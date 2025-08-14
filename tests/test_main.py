import pytest
import pytest_asyncio
from httpx import AsyncClient

@pytest_asyncio.fixture(scope="function")
async def test_user(client: AsyncClient):
    response = await client.post("/users/", json={"username": "testuser", "bio": "test bio", "skills": "python, fastapi"})
    assert response.status_code == 200
    return response.json()

@pytest.mark.asyncio
async def test_get_user(client: AsyncClient, test_user):
    user_id = test_user["id"]
    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["bio"] == "test bio"

@pytest.mark.asyncio
async def test_update_user(client: AsyncClient, test_user):
    user_id = test_user["id"]
    response = await client.put(f"/users/{user_id}", json={"bio": "updated bio"})
    assert response.status_code == 200
    data = response.json()
    assert data["bio"] == "updated bio"

@pytest.mark.asyncio
async def test_create_learning_goal(client: AsyncClient, test_user):
    user_id = test_user["id"]
    response = await client.post(f"/users/{user_id}/goals", json={"title": "learn pytest", "description": "master pytest", "status": "in-progress"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "learn pytest"
    assert "id" in data

@pytest.mark.asyncio
async def test_get_learning_goals(client: AsyncClient, test_user):
    user_id = test_user["id"]
    # Create a goal first to ensure there is at least one
    await client.post(f"/users/{user_id}/goals", json={"title": "another goal", "description": "...", "status": "in-progress"})

    response = await client.get(f"/users/{user_id}/goals")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

@pytest.mark.asyncio
async def test_update_learning_goal(client: AsyncClient, test_user):
    user_id = test_user["id"]
    # First create a goal
    response = await client.post(f"/users/{user_id}/goals", json={"title": "learn pytest", "description": "master pytest", "status": "in-progress"})
    goal_id = response.json()["id"]

    response = await client.put(f"/users/{user_id}/goals/{goal_id}", json={"status": "completed"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"

@pytest.mark.asyncio
async def test_delete_learning_goal(client: AsyncClient, test_user):
    user_data = test_user
    user_id = user_data["id"]
    # First create a goal
    response = await client.post(f"/users/{user_id}/goals", json={"title": "to be deleted", "description": "...", "status": "in-progress"})
    goal_id = response.json()["id"]

    response = await client.delete(f"/users/{user_id}/goals/{goal_id}")
    assert response.status_code == 200

    # Verify it's deleted by trying to get it again, which should result in a 404
    # This requires the get_learning_goal endpoint to be implemented and return 404 if not found
    # The current implementation of delete returns ok, but doesn't verify deletion.
    # Let's assume the service for get goal is not implemented, so we can't verify this way.
    # A better test would be to list all goals and check it's not there.
    response = await client.get(f"/users/{user_id}/goals")
    all_goals = response.json()
    assert goal_id not in [g["id"] for g in all_goals]

@pytest.mark.asyncio
async def test_get_badges(client: AsyncClient, test_user):
    user_data = test_user
    user_id = user_data["id"]
    response = await client.get(f"/users/{user_id}/badges")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
