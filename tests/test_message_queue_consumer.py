# Unit tests for the message queue consumer functionality
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import json
from app.services.message_queue_consumer import MessageQueueConsumer
from tests.test_utils import SAMPLE_USER_ID, SAMPLE_USER_DATA


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
        mock_channel.queue_declare.assert_any_call("user_events", durable=True)
        mock_channel.queue_declare.assert_any_call("user_events_dlq", durable=True)


@pytest.mark.asyncio
async def test_message_queue_consumer_connect_failure():
    """Test that the message queue consumer handles connection failures gracefully."""
    with patch('aiormq.connect', side_effect=Exception("Connection failed")), \
         patch('app.services.message_queue_consumer.settings', MockSettings()):
        # Create the consumer and try to connect
        consumer = MessageQueueConsumer()
        await consumer.connect()
        
        # Verify that the consumer handles the failure gracefully
        assert consumer.connection is None
        assert consumer.channel is None


@pytest.mark.asyncio
async def test_message_queue_consumer_consume_user_events():
    """Test that the message queue consumer can start consuming events."""
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
        
        # Start consuming events
        await consumer.consume_user_events()
        
        # Verify that basic_consume was called
        mock_channel.basic_consume.assert_called_once()


@pytest.mark.asyncio
async def test_message_queue_consumer_consume_user_events_not_connected():
    """Test that the message queue consumer handles consuming when not connected."""
    # Create the consumer without connecting
    consumer = MessageQueueConsumer()
    
    # Start consuming events (should not raise an exception)
    await consumer.consume_user_events()
    
    # Consumer should try to connect and then return since connection failed


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
            "user_id": SAMPLE_USER_ID,
            "username": "testuser",
            "email": "test@example.com"
        }
        
        # Handle the event (this should not raise an exception)
        await consumer.handle_user_created_event(event_data)
        
        # Verify that db.add and db.commit were called
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()


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
            "user_id": SAMPLE_USER_ID,
            "username": "testuser",
            "email": "test@example.com"
        }
        
        # Handle the event (this should not raise an exception)
        await consumer.handle_user_created_event(event_data)
        
        # Verify that db.add and db.commit were NOT called
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_message_queue_consumer_handle_user_created_event_db_error():
    """Test that the message queue consumer handles database errors in UserCreated events."""
    # Mock the database operations
    with patch('app.db.database.engine'), \
         patch('sqlalchemy.ext.asyncio.AsyncSession') as mock_session_class:
        
        # Mock the database session to raise an exception
        mock_session = AsyncMock()
        mock_session.execute.side_effect = Exception("Database error")
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        # Create the consumer
        consumer = MessageQueueConsumer()
        
        # Test data
        event_data = {
            "event_type": "UserCreated",
            "user_id": SAMPLE_USER_ID,
            "username": "testuser",
            "email": "test@example.com"
        }
        
        # Handle the event and expect an exception
        with pytest.raises(Exception) as exc_info:
            await consumer.handle_user_created_event(event_data)
        
        # Verify the exception
        assert "Database error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_message_queue_consumer_handles_message_user_created():
    """Test that the message queue consumer can handle UserCreated messages."""
    with patch.object(MessageQueueConsumer, 'handle_user_created_event') as mock_handle_user_created:
        # Mock the channel for acknowledgment
        mock_channel = AsyncMock()
        
        # Create the consumer and set the channel
        consumer = MessageQueueConsumer()
        consumer.channel = mock_channel
        
        # Create a mock message
        mock_message = MagicMock()
        mock_message.body = json.dumps({
            "event_type": "UserCreated",
            "user_id": SAMPLE_USER_ID,
            "username": "testuser",
            "email": "test@example.com"
        }).encode()
        mock_message.delivery_tag = 1
        
        # Mock process_with_retry to return success
        with patch.object(consumer, 'process_with_retry', return_value=True):
            # Handle the message
            await consumer.handle_message(mock_message)
            
            # Verify that the appropriate handler was called
            mock_handle_user_created.assert_called_once()
            
            # Verify that the message was acknowledged
            mock_channel.basic_ack.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_message_queue_consumer_handles_message_unknown_event():
    """Test that the message queue consumer handles unknown events gracefully."""
    # Mock the channel for acknowledgment
    mock_channel = AsyncMock()
    
    # Create the consumer and set the channel
    consumer = MessageQueueConsumer()
    consumer.channel = mock_channel
    
    # Create a mock message with unknown event type
    mock_message = MagicMock()
    mock_message.body = json.dumps({
        "event_type": "UnknownEvent",
        "data": "test"
    }).encode()
    mock_message.delivery_tag = 1
    
    # Handle the message
    await consumer.handle_message(mock_message)
    
    # Verify that the unknown event was acknowledged (not requeued)
    mock_channel.basic_ack.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_message_queue_consumer_handles_message_parsing_error():
    """Test that the message queue consumer handles message parsing errors."""
    # Mock the channel for negative acknowledgment
    mock_channel = AsyncMock()
    
    # Create the consumer and set the channel
    consumer = MessageQueueConsumer()
    consumer.channel = mock_channel
    
    # Create a mock message with invalid JSON
    mock_message = MagicMock()
    mock_message.body = b"invalid json"
    mock_message.delivery_tag = 1
    
    # Handle the message
    await consumer.handle_message(mock_message)
    
    # Verify that the message was negatively acknowledged and moved to DLQ
    mock_channel.basic_nack.assert_called_once_with(1, requeue=False)


