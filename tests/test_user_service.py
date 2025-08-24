import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.services.user import UserService
from app.schemas.badge import BadgeCreate
from app.schemas.learning_goal import LearningGoalCreate, LearningGoalUpdate
from app.models.badge import Badge
from app.models.learning_goal import LearningGoal
from app.services.auth_service import auth_service_client

@pytest.fixture
def user_service():
    """Create a UserService instance with a mock database session."""
    mock_db = AsyncMock(spec=AsyncSession)
    return UserService(mock_db)

@pytest.mark.asyncio
async def test_get_user_profile(user_service):
    """Test getting a user's profile."""
    # Mock the auth service client
    with patch('app.services.user.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'get_user') as mock_get_user:
            # Mock the user data from auth service
            mock_get_user.return_value = {
                "id": 1,
                "username": "testuser",
                "email": "test@example.com"
            }
            
            # Mock the badge CRUD functions
            with patch('app.services.user.crud.badge.get_badges_by_user') as mock_get_badges:
                mock_get_badges.return_value = [
                    Badge(id=1, name="Test Badge", description="Test Description", icon_url="http://example.com/icon.png", auth_user_id=1)
                ]
                
                # Mock the learning goal CRUD functions
                with patch('app.services.user.crud.learning_goal.get_learning_goals_by_user') as mock_get_goals:
                    mock_get_goals.return_value = [
                        LearningGoal(id=1, title="Test Goal", description="Test Description", status="in-progress", streak_count=5, auth_user_id=1)
                    ]
                    
                    # Call the function
                    result = await user_service.get_user_profile(1)
                    
                    # Verify the results
                    assert result["id"] == 1
                    assert result["username"] == "testuser"
                    assert result["email"] == "test@example.com"
                    assert len(result["badges"]) == 1
                    assert len(result["learning_goals"]) == 1

@pytest.mark.asyncio
async def test_get_user_profile_user_not_found(user_service):
    """Test getting a user's profile when the user is not found."""
    # Mock the auth service client
    with patch('app.services.user.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'get_user') as mock_get_user:
            # Mock the user data from auth service as None
            mock_get_user.return_value = None
            
            # Call the function and expect an HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await user_service.get_user_profile(999)
            
            # Verify the exception
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "User not found"

@pytest.mark.asyncio
async def test_create_badge_authorized(user_service):
    """Test creating a badge when the user is authorized."""
    # Mock the current user
    current_user = {"id": 1, "username": "testuser"}
    
    # Mock the badge CRUD functions
    with patch('app.services.user.crud.badge.create_user_badge') as mock_create_badge:
        mock_create_badge.return_value = Badge(
            id=1, 
            name="Test Badge", 
            description="Test Description", 
            icon_url="http://example.com/icon.png", 
            auth_user_id=1
        )
        
        # Mock the badge create schema
        badge_create = BadgeCreate(
            name="Test Badge",
            description="Test Description",
            icon_url="http://example.com/icon.png"
        )
        
        # Call the function
        result = await user_service.create_badge(1, badge_create, current_user)
        
        # Verify the results
        assert result.id == 1
        assert result.name == "Test Badge"

@pytest.mark.asyncio
async def test_create_badge_unauthorized(user_service):
    """Test creating a badge when the user is not authorized."""
    # Mock the current user
    current_user = {"id": 2, "username": "otheruser"}
    
    # Mock the badge create schema
    badge_create = BadgeCreate(
        name="Test Badge",
        description="Test Description",
        icon_url="http://example.com/icon.png"
    )
    
    # Call the function and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await user_service.create_badge(1, badge_create, current_user)
    
    # Verify the exception
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not authorized to create a badge for this user"