from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas
from app.db.database import get_db
from app.services.auth_service import auth_service_client
from typing import List

# This is a placeholder for the actual dependency that will get the current user from the JWT token
async def get_current_user_from_token() -> dict:
    # In a real application, this would decode the JWT token and return the user
    # For now, we'll return a dummy user
    return {"id": 1, "username": "testuser", "email": "test@example.com"}

class UserService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def get_user_profile(self, auth_user_id: int) -> dict:
        """Get a user's profile by auth-service user ID."""
        # Fetch user data from auth-service
        user_data = await auth_service_client.get_user(auth_user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user's badges and learning goals from our service
        badges = await crud.badge.get_badges_by_user(self.db, auth_user_id)
        learning_goals = await crud.learning_goal.get_learning_goals_by_user(self.db, auth_user_id)
        
        # Combine the data
        user_profile = {
            "id": user_data["id"],
            "username": user_data["username"],
            "email": user_data.get("email"),
            "badges": badges,
            "learning_goals": learning_goals
        }
        
        return user_profile

    async def get_my_profile(self, current_user: dict = Depends(get_current_user_from_token)) -> dict:
        """Get the current user's profile."""
        return current_user

    async def get_user_badges(self, auth_user_id: int) -> List[schemas.Badge]:
        """Get badges for a user by auth-service user ID."""
        # Ensure the auth user reference exists
        await auth_service_client.ensure_auth_user_reference_exists(auth_user_id, self.db)
        
        return await crud.badge.get_badges_by_user(self.db, auth_user_id=auth_user_id)

    async def create_badge(self, auth_user_id: int, badge: schemas.BadgeCreate, current_user: dict = Depends(get_current_user_from_token)) -> schemas.Badge:
        """Create a badge for a user."""
        if current_user["id"] != auth_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to create a badge for this user")
        
        # Ensure the auth user reference exists
        await auth_service_client.ensure_auth_user_reference_exists(auth_user_id, self.db)
        
        return await crud.badge.create_user_badge(self.db, badge=badge, auth_user_id=auth_user_id)

    async def get_user_learning_goals(self, auth_user_id: int):
        """Get learning goals for a user by auth-service user ID."""
        # Ensure the auth user reference exists
        await auth_service_client.ensure_auth_user_reference_exists(auth_user_id, self.db)
        
        return await crud.learning_goal.get_learning_goals_by_user(self.db, auth_user_id=auth_user_id)

    async def create_learning_goal(self, auth_user_id: int, learning_goal: schemas.LearningGoalCreate, current_user: dict = Depends(get_current_user_from_token)):
        """Create a learning goal for a user."""
        if current_user["id"] != auth_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to create a learning goal for this user")
        
        # Ensure the auth user reference exists
        await auth_service_client.ensure_auth_user_reference_exists(auth_user_id, self.db)
        
        return await crud.learning_goal.create_user_learning_goal(self.db, learning_goal=learning_goal, auth_user_id=auth_user_id)

    async def update_learning_goal(self, auth_user_id: int, goal_id: int, learning_goal: schemas.LearningGoalUpdate, current_user: dict = Depends(get_current_user_from_token)):
        """Update a learning goal for a user."""
        if current_user["id"] != auth_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this learning goal")
        
        # Ensure the auth user reference exists
        await auth_service_client.ensure_auth_user_reference_exists(auth_user_id, self.db)
        
        db_learning_goal = await crud.learning_goal.update_learning_goal(self.db, goal_id=goal_id, auth_user_id=auth_user_id, learning_goal=learning_goal)
        if db_learning_goal is None:
            raise HTTPException(status_code=404, detail="Learning goal not found")
        return db_learning_goal

    async def delete_learning_goal(self, auth_user_id: int, goal_id: int, current_user: dict = Depends(get_current_user_from_token)):
        """Delete a learning goal for a user."""
        if current_user["id"] != auth_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this learning goal")
        
        # Ensure the auth user reference exists
        await auth_service_client.ensure_auth_user_reference_exists(auth_user_id, self.db)
        
        db_learning_goal = await crud.learning_goal.delete_learning_goal(self.db, goal_id=goal_id, auth_user_id=auth_user_id)
        if db_learning_goal is None:
            raise HTTPException(status_code=404, detail="Learning goal not found")
        return db_learning_goal