from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas
from app.db.database import get_db
from typing import List, Optional
from app.services.auth_service import auth_service_client
import httpx

class UserService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def get_auth_user(self, user_id: int) -> Optional[dict]:
        """Get user data from auth service"""
        try:
            return await auth_service_client.get_user(user_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to fetch user data from auth service"
            )

    async def get_user_profile(self, user_id: int) -> dict:
        """Get a user's profile by user ID."""
        # Fetch user data from our service
        user_data = await crud.user.get_user(self.db, user_id)
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Fetch user data from auth service
        auth_user_data = await self.get_auth_user(user_id)
        if not auth_user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found in auth service")
        
        # Get user's badges and learning goals from our service
        badges = await crud.badge.get_badges_by_user(self.db, user_id)
        learning_goals = await crud.learning_goal.get_learning_goals_by_user(self.db, user_id)
        
        # Combine the data
        user_profile = {
            "id": user_data.id,
            "username": auth_user_data["username"],
            "email": auth_user_data["email"],
            "display_name": user_data.display_name,
            "bio": user_data.bio,
            "avatar_url": user_data.avatar_url,
            "location": user_data.location,
            "badges": badges,
            "learning_goals": learning_goals,
            "created_at": user_data.created_at,
            "updated_at": user_data.updated_at
        }
        
        return user_profile

    async def get_user_badges(self, user_id: int) -> List[schemas.Badge]:
        """Get badges for a user by user ID."""
        # Verify user exists in auth service
        auth_user_data = await self.get_auth_user(user_id)
        if not auth_user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
        return await crud.badge.get_badges_by_user(self.db, user_id)

    async def create_badge(self, user_id: int, badge: schemas.BadgeCreate) -> schemas.Badge:
        """Create a badge for a user."""
        # Verify user exists in auth service
        auth_user_data = await self.get_auth_user(user_id)
        if not auth_user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
        return await crud.badge.create_user_badge(self.db, badge=badge, user_id=user_id)

    async def get_user_learning_goals(self, user_id: int):
        """Get learning goals for a user by user ID."""
        # Verify user exists in auth service
        auth_user_data = await self.get_auth_user(user_id)
        if not auth_user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
        return await crud.learning_goal.get_learning_goals_by_user(self.db, user_id)

    async def create_learning_goal(self, user_id: int, learning_goal: schemas.LearningGoalCreate):
        """Create a learning goal for a user."""
        # Verify user exists in auth service
        auth_user_data = await self.get_auth_user(user_id)
        if not auth_user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
        return await crud.learning_goal.create_user_learning_goal(self.db, learning_goal=learning_goal, user_id=user_id)

    async def update_learning_goal(self, user_id: int, goal_id: int, learning_goal: schemas.LearningGoalUpdate):
        """Update a learning goal for a user."""
        # Verify user exists in auth service
        auth_user_data = await self.get_auth_user(user_id)
        if not auth_user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
        db_learning_goal = await crud.learning_goal.update_learning_goal(self.db, goal_id=goal_id, user_id=user_id, learning_goal=learning_goal)
        if db_learning_goal is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning goal not found")
        return db_learning_goal

    async def delete_learning_goal(self, user_id: int, goal_id: int):
        """Delete a learning goal for a user."""
        # Verify user exists in auth service
        auth_user_data = await self.get_auth_user(user_id)
        if not auth_user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
        db_learning_goal = await crud.learning_goal.delete_learning_goal(self.db, goal_id=goal_id, user_id=user_id)
        if db_learning_goal is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning goal not found")
        return db_learning_goal