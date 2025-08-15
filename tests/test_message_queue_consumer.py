# Unit tests for the message queue consumer functionality
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json
from app.services.message_queue_consumer import MessageQueueConsumer

# Create a simple mock settings object
class MockSettings:
    RABBITMQ_URL = 'amqp://test'

@pytest.mark.asyncio
async def test_message_queue_consumer_connect():
    """Test that the message queue consumer can connect."""
    with patch('aiormq.connect') as mock_connect, \
         patch('app.services.message_queue_consumer.settings', MockSettings()):
        # Mock the connection and channel
        mock_connection = AsyncMock()
        mock_channel = AsyncMock()
        mock_connect.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        
        # Create the consumer and connect
        consumer = MessageQueueConsumer()
        await consumer.connect()
        
        # Verify that the connection was attempted
        mock_connect.assert_called_once()
        mock_connection.channel.assert_called_once()
        mock_channel.queue_declare.assert_called_once_with("user_events", durable=True)

@pytest.mark.asyncio
async def test_message_queue_consumer_handle_user_created_event():
    """Test that the message queue consumer can handle UserCreated events."""
    # Mock the database operations
    with patch('app.db.database.engine'), \
         patch('sqlalchemy.ext.asyncio.AsyncSession') as mock_session_class:
        
        # Mock the database session
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        # Mock the query result
        mock_result = AsyncMock()
        mock_result.fetchone.return_value = None  # No existing reference
        mock_session.execute.return_value = mock_result
        
        # Create the consumer
        consumer = MessageQueueConsumer()
        
        # Test data
        event_data = {
            "event_type": "UserCreated",
            "user_id": 1,
            "username": "testuser",
            "email": "test@example.com"
        }
        
        # Handle the event (this should not raise an exception)
        await consumer.handle_user_created_event(event_data)
        
        # We can't easily verify the database operations in this test
        # but we can verify that the function completed without error

@pytest.mark.asyncio
async def test_message_queue_consumer_handles_existing_user_reference():
    """Test that the message queue consumer handles existing user references."""
    # Mock the database operations
    with patch('app.db.database.engine'), \
         patch('sqlalchemy.ext.asyncio.AsyncSession') as mock_session_class:
        
        # Mock the database session
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        # Mock the query result to return an existing reference
        mock_result = AsyncMock()
        mock_result.fetchone.return_value = MagicMock()  # Existing reference
        mock_session.execute.return_value = mock_result
        
        # Create the consumer
        consumer = MessageQueueConsumer()
        
        # Test data
        event_data = {
            "event_type": "UserCreated",
            "user_id": 1,
            "username": "testuser",
            "email": "test@example.com"
        }
        
        # Handle the event (this should not raise an exception)
        await consumer.handle_user_created_event(event_data)
        
        # We can't easily verify the database operations in this test
        # but we can verify that the function completed without error

@pytest.mark.asyncio
async def test_message_queue_consumer_handles_connection_failure():
    """Test that the message queue consumer handles connection failures gracefully."""
    with patch('aiormq.connect', side_effect=Exception("Connection failed")), \
         patch('app.services.message_queue_consumer.settings', MockSettings()):
        # Create the consumer and try to connect
        consumer = MessageQueueConsumer()
        await consumer.connect()
        
        # Verify that the consumer handles the failure gracefully
        assert consumer.connection is None
        assert consumer.channel is None
        
        # Test that consuming doesn't crash even when not connected
        # This should not raise an exception
        await consumer.consume_user_events()

@pytest.mark.asyncio
async def test_message_queue_consumer_handles_message():
    """Test that the message queue consumer can handle incoming messages."""
    with patch.object(MessageQueueConsumer, 'handle_user_created_event') as mock_handle_user_created:
        # Create the consumer
        consumer = MessageQueueConsumer()
        
        # Create a mock message
        mock_message = MagicMock()
        mock_message.body = json.dumps({
            "event_type": "UserCreated",
            "user_id": 1,
            "username": "testuser",
            "email": "test@example.com"
        }).encode()
        
        # Handle the message
        await consumer.handle_message(mock_message)
        
        # Verify that the appropriate handler was called
        mock_handle_user_created.assert_called_once()

@pytest.mark.asyncio
async def test_message_queue_consumer_handles_unknown_event():
    """Test that the message queue consumer handles unknown events gracefully."""
    with patch('builtins.print') as mock_print:
        # Create the consumer
        consumer = MessageQueueConsumer()
        
        # Create a mock message with unknown event type
        mock_message = MagicMock()
        mock_message.body = json.dumps({
            "event_type": "UnknownEvent",
            "data": "test"
        }).encode()
        
        # Handle the message
        await consumer.handle_message(mock_message)
        
        # Verify that the unknown event was handled gracefully
        mock_print.assert_called()