import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from app.services.auth_service import AuthServiceClient
from app.models.auth_user_reference import AuthUserReference
from tests.test_utils import SAMPLE_USER_ID, SAMPLE_USER_DATA


@pytest.fixture
def auth_service_client():
    """Create an AuthServiceClient instance."""
    return AuthServiceClient()


@pytest.mark.asyncio
async def test_auth_service_client_init():
    """Test AuthServiceClient initialization."""
    client = AuthServiceClient()
    # The base_url might be set from environment variables, so we'll check it's a string
    assert isinstance(client.base_url, str)
    assert len(client.base_url) > 0
    assert isinstance(client.client, httpx.AsyncClient)


@pytest.mark.asyncio
async def test_get_user_success(auth_service_client):
    """Test getting a user when the request is successful."""
    # Mock the HTTP response
    mock_response = AsyncMock()
    mock_response.json = MagicMock(return_value=SAMPLE_USER_DATA)
    mock_response.raise_for_status = MagicMock()
    
    # Mock the HTTP client
    with patch.object(auth_service_client.client, 'get', return_value=mock_response):
        # Call the function
        result = await auth_service_client.get_user(SAMPLE_USER_ID)
        
        # Verify the results
        assert result is not None
        assert result["id"] == SAMPLE_USER_ID
        assert result["username"] == "testuser"


@pytest.mark.asyncio
async def test_get_user_http_error(auth_service_client):
    """Test getting a user when the HTTP request fails."""
    # Mock the HTTP client to raise an exception
    with patch.object(auth_service_client.client, 'get', side_effect=httpx.HTTPError("HTTP error")):
        # Call the function
        result = await auth_service_client.get_user(SAMPLE_USER_ID)
        
        # Verify the results
        assert result is None


@pytest.mark.asyncio
async def test_get_user_by_email_success(auth_service_client):
    """Test getting a user by email when the request is successful."""
    # Mock the HTTP response
    mock_response = AsyncMock()
    mock_response.json = MagicMock(return_value=SAMPLE_USER_DATA)
    mock_response.raise_for_status = MagicMock()
    
    # Mock the HTTP client
    with patch.object(auth_service_client.client, 'get', return_value=mock_response):
        # Call the function
        result = await auth_service_client.get_user_by_email("test@example.com")
        
        # Verify the results
        assert result is not None
        assert result["id"] == SAMPLE_USER_ID
        assert result["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_by_email_http_error(auth_service_client):
    """Test getting a user by email when the HTTP request fails."""
    # Mock the HTTP client to raise an exception
    with patch.object(auth_service_client.client, 'get', side_effect=httpx.HTTPError("HTTP error")):
        # Call the function
        result = await auth_service_client.get_user_by_email("test@example.com")
        
        # Verify the results
        assert result is None


@pytest.mark.asyncio
async def test_create_auth_user_reference(auth_service_client):
    """Test creating an auth user reference."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the database refresh
    mock_db.refresh = AsyncMock()
    
    # Call the function
    result = await auth_service_client.create_auth_user_reference(SAMPLE_USER_ID, mock_db)
    
    # Verify that db.add, db.commit, and db.refresh were called
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    
    # Verify the result type
    assert isinstance(result, AuthUserReference)
    assert result.id == SAMPLE_USER_ID


@pytest.mark.asyncio
async def test_ensure_auth_user_reference_exists_when_exists(auth_service_client):
    """Test ensuring an auth user reference exists when it already exists."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the database query result
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = AuthUserReference(id=SAMPLE_USER_ID)
    mock_db.execute.return_value = mock_result
    
    # Call the function
    result = await auth_service_client.ensure_auth_user_reference_exists(SAMPLE_USER_ID, mock_db)
    
    # Verify the results
    assert isinstance(result, AuthUserReference)
    assert result.id == SAMPLE_USER_ID
    
    # Verify that db.add, db.commit, and db.refresh were NOT called
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()
    mock_db.refresh.assert_not_called()


@pytest.mark.asyncio
async def test_ensure_auth_user_reference_exists_when_not_exists(auth_service_client):
    """Test ensuring an auth user reference exists when it doesn't exist yet."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the database query result for the first call (not found)
    mock_result1 = AsyncMock()
    mock_result1.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result1
    
    # Mock the database refresh for the create operation
    mock_db.refresh = AsyncMock()
    
    # Mock the database query result for the second call (after creation)
    mock_result2 = AsyncMock()
    mock_result2.scalar_one_or_none.return_value = AuthUserReference(id=SAMPLE_USER_ID)
    
    # We need to mock the execute method to return different results on subsequent calls
    execute_side_effect = [mock_result1, mock_result2]
    
    with patch.object(mock_db, 'execute', side_effect=execute_side_effect):
        # Call the function
        result = await auth_service_client.ensure_auth_user_reference_exists(SAMPLE_USER_ID, mock_db)
        
        # Verify the results
        assert isinstance(result, AuthUserReference)
        assert result.id == SAMPLE_USER_ID
        
        # Verify that db.add and db.commit were called
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_ensure_auth_user_reference_exists_db_error(auth_service_client):
    """Test ensuring an auth user reference exists when a database error occurs."""
    # Mock the database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock the database execute to raise an exception
    mock_db.execute.side_effect = Exception("Database error")
    
    # Call the function and expect an exception
    with pytest.raises(Exception) as exc_info:
        await auth_service_client.ensure_auth_user_reference_exists(SAMPLE_USER_ID, mock_db)
    
    # Verify the exception
    assert "Database error" in str(exc_info.value)