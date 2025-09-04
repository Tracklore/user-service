import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from app.main import app
from app.models.badge import Badge
from app.models.learning_goal import LearningGoal
from app.schemas.badge import BadgeCreate
from app.schemas.learning_goal import LearningGoalCreate, LearningGoalUpdate
from app.services.auth_service import auth_service_client
from tests.test_utils import SAMPLE_USER_ID, SAMPLE_USER_DATA, SAMPLE_BADGE_DATA, SAMPLE_LEARNING_GOAL_DATA


@pytest.mark.asyncio
async def test_read_user(client: AsyncClient):
    """Test getting a user's profile by ID."""
    # Mock the UserService dependency
    user_profile_data = {
        "id": SAMPLE_USER_ID,
        "username": "testuser",
        "email": "test@example.com",
        "badges": [
            {
                "id": 1,
                "name": "Test Badge",
                "description": "Test Description",
                "icon_url": "http://example.com/icon.png",
                "date_achieved": "2023-01-01T00:00:00",
                "auth_user_id": SAMPLE_USER_ID
            }
        ],
        "learning_goals": [
            {
                "id": 1,
                "title": "Test Goal",
                "description": "Test Description",
                "status": "in-progress",
                "streak_count": 5,
                "auth_user_id": SAMPLE_USER_ID
            }
        ],
        "statistics": {
            "total_badges": 1,
            "total_goals": 1,
            "level": 1
        }
    }
    
    with patch('app.api.routes.get_user_service') as mock_get_user_service, \
         patch('app.services.auth_service.auth_service_client') as mock_auth_client:
        # Mock the auth service client to return a valid user
        mock_auth_client.get_user.return_value = {
            "id": SAMPLE_USER_ID,
            "username": "testuser",
            "email": "test@example.com"
        }
        
        mock_user_service = AsyncMock()
        mock_user_service.get_user_profile.return_value = user_profile_data
        mock_get_user_service.return_value = mock_user_service
        
        # Make the request
        response = await client.get(f"/users/{SAMPLE_USER_ID}")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == SAMPLE_USER_ID
        assert data["username"] == "testuser"
        assert len(data["badges"]) == 1
        assert len(data["learning_goals"]) == 1


@pytest.mark.asyncio
async def test_read_user_not_found(client: AsyncClient):
    """Test getting a user's profile when the user is not found."""
    with patch('app.api.routes.get_user_service') as mock_get_user_service, \
         patch('app.services.auth_service.auth_service_client') as mock_auth_client:
        # Mock the auth service client to return None (user not found)
        mock_auth_client.get_user.return_value = None
        
        mock_user_service = AsyncMock()
        mock_user_service.get_user_profile.side_effect = HTTPException(status_code=404, detail="User not found")
        mock_get_user_service.return_value = mock_user_service
        
        # Make the request
        response = await client.get("/users/999")
        
        # Verify the response
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_read_user_badges(client: AsyncClient):
    """Test getting a user's badges."""
    badges_data = [
        {
            "id": 1,
            "name": "Test Badge",
            "description": "Test Description",
            "icon_url": "http://example.com/icon.png",
            "date_achieved": "2023-01-01T00:00:00",
            "auth_user_id": SAMPLE_USER_ID
        },
        {
            "id": 2,
            "name": "Another Badge",
            "description": "Another Description",
            "icon_url": "http://example.com/icon2.png",
            "date_achieved": "2023-01-02T00:00:00",
            "auth_user_id": SAMPLE_USER_ID
        }
    ]
    
    with patch('app.api.routes.get_user_service') as mock_get_user_service, \
         patch('app.services.auth_service.auth_service_client') as mock_auth_client:
        # Mock the auth service client to return a valid user
        mock_auth_client.get_user.return_value = {
            "id": SAMPLE_USER_ID,
            "username": "testuser",
            "email": "test@example.com"
        }
        
        mock_user_service = AsyncMock()
        mock_user_service.get_user_badges.return_value = badges_data
        mock_get_user_service.return_value = mock_user_service
        
        # Make the request
        response = await client.get(f"/users/{SAMPLE_USER_ID}/badges")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Test Badge"
        assert data[1]["name"] == "Another Badge"


