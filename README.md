# User Service

## Overview
The user-service is a microservice responsible for managing all user-related data including authentication, profiles, activity tracking, gamification (badges), and the learning tracker.

In the updated architecture, the user-service manages user authentication data directly rather than relying on an external auth-service.

## API Endpoints
All endpoints are prefixed with `/users`.

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/me` | GET | Retrieves the authenticated user's profile. | Required |
| `/{user_id}` | GET | Retrieves a specific user's public profile. | None |
| `/{user_id}/badges` | GET | Retrieves all badges earned by a user. | None |
| `/{user_id}/badges` | POST | Creates a new badge for the user. | Required (for user_id matching authenticated user) |
| `/{user_id}/goals` | GET | Retrieves all learning goals for a user. | None |
| `/{user_id}/goals` | POST | Creates a new learning goal for the user. | Required (for user_id matching authenticated user) |
| `/{user_id}/goals/{goal_id}` | PUT | Updates a specific learning goal. | Required (for user_id matching authenticated user) |
| `/{user_id}/goals/{goal_id}` | DELETE | Deletes a specific learning goal. | Required (for user_id matching authenticated user) |
| `/` | POST | Creates a new user. | None |
| `/{user_id}` | PUT | Updates a user's profile. | Required (for user_id matching authenticated user) |
| `/{user_id}` | DELETE | Deletes a user. | Required (for user_id matching authenticated user) |

## Data Models & Schemas

### User
A model for user data with the following fields:
- `id`: UUID (Primary Key)
- `username`: VARCHAR(50) UNIQUE NOT NULL
- `email`: VARCHAR(100) UNIQUE NOT NULL
- `password_hash`: TEXT NOT NULL
- `display_name`: VARCHAR(100)
- `bio`: TEXT
- `avatar_url`: TEXT
- `location`: VARCHAR(100)
- `created_at`: TIMESTAMP DEFAULT NOW()
- `updated_at`: TIMESTAMP DEFAULT NOW()

### Badge
A schema for a badge object, including name, description, icon_url, and the date_achieved.

### LearningGoal
A schema for a user's learning goal, containing a title, description, status (e.g., 'in-progress', 'completed'), and a streak_count.

## Core Logic

### User Management
The service now manages user authentication data directly:
1. **User Registration**: Users can register with username, email, and password
2. **User Authentication**: JWT-based authentication
3. **Profile Management**: Users can update their profile information
4. **Data References**: Badges and learning goals are linked to users via foreign keys

### Gamification & Learning
The service uses separate database tables to store badges and learning goals. These tables have a foreign key relationship with the `users` table to link the data to a specific user.

## Database Migration
To migrate to the new architecture:
1. Run the migration scripts in order:
   - First migration updates the existing schema
   - Second migration creates the new users table
2. Existing data will need to be migrated to the new schema

## Running the Service
To run the service:
```bash
docker-compose up
```

This will start the user-service, database, and RabbitMQ in separate containers.

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