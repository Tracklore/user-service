from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.learning_goal import LearningGoal
from app.schemas.learning_goal import LearningGoalCreate, LearningGoalUpdate

async def get_learning_goals_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    """Get learning goals for a user by user ID."""
    try:
        result = await db.execute(
            select(LearningGoal)
            .filter(LearningGoal.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    except Exception as e:
        raise Exception(f"Error fetching learning goals for user {user_id}: {str(e)}")

async def get_learning_goals_count_by_user(db: AsyncSession, user_id: int) -> int:
    """Get the total count of learning goals for a user."""
    try:
        result = await db.execute(
            select(func.count(LearningGoal.id))
            .filter(LearningGoal.user_id == user_id)
        )
        return await result.scalar_one()
    except Exception as e:
        raise Exception(f"Error counting learning goals for user {user_id}: {str(e)}")

async def create_user_learning_goal(db: AsyncSession, learning_goal: LearningGoalCreate, user_id: int):
    """Create a new learning goal for a user."""
    try:
        db_learning_goal = LearningGoal(**learning_goal.dict(), user_id=user_id)
        db.add(db_learning_goal)
        await db.commit()
        await db.refresh(db_learning_goal)
        return db_learning_goal
    except Exception as e:
        await db.rollback()
        raise Exception(f"Error creating learning goal for user {user_id}: {str(e)}")

async def get_learning_goal(db: AsyncSession, goal_id: int, user_id: int):
    """Get a specific learning goal for a user."""
    try:
        result = await db.execute(
            select(LearningGoal).filter(
                LearningGoal.id == goal_id, 
                LearningGoal.user_id == user_id
            )
        )
        return result.scalars().first()
    except Exception as e:
        raise Exception(f"Error fetching learning goal {goal_id} for user {user_id}: {str(e)}")

async def update_learning_goal(db: AsyncSession, goal_id: int, user_id: int, learning_goal: LearningGoalUpdate):
    """Update a learning goal for a user."""
    try:
        db_learning_goal = await get_learning_goal(db, goal_id, user_id)
        if db_learning_goal:
            update_data = learning_goal.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_learning_goal, key, value)
            await db.commit()
            await db.refresh(db_learning_goal)
        return db_learning_goal
    except Exception as e:
        await db.rollback()
        raise Exception(f"Error updating learning goal {goal_id} for user {user_id}: {str(e)}")

async def delete_learning_goal(db: AsyncSession, goal_id: int, user_id: int):
    """Delete a learning goal for a user."""
    try:
        db_learning_goal = await get_learning_goal(db, goal_id, user_id)
        if db_learning_goal:
            await db.delete(db_learning_goal)
            await db.commit()
        return db_learning_goal
    except Exception as e:
        await db.rollback()
        raise Exception(f"Error deleting learning goal {goal_id} for user {user_id}: {str(e)}")