@pytest.mark.asyncio
async def test_create_badge_authorized(client: AsyncClient):
    """Test creating a badge when the user is authorized."""
    badge_data = {
        "id": 1,
        "name": "Test Badge",
        "description": "Test Description",
        "icon_url": "http://example.com/icon.png",
        "date_achieved": "2023-01-01T00:00:00",
        "auth_user_id": SAMPLE_USER_ID
    }
    
    with patch('app.api.routes.get_user_service') as mock_get_user_service, 
         patch('app.services.auth_service.auth_service_client') as mock_auth_client:
        # Mock the auth service client to return a valid user
        mock_auth_client.get_user.return_value = {
            "id": SAMPLE_USER_ID,
            "username": "testuser",
            "email": "test@example.com"
        }
        
        # Mock the user service
        mock_user_service = AsyncMock()
        mock_user_service.create_badge.return_value = Badge(
            id=1,
            name="Test Badge",
            description="Test Description",
            icon_url="http://example.com/icon.png",
            auth_user_id=SAMPLE_USER_ID
        )
        mock_get_user_service.return_value = mock_user_service
        
        # Make the request
        response = await client.post(
            f"/users/{SAMPLE_USER_ID}/badges",
            json=SAMPLE_BADGE_DATA
        )
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Test Badge"


@pytest.mark.asyncio
async def test_create_badge_unauthorized(client: AsyncClient):
    """Test creating a badge when the user is not authorized."""
    with patch('app.api.routes.get_user_service') as mock_get_user_service, 
         patch('app.services.auth_service.auth_service_client') as mock_auth_client:
        # Mock the auth service client to return None (user not found)
        mock_auth_client.get_user.return_value = None
        
        # Mock the user service
        mock_user_service = AsyncMock()
        mock_get_user_service.return_value = mock_user_service
        
        # Make the request
        response = await client.post(
            f"/users/{SAMPLE_USER_ID}/badges",
            json=SAMPLE_BADGE_DATA
        )
        
        # Verify the response
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_read_user_learning_goals(client: AsyncClient):
    """Test getting a user's learning goals."""
    goals_data = [
        {
            "id": 1,
            "title": "Test Goal",
            "description": "Test Description",
            "status": "in-progress",
            "streak_count": 5,
            "auth_user_id": SAMPLE_USER_ID
        },
        {
            "id": 2,
            "title": "Another Goal",
            "description": "Another Description",
            "status": "completed",
            "streak_count": 10,
            "auth_user_id": SAMPLE_USER_ID
        }
    ]
    
    # Mock the auth service client to avoid database operations
    with patch('app.services.auth_service.auth_service_client') as mock_auth_client:
        mock_auth_client.ensure_auth_user_reference_exists = AsyncMock()
        
        with patch('app.api.routes.get_user_service') as mock_get_user_service:
            mock_user_service = AsyncMock()
            mock_user_service.get_user_learning_goals.return_value = goals_data
            mock_get_user_service.return_value = mock_user_service
            
            # Make the request
            response = await client.get(f"/users/{SAMPLE_USER_ID}/goals")
            
            # Verify the response
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["title"] == "Test Goal"
            assert data[1]["title"] == "Another Goal"


@pytest.mark.asyncio
async def test_create_learning_goal_authorized(client: AsyncClient):
    """Test creating a learning goal when the user is authorized."""
    goal_data = {
        "id": 1,
        "title": "Test Goal",
        "description": "Test Description",
        "status": "in-progress",
        "streak_count": 5,
        "auth_user_id": SAMPLE_USER_ID
    }
    
    with patch('app.api.routes.get_current_user_from_token') as mock_get_current_user, \
         patch('app.api.routes.get_user_service') as mock_get_user_service:
        
        # Mock the current user
        mock_get_current_user.return_value = SAMPLE_USER_DATA
        
        # Mock the user service
        mock_user_service = AsyncMock()
        mock_user_service.create_learning_goal.return_value = LearningGoal(
            id=1,
            title="Test Goal",
            description="Test Description",
            status="in-progress",
            streak_count=5,
            auth_user_id=SAMPLE_USER_ID
        )
        mock_get_user_service.return_value = mock_user_service
        
        # Make the request
        response = await client.post(
            f"/users/{SAMPLE_USER_ID}/goals",
            json=SAMPLE_LEARNING_GOAL_DATA
        )
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Test Learning Goal"


