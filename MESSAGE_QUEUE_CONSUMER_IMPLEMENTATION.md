# User-Service Message Queue Consumer Implementation

## Summary of Changes

### New Features Added
1. **Message Queue Consumer**: Implemented RabbitMQ consumer for processing "UserCreated" events
2. **Event-Driven Architecture**: User-service now consumes events from auth-service to create auth user references
3. **Improved Microservice Communication**: Replaced direct database operations with message-based communication

### Files Modified/Added

#### New Files
1. `app/services/message_queue_consumer.py` - Message queue consumer implementation
2. Updated `requirements.txt` - Added `aiormq` dependency for RabbitMQ integration

#### Modified Files
1. `app/core/settings.py` - Added RabbitMQ URL configuration
2. `app/main.py` - Added startup/shutdown event handlers for message queue consumer
3. `.env` - Added RabbitMQ URL configuration
4. `docker-compose.yml` - Added RabbitMQ service
5. `README.md` - Documented new message queue functionality

### Implementation Details

#### Message Queue Consumer
- Uses `aiormq` library for RabbitMQ integration
- Implements connection management with automatic reconnection
- Consumes "UserCreated" events from the message queue
- Creates AuthUserReference records when new users are created in auth-service
- Gracefully handles message queue unavailability

#### Event Structure
The consumer expects messages in the following format:
```json
{
  "event_type": "UserCreated",
  "user_id": 123,
  "username": "johndoe",
  "email": "john@example.com",
  "timestamp": 1234567890.123
}
```

#### Flow
1. Auth-service publishes "UserCreated" events to RabbitMQ when users are created
2. User-service consumes these events from the message queue
3. For each event, user-service creates an AuthUserReference record if one doesn't already exist
4. This maintains referential integrity while keeping services separate

### Benefits
1. **Decoupled Services**: Services no longer need shared databases
2. **Automatic Synchronization**: User references are automatically created when users are created
3. **Scalability**: Services can scale independently
4. **Reliability**: Message queue provides buffering if services are temporarily unavailable
5. **Extensibility**: Easy to add more event types or processing logic

### Docker Configuration
- Added RabbitMQ service to docker-compose.yml
- Updated environment variables to use service names for networking

### Environment Variables
- `RABBITMQ_URL`: Configures connection to RabbitMQ (default: amqp://guest:guest@rabbitmq:5672/)

## Testing
The message queue consumer has been designed to not block service startup if the message queue is unavailable, ensuring the user-service remains functional even if the message queue is down.