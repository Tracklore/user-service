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

### Profile Management
The service no longer performs CRUD operations on user profile fields in a shared users table. Instead, it:
1. Fetches user authentication data from the auth-service
2. Manages additional profile data (badges, learning goals) in its own database
3. Links this data to auth-service users via foreign key references

### Gamification & Learning
The service uses separate database tables to store badges and learning goals. These tables have a foreign key relationship with the `auth_users` table to link the data to a specific user managed by the auth-service.

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

This will start the user-service, auth-service, and database in separate containers.