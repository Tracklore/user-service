import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.models.badge import Badge
from app.models.learning_goal import LearningGoal
from app.models.auth_user_reference import AuthUserReference
from app.schemas.badge import BadgeCreate
from app.schemas.learning_goal import LearningGoalCreate, LearningGoalUpdate
from tests.test_utils import SAMPLE_USER_ID, SAMPLE_USER_DATA, SAMPLE_BADGE_DATA, SAMPLE_LEARNING_GOAL_DATA


@pytest.mark.asyncio
async def test_full_user_profile_flow(client: AsyncClient):
    """Test the full flow of getting a user's profile with badges and learning goals."""
    # Mock user data from auth service
    user_profile_data = {
        "id": SAMPLE_USER_ID,
        "username": "testuser",
        "email": "test@example.com"
    }
    
    # Mock badges data
    badges_data = [
        {
            "id": 1,
            "name": "First Badge",
            "description": "First achievement",
            "icon_url": "http://example.com/badge1.png",
            "date_achieved": "2023-01-01T00:00:00",
            "auth_user_id": SAMPLE_USER_ID
        },
        {
            "id": 2,
            "name": "Second Badge",
            "description": "Second achievement",
            "icon_url": "http://example.com/badge2.png",
            "date_achieved": "2023-01-02T00:00:00",
            "auth_user_id": SAMPLE_USER_ID
        }
    ]
    
    # Mock learning goals data
    goals_data = [
        {
            "id": 1,
            "title": "Learn Python",
            "description": "Master Python programming",
            "status": "in-progress",
            "streak_count": 5,
            "auth_user_id": SAMPLE_USER_ID
        },
        {
            "id": 2,
            "title": "Learn FastAPI",
            "description": "Build APIs with FastAPI",
            "status": "completed",
            "streak_count": 10,
            "auth_user_id": SAMPLE_USER_ID
        }
    ]
    
    # Mock the UserService methods
    with patch('app.api.routes.get_user_service') as mock_get_user_service:
        mock_user_service = AsyncMock()
        mock_user_service.get_user_profile.return_value = {
            "id": SAMPLE_USER_ID,
            "username": "testuser",
            "email": "test@example.com",
            "badges": badges_data,
            "learning_goals": goals_data
        }
        mock_get_user_service.return_value = mock_user_service
        
        # Make the request
        response = await client.get(f"/users/{SAMPLE_USER_ID}")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == SAMPLE_USER_ID
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert len(data["badges"]) == 2
        assert len(data["learning_goals"]) == 2
        
        # Verify badge data
        assert data["badges"][0]["name"] == "First Badge"
        assert data["badges"][1]["name"] == "Second Badge"
        
        # Verify learning goal data
        assert data["learning_goals"][0]["title"] == "Learn Python"
        assert data["learning_goals"][1]["title"] == "Learn FastAPI"


@pytest.mark.asyncio
async def test_create_and_manage_badge_flow(client: AsyncClient):
    """Test the full flow of creating and managing badges."""
    # Mock the current user
    current_user = SAMPLE_USER_DATA
    
    # Mock the created badge
    created_badge = {
        "id": 1,
        "name": "New Badge",
        "description": "A newly created badge",
        "icon_url": "http://example.com/new_badge.png",
        "date_achieved": "2023-01-01T00:00:00",
        "auth_user_id": SAMPLE_USER_ID
    }
    
    with patch('app.api.routes.get_current_user_from_token') as mock_get_current_user, \
         patch('app.api.routes.get_user_service') as mock_get_user_service:
        
        # Mock the current user
        mock_get_current_user.return_value = current_user
        
        # Mock the user service
        mock_user_service = AsyncMock()
        mock_user_service.create_badge.return_value = Badge(
            id=1,
            name="New Badge",
            description="A newly created badge",
            icon_url="http://example.com/new_badge.png",
            auth_user_id=SAMPLE_USER_ID
        )
        mock_get_user_service.return_value = mock_user_service
        
        # Step 1: Create a badge
        response = await client.post(
            f"/users/{SAMPLE_USER_ID}/badges",
            json=SAMPLE_BADGE_DATA
        )
        
        # Verify the badge was created
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Test Badge"
        
        # Step 2: Retrieve the user's badges
        mock_user_service.get_user_badges.return_value = [created_badge]
        
        response = await client.get(f"/users/{SAMPLE_USER_ID}/badges")
        
        # Verify the badge is in the list
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "New Badge"


