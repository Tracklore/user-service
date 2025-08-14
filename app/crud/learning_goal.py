from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.learning_goal import LearningGoal
from app.schemas.learning_goal import LearningGoalCreate, LearningGoalUpdate

async def get_learning_goals_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(select(LearningGoal).filter(LearningGoal.owner_id == user_id).offset(skip).limit(limit))
    return result.scalars().all()

async def create_user_learning_goal(db: AsyncSession, learning_goal: LearningGoalCreate, user_id: int):
    db_learning_goal = LearningGoal(**learning_goal.dict(), owner_id=user_id)
    db.add(db_learning_goal)
    await db.commit()
    await db.refresh(db_learning_goal)
    return db_learning_goal

async def get_learning_goal(db: AsyncSession, goal_id: int, user_id: int):
    result = await db.execute(select(LearningGoal).filter(LearningGoal.id == goal_id, LearningGoal.owner_id == user_id))
    return result.scalars().first()

async def update_learning_goal(db: AsyncSession, goal_id: int, user_id: int, learning_goal: LearningGoalUpdate):
    db_learning_goal = await get_learning_goal(db, goal_id, user_id)
    if db_learning_goal:
        update_data = learning_goal.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_learning_goal, key, value)
        await db.commit()
        await db.refresh(db_learning_goal)
    return db_learning_goal

async def delete_learning_goal(db: AsyncSession, goal_id: int, user_id: int):
    db_learning_goal = await get_learning_goal(db, goal_id, user_id)
    if db_learning_goal:
        await db.delete(db_learning_goal)
        await db.commit()
    return db_learning_goal
