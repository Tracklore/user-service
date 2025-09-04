from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud, models
from app.services.user import UserService
from app.db.database import get_db
from app.schemas.user import UserProfileResponse, UserUpdate, UserCreate
from app.schemas.learning_goal import LearningGoalCreate, LearningGoalUpdate
from app.schemas.badge import Badge, BadgeCreate

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "User not found"}},
)

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Dependency to get UserService instance."""
    return UserService(db)

@router.get("/{user_id}", response_model=dict, summary="Get user profile", description="Retrieve a user's profile by their user ID, including badges and learning goals.")
async def read_user(user_id: int, user_service: UserService = Depends(get_user_service)):
    """
    Get a user's profile by user ID.
    
    Args:
        user_id (int): The ID of the user.
        
    Returns:
        dict: The user's profile data including badges and learning goals.
        
    Raises:
        HTTPException: If the user is not found (404).
    """
    return await user_service.get_user_profile(user_id)

@router.get("/{user_id}/badges", response_model=List[schemas.Badge], summary="Get user badges", description="Retrieve all badges earned by a specific user.")
async def read_user_badges(user_id: int, user_service: UserService = Depends(get_user_service)):
    """
    Retrieve all badges earned by a user.
    
    Args:
        user_id (int): The ID of the user.
        
    Returns:
        List[schemas.Badge]: A list of badges earned by the user.
    """
    return await user_service.get_user_badges(user_id)

@router.post("/{user_id}/badges", response_model=schemas.Badge, summary="Create user badge", description="Create a new badge for a user.")
async def create_badge(
    user_id: int, 
    badge: schemas.BadgeCreate, 
    user_service: UserService = Depends(get_user_service)
):
    """
    Creates a new badge for a user.
    
    Args:
        user_id (int): The ID of the user.
        badge (schemas.BadgeCreate): The badge data to create.
        user_service (UserService): The user service instance.
        
    Returns:
        schemas.Badge: The created badge.
        
    Raises:
        HTTPException: If the user is not found (404).
    """
    return await user_service.create_badge(user_id, badge)

@router.get("/{user_id}/goals", response_model=List[schemas.LearningGoal], summary="Get user learning goals", description="Retrieve all learning goals for a specific user.")
async def read_user_learning_goals(user_id: int, user_service: UserService = Depends(get_user_service)):
    """
    Retrieve all learning goals for a user.
    
    Args:
        user_id (int): The ID of the user.
        
    Returns:
        List[schemas.LearningGoal]: A list of learning goals for the user.
    """
    return await user_service.get_user_learning_goals(user_id)

@router.post("/{user_id}/goals", response_model=schemas.LearningGoal, summary="Create learning goal", description="Create a new learning goal for a user.")
async def create_learning_goal(
    user_id: int, 
    learning_goal: schemas.LearningGoalCreate, 
    user_service: UserService = Depends(get_user_service)
):
    """
    Create a new learning goal for a user.
    
    Args:
        user_id (int): The ID of the user.
        learning_goal (schemas.LearningGoalCreate): The learning goal data to create.
        user_service (UserService): The user service instance.
        
    Returns:
        schemas.LearningGoal: The created learning goal.
        
    Raises:
        HTTPException: If the user is not found (404).
    """
    return await user_service.create_learning_goal(user_id, learning_goal)

@router.put("/{user_id}/goals/{goal_id}", response_model=schemas.LearningGoal, summary="Update learning goal", description="Update a specific learning goal for a user.", responses={404: {"description": "Learning goal not found"}})
async def update_learning_goal(
    user_id: int, 
    goal_id: int, 
    learning_goal: schemas.LearningGoalUpdate, 
    user_service: UserService = Depends(get_user_service)
):
    """
    Update a learning goal for a user.
    
    Args:
        user_id (int): The ID of the user.
        goal_id (int): The ID of the learning goal to update.
        learning_goal (schemas.LearningGoalUpdate): The learning goal data to update.
        user_service (UserService): The user service instance.
        
    Returns:
        schemas.LearningGoal: The updated learning goal.
        
    Raises:
        HTTPException: If the learning goal is not found (404).
    """
    return await user_service.update_learning_goal(user_id, goal_id, learning_goal)

@router.delete("/{user_id}/goals/{goal_id}", summary="Delete learning goal", description="Delete a specific learning goal for a user.", responses={404: {"description": "Learning goal not found"}})
async def delete_learning_goal(
    user_id: int, 
    goal_id: int, 
    user_service: UserService = Depends(get_user_service)
):
    """
    Delete a learning goal for a user.
    
    Args:
        user_id (int): The ID of the user.
        goal_id (int): The ID of the learning goal to delete.
        user_service (UserService): The user service instance.
        
    Returns:
        dict: A confirmation that the learning goal was deleted.
        
    Raises:
        HTTPException: If the learning goal is not found (404).
    """
    await user_service.delete_learning_goal(user_id, goal_id)
    return {"ok": True}

@router.put("/{user_id}", response_model=schemas.User, summary="Update user", description="Update a user's profile.", responses={404: {"description": "User not found"}})
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    """
    Update a user's profile.
    
    Args:
        user_id (int): The ID of the user to update.
        user_update (UserUpdate): The user data to update.
        db (AsyncSession): The database session.
        user_service (UserService): The user service instance.
        
    Returns:
        schemas.User: The updated user.
        
    Raises:
        HTTPException: If the user is not found (404).
    """
    db_user = await crud.user.update_user(db, user_id, user_update)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.delete("/{user_id}", summary="Delete user", description="Delete a user.", responses={404: {"description": "User not found"}})
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a user.
    
    Args:
        user_id (int): The ID of the user to delete.
        db (AsyncSession): The database session.
        
    Returns:
        dict: A confirmation that the user was deleted.
        
    Raises:
        HTTPException: If the user is not found (404).
    """
    success = await crud.user.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"ok": True}