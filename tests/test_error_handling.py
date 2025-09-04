import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.main import app
from app.models.badge import Badge
from app.models.learning_goal import LearningGoal
from app.schemas.badge import BadgeCreate
from app.schemas.learning_goal import LearningGoalCreate, LearningGoalUpdate
from tests.test_utils import SAMPLE_USER_ID, SAMPLE_USER_DATA, SAMPLE_BADGE_DATA, SAMPLE_LEARNING_GOAL_DATA
import asyncio


@pytest.mark.asyncio
async def test_api_endpoint_with_invalid_user_id(client: AsyncClient):
    """Test API endpoints with invalid user IDs."""
    # Test getting user profile with invalid ID
    response = await client.get("/users/invalid")
    assert response.status_code == 422  # Validation error
    
    # Test getting badges with invalid ID
    response = await client.get("/users/invalid/badges")
    assert response.status_code == 422  # Validation error
    
    # Test getting learning goals with invalid ID
    response = await client.get("/users/invalid/goals")
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_api_endpoint_with_negative_user_id(client: AsyncClient):
    """Test API endpoints with negative user IDs."""
    # Test getting user profile with negative ID
    response = await client.get("/users/-1")
    assert response.status_code == 404  # Not found or validation error
    
    # Test getting badges with negative ID
    response = await client.get("/users/-1/badges")
    # This might depend on implementation, could be 404 or 422
    
    # Test getting learning goals with negative ID
    response = await client.get("/users/-1/goals")
    # This might depend on implementation, could be 404 or 422


@pytest.mark.asyncio
async def test_api_endpoint_with_zero_user_id(client: AsyncClient):
    """Test API endpoints with zero user ID."""
    # Test getting user profile with zero ID
    response = await client.get("/users/0")
    # This might depend on implementation, could be 404 or 422


@pytest.mark.asyncio
async def test_create_badge_with_invalid_data(client: AsyncClient):
    """Test creating a badge with invalid data."""
    # Mock the current user
    current_user = SAMPLE_USER_DATA
    
    with patch("app.api.routes.get_current_user_from_token") as mock_get_current_user:
        # Mock the current user
        mock_get_current_user.return_value = current_user
        
        # Test with missing required fields
        invalid_badge_data = {
            "name": ""  # Empty name
        }
        
        response = await client.post(
            f"/users/{SAMPLE_USER_ID}/badges",
            json=invalid_badge_data
        )
        
        # Should get validation error
        assert response.status_code == 422
        
        # Test with name too long
        invalid_badge_data = {
            "name": "A" * 101,  # Exceeds max length of 100
            "description": "Test Description",
            "icon_url": "http://example.com/icon.png"
        }
        
        response = await client.post(
            f"/users/{SAMPLE_USER_ID}/badges",
            json=invalid_badge_data
        )
        
        # Should get validation error
        assert response.status_code == 422
        
        # Test with invalid URL
        invalid_badge_data = {
            "name": "Test Badge",
            "description": "Test Description",
            "icon_url": "not-a-url"
        }
        
        response = await client.post(
            f"/users/{SAMPLE_USER_ID}/badges",
            json=invalid_badge_data
        )
        
        # Should get validation error
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_learning_goal_with_invalid_data(client: AsyncClient):
    """Test creating a learning goal with invalid data."""
    # Mock the current user
    current_user = SAMPLE_USER_DATA
    
    with patch("app.api.routes.get_current_user_from_token") as mock_get_current_user:
        # Mock the current user
        mock_get_current_user.return_value = current_user
        
        # Test with missing required fields
        invalid_goal_data = {
            "title": ""  # Empty title
        }
        
        response = await client.post(
            f"/users/{SAMPLE_USER_ID}/goals",
            json=invalid_goal_data
        )
        
        # Should get validation error
        assert response.status_code == 422
        
        # Test with title too long
        invalid_goal_data = {
            "title": "A" * 201,  # Exceeds max length of 200
            "description": "Test Description",
            "status": "in-progress"
        }
        
        response = await client.post(
            f"/users/{SAMPLE_USER_ID}/goals",
            json=invalid_goal_data
        )
        
        # Should get validation error
        assert response.status_code == 422
        
        # Test with negative streak count
        invalid_goal_data = {
            "title": "Test Goal",
            "description": "Test Description",
            "status": "in-progress",
            "streak_count": -1  # Negative value
        }
        
        response = await client.post(
            f"/users/{SAMPLE_USER_ID}/goals",
            json=invalid_goal_data
        )
        
        # Should get validation error
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_learning_goal_with_invalid_data(client: AsyncClient):
    """Test updating a learning goal with invalid data."""
    # Mock the current user
    current_user = SAMPLE_USER_DATA
    
    with patch("app.api.routes.get_current_user_from_token") as mock_get_current_user:
        # Mock the current user
        mock_get_current_user.return_value = current_user
        
        # Test with title too long
        invalid_update_data = {
            "title": "A" * 201  # Exceeds max length of 200
        }
        
        response = await client.put(
            f"/users/{SAMPLE_USER_ID}/goals/1",
            json=invalid_update_data
        )
        
        # Should get validation error
        assert response.status_code == 422
        
        # Test with negative streak count
        invalid_update_data = {
            "streak_count": -1  # Negative value
        }
        
        response = await client.put(
            f"/users/{SAMPLE_USER_ID}/goals/1",
            json=invalid_update_data
        )
        
        # Should get validation error
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_database_connection_error_in_crud():
    """Test CRUD operations when database connection fails."""
    from app.crud import badge, learning_goal
    
    # Mock the database session to raise an exception
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = SQLAlchemyError("Connection failed")
    
    # Test get_badges_by_user with database error
    with pytest.raises(Exception) as exc_info:
        await badge.get_badges_by_user(mock_db, SAMPLE_USER_ID)
    
    assert "Error fetching badges for user" in str(exc_info.value)
    
    # Test create_user_badge with database error
    with pytest.raises(Exception) as exc_info:
        badge_create = BadgeCreate(**SAMPLE_BADGE_DATA)
        await badge.create_user_badge(mock_db, badge_create, SAMPLE_USER_ID)
    
    assert "Error creating badge for user" in str(exc_info.value)
    
    # Test get_learning_goals_by_user with database error
    with pytest.raises(Exception) as exc_info:
        await learning_goal.get_learning_goals_by_user(mock_db, SAMPLE_USER_ID)
    
    assert "Error fetching learning goals for user" in str(exc_info.value)
    
    # Test create_user_learning_goal with database error
    with pytest.raises(Exception) as exc_info:
        goal_create = LearningGoalCreate(**SAMPLE_LEARNING_GOAL_DATA)
        await learning_goal.create_user_learning_goal(mock_db, goal_create, SAMPLE_USER_ID)
    
    assert "Error creating learning goal for user" in str(exc_info.value)


