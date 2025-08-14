from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud
from app.services.user import UserService, get_current_user
from app.models.user import User
from app.db.database import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/", response_model=schemas.UserProfileResponse)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.user.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    # Create the user
    created_user = await crud.user.create_user(db=db, user=user)
    # Fetch the user again with relationships loaded
    full_user = await crud.user.get_user(db, created_user.id)
    return full_user

@router.get("/me", response_model=schemas.User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=schemas.UserProfileResponse)
async def read_user(user_id: int, user_service: UserService = Depends(UserService)):
    user_profile = await user_service.get_user_profile(user_id)
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")
    return user_profile

@router.put("/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, user: schemas.UserUpdate, user_service: UserService = Depends(UserService), current_user: User = Depends(get_current_user)):
    return await user_service.update_user_profile(user_id, user, current_user)

@router.get("/{user_id}/badges", response_model=List[schemas.Badge])
async def read_user_badges(user_id: int, user_service: UserService = Depends(UserService)):
    return await user_service.get_user_badges(user_id)

@router.get("/{user_id}/goals", response_model=List[schemas.LearningGoal])
async def read_user_learning_goals(user_id: int, user_service: UserService = Depends(UserService)):
    return await user_service.get_user_learning_goals(user_id)

@router.post("/{user_id}/goals", response_model=schemas.LearningGoal)
async def create_learning_goal(user_id: int, learning_goal: schemas.LearningGoalCreate, user_service: UserService = Depends(UserService), current_user: User = Depends(get_current_user)):
    return await user_service.create_learning_goal(user_id, learning_goal, current_user)

@router.put("/{user_id}/goals/{goal_id}", response_model=schemas.LearningGoal)
async def update_learning_goal(user_id: int, goal_id: int, learning_goal: schemas.LearningGoalUpdate, user_service: UserService = Depends(UserService), current_user: User = Depends(get_current_user)):
    return await user_service.update_learning_goal(user_id, goal_id, learning_goal, current_user)

@router.delete("/{user_id}/goals/{goal_id}")
async def delete_learning_goal(user_id: int, goal_id: int, user_service: UserService = Depends(UserService), current_user: User = Depends(get_current_user)):
    await user_service.delete_learning_goal(user_id, goal_id, current_user)
    return {"ok": True}