@pytest.mark.asyncio
async def test_create_learning_goal_unauthorized(client: AsyncClient):
    """Test creating a learning goal when the user is not authorized."""
    with patch('app.api.routes.get_current_user_from_token') as mock_get_current_user, \
         patch('app.api.routes.get_user_service') as mock_get_user_service:
        
        # Mock the current user as a different user
        mock_get_current_user.return_value = {"id": 2, "username": "otheruser"}
        
        # Mock the user service
        mock_user_service = AsyncMock()
        mock_get_user_service.return_value = mock_user_service
        
        # Make the request
        response = await client.post(
            f"/users/{SAMPLE_USER_ID}/goals",
            json=SAMPLE_LEARNING_GOAL_DATA
        )
        
        # Verify the response
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_learning_goal_authorized(client: AsyncClient):
    """Test updating a learning goal when the user is authorized."""
    updated_goal_data = {
        "id": 1,
        "title": "Updated Goal",
        "description": "Updated Description",
        "status": "completed",
        "streak_count": 10,
        "auth_user_id": SAMPLE_USER_ID
    }
    
    with patch('app.api.routes.get_current_user_from_token') as mock_get_current_user, \
         patch('app.api.routes.get_user_service') as mock_get_user_service:
        
        # Mock the current user
        mock_get_current_user.return_value = SAMPLE_USER_DATA
        
        # Mock the user service
        mock_user_service = AsyncMock()
        mock_user_service.update_learning_goal.return_value = LearningGoal(
            id=1,
            title="Updated Goal",
            description="Updated Description",
            status="completed",
            streak_count=10,
            auth_user_id=SAMPLE_USER_ID
        )
        mock_get_user_service.return_value = mock_user_service
        
        # Make the request
        update_data = {
            "title": "Updated Goal",
            "description": "Updated Description",
            "status": "completed",
            "streak_count": 10
        }
        
        response = await client.put(
            f"/users/{SAMPLE_USER_ID}/goals/1",
            json=update_data
        )
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Updated Goal"
        assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_update_learning_goal_unauthorized(client: AsyncClient):
    """Test updating a learning goal when the user is not authorized."""
    with patch('app.api.routes.get_current_user_from_token') as mock_get_current_user, \
         patch('app.api.routes.get_user_service') as mock_get_user_service:
        
        # Mock the current user as a different user
        mock_get_current_user.return_value = {"id": 2, "username": "otheruser"}
        
        # Mock the user service
        mock_user_service = AsyncMock()
        mock_get_user_service.return_value = mock_user_service
        
        # Make the request
        update_data = {
            "title": "Updated Goal",
            "description": "Updated Description"
        }
        
        response = await client.put(
            f"/users/{SAMPLE_USER_ID}/goals/1",
            json=update_data
        )
        
        # Verify the response
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_learning_goal_authorized(client: AsyncClient):
    """Test deleting a learning goal when the user is authorized."""
    with patch('app.api.routes.get_current_user_from_token') as mock_get_current_user, \
         patch('app.api.routes.get_user_service') as mock_get_user_service:
        
        # Mock the current user
        mock_get_current_user.return_value = SAMPLE_USER_DATA
        
        # Mock the user service
        mock_user_service = AsyncMock()
        mock_user_service.delete_learning_goal.return_value = None  # Successful deletion returns None
        mock_get_user_service.return_value = mock_user_service
        
        # Make the request
        response = await client.delete(f"/users/{SAMPLE_USER_ID}/goals/1")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data == {"ok": True}


@pytest.mark.asyncio
async def test_delete_learning_goal_unauthorized(client: AsyncClient):
    """Test deleting a learning goal when the user is not authorized."""
    with patch('app.api.routes.get_current_user_from_token') as mock_get_current_user, \
         patch('app.api.routes.get_user_service') as mock_get_user_service:
        
        # Mock the current user as a different user
        mock_get_current_user.return_value = {"id": 2, "username": "otheruser"}
        
        # Mock the user service
        mock_user_service = AsyncMock()
        mock_get_user_service.return_value = mock_user_service
        
        # Make the request
        response = await client.delete(f"/users/{SAMPLE_USER_ID}/goals/1")
        
        # Verify the response
        assert response.status_code == 403