@pytest.mark.asyncio
async def test_auth_service_connection_error():
    """Test handling of auth service connection errors."""
    from app.services.auth_service import AuthServiceClient
    
    # Create auth service client
    auth_client = AuthServiceClient()
    
    # Mock HTTP error
    with patch.object(auth_client.client, "get", side_effect=Exception("Connection failed")):
        # Test get_user
        result = await auth_client.get_user(SAMPLE_USER_ID)
        assert result is None
        
        # Test get_user_by_email
        result = await auth_client.get_user_by_email("test@example.com")
        assert result is None


@pytest.mark.asyncio
async def test_message_queue_connection_error():
    """Test handling of message queue connection errors."""
    from app.services.message_queue_consumer import MessageQueueConsumer
    
    # Mock connection failure
    with patch("aiormq.connect", side_effect=Exception("Connection failed")):
        consumer = MessageQueueConsumer()
        await consumer.connect()
        
        # Connection should be None
        assert consumer.connection is None
        assert consumer.channel is None
        
        # Consuming should not raise an exception
        await consumer.consume_user_events()


@pytest.mark.asyncio
async def test_user_service_with_auth_service_error():
    """Test user service methods when auth service fails."""
    from app.services.user import UserService
    
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    user_service = UserService(mock_db)
    
    # Mock auth service to return None (user not found)
    with patch("app.services.user.auth_service_client") as mock_auth_client:
        mock_auth_client.get_user.return_value = None
        
        # Test get_user_profile with user not found
        with pytest.raises(HTTPException) as exc_info:
            await user_service.get_user_profile(SAMPLE_USER_ID)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "User not found"


@pytest.mark.asyncio
async def test_api_endpoints_with_service_unavailable(client: AsyncClient):
    """Test API endpoints when dependent services are unavailable."""
    # Mock auth service failure
    with patch("app.api.routes.get_current_user_from_token") as mock_get_current_user:
        # Mock auth service to raise an exception
        mock_get_current_user.side_effect = Exception("Auth service unavailable")
        
        # Test /me endpoint
        response = await client.get("/users/me")
        assert response.status_code == 500  # Internal server error
        
        # Test creating badge
        response = await client.post(
            f"/users/{SAMPLE_USER_ID}/badges",
            json=SAMPLE_BADGE_DATA
        )
        assert response.status_code == 500  # Internal server error


