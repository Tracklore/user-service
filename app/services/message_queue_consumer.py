import asyncio
import json
import aiormq
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.settings import settings
from app.models.auth_user_reference import AuthUserReference
from app.db.database import engine

class MessageQueueConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = "user_events"
        self.consumer_tag = None
        
    async def connect(self):
        """Connect to the message queue."""
        try:
            # Connect to RabbitMQ
            self.connection = await aiormq.connect(settings.RABBITMQ_URL)
            self.channel = await self.connection.channel()
            # Declare the same queue that the auth-service publishes to
            await self.channel.queue_declare(self.queue_name, durable=True)
        except Exception as e:
            print(f"Failed to connect to message queue: {e}")
            self.connection = None
            self.channel = None
    
    async def consume_user_events(self):
        """Consume UserCreated events from the message queue."""
        # If we're not connected to the message queue, try to connect
        if not self.connection or not self.channel:
            await self.connect()
            
        # If we still can't connect, log and return
        if not self.connection or not self.channel:
            print("Warning: Message queue not available, cannot consume events")
            return
            
        try:
            # Start consuming messages
            self.consumer_tag = await self.channel.basic_consume(
                self.queue_name, 
                self.handle_message,
                no_ack=True  # Auto acknowledge messages
            )
            print(f"Started consuming messages from queue: {self.queue_name}")
        except Exception as e:
            print(f"Failed to start consuming messages: {e}")
    
    async def handle_message(self, message):
        """Handle incoming messages from the queue."""
        try:
            # Parse the message body
            event_data = json.loads(message.body.decode())
            
            # Check if this is a UserCreated event
            if event_data.get("event_type") == "UserCreated":
                await self.handle_user_created_event(event_data)
            else:
                print(f"Unknown event type: {event_data.get('event_type')}")
        except Exception as e:
            print(f"Error handling message: {e}")
    
    async def handle_user_created_event(self, event_data):
        """Handle UserCreated events by creating an auth user reference."""
        try:
            user_id = event_data.get("user_id")
            username = event_data.get("username")
            email = event_data.get("email")
            
            print(f"Processing UserCreated event for user {user_id} ({username})")
            
            # Create a database session
            async with AsyncSession(engine) as db:
                # Check if we already have a reference to this user
                result = await db.execute(
                    AuthUserReference.__table__.select().where(AuthUserReference.id == user_id)
                )
                existing_ref = result.fetchone()
                
                # If we don't have a reference, create one
                if not existing_ref:
                    auth_user_ref = AuthUserReference(id=user_id)
                    db.add(auth_user_ref)
                    await db.commit()
                    print(f"Created auth user reference for user {user_id}")
                else:
                    print(f"Auth user reference already exists for user {user_id}")
        except Exception as e:
            print(f"Error handling UserCreated event: {e}")
            # In a production system, you might want to implement retry logic or dead letter queues
    
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