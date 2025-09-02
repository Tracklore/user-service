# User Service

## Overview
The user-service is a microservice responsible for managing all user-related data beyond core authentication. It provides functionality for user profiles, activity tracking, gamification (badges), and the learning tracker. It relies on the auth-service to identify the authenticated user via a JWT token.

In the new microservice architecture, the user-service no longer manages user authentication data. Instead, it maintains references to users managed by the auth-service and stores additional user profile data such as badges and learning goals.

## API Endpoints
All endpoints are prefixed with `/users`.

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/me` | GET | Retrieves the authenticated user's profile. | Required |
| `/{auth_user_id}` | GET | Retrieves a specific user's public profile. | None |
| `/{auth_user_id}/badges` | GET | Retrieves all badges earned by a user. | None |
| `/{auth_user_id}/badges` | POST | Creates a new badge for the user. | Required (for auth_user_id matching authenticated user) |
| `/{auth_user_id}/goals` | GET | Retrieves all learning goals for a user. | None |
| `/{auth_user_id}/goals` | POST | Creates a new learning goal for the user. | Required (for auth_user_id matching authenticated user) |
| `/{auth_user_id}/goals/{goal_id}` | PUT | Updates a specific learning goal. | Required (for auth_user_id matching authenticated user) |
| `/{auth_user_id}/goals/{goal_id}` | DELETE | Deletes a specific learning goal. | Required (for auth_user_id matching authenticated user) |

## Data Models & Schemas

### AuthUserReference
A reference to a user managed by the auth-service. This model maintains referential integrity while keeping services separate.

### Badge
A schema for a badge object, including name, description, icon_url, and the date_achieved.

### LearningGoal
A schema for a user's learning goal, containing a title, description, status (e.g., 'in-progress', 'completed'), and a streak_count.

## Core Logic

### Microservice Architecture
The user-service now strictly follows microservice principles:
1. **Separation of Concerns**: Authentication data is managed entirely by the auth-service
2. **Data References**: The user-service maintains references to auth-service users via foreign keys
3. **Service Communication**: The user-service communicates with the auth-service via HTTP requests to fetch user data when needed
4. **Event-Driven Communication**: The user-service consumes "UserCreated" events from a message queue to create auth user references

### Profile Management
The service no longer performs CRUD operations on user profile fields in a shared users table. Instead, it:
1. Fetches user authentication data from the auth-service
2. Manages additional profile data (badges, learning goals) in its own database
3. Links this data to auth-service users via foreign key references

### Gamification & Learning
The service uses separate database tables to store badges and learning goals. These tables have a foreign key relationship with the `auth_users` table to link the data to a specific user managed by the auth-service.

## Message Queue Integration
The user-service now consumes "UserCreated" events from a RabbitMQ message queue. When the auth-service creates a new user, it publishes an event to the queue. The user-service consumes this event and automatically creates an AuthUserReference record to maintain referential integrity.

This approach eliminates the need for shared databases between services and provides a scalable, decoupled communication mechanism.

## Database Migration
To migrate to the new microservice architecture:
1. Run the migration script: `python apply_migrations.py`
2. This will create the new `auth_users` reference table and update foreign key relationships
3. Existing data will need to be migrated to the new schema

## Running the Service
To run the service:
```bash
docker-compose up
```

This will start the user-service, auth-service, database, and RabbitMQ in separate containers.

## Testing
A simple health check test is included to verify the service is running correctly.

## Environment Variables
The service requires several environment variables to be set. Copy the `.env.example` file to `.env` and configure the values appropriately:

```bash
cp .env.example .env
```

Key environment variables:
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Secret key for JWT token signing (must be unique and secure in production)
- `RABBITMQ_URL`: Connection string for RabbitMQ message queue

### Generating Secure Secrets
For production environments, generate secure secret keys using one of these methods:

1. Using OpenSSL:
   ```bash
   openssl rand -hex 32
   ```

2. Using Python:
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

3. Using the provided script:
   ```bash
   python generate_secrets.py
   ```

   You can also specify a custom length:
   ```bash
   python generate_secrets.py --length 64
   ```

### Security Best Practices
1. Never commit `.env` files to version control
2. Use different secret keys for different environments
3. Rotate secrets periodically
4. Use a secrets management system (like HashiCorp Vault or AWS Secrets Manager) in production
5. Ensure environment variables are properly secured in your deployment environment

## Database Connection Management

The application uses SQLAlchemy's connection pooling to efficiently manage database connections. For details on best practices for database connection management, see [DATABASE_CONNECTION_BEST_PRACTICES.md](DATABASE_CONNECTION_BEST_PRACTICES.md).

Key environment variables for connection pooling:
- `DATABASE_POOL_SIZE`: The number of connections to maintain in the pool (default: 20)
- `DATABASE_MAX_OVERFLOW`: The maximum number of connections that can be created beyond the pool size (default: 30)
- `DATABASE_POOL_TIMEOUT`: The number of seconds to wait before giving up on getting a connection from the pool (default: 30)
- `DATABASE_POOL_RECYCLE`: The number of seconds after which to recreate database connections (default: 3600)