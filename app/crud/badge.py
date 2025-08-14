from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.badge import Badge
from app.schemas.badge import BadgeCreate

async def get_badges_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Badge).filter(Badge.owner_id == user_id).offset(skip).limit(limit))
    return result.scalars().all()

async def create_user_badge(db: AsyncSession, badge: BadgeCreate, user_id: int):
    db_badge = Badge(**badge.dict(), owner_id=user_id)
    db.add(db_badge)
    await db.commit()
    await db.refresh(db_badge)
    return db_badge