@pytest.mark.asyncio
async def test_create_and_manage_learning_goal_flow(client: AsyncClient):
    """Test the full flow of creating and managing learning goals."""
    # Mock the current user
    current_user = SAMPLE_USER_DATA
    
    # Mock the created learning goal
    created_goal = {
        "id": 1,
        "title": "New Goal",
        "description": "A newly created goal",
        "status": "in-progress",
        "streak_count": 0,
        "auth_user_id": SAMPLE_USER_ID
    }
    
    with patch('app.api.routes.get_current_user_from_token') as mock_get_current_user, \
         patch('app.api.routes.get_user_service') as mock_get_user_service:
        
        # Mock the current user
        mock_get_current_user.return_value = current_user
        
        # Mock the user service
        mock_user_service = AsyncMock()
        mock_user_service.create_learning_goal.return_value = LearningGoal(
            id=1,
            title="New Goal",
            description="A newly created goal",
            status="in-progress",
            streak_count=0,
            auth_user_id=SAMPLE_USER_ID
        )
        mock_get_user_service.return_value = mock_user_service
        
        # Step 1: Create a learning goal
        response = await client.post(
            f"/users/{SAMPLE_USER_ID}/goals",
            json=SAMPLE_LEARNING_GOAL_DATA
        )
        
        # Verify the learning goal was created
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Test Learning Goal"
        
        # Step 2: Retrieve the user's learning goals
        mock_user_service.get_user_learning_goals.return_value = [created_goal]
        
        response = await client.get(f"/users/{SAMPLE_USER_ID}/goals")
        
        # Verify the goal is in the list
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "New Goal"
        
        # Step 3: Update the learning goal
        mock_user_service.update_learning_goal.return_value = LearningGoal(
            id=1,
            title="Updated Goal",
            description="An updated goal",
            status="completed",
            streak_count=5,
            auth_user_id=SAMPLE_USER_ID
        )
        
        update_data = {
            "title": "Updated Goal",
            "description": "An updated goal",
            "status": "completed",
            "streak_count": 5
        }
        
        response = await client.put(
            f"/users/{SAMPLE_USER_ID}/goals/1",
            json=update_data
        )
        
        # Verify the learning goal was updated
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Updated Goal"
        assert data["status"] == "completed"
        assert data["streak_count"] == 5
        
        # Step 4: Delete the learning goal
        mock_user_service.delete_learning_goal.return_value = None  # Successful deletion returns None
        
        response = await client.delete(f"/users/{SAMPLE_USER_ID}/goals/1")
        
        # Verify the learning goal was deleted
        assert response.status_code == 200
        data = response.json()
        assert data == {"ok": True}


@pytest.mark.asyncio
async def test_user_created_event_flow():
    """Test the full flow of handling a UserCreated event."""
    # Import the message queue consumer
    from app.services.message_queue_consumer import MessageQueueConsumer
    
    # Mock the database operations
    with patch('app.db.database.engine'), \
         patch('sqlalchemy.ext.asyncio.AsyncSession') as mock_session_class:
        
        # Mock the database session
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        # Mock the query result (no existing reference)
        mock_result = AsyncMock()
        mock_result.fetchone.return_value = None  # No existing reference
        mock_session.execute.return_value = mock_result
        
        # Create the consumer
        consumer = MessageQueueConsumer()
        
        # Test data
        event_data = {
            "event_type": "UserCreated",
            "user_id": SAMPLE_USER_ID,
            "username": "testuser",
            "email": "test@example.com"
        }
        
        # Handle the event
        await consumer.handle_user_created_event(event_data)
        
        # Verify that the auth user reference was created
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_unauthorized_access_flow(client: AsyncClient):
    """Test the flow when a user tries to access unauthorized resources."""
    # Mock a different user as the current user
    current_user = {"id": 2, "username": "otheruser"}
    
    with patch('app.api.routes.get_current_user_from_token') as mock_get_current_user, \
         patch('app.api.routes.get_user_service') as mock_get_user_service:
        
        # Mock the current user
        mock_get_current_user.return_value = current_user
        
        # Mock the user service
        mock_user_service = AsyncMock()
        mock_get_user_service.return_value = mock_user_service
        
        # Try to create a badge for a different user
        response = await client.post(
            f"/users/{SAMPLE_USER_ID}/badges",
            json=SAMPLE_BADGE_DATA
        )
        
        # Verify access is denied
        assert response.status_code == 403
        
        # Try to create a learning goal for a different user
        response = await client.post(
            f"/users/{SAMPLE_USER_ID}/goals",
            json=SAMPLE_LEARNING_GOAL_DATA
        )
        
        # Verify access is denied
        assert response.status_code == 403
        
        # Try to update a learning goal for a different user
        update_data = {
            "title": "Updated Goal",
            "description": "Updated Description"
        }
        
        response = await client.put(
            f"/users/{SAMPLE_USER_ID}/goals/1",
            json=update_data
        )
        
        # Verify access is denied
        assert response.status_code == 403
        
        # Try to delete a learning goal for a different user
        response = await client.delete(f"/users/{SAMPLE_USER_ID}/goals/1")
        
        # Verify access is denied
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_data_integrity_flow(client: AsyncClient):
    """Test data integrity during CRUD operations."""
    # Mock the current user
    current_user = SAMPLE_USER_DATA
    
    # Mock badge data with proper foreign key relationship
    badge_with_fk = Badge(
        id=1,
        name="Test Badge",
        description="Test Description",
        icon_url="http://example.com/icon.png",
        auth_user_id=SAMPLE_USER_ID
    )
    
    # Mock learning goal data with proper foreign key relationship
    goal_with_fk = LearningGoal(
        id=1,
        title="Test Goal",
        description="Test Description",
        status="in-progress",
        streak_count=5,
        auth_user_id=SAMPLE_USER_ID
    )
    
    with patch('app.api.routes.get_current_user_from_token') as mock_get_current_user, \
         patch('app.api.routes.get_user_service') as mock_get_user_service:
        
        # Mock the current user
        mock_get_current_user.return_value = current_user
        
        # Mock the user service
        mock_user_service = AsyncMock()
        mock_user_service.create_badge.return_value = badge_with_fk
        mock_user_service.create_learning_goal.return_value = goal_with_fk
        mock_get_user_service.return_value = mock_user_service
        
        # Create a badge
        response = await client.post(
            f"/users/{SAMPLE_USER_ID}/badges",
            json=SAMPLE_BADGE_DATA
        )
        
        # Verify the badge has the correct foreign key
        assert response.status_code == 200
        data = response.json()
        assert data["auth_user_id"] == SAMPLE_USER_ID
        
        # Create a learning goal
        response = await client.post(
            f"/users/{SAMPLE_USER_ID}/goals",
            json=SAMPLE_LEARNING_GOAL_DATA
        )
        
        # Verify the learning goal has the correct foreign key
        assert response.status_code == 200
        data = response.json()
        assert data["auth_user_id"] == SAMPLE_USER_ID