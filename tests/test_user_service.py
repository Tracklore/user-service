import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.services.user import UserService, get_current_user_from_token
from app.schemas.badge import BadgeCreate
from app.schemas.learning_goal import LearningGoalCreate, LearningGoalUpdate
from app.models.badge import Badge
from app.models.learning_goal import LearningGoal
from app.services.auth_service import auth_service_client
from tests.test_utils import SAMPLE_USER_ID, SAMPLE_USER_DATA, SAMPLE_BADGE_DATA, SAMPLE_LEARNING_GOAL_DATA
import asyncio


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
async def test_get_my_profile(user_service):
    """Test getting the current user's profile."""
    # Mock the current user data
    current_user = SAMPLE_USER_DATA
    
    # Mock the badge CRUD functions
    with patch('app.services.user.crud.badge.get_badges_by_user') as mock_get_badges:
        mock_get_badges.return_value = [
            Badge(id=1, name="Test Badge", description="Test Description", icon_url="http://example.com/icon.png", auth_user_id=1),
            Badge(id=2, name="Another Badge", description="Another Description", icon_url="http://example.com/icon2.png", auth_user_id=1)
        ]
        
        # Mock the learning goal CRUD functions
        with patch('app.services.user.crud.learning_goal.get_learning_goals_by_user') as mock_get_goals:
            mock_get_goals.return_value = [
                LearningGoal(id=1, title="Test Goal", description="Test Description", status="in-progress", streak_count=5, auth_user_id=1),
                LearningGoal(id=2, title="Another Goal", description="Another Description", status="completed", streak_count=10, auth_user_id=1)
            ]
            
            # Call the function
            result = await user_service.get_my_profile(current_user)
            
            # Verify the results
            assert "statistics" in result
            assert result["id"] == current_user["id"]
            assert result["username"] == current_user["username"]


