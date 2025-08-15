from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud, models
from app.services.user import UserService, get_current_user_from_token
from app.db.database import get_db
from app.schemas.user import UserProfileResponse, UserUpdate
from app.schemas.learning_goal import LearningGoalCreate, LearningGoalUpdate
from app.schemas.badge import Badge, BadgeCreate
from app.services.auth_service import auth_service_client

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("/me", response_model=dict)
async def read_users_me(current_user: dict = Depends(get_current_user_from_token)):
    """Get the current user's profile from auth-service."""
    # Current user is already provided by the auth service
    return current_user

@router.get("/{auth_user_id}", response_model=dict)
async def read_user(auth_user_id: int, db: AsyncSession = Depends(get_db)):
    """Get a user's profile by auth-service user ID."""
    # Fetch user data from auth-service
    user_data = await auth_service_client.get_user(auth_user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's badges and learning goals from our service
    badges = await crud.badge.get_badges_by_user(db, auth_user_id)
    learning_goals = await crud.learning_goal.get_learning_goals_by_user(db, auth_user_id)
    
    # Combine the data
    user_profile = {
        "id": user_data["id"],
        "username": user_data["username"],
        "email": user_data.get("email"),
        "badges": badges,
        "learning_goals": learning_goals
    }
    
    return user_profile

@router.get("/{auth_user_id}/badges", response_model=List[schemas.Badge])
async def read_user_badges(auth_user_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve all badges earned by a user."""
    # Ensure the auth user reference exists
    await auth_service_client.ensure_auth_user_reference_exists(auth_user_id, db)
    
    badges = await crud.badge.get_badges_by_user(db, auth_user_id)
    return badges

@router.post("/{auth_user_id}/badges", response_model=schemas.Badge)
async def create_badge(
    auth_user_id: int, 
    badge: schemas.BadgeCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(get_current_user_from_token)
):
    """Creates a new badge for the authenticated user."""
    if current_user["id"] != auth_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create a badge for this user")
    
    # Ensure the auth user reference exists
    await auth_service_client.ensure_auth_user_reference_exists(auth_user_id, db)
    
    return await crud.badge.create_user_badge(db, badge, auth_user_id)

@router.get("/{auth_user_id}/goals", response_model=List[schemas.LearningGoal])
async def read_user_learning_goals(auth_user_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve all learning goals for a user."""
    # Ensure the auth user reference exists
    await auth_service_client.ensure_auth_user_reference_exists(auth_user_id, db)
    
    goals = await crud.learning_goal.get_learning_goals_by_user(db, auth_user_id)
    return goals

@router.post("/{auth_user_id}/goals", response_model=schemas.LearningGoal)
async def create_learning_goal(
    auth_user_id: int, 
    learning_goal: schemas.LearningGoalCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(get_current_user_from_token)
):
    """Create a new learning goal for the authenticated user."""
    if current_user["id"] != auth_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create a learning goal for this user")
    
    # Ensure the auth user reference exists
    await auth_service_client.ensure_auth_user_reference_exists(auth_user_id, db)
    
    return await crud.learning_goal.create_user_learning_goal(db, learning_goal, auth_user_id)

@router.put("/{auth_user_id}/goals/{goal_id}", response_model=schemas.LearningGoal)
async def update_learning_goal(
    auth_user_id: int, 
    goal_id: int, 
    learning_goal: schemas.LearningGoalUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(get_current_user_from_token)
):
    """Update a learning goal for the authenticated user."""
    if current_user["id"] != auth_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this learning goal")
    
    # Ensure the auth user reference exists
    await auth_service_client.ensure_auth_user_reference_exists(auth_user_id, db)
    
    updated_goal = await crud.learning_goal.update_learning_goal(db, goal_id, auth_user_id, learning_goal)
    if not updated_goal:
        raise HTTPException(status_code=404, detail="Learning goal not found")
    
    return updated_goal

@router.delete("/{auth_user_id}/goals/{goal_id}")
async def delete_learning_goal(
    auth_user_id: int, 
    goal_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(get_current_user_from_token)
):
    """Delete a learning goal for the authenticated user."""
    if current_user["id"] != auth_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this learning goal")
    
    # Ensure the auth user reference exists
    await auth_service_client.ensure_auth_user_reference_exists(auth_user_id, db)
    
    deleted_goal = await crud.learning_goal.delete_learning_goal(db, goal_id, auth_user_id)
    if not deleted_goal:
        raise HTTPException(status_code=404, detail="Learning goal not found")
    
    return {"ok": True}