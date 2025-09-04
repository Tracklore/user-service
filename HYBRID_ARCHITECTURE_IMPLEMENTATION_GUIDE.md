# Hybrid Microservice Architecture Implementation Guide

## Project Context
**Date**: Tuesday, September 2, 2025

**Working Directory**: `C:\Users\bhumi\Documents\Tracklore`

**Project Structure**:
```
Tracklore/
├── auth-service/     (Existing, working, tested authentication service)
├── user-service/     (Current service modified to handle authentication directly)
├── shared_libs/      (Shared libraries between services)
└── frontend/         (Frontend application)
```

## Background & Decision

### Current Situation
The user-service was recently modified to handle authentication directly, including:
- Complete User model with authentication fields (password_hash, etc.)
- Direct JWT token management
- Authentication endpoints (login/signup/logout)
- Message queue consumer creating User records directly

### Why Revert to Hybrid Approach
1. **Proven Reliability**: The existing auth-service is already built, tested, and working end-to-end
2. **Risk Management**: Avoid reimplementing and retesting authentication functionality
3. **Development Efficiency**: Leverage existing, proven code rather than rebuilding
4. **Team Knowledge**: Development team already familiar with current architecture

## Target Architecture

### Service Responsibilities
**Auth Service**:
- User authentication (login/signup/logout)
- Token management and validation
- Password reset flows
- User session management

**User Service**:
- Enhanced user profile data (display_name, bio, avatar_url, location)
- Badges and learning goals
- User-specific application data
- Referential integrity with auth-service users

### Communication Pattern
```
Client → Auth Service (authentication) 
Client → User Service (profile/badges/goals) 
User Service → Auth Service (verify token/user exists)
Message Queue: Auth Service → User Service (UserCreated events)
```

## Implementation Tasks

### 1. Revert User Model
- Remove authentication fields from User model
- Keep enhanced profile fields:
  - `display_name`: VARCHAR(100)
  - `bio`: TEXT
  - `avatar_url`: TEXT
  - `location`: VARCHAR(100)
- Restore integer ID (matching auth-service user ID)

### 2. Restore Microservice Components
- Reinstate `AuthUserReference` model for referential integrity
- Restore `auth_service_client` for HTTP communication
- Update message queue consumer to create `AuthUserReference` records
- Remove direct authentication logic from user service

### 3. API Endpoint Updates
- Remove authentication endpoints from user service
- Restore endpoints that fetch user data from auth-service when needed
- Maintain badge and learning goal functionality
- Ensure proper JWT token validation through auth-service

### 4. Database Changes
- Revert database migrations to original microservice schema
- Maintain enhanced user profile fields
- Restore foreign key relationships to `auth_users` table

### 5. Service Communication
- Restore HTTP client for auth-service communication
- Maintain message queue integration for `UserCreated` events
- Implement proper error handling for service-to-service calls

## Benefits of Hybrid Approach

### Advantages
1. **Leverage Existing Work**: Keep tested auth-service unchanged
2. **Clear Separation of Concerns**: Auth vs. user data management
3. **Independent Scaling**: Services can scale based on their specific loads
4. **Technology Optimization**: Each service can use optimal technologies
5. **Reduced Development Risk**: Minimal changes to proven systems

### Maintained Features
- Enhanced user profile fields (bio, avatar, location, etc.)
- Complete badge and learning goal functionality
- Proper referential integrity between services
- Event-driven user creation via message queue
- JWT token validation

## Success Criteria
1. User service communicates with auth service for authentication verification
2. User service maintains enhanced profile data
3. Message queue integration works for user creation events
4. All existing badge and learning goal functionality intact
5. Database schema supports referential integrity
6. API endpoints function correctly with service-to-service communication

## Next Steps
1. Begin implementation from current user-service state
2. Revert authentication-related changes
3. Restore microservice communication patterns
4. Test service-to-service communication
5. Verify all functionality works with hybrid approach
6. Update documentation to reflect architecture