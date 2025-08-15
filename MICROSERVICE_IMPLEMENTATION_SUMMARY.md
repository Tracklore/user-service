# Microservice Architecture Implementation - User Service

## Summary of Changes

### Database Schema Changes
1. Removed the `users` table from user-service database
2. Created an `auth_users` reference table to maintain foreign key relationships with auth-service
3. Updated `badges` and `learning_goals` tables to reference `auth_users.id` instead of `users.id`

### Code Changes
1. Removed the User model from user-service
2. Created an AuthUserReference model for maintaining referential integrity
3. Updated Badge and LearningGoal models to reference auth-service users
4. Created an AuthServiceClient for communicating with the auth-service
5. Updated all CRUD operations to work with the new architecture
6. Updated API routes to use auth-service user IDs
7. Created database migrations for the new schema

### Configuration Changes
1. Updated settings to include AUTH_SERVICE_URL
2. Updated environment files with new configuration
3. Updated requirements.txt with necessary dependencies
4. Created Dockerfile for containerization
5. Created docker-compose.yml for running services together

### Documentation Updates
1. Updated README.md to reflect the new microservice architecture
2. Documented the new API endpoints
3. Documented the core logic of the new architecture

## Key Features of the New Architecture

### Separation of Concerns
- Authentication data is managed entirely by the auth-service
- User profile data (badges, learning goals) is managed by the user-service
- Services communicate via HTTP requests when needed

### Data References
- The user-service maintains references to auth-service users via foreign keys
- Referential integrity is maintained through the `auth_users` reference table

### Service Communication
- The user-service communicates with the auth-service via HTTP requests to fetch user data when needed
- The AuthServiceClient handles all communication with the auth-service

## API Endpoints

All endpoints are prefixed with `/users`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check endpoint |
| `/users/me` | GET | Retrieves the authenticated user's profile |
| `/users/{auth_user_id}` | GET | Retrieves a specific user's public profile |
| `/users/{auth_user_id}/badges` | GET | Retrieves all badges earned by a user |
| `/users/{auth_user_id}/badges` | POST | Creates a new badge for the user |
| `/users/{auth_user_id}/goals` | GET | Retrieves all learning goals for a user |
| `/users/{auth_user_id}/goals` | POST | Creates a new learning goal for the user |
| `/users/{auth_user_id}/goals/{goal_id}` | PUT | Updates a specific learning goal |
| `/users/{auth_user_id}/goals/{goal_id}` | DELETE | Deletes a specific learning goal |

## Running the Service

To run the service:
```bash
docker-compose up
```

This will start the user-service, auth-service, and database in separate containers.

## Testing

A simple health check test is included to verify the service is running correctly.