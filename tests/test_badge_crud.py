import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.crud import badge
from app.schemas.badge import BadgeCreate
from app.models.badge import Badge
from app.services.auth_service import auth_service_client
from tests.test_utils import create_mock_db_result, SAMPLE_USER_ID, SAMPLE_BADGE_DATA


@pytest.mark.asyncio
async def test_get_badges_by_user():
    """Test getting badges for a user."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the auth service client
    with patch('app.crud.badge.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'ensure_auth_user_reference_exists') as mock_ensure:
            # Mock the database query result
            mock_result = AsyncMock()
            mock_scalars = MagicMock()  # Use MagicMock instead of AsyncMock for synchronous methods
            mock_scalars.all.return_value = [
                Badge(id=1, name="Test Badge", description="Test Description", icon_url="http://example.com/icon.png", auth_user_id=1),
                Badge(id=2, name="Another Badge", description="Another Description", icon_url="http://example.com/icon2.png", auth_user_id=1)
            ]
            mock_result.scalars = MagicMock(return_value=mock_scalars)
            mock_db.execute.return_value = mock_result
            
            # Call the function
            result = await badge.get_badges_by_user(mock_db, 1, 0, 10)
            
            # Verify the results
            assert len(result) == 2
            assert result[0].name == "Test Badge"
            assert result[1].name == "Another Badge"
            
            # Verify that ensure_auth_user_reference_exists was called
            mock_ensure.assert_called_once_with(1, mock_db)


@pytest.mark.asyncio
async def test_get_badges_by_user_empty_result():
    """Test getting badges for a user when there are no badges."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the auth service client
    with patch('app.crud.badge.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'ensure_auth_user_reference_exists') as mock_ensure:
            # Mock the database query result with empty list
            mock_result = AsyncMock()
            mock_scalars = MagicMock()  # Use MagicMock instead of AsyncMock for synchronous methods
            mock_scalars.all.return_value = []
            mock_result.scalars = MagicMock(return_value=mock_scalars)
            mock_db.execute.return_value = mock_result
            
            # Call the function
            result = await badge.get_badges_by_user(mock_db, 1, 0, 10)
            
            # Verify the results
            assert len(result) == 0
            
            # Verify that ensure_auth_user_reference_exists was called
            mock_ensure.assert_called_once_with(1, mock_db)


@pytest.mark.asyncio
async def test_get_badges_by_user_with_db_error():
    """Test getting badges for a user when database error occurs."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the auth service client
    with patch('app.crud.badge.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'ensure_auth_user_reference_exists') as mock_ensure:
            # Mock the database execute to raise an exception
            mock_db.execute.side_effect = SQLAlchemyError("Database error")
            
            # Call the function and expect an exception
            with pytest.raises(Exception) as exc_info:
                await badge.get_badges_by_user(mock_db, 1, 0, 10)
            
            # Verify the exception
            assert "Error fetching badges for user 1" in str(exc_info.value)
            
            # Verify that ensure_auth_user_reference_exists was called
            mock_ensure.assert_called_once_with(1, mock_db)


@pytest.mark.asyncio
async def test_get_badges_count_by_user():
    """Test getting the count of badges for a user."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the auth service client
    with patch('app.crud.badge.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'ensure_auth_user_reference_exists') as mock_ensure:
            # Mock the database query result
            mock_result = AsyncMock()
            mock_result.scalar_one.return_value = 5
            mock_db.execute = AsyncMock(return_value=mock_result)
            
            # Call the function
            result = await badge.get_badges_count_by_user(mock_db, 1)
            
            # Verify the results
            assert result == 5
            
            # Verify that ensure_auth_user_reference_exists was called
            mock_ensure.assert_called_once_with(1, mock_db)


@pytest.mark.asyncio
async def test_get_badges_count_by_user_with_db_error():
    """Test getting the count of badges for a user when database error occurs."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the auth service client
    with patch('app.crud.badge.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'ensure_auth_user_reference_exists') as mock_ensure:
            # Mock the database execute to raise an exception
            mock_db.execute.side_effect = SQLAlchemyError("Database error")
            
            # Call the function and expect an exception
            with pytest.raises(Exception) as exc_info:
                await badge.get_badges_count_by_user(mock_db, 1)
            
            # Verify the exception
            assert "Error counting badges for user 1" in str(exc_info.value)
            
            # Verify that ensure_auth_user_reference_exists was called
            mock_ensure.assert_called_once_with(1, mock_db)


@pytest.mark.asyncio
async def test_create_user_badge():
    """Test creating a badge for a user."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the auth service client
    with patch('app.crud.badge.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'ensure_auth_user_reference_exists') as mock_ensure:
            # Mock the badge to be created
            badge_create = BadgeCreate(**SAMPLE_BADGE_DATA)
            
            # Mock the database refresh
            mock_db.refresh = AsyncMock()
            
            # Call the function
            result = await badge.create_user_badge(mock_db, badge_create, 1)
            
            # Verify that ensure_auth_user_reference_exists was called
            mock_ensure.assert_called_once_with(1, mock_db)
            
            # Verify that db.add, db.commit, and db.refresh were called
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_badge_with_db_error():
    """Test creating a badge for a user when database error occurs."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the auth service client
    with patch('app.crud.badge.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'ensure_auth_user_reference_exists') as mock_ensure:
            # Mock the badge to be created
            badge_create = BadgeCreate(**SAMPLE_BADGE_DATA)
            
            # Mock the database commit to raise an exception
            mock_db.commit.side_effect = SQLAlchemyError("Database error")
            mock_db.rollback = AsyncMock()
            
            # Call the function and expect an exception
            with pytest.raises(Exception) as exc_info:
                await badge.create_user_badge(mock_db, badge_create, 1)
            
            # Verify the exception
            assert "Error creating badge for user 1" in str(exc_info.value)
            
            # Verify that ensure_auth_user_reference_exists was called
            mock_ensure.assert_called_once_with(1, mock_db)
            
            # Verify that db.add was called and db.rollback was called
            mock_db.add.assert_called_once()
            mock_db.rollback.assert_called_once()