from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud, models
from app.services.user import UserService
from app.db.database import get_db
from app.schemas.user import UserProfileResponse, UserUpdate
from app.schemas.learning_goal import LearningGoalCreate, LearningGoalUpdate
from app.schemas.badge import Badge, BadgeCreate
from app.services.auth_service import auth_service_client

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "User not found"}},
)

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Dependency to get UserService instance."""
    return UserService(db)

@router.get("/{auth_user_id}", response_model=dict, summary="Get user profile", description="Retrieve a user's profile by their auth-service user ID, including badges and learning goals.")
async def read_user(auth_user_id: int, user_service: UserService = Depends(get_user_service)):
    """
    Get a user's profile by auth-service user ID.
    
    Args:
        auth_user_id (int): The ID of the user in the auth-service.
        
    Returns:
        dict: The user's profile data including badges and learning goals.
        
    Raises:
        HTTPException: If the user is not found (404).
    """
    return await user_service.get_user_profile(auth_user_id)

@router.get("/{auth_user_id}/badges", response_model=List[schemas.Badge], summary="Get user badges", description="Retrieve all badges earned by a specific user.")
async def read_user_badges(auth_user_id: int, user_service: UserService = Depends(get_user_service)):
    """
    Retrieve all badges earned by a user.
    
    Args:
        auth_user_id (int): The ID of the user in the auth-service.
        
    Returns:
        List[schemas.Badge]: A list of badges earned by the user.
    """
    return await user_service.get_user_badges(auth_user_id)

@router.post("/{auth_user_id}/badges", response_model=schemas.Badge, summary="Create user badge", description="Create a new badge for a user.", responses={403: {"description": "Not authorized to create a badge for this user"}})
async def create_badge(
    auth_user_id: int, 
    badge: schemas.BadgeCreate, 
    user_service: UserService = Depends(get_user_service)
):
    """
    Creates a new badge for a user.
    
    Args:
        auth_user_id (int): The ID of the user in the auth-service.
        badge (schemas.BadgeCreate): The badge data to create.
        user_service (UserService): The user service instance.
        
    Returns:
        schemas.Badge: The created badge.
        
    Raises:
        HTTPException: If there's an issue creating the badge.
    """
    return await user_service.create_badge(auth_user_id, badge)

@router.get("/{auth_user_id}/goals", response_model=List[schemas.LearningGoal], summary="Get user learning goals", description="Retrieve all learning goals for a specific user.")
async def read_user_learning_goals(auth_user_id: int, user_service: UserService = Depends(get_user_service)):
    """
    Retrieve all learning goals for a user.
    
    Args:
        auth_user_id (int): The ID of the user in the auth-service.
        
    Returns:
        List[schemas.LearningGoal]: A list of learning goals for the user.
    """
    return await user_service.get_user_learning_goals(auth_user_id)

@router.post("/{auth_user_id}/goals", response_model=schemas.LearningGoal, summary="Create learning goal", description="Create a new learning goal for a user.", responses={403: {"description": "Not authorized to create a learning goal for this user"}})
async def create_learning_goal(
    auth_user_id: int, 
    learning_goal: schemas.LearningGoalCreate, 
    user_service: UserService = Depends(get_user_service)
):
    """
    Create a new learning goal for a user.
    
    Args:
        auth_user_id (int): The ID of the user in the auth-service.
        learning_goal (schemas.LearningGoalCreate): The learning goal data to create.
        user_service (UserService): The user service instance.
        
    Returns:
        schemas.LearningGoal: The created learning goal.
        
    Raises:
        HTTPException: If there's an issue creating the learning goal.
    """
    return await user_service.create_learning_goal(auth_user_id, learning_goal)

@router.put("/{auth_user_id}/goals/{goal_id}", response_model=schemas.LearningGoal, summary="Update learning goal", description="Update a specific learning goal for a user.", responses={403: {"description": "Not authorized to update this learning goal"}, 404: {"description": "Learning goal not found"}})
async def update_learning_goal(
    auth_user_id: int, 
    goal_id: int, 
    learning_goal: schemas.LearningGoalUpdate, 
    user_service: UserService = Depends(get_user_service)
):
    """
    Update a learning goal for a user.
    
    Args:
        auth_user_id (int): The ID of the user in the auth-service.
        goal_id (int): The ID of the learning goal to update.
        learning_goal (schemas.LearningGoalUpdate): The learning goal data to update.
        user_service (UserService): The user service instance.
        
    Returns:
        schemas.LearningGoal: The updated learning goal.
        
    Raises:
        HTTPException: If the learning goal is not found (404).
    """
    return await user_service.update_learning_goal(auth_user_id, goal_id, learning_goal)

@router.delete("/{auth_user_id}/goals/{goal_id}", summary="Delete learning goal", description="Delete a specific learning goal for a user.", responses={403: {"description": "Not authorized to delete this learning goal"}, 404: {"description": "Learning goal not found"}})
async def delete_learning_goal(
    auth_user_id: int, 
    goal_id: int, 
    user_service: UserService = Depends(get_user_service)
):
    """
    Delete a learning goal for a user.
    
    Args:
        auth_user_id (int): The ID of the user in the auth-service.
        goal_id (int): The ID of the learning goal to delete.
        user_service (UserService): The user service instance.
        
    Returns:
        dict: A confirmation that the learning goal was deleted.
        
    Raises:
        HTTPException: If the learning goal is not found (404).
    """
    await user_service.delete_learning_goal(auth_user_id, goal_id)
    return {"ok": True}