@pytest.mark.asyncio
async def test_get_user_badges(user_service):
    """Test getting badges for a user."""
    # Mock the auth service client
    with patch('app.services.user.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'get_user') as mock_get_user:
            mock_get_user.return_value = {"id": 1, "username": "testuser"}
            
            with patch.object(auth_service_client, 'ensure_auth_user_reference_exists') as mock_ensure:
                # Mock the badge CRUD functions
                mock_get_badges = AsyncMock()
                mock_get_badges.return_value = [
                    Badge(id=1, name="Test Badge", description="Test Description", icon_url="http://example.com/icon.png", auth_user_id=1),
                    Badge(id=2, name="Another Badge", description="Another Description", icon_url="http://example.com/icon2.png", auth_user_id=1)
                ]
                with patch('app.services.user.crud.badge.get_badges_by_user', mock_get_badges):
                    
                    # Call the function
                    result = await user_service.get_user_badges(1)
                    
                    # Verify the results
                    assert len(result) == 2
                    # Badges are sorted by ID in descending order, so ID 2 comes first
                    assert result[0].name == "Another Badge"
                    assert result[1].name == "Test Badge"
                    
                    # Verify that ensure_auth_user_reference_exists was called
                    mock_ensure.assert_called_once_with(1, user_service.db)


@pytest.mark.asyncio
async def test_create_badge_authorized(user_service):
    """Test creating a badge when the user is authorized."""
    # Mock the current user
    current_user = {"id": 1, "username": "testuser"}
    
    # Mock the auth service client
    with patch('app.services.user.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'get_user') as mock_get_user:
            mock_get_user.return_value = {"id": 1, "username": "testuser"}
            
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
                badge_create = BadgeCreate(**SAMPLE_BADGE_DATA)
                
                # Call the function
                result = await user_service.create_badge(1, badge_create, current_user)
                
                # Verify the results
                assert result.id == 1
                assert result.name == "Test Badge"
                assert result.auth_user_id == 1


@pytest.mark.asyncio
async def test_create_badge_unauthorized(user_service):
    """Test creating a badge when the user is not authorized."""
    # Mock the current user
    current_user = {"id": 2, "username": "otheruser"}
    
    # Mock the badge create schema
    badge_create = BadgeCreate(**SAMPLE_BADGE_DATA)
    
    # Call the function and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await user_service.create_badge(1, badge_create, current_user)
    
    # Verify the exception
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not authorized to create a badge for this user"


@pytest.mark.asyncio
async def test_get_user_learning_goals(user_service):
    """Test getting learning goals for a user."""
    # Mock the auth service client
    with patch('app.services.user.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'get_user') as mock_get_user:
            mock_get_user.return_value = {"id": 1, "username": "testuser"}
            
            with patch.object(auth_service_client, 'ensure_auth_user_reference_exists') as mock_ensure:
                # Mock the learning goal CRUD functions
                mock_get_goals = AsyncMock()
                mock_get_goals.return_value = [
                    LearningGoal(id=1, title="Test Goal", description="Test Description", status="in-progress", streak_count=5, auth_user_id=1),
                    LearningGoal(id=2, title="Another Goal", description="Another Description", status="completed", streak_count=10, auth_user_id=1)
                ]
                with patch('app.services.user.crud.learning_goal.get_learning_goals_by_user', mock_get_goals):
                    
                    # Call the function
                    result = await user_service.get_user_learning_goals(1)
                    
                    # Verify the results
                    assert len(result) == 2
                    # Goals are sorted by ID in descending order, so ID 2 comes first
                    assert result[0].title == "Another Goal"
                    assert result[1].title == "Test Goal"
                    
                    # Verify that ensure_auth_user_reference_exists was called
                    mock_ensure.assert_called_once_with(1, user_service.db)


@pytest.mark.asyncio
async def test_create_learning_goal_authorized(user_service):
    """Test creating a learning goal when the user is authorized."""
    # Mock the current user
    current_user = {"id": 1, "username": "testuser"}
    
    # Mock the auth service client
    with patch('app.services.user.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'get_user') as mock_get_user:
            mock_get_user.return_value = {"id": 1, "username": "testuser"}
            
            # Mock the learning goal CRUD functions
            with patch('app.services.user.crud.learning_goal.create_user_learning_goal') as mock_create_goal:
                mock_create_goal.return_value = LearningGoal(
                    id=1,
                    title="Test Learning Goal",
                    description="Test Description",
                    status="in-progress",
                    streak_count=5,
                    auth_user_id=1
                )
                
                # Mock the learning goal create schema
                learning_goal_create = LearningGoalCreate(**SAMPLE_LEARNING_GOAL_DATA)
                
                # Call the function
                result = await user_service.create_learning_goal(1, learning_goal_create, current_user)
                
                # Verify the results
                assert result.id == 1
                assert result.title == "Test Learning Goal"
                assert result.auth_user_id == 1


@pytest.mark.asyncio
async def test_create_learning_goal_unauthorized(user_service):
    """Test creating a learning goal when the user is not authorized."""
    # Mock the current user
    current_user = {"id": 2, "username": "otheruser"}
    
    # Mock the learning goal create schema
    learning_goal_create = LearningGoalCreate(**SAMPLE_LEARNING_GOAL_DATA)
    
    # Call the function and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await user_service.create_learning_goal(1, learning_goal_create, current_user)
    
    # Verify the exception
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not authorized to create a learning goal for this user"


@pytest.mark.asyncio
async def test_update_learning_goal_authorized(user_service):
    """Test updating a learning goal when the user is authorized."""
    # Mock the current user
    current_user = {"id": 1, "username": "testuser"}
    
    # Mock the auth service client
    with patch('app.services.user.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'get_user') as mock_get_user:
            mock_get_user.return_value = {"id": 1, "username": "testuser"}
            
            # Mock the learning goal CRUD functions
            with patch('app.services.user.crud.learning_goal.update_learning_goal') as mock_update_goal:
                mock_update_goal.return_value = LearningGoal(
                    id=1,
                    title="Updated Goal",
                    description="Updated Description",
                    status="completed",
                    streak_count=10,
                    auth_user_id=1
                )
                
                # Mock the learning goal update schema
                learning_goal_update = LearningGoalUpdate(
                    title="Updated Goal",
                    description="Updated Description",
                    status="completed",
                    streak_count=10
                )
                
                # Call the function
                result = await user_service.update_learning_goal(1, 1, learning_goal_update, current_user)
                
                # Verify the results
                assert result.id == 1
                assert result.title == "Updated Goal"
                assert result.status == "completed"


@pytest.mark.asyncio
async def test_update_learning_goal_unauthorized(user_service):
    """Test updating a learning goal when the user is not authorized."""
    # Mock the current user
    current_user = {"id": 2, "username": "otheruser"}
    
    # Mock the learning goal update schema
    learning_goal_update = LearningGoalUpdate(
        title="Updated Goal",
        description="Updated Description"
    )
    
    # Call the function and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await user_service.update_learning_goal(1, 1, learning_goal_update, current_user)
    
    # Verify the exception
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not authorized to update this learning goal"


@pytest.mark.asyncio
async def test_update_learning_goal_not_found(user_service):
    """Test updating a learning goal when the goal is not found."""
    # Mock the current user
    current_user = {"id": 1, "username": "testuser"}
    
    # Mock the auth service client
    with patch('app.services.user.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'get_user') as mock_get_user:
            mock_get_user.return_value = {"id": 1, "username": "testuser"}
            
            # Mock the get_learning_goal method to return None
            with patch.object(user_service, 'get_learning_goal') as mock_get_learning_goal:
                mock_get_learning_goal.return_value = None
                
                # Mock the learning goal update schema
                learning_goal_update = LearningGoalUpdate(
                    title="Updated Goal",
                    description="Updated Description"
                )
                
                # Call the function and expect an HTTPException
                with pytest.raises(HTTPException) as exc_info:
                    await user_service.update_learning_goal(1, 999, learning_goal_update, current_user)
                
                # Verify the exception
                assert exc_info.value.status_code == 404
                assert exc_info.value.detail == "Learning goal not found"


@pytest.mark.asyncio
async def test_delete_learning_goal_authorized(user_service):
    """Test deleting a learning goal when the user is authorized."""
    # Mock the current user
    current_user = {"id": 1, "username": "testuser"}
    
    # Mock the auth service client
    with patch('app.services.user.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'get_user') as mock_get_user:
            mock_get_user.return_value = {"id": 1, "username": "testuser"}
            
            # Mock the learning goal CRUD functions
            with patch('app.services.user.crud.learning_goal.delete_learning_goal') as mock_delete_goal:
                mock_delete_goal.return_value = LearningGoal(
                    id=1,
                    title="Test Goal",
                    description="Test Description",
                    status="in-progress",
                    streak_count=5,
                    auth_user_id=1
                )
                
                # Call the function
                result = await user_service.delete_learning_goal(1, 1, current_user)
                
                # Verify the results
                assert result is not None
                assert result.id == 1


@pytest.mark.asyncio
async def test_delete_learning_goal_unauthorized(user_service):
    """Test deleting a learning goal when the user is not authorized."""
    # Mock the current user
    current_user = {"id": 2, "username": "otheruser"}
    
    # Call the function and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await user_service.delete_learning_goal(1, 1, current_user)
    
    # Verify the exception
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not authorized to delete this learning goal"


@pytest.mark.asyncio
async def test_delete_learning_goal_not_found(user_service):
    """Test deleting a learning goal when the goal is not found."""
    # Mock the current user
    current_user = {"id": 1, "username": "testuser"}
    
    # Mock the auth service client
    with patch('app.services.user.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'get_user') as mock_get_user:
            mock_get_user.return_value = {"id": 1, "username": "testuser"}
            
            # Mock the get_learning_goal method to return None
            with patch.object(user_service, 'get_learning_goal') as mock_get_learning_goal:
                mock_get_learning_goal.return_value = None
                
                # Mock the learning goal CRUD functions to return None
                with patch('app.services.user.crud.learning_goal.delete_learning_goal') as mock_delete_goal:
                    mock_delete_goal.return_value = None
                    
                    # Call the function and expect an HTTPException
                    with pytest.raises(HTTPException) as exc_info:
                        await user_service.delete_learning_goal(1, 999, current_user)
                    
                    # Verify the exception
                    assert exc_info.value.status_code == 404
                    assert exc_info.value.detail == "Learning goal not found"


# Tests for get_current_user_from_token would require more complex mocking
# of JWT and HTTP calls, which would be better suited for integration tests