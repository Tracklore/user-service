import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.crud import learning_goal
from app.schemas.learning_goal import LearningGoalCreate, LearningGoalUpdate
from app.models.learning_goal import LearningGoal
from app.services.auth_service import auth_service_client
from tests.test_utils import create_mock_db_result, SAMPLE_USER_ID, SAMPLE_LEARNING_GOAL_DATA


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
            mock_scalars = MagicMock()  # Use MagicMock instead of AsyncMock for synchronous methods
            mock_scalars.all.return_value = [
                LearningGoal(id=1, title="Test Goal", description="Test Description", status="in-progress", streak_count=5, auth_user_id=1),
                LearningGoal(id=2, title="Another Goal", description="Another Description", status="completed", streak_count=10, auth_user_id=1)
            ]
            mock_result.scalars = MagicMock(return_value=mock_scalars)
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
async def test_get_learning_goals_by_user_empty_result():
    """Test getting learning goals for a user when there are no goals."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the auth service client
    with patch('app.crud.learning_goal.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'ensure_auth_user_reference_exists') as mock_ensure:
            # Mock the database query result with empty list
            mock_result = AsyncMock()
            mock_scalars = MagicMock()  # Use MagicMock instead of AsyncMock for synchronous methods
            mock_scalars.all.return_value = []
            mock_result.scalars = MagicMock(return_value=mock_scalars)
            mock_db.execute.return_value = mock_result
            
            # Call the function
            result = await learning_goal.get_learning_goals_by_user(mock_db, 1, 0, 10)
            
            # Verify the results
            assert len(result) == 0
            
            # Verify that ensure_auth_user_reference_exists was called
            mock_ensure.assert_called_once_with(1, mock_db)


@pytest.mark.asyncio
async def test_get_learning_goals_by_user_with_db_error():
    """Test getting learning goals for a user when database error occurs."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the auth service client
    with patch('app.crud.learning_goal.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'ensure_auth_user_reference_exists') as mock_ensure:
            # Mock the database execute to raise an exception
            mock_db.execute.side_effect = SQLAlchemyError("Database error")
            
            # Call the function and expect an exception
            with pytest.raises(Exception) as exc_info:
                await learning_goal.get_learning_goals_by_user(mock_db, 1, 0, 10)
            
            # Verify the exception
            assert "Error fetching learning goals for user 1" in str(exc_info.value)
            
            # Verify that ensure_auth_user_reference_exists was called
            mock_ensure.assert_called_once_with(1, mock_db)


@pytest.mark.asyncio
async def test_get_learning_goals_count_by_user():
    """Test getting the count of learning goals for a user."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the auth service client
    with patch('app.crud.learning_goal.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'ensure_auth_user_reference_exists') as mock_ensure:
            # Mock the database query result
            mock_result = AsyncMock()
            mock_result.scalar_one.return_value = 3
            mock_db.execute.return_value = mock_result
            
            # Call the function
            result = await learning_goal.get_learning_goals_count_by_user(mock_db, 1)
            
            # Verify the results
            assert result == 3
            
            # Verify that ensure_auth_user_reference_exists was called
            mock_ensure.assert_called_once_with(1, mock_db)


@pytest.mark.asyncio
async def test_get_learning_goals_count_by_user_with_db_error():
    """Test getting the count of learning goals for a user when database error occurs."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the auth service client
    with patch('app.crud.learning_goal.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'ensure_auth_user_reference_exists') as mock_ensure:
            # Mock the database execute to raise an exception
            mock_db.execute.side_effect = SQLAlchemyError("Database error")
            
            # Call the function and expect an exception
            with pytest.raises(Exception) as exc_info:
                await learning_goal.get_learning_goals_count_by_user(mock_db, 1)
            
            # Verify the exception
            assert "Error counting learning goals for user 1" in str(exc_info.value)
            
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
            learning_goal_create = LearningGoalCreate(**SAMPLE_LEARNING_GOAL_DATA)
            
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
async def test_create_user_learning_goal_with_db_error():
    """Test creating a learning goal for a user when database error occurs."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the auth service client
    with patch('app.crud.learning_goal.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'ensure_auth_user_reference_exists') as mock_ensure:
            # Mock the learning goal to be created
            learning_goal_create = LearningGoalCreate(**SAMPLE_LEARNING_GOAL_DATA)
            
            # Mock the database commit to raise an exception
            mock_db.commit.side_effect = SQLAlchemyError("Database error")
            mock_db.rollback = AsyncMock()
            
            # Call the function and expect an exception
            with pytest.raises(Exception) as exc_info:
                await learning_goal.create_user_learning_goal(mock_db, learning_goal_create, 1)
            
            # Verify the exception
            assert "Error creating learning goal for user 1" in str(exc_info.value)
            
            # Verify that ensure_auth_user_reference_exists was called
            mock_ensure.assert_called_once_with(1, mock_db)
            
            # Verify that db.add was called and db.rollback was called
            mock_db.add.assert_called_once()
            mock_db.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_get_learning_goal():
    """Test getting a specific learning goal."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the database query result
    mock_result = AsyncMock()
    mock_scalars = MagicMock()  # Use MagicMock instead of AsyncMock for synchronous methods
    mock_scalars.first.return_value = LearningGoal(
        id=1, 
        title="Test Goal", 
        description="Test Description", 
        status="in-progress", 
        streak_count=5, 
        auth_user_id=1
    )
    mock_result.scalars = MagicMock(return_value=mock_scalars)
    mock_db.execute.return_value = mock_result
    
    # Call the function
    result = await learning_goal.get_learning_goal(mock_db, 1, 1)
    
    # Verify the results
    assert result is not None
    assert result.id == 1
    assert result.title == "Test Goal"


@pytest.mark.asyncio
async def test_get_learning_goal_not_found():
    """Test getting a specific learning goal when it doesn't exist."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the database query result with None
    mock_result = AsyncMock()
    mock_scalars = MagicMock()  # Use MagicMock instead of AsyncMock for synchronous methods
    mock_scalars.first.return_value = None
    mock_result.scalars = MagicMock(return_value=mock_scalars)
    mock_db.execute.return_value = mock_result
    
    # Call the function
    result = await learning_goal.get_learning_goal(mock_db, 999, 1)
    
    # Verify the results
    assert result is None


@pytest.mark.asyncio
async def test_get_learning_goal_with_db_error():
    """Test getting a specific learning goal when database error occurs."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the database execute to raise an exception
    mock_db.execute.side_effect = SQLAlchemyError("Database error")
    
    # Call the function and expect an exception
    with pytest.raises(Exception) as exc_info:
        await learning_goal.get_learning_goal(mock_db, 1, 1)
    
    # Verify the exception
    assert "Error fetching learning goal 1 for user 1" in str(exc_info.value)


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
async def test_update_learning_goal_not_found():
    """Test updating a learning goal when it doesn't exist."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the get_learning_goal function to return None
    with patch('app.crud.learning_goal.get_learning_goal', return_value=None):
        # Mock the learning goal update data
        learning_goal_update = LearningGoalUpdate(
            title="New Title",
            description="New Description"
        )
        
        # Call the function
        result = await learning_goal.update_learning_goal(mock_db, 999, 1, learning_goal_update)
        
        # Verify the results
        assert result is None
        
        # Verify that db.commit and db.refresh were not called
        mock_db.commit.assert_not_called()
        mock_db.refresh.assert_not_called()


@pytest.mark.asyncio
async def test_update_learning_goal_with_db_error():
    """Test updating a learning goal when database error occurs."""
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
        
        # Mock the database commit to raise an exception
        mock_db.commit.side_effect = SQLAlchemyError("Database error")
        mock_db.rollback = AsyncMock()
        
        # Call the function and expect an exception
        with pytest.raises(Exception) as exc_info:
            await learning_goal.update_learning_goal(mock_db, 1, 1, learning_goal_update)
        
        # Verify the exception
        assert "Error updating learning goal 1 for user 1" in str(exc_info.value)
        
        # Verify that db.rollback was called
        mock_db.rollback.assert_called_once()


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


@pytest.mark.asyncio
async def test_delete_learning_goal_not_found():
    """Test deleting a learning goal when it doesn't exist."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the get_learning_goal function to return None
    with patch('app.crud.learning_goal.get_learning_goal', return_value=None):
        # Call the function
        result = await learning_goal.delete_learning_goal(mock_db, 999, 1)
        
        # Verify the results
        assert result is None
        
        # Verify that db.delete and db.commit were not called
        mock_db.delete.assert_not_called()
        mock_db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_learning_goal_with_db_error():
    """Test deleting a learning goal when database error occurs."""
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
        # Mock the database commit to raise an exception
        mock_db.commit.side_effect = SQLAlchemyError("Database error")
        mock_db.rollback = AsyncMock()
        
        # Call the function and expect an exception
        with pytest.raises(Exception) as exc_info:
            await learning_goal.delete_learning_goal(mock_db, 1, 1)
        
        # Verify the exception
        assert "Error deleting learning goal 1 for user 1" in str(exc_info.value)
        
        # Verify that db.delete was called and db.rollback was called
        mock_db.delete.assert_called_once_with(existing_goal)
        mock_db.rollback.assert_called_once()