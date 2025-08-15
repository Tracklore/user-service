from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.learning_goal import LearningGoal
from app.schemas.learning_goal import LearningGoalCreate, LearningGoalUpdate
from app.services.auth_service import auth_service_client

async def get_learning_goals_by_user(db: AsyncSession, auth_user_id: int, skip: int = 0, limit: int = 100):
    """Get learning goals for a user by auth-service user ID."""
    # Ensure the auth user reference exists
    await auth_service_client.ensure_auth_user_reference_exists(auth_user_id, db)
    
    result = await db.execute(
        select(LearningGoal).filter(LearningGoal.auth_user_id == auth_user_id).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def create_user_learning_goal(db: AsyncSession, learning_goal: LearningGoalCreate, auth_user_id: int):
    """Create a new learning goal for a user."""
    # Ensure the auth user reference exists
    await auth_service_client.ensure_auth_user_reference_exists(auth_user_id, db)
    
    db_learning_goal = LearningGoal(**learning_goal.model_dump(), auth_user_id=auth_user_id)
    db.add(db_learning_goal)
    await db.commit()
    await db.refresh(db_learning_goal)
    return db_learning_goal

async def get_learning_goal(db: AsyncSession, goal_id: int, auth_user_id: int):
    """Get a specific learning goal for a user."""
    result = await db.execute(
        select(LearningGoal).filter(
            LearningGoal.id == goal_id, 
            LearningGoal.auth_user_id == auth_user_id
        )
    )
    return result.scalars().first()

async def update_learning_goal(db: AsyncSession, goal_id: int, auth_user_id: int, learning_goal: LearningGoalUpdate):
    """Update a learning goal for a user."""
    db_learning_goal = await get_learning_goal(db, goal_id, auth_user_id)
    if db_learning_goal:
        update_data = learning_goal.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_learning_goal, key, value)
        await db.commit()
        await db.refresh(db_learning_goal)
    return db_learning_goal

async def delete_learning_goal(db: AsyncSession, goal_id: int, auth_user_id: int):
    """Delete a learning goal for a user."""
    db_learning_goal = await get_learning_goal(db, goal_id, auth_user_id)
    if db_learning_goal:
        await db.delete(db_learning_goal)
        await db.commit()
    return db_learning_goal