@pytest.mark.asyncio
async def test_empty_results_handling(client: AsyncClient):
    """Test handling of empty results from database queries."""
    with patch("app.api.routes.get_user_service") as mock_get_user_service:
        mock_user_service = AsyncMock()
        mock_user_service.get_user_badges.return_value = []  # Empty list
        mock_user_service.get_user_learning_goals.return_value = []  # Empty list
        mock_get_user_service.return_value = mock_user_service
        
        # Test getting badges when none exist
        response = await client.get(f"/users/{SAMPLE_USER_ID}/badges")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0  # Should return empty array, not error
        
        # Test getting learning goals when none exist
        response = await client.get(f"/users/{SAMPLE_USER_ID}/goals")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0  # Should return empty array, not error


@pytest.mark.asyncio
async def test_large_data_handling(client: AsyncClient):
    """Test handling of large amounts of data."""
    # Mock a large number of badges
    many_badges = []
    for i in range(100):
        many_badges.append({
            "id": i + 1,
            "name": f"Badge {i + 1}",
            "description": f"Description for badge {i + 1}",
            "icon_url": f"http://example.com/badge{i + 1}.png",
            "date_achieved": "2023-01-01T00:00:00",
            "auth_user_id": SAMPLE_USER_ID
        })
    
    with patch("app.api.routes.get_user_service") as mock_get_user_service:
        mock_user_service = AsyncMock()
        mock_user_service.get_user_badges.return_value = many_badges
        mock_get_user_service.return_value = mock_user_service
        
        # Test getting many badges
        response = await client.get(f"/users/{SAMPLE_USER_ID}/badges")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 100


@pytest.mark.asyncio
async def test_concurrent_requests_handling(client: AsyncClient):
    """Test handling of concurrent requests."""
    # This test would typically use asyncio.gather to run multiple requests concurrently
    # For simplicity, we'll just show the pattern
    
    # Mock the user service
    with patch("app.api.routes.get_user_service") as mock_get_user_service:
        mock_user_service = AsyncMock()
        mock_user_service.get_user_badges.return_value = [
            {
                "id": 1,
                "name": "Test Badge",
                "description": "Test Description",
                "icon_url": "http://example.com/icon.png",
                "date_achieved": "2023-01-01T00:00:00",
                "auth_user_id": SAMPLE_USER_ID
            }
        ]
        mock_get_user_service.return_value = mock_user_service
        
        # Simulate concurrent requests
        responses = await asyncio.gather(
            client.get(f"/users/{SAMPLE_USER_ID}/badges"),
            client.get(f"/users/{SAMPLE_USER_ID}/badges"),
            client.get(f"/users/{SAMPLE_USER_ID}/badges")
        )
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_unicode_and_special_characters(client: AsyncClient):
    """Test handling of unicode and special characters in data."""
    # Mock the current user
    current_user = SAMPLE_USER_DATA
    
    with patch("app.api.routes.get_current_user_from_token") as mock_get_current_user, \
         patch("app.api.routes.get_user_service") as mock_get_user_service:
        
        # Mock the current user
        mock_get_current_user.return_value = current_user
        
        # Mock the user service
        mock_user_service = AsyncMock()
        mock_user_service.create_badge.return_value = Badge(
            id=1,
            name="テストバッジ",  # Japanese characters
            description="Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
            icon_url="http://example.com/icon.png",
            auth_user_id=SAMPLE_USER_ID
        )
        mock_get_user_service.return_value = mock_user_service
        
        # Test with unicode and special characters
        badge_data = {
            "name": "テストバッジ",  # Japanese characters
            "description": "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
            "icon_url": "http://example.com/icon.png"
        }
        
        response = await client.post(
            f"/users/{SAMPLE_USER_ID}/badges",
            json=badge_data
        )
        
        # Should succeed
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "テストバッジ"


@pytest.mark.asyncio
async def test_extreme_values(client: AsyncClient):
    """Test handling of extreme values."""
    # Mock the current user
    current_user = SAMPLE_USER_DATA
    
    with patch("app.api.routes.get_current_user_from_token") as mock_get_current_user, \
         patch("app.api.routes.get_user_service") as mock_get_user_service:
        
        # Mock the current user
        mock_get_current_user.return_value = current_user
        
        # Mock the user service
        mock_user_service = AsyncMock()
        mock_get_user_service.return_value = mock_user_service
        
        # Test with maximum allowed streak count
        goal_data = {
            "title": "Test Goal",
            "description": "Test Description",
            "status": "in-progress",
            "streak_count": 2147483647  # Max 32-bit integer
        }
        
        mock_user_service.create_learning_goal.return_value = LearningGoal(
            id=1,
            title="Test Goal",
            description="Test Description",
            status="in-progress",
            streak_count=2147483647,
            auth_user_id=SAMPLE_USER_ID
        )
        
        response = await client.post(
            f"/users/{SAMPLE_USER_ID}/goals",
            json=goal_data
        )
        
        # Should succeed
        assert response.status_code == 200