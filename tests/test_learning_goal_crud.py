import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import learning_goal
from app.schemas.learning_goal import LearningGoalCreate, LearningGoalUpdate
from app.models.learning_goal import LearningGoal
from app.services.auth_service import auth_service_client

@pytest.mark.asyncio
async def test_get_learning_goals_by_user():
    """Test getting learning goals for a user."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the auth service client
    with patch('app.crud.learning_goal.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'ensure_auth_user_reference_exists') as mock_ensure:
            # Mock the database query result
            mock_result = AsyncMock()
            mock_result.scalars().all.return_value = [
                LearningGoal(id=1, title="Test Goal", description="Test Description", status="in-progress", streak_count=5, auth_user_id=1),
                LearningGoal(id=2, title="Another Goal", description="Another Description", status="completed", streak_count=10, auth_user_id=1)
            ]
            mock_db.execute.return_value = mock_result
            
            # Call the function
            result = await learning_goal.get_learning_goals_by_user(mock_db, 1, 0, 10)
            
            # Verify the results
            assert len(result) == 2
            assert result[0].title == "Test Goal"
            assert result[1].title == "Another Goal"
            
            # Verify that ensure_auth_user_reference_exists was called
            mock_ensure.assert_called_once_with(1, mock_db)

@pytest.mark.asyncio
async def test_create_user_learning_goal():
    """Test creating a learning goal for a user."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the auth service client
    with patch('app.crud.learning_goal.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'ensure_auth_user_reference_exists') as mock_ensure:
            # Mock the learning goal to be created
            learning_goal_create = LearningGoalCreate(
                title="New Goal",
                description="New Description",
                status="in-progress",
                streak_count=0
            )
            
            # Mock the database refresh
            mock_db.refresh = AsyncMock()
            
            # Call the function
            result = await learning_goal.create_user_learning_goal(mock_db, learning_goal_create, 1)
            
            # Verify that ensure_auth_user_reference_exists was called
            mock_ensure.assert_called_once_with(1, mock_db)
            
            # Verify that db.add, db.commit, and db.refresh were called
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_get_learning_goal():
    """Test getting a specific learning goal."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the database query result
    mock_result = AsyncMock()
    mock_result.scalars().first.return_value = LearningGoal(
        id=1, 
        title="Test Goal", 
        description="Test Description", 
        status="in-progress", 
        streak_count=5, 
        auth_user_id=1
    )
    mock_db.execute.return_value = mock_result
    
    # Call the function
    result = await learning_goal.get_learning_goal(mock_db, 1, 1)
    
    # Verify the results
    assert result is not None
    assert result.id == 1
    assert result.title == "Test Goal"

@pytest.mark.asyncio
async def test_update_learning_goal():
    """Test updating a learning goal."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the existing learning goal
    existing_goal = LearningGoal(
        id=1, 
        title="Old Title", 
        description="Old Description", 
        status="in-progress", 
        streak_count=5, 
        auth_user_id=1
    )
    
    # Mock the get_learning_goal function to return the existing goal
    with patch('app.crud.learning_goal.get_learning_goal', return_value=existing_goal):
        # Mock the learning goal update data
        learning_goal_update = LearningGoalUpdate(
            title="New Title",
            description="New Description"
        )
        
        # Mock the database refresh
        mock_db.refresh = AsyncMock()
        
        # Call the function
        result = await learning_goal.update_learning_goal(mock_db, 1, 1, learning_goal_update)
        
        # Verify the results
        assert result is not None
        assert result.title == "New Title"
        assert result.description == "New Description"
        
        # Verify that db.commit and db.refresh were called
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_delete_learning_goal():
    """Test deleting a learning goal."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the existing learning goal
    existing_goal = LearningGoal(
        id=1, 
        title="Test Goal", 
        description="Test Description", 
        status="in-progress", 
        streak_count=5, 
        auth_user_id=1
    )
    
    # Mock the get_learning_goal function to return the existing goal
    with patch('app.crud.learning_goal.get_learning_goal', return_value=existing_goal):
        # Call the function
        result = await learning_goal.delete_learning_goal(mock_db, 1, 1)
        
        # Verify the results
        assert result is not None
        
        # Verify that db.delete and db.commit were called
        mock_db.delete.assert_called_once_with(existing_goal)
        mock_db.commit.assert_called_once()