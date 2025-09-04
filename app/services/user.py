from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas
from app.db.database import get_db
from typing import List
from app.services.auth_service import auth_service_client
from app.core.settings import settings

class UserService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def get_user_profile(self, auth_user_id: int) -> dict:
        """Get a user's profile by auth-service user ID."""
        # Fetch user data from auth-service
        user_data = await auth_service_client.get_user(auth_user_id)
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Get user's badges and learning goals from our service
        badges = await self.get_user_badges(auth_user_id)
        learning_goals = await self.get_user_learning_goals(auth_user_id)
        
        # Calculate user statistics
        total_badges = len(badges)
        total_goals = len(learning_goals)
        
        # Determine user level based on badges
        user_level = min(total_badges // 5 + 1, 10)  # Level 1-10 based on badges
        
        # Combine the data
        user_profile = {
            "id": user_data["id"],
            "username": user_data["username"],
            "email": user_data.get("email"),
            "badges": badges,
            "learning_goals": learning_goals,
            "statistics": {
                "total_badges": total_badges,
                "total_goals": total_goals,
                "level": user_level
            }
        }
        
        return user_profile

    async def get_user_badges(self, auth_user_id: int) -> List[schemas.Badge]:
        """Get badges for a user by auth-service user ID."""
        # Validate user exists in auth service
        user_data = await auth_service_client.get_user(auth_user_id)
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Get badges from database
        badges = await crud.badge.get_badges_by_user(self.db, auth_user_id=auth_user_id)
        
        # Sort badges by achievement date (newest first)
        badges.sort(key=lambda x: x.date_achieved, reverse=True)
        
        return badges

    async def create_badge(self, auth_user_id: int, badge: schemas.BadgeCreate) -> schemas.Badge:
        """Create a badge for a user."""
        # Validate user exists in auth service
        user_data = await auth_service_client.get_user(auth_user_id)
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Validate badge data
        if not badge.name or len(badge.name.strip()) == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Badge name is required")
        
        # Limit the number of badges a user can have
        existing_badges = await self.get_user_badges(auth_user_id)
        if len(existing_badges) >= 100:  # Limit to 100 badges per user
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum number of badges (100) reached")
        
        # Create the badge
        created_badge = await crud.badge.create_user_badge(self.db, badge=badge, auth_user_id=auth_user_id)
        
        return created_badge

    async def get_user_learning_goals(self, auth_user_id: int):
        """Get learning goals for a user by auth-service user ID."""
        # Validate user exists in auth service
        user_data = await auth_service_client.get_user(auth_user_id)
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Get learning goals from database
        goals = await crud.learning_goal.get_learning_goals_by_user(self.db, auth_user_id=auth_user_id)
        
        # Sort goals by ID (newest first, assuming higher ID means newer)
        goals.sort(key=lambda x: x.id, reverse=True)
        
        return goals

    async def create_learning_goal(self, auth_user_id: int, learning_goal: schemas.LearningGoalCreate):
        """Create a learning goal for a user."""
        # Validate user exists in auth service
        user_data = await auth_service_client.get_user(auth_user_id)
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Validate learning goal data
        if not learning_goal.title or len(learning_goal.title.strip()) == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Learning goal title is required")
        
        # Limit the number of learning goals a user can have
        existing_goals = await self.get_user_learning_goals(auth_user_id)
        if len(existing_goals) >= 50:  # Limit to 50 learning goals per user
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum number of learning goals (50) reached")
        
        # Set default status if not provided
        if not learning_goal.status:
            learning_goal.status = "not_started"
        
        # Create the learning goal
        created_goal = await crud.learning_goal.create_user_learning_goal(self.db, learning_goal=learning_goal, auth_user_id=auth_user_id)
        
        return created_goal

    async def update_learning_goal(self, auth_user_id: int, goal_id: int, learning_goal: schemas.LearningGoalUpdate):
        """Update a learning goal for a user."""
        # Validate user exists in auth service
        user_data = await auth_service_client.get_user(auth_user_id)
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Validate that the learning goal exists and belongs to the user
        existing_goal = await self.get_learning_goal(auth_user_id, goal_id)
        if existing_goal is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning goal not found")
        
        # Validate status transitions
        if learning_goal.status and existing_goal.status:
            valid_transitions = {
                "not_started": ["in_progress", "completed", "archived"],
                "in_progress": ["paused", "completed", "archived"],
                "paused": ["in_progress", "completed", "archived"],
                "completed": ["archived"],
                "archived": []
            }
            if learning_goal.status not in valid_transitions.get(existing_goal.status, []):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status transition from {existing_goal.status} to {learning_goal.status}")
        
        # Update the learning goal
        updated_goal = await crud.learning_goal.update_learning_goal(self.db, goal_id=goal_id, auth_user_id=auth_user_id, learning_goal=learning_goal)
        if updated_goal is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning goal not found")
        
        return updated_goal

    async def get_learning_goal(self, auth_user_id: int, goal_id: int):
        """Get a specific learning goal for a user."""
        return await crud.learning_goal.get_learning_goal(self.db, goal_id=goal_id, auth_user_id=auth_user_id)

    async def delete_learning_goal(self, auth_user_id: int, goal_id: int):
        """Delete a learning goal for a user."""
        # Validate user exists in auth service
        user_data = await auth_service_client.get_user(auth_user_id)
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Validate that the learning goal exists and belongs to the user
        existing_goal = await self.get_learning_goal(auth_user_id, goal_id)
        if existing_goal is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning goal not found")
        
        # Prevent deletion of completed goals (archive instead)
        if existing_goal.status == "completed":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete completed learning goals. Please archive them instead.")
        
        # Delete the learning goal
        deleted_goal = await crud.learning_goal.delete_learning_goal(self.db, goal_id=goal_id, auth_user_id=auth_user_id)
        if deleted_goal is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning goal not found")
        
        return deleted_goal