@pytest.mark.asyncio
async def test_message_queue_consumer_process_with_retry_success():
    """Test that process_with_retry works correctly on success."""
    # Create the consumer
    consumer = MessageQueueConsumer()
    
    # Test data
    event_data = {
        "event_type": "UserCreated",
        "user_id": SAMPLE_USER_ID,
        "username": "testuser",
        "email": "test@example.com"
    }
    
    # Mock message
    mock_message = MagicMock()
    
    # Mock handle_user_created_event to succeed
    with patch.object(consumer, 'handle_user_created_event') as mock_handle:
        # Process with retry
        result = await consumer.process_with_retry(event_data, mock_message)
        
        # Verify the result
        assert result is True
        mock_handle.assert_called_once_with(event_data)


@pytest.mark.asyncio
async def test_message_queue_consumer_process_with_retry_failure():
    """Test that process_with_retry works correctly on failure."""
    # Create the consumer
    consumer = MessageQueueConsumer()
    
    # Test data
    event_data = {
        "event_type": "UserCreated",
        "user_id": SAMPLE_USER_ID,
        "username": "testuser",
        "email": "test@example.com"
    }
    
    # Mock message
    mock_message = MagicMock()
    
    # Mock handle_user_created_event to fail
    with patch.object(consumer, 'handle_user_created_event', side_effect=Exception("Processing failed")):
        # Process with retry
        result = await consumer.process_with_retry(event_data, mock_message)
        
        # Verify the result
        assert result is False


@pytest.mark.asyncio
async def test_message_queue_consumer_stop_consuming():
    """Test that the message queue consumer can stop consuming."""
    # Mock the channel
    mock_channel = AsyncMock()
    
    # Create the consumer and set up consuming
    consumer = MessageQueueConsumer()
    consumer.channel = mock_channel
    consumer.consumer_tag = "test_tag"
    
    # Stop consuming
    await consumer.stop_consuming()
    
    # Verify that basic_cancel was called
    mock_channel.basic_cancel.assert_called_once_with("test_tag")


@pytest.mark.asyncio
async def test_message_queue_consumer_close():
    """Test that the message queue consumer can close the connection."""
    # Mock the connection
    mock_connection = AsyncMock()
    
    # Create the consumer and set the connection
    consumer = MessageQueueConsumer()
    consumer.connection = mock_connection
    
    # Close the connection
    await consumer.close()
    
    # Verify that connection.close was called
    mock_connection.close.assert_called_once()