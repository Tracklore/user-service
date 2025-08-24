import asyncio
import json
import aiormq
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.settings import settings
from app.models.auth_user_reference import AuthUserReference
from app.db.database import engine

# Set up logging
logger = logging.getLogger(__name__)

class MessageQueueConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = "user_events"
        self.dlq_name = "user_events_dlq"
        self.consumer_tag = None
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        
    async def connect(self):
        """Connect to the message queue."""
        try:
            # Connect to RabbitMQ
            self.connection = await aiormq.connect(settings.RABBITMQ_URL)
            self.channel = await self.connection.channel()
            # Declare the main queue that the auth-service publishes to
            await self.channel.queue_declare(self.queue_name, durable=True)
            # Declare the dead letter queue
            await self.channel.queue_declare(self.dlq_name, durable=True)
            logger.info(f"Connected to message queue. Main queue: {self.queue_name}, DLQ: {self.dlq_name}")
        except Exception as e:
            logger.error(f"Failed to connect to message queue: {e}")
            self.connection = None
            self.channel = None
    
    async def consume_user_events(self):
        """Consume UserCreated events from the message queue."""
        # If we're not connected to the message queue, try to connect
        if not self.connection or not self.channel:
            await self.connect()
            
        # If we still can't connect, log and return
        if not self.connection or not self.channel:
            logger.warning("Message queue not available, cannot consume events")
            return
            
        try:
            # Start consuming messages
            self.consumer_tag = await self.channel.basic_consume(
                self.queue_name, 
                self.handle_message,
                no_ack=False  # Manual acknowledgment for better control
            )
            logger.info(f"Started consuming messages from queue: {self.queue_name}")
        except Exception as e:
            logger.error(f"Failed to start consuming messages: {e}")
    
    async def handle_message(self, message):
        """Handle incoming messages from the queue with retry logic."""
        try:
            # Parse the message body
            event_data = json.loads(message.body.decode())
            
            # Check if this is a UserCreated event
            if event_data.get("event_type") == "UserCreated":
                # Try to process the message with retries
                success = await self.process_with_retry(event_data, message)
                if success:
                    # Acknowledge the message if processed successfully
                    await self.channel.basic_ack(message.delivery_tag)
                else:
                    # Reject and move to DLQ if processing failed after retries
                    await self.channel.basic_nack(message.delivery_tag, requeue=False)
                    logger.warning(f"Message moved to DLQ after {self.max_retries} attempts: {event_data}")
            else:
                logger.warning(f"Unknown event type: {event_data.get('event_type')}")
                # Acknowledge unknown events to prevent requeuing
                await self.channel.basic_ack(message.delivery_tag)
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            # Reject and move to DLQ for unhandled errors
            await self.channel.basic_nack(message.delivery_tag, requeue=False)
    
    async def process_with_retry(self, event_data, message):
        """Process a message with retry logic."""
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                await self.handle_user_created_event(event_data)
                return True  # Success
            except Exception as e:
                retry_count += 1
                if retry_count <= self.max_retries:
                    logger.warning(f"Attempt {retry_count} failed for message {event_data.get('user_id', 'unknown')}: {e}. Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error(f"All {self.max_retries} attempts failed for message {event_data.get('user_id', 'unknown')}: {e}")
                    return False  # Failed after all retries
    
    async def handle_user_created_event(self, event_data):
        """Handle UserCreated events by creating an auth user reference."""
        try:
            user_id = event_data.get("user_id")
            username = event_data.get("username")
            email = event_data.get("email")
            
            logger.info(f"Processing UserCreated event for user {user_id} ({username})")
            
            # Create a database session
            async with AsyncSession(engine) as db:
                # Check if we already have a reference to this user
                result = await db.execute(
                    AuthUserReference.__table__.select().where(AuthUserReference.id == user_id)
                )
                existing_ref = await result.fetchone()
                
                # If we don't have a reference, create one
                if not existing_ref:
                    auth_user_ref = AuthUserReference(id=user_id)
                    db.add(auth_user_ref)
                    await db.commit()
                    logger.info(f"Created auth user reference for user {user_id}")
                else:
                    logger.info(f"Auth user reference already exists for user {user_id}")
        except Exception as e:
            logger.error(f"Error handling UserCreated event: {e}")
            # Re-raise the exception to trigger retry logic
            raise
    
    async def stop_consuming(self):
        """Stop consuming messages."""
        if self.channel and self.consumer_tag:
            await self.channel.basic_cancel(self.consumer_tag)
    
    async def close(self):
        """Close the connection to the message queue."""
        if self.connection:
            await self.connection.close()

# Global instance
message_queue_consumer = MessageQueueConsumer()