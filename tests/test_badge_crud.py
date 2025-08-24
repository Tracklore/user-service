import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import badge
from app.schemas.badge import BadgeCreate
from app.models.badge import Badge
from app.services.auth_service import auth_service_client

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
            mock_result.scalars().all.return_value = [
                Badge(id=1, name="Test Badge", description="Test Description", icon_url="http://example.com/icon.png", auth_user_id=1),
                Badge(id=2, name="Another Badge", description="Another Description", icon_url="http://example.com/icon2.png", auth_user_id=1)
            ]
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
async def test_create_user_badge():
    """Test creating a badge for a user."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the auth service client
    with patch('app.crud.badge.auth_service_client', auth_service_client):
        with patch.object(auth_service_client, 'ensure_auth_user_reference_exists') as mock_ensure:
            # Mock the badge to be created
            badge_create = BadgeCreate(
                name="New Badge",
                description="New Description",
                icon_url="http://example.com/new_icon.png"
            )
            
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