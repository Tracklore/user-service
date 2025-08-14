Overview
The user-service is a microservice responsible for managing all user-related data beyond core authentication. It provides functionality for user profiles, activity tracking, gamification (badges), and the learning tracker. It relies on the auth-service to identify the authenticated user via a JWT token.

API Endpoints
All endpoints are prefixed with /users.

EndpointMethodDescriptionAuthentication
/meGETRetrieves the authenticated user's profile.Required
/{user_id}GETRetrieves a specific user's public profile.None
/{user_id}PUTUpdates the authenticated user's profile.Required (for user_id matching auth_user_id)
/{user_id}/badgesGETRetrieves all badges earned by a user.None
/{user_id}/goalsGETRetrieves all learning goals for a user.None
/{user_id}/goalsPOSTCreates a new learning goal for the user.Required (for user_id matching auth_user_id)
/{user_id}/goals/{goal_id}PUTUpdates a specific learning goal.Required (for user_id matching auth_user_id)
/{user_id}/goals/{goal_id}DELETEDeletes a specific learning goal.Required (for user_id matching auth_user_id)

Export to Sheets
Data Models & Schemas
The service will use Pydantic schemas to validate data and format API responses.

UserUpdate: Defines the fields that can be updated on a user's profile, such as bio and skills. All fields are optional.

UserProfileResponse: Represents the public profile data returned by the API, including username, bio, skills, and links to activity stats and badges. It does not include sensitive information.

Badge: A schema for a badge object, including name, description, icon_url, and the date_achieved.

LearningGoal: A schema for a user's learning goal, containing a title, description, status (e.g., 'in-progress', 'completed'), and a streak_count.

Core Logic
Profile Management: The service will perform CRUD (Create, Read, Update, Delete) operations on the user profile fields in the shared users table. It will use the user_id from the decoded JWT to ensure that a user can only modify their own profile.

Gamification & Learning: The service will use separate, new database tables to store badges and learning goals. These tables will have a foreign key relationship with the users table to link the data to a specific user. This keeps the data organized and modular.