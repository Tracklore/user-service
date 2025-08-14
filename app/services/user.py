from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas
from app.db.database import get_db

# This is a placeholder for the actual dependency that will get the current user from the JWT token
async def get_current_user() -> models.User:
    # In a real application, this would decode the JWT token and return the user
    # For now, we'll return a dummy user
    return models.User(id=1, username="testuser")

class UserService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def get_user_profile(self, user_id: int) -> schemas.UserProfileResponse:
        db_user = await crud.user.get_user(self.db, user_id=user_id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user

    async def get_my_profile(self, current_user: models.User = Depends(get_current_user)) -> schemas.User:
        return current_user

    async def update_user_profile(self, user_id: int, user: schemas.UserUpdate, current_user: models.User = Depends(get_current_user)):
        if current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this profile")
        db_user = await crud.user.update_user(self.db, user_id=user_id, user=user)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user

    async def get_user_badges(self, user_id: int):
        return await crud.badge.get_badges_by_user(self.db, user_id=user_id)

    async def get_user_learning_goals(self, user_id: int):
        return await crud.learning_goal.get_learning_goals_by_user(self.db, user_id=user_id)

    async def create_learning_goal(self, user_id: int, learning_goal: schemas.LearningGoalCreate, current_user: models.User = Depends(get_current_user)):
        if current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to create a learning goal for this user")
        return await crud.learning_goal.create_user_learning_goal(self.db, learning_goal=learning_goal, user_id=user_id)

    async def update_learning_goal(self, user_id: int, goal_id: int, learning_goal: schemas.LearningGoalUpdate, current_user: models.User = Depends(get_current_user)):
        if current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this learning goal")
        db_learning_goal = await crud.learning_goal.update_learning_goal(self.db, goal_id=goal_id, user_id=user_id, learning_goal=learning_goal)
        if db_learning_goal is None:
            raise HTTPException(status_code=404, detail="Learning goal not found")
        return db_learning_goal

    async def delete_learning_goal(self, user_id: int, goal_id: int, current_user: models.User = Depends(get_current_user)):
        if current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this learning goal")
        db_learning_goal = await crud.learning_goal.delete_learning_goal(self.db, goal_id=goal_id, user_id=user_id)
        if db_learning_goal is None:
            raise HTTPException(status_code=404, detail="Learning goal not found")
        return db_learning_goal
