from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.badge import Badge
from app.schemas.badge import BadgeCreate
from app.services.auth_service import auth_service_client

async def get_badges_by_user(db: AsyncSession, auth_user_id: int, skip: int = 0, limit: int = 100):
    """Get badges for a user by auth-service user ID."""
    # Ensure the auth user reference exists
    await auth_service_client.ensure_auth_user_reference_exists(auth_user_id, db)
    
    result = await db.execute(
        select(Badge).filter(Badge.auth_user_id == auth_user_id).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def create_user_badge(db: AsyncSession, badge: BadgeCreate, auth_user_id: int):
    """Create a new badge for a user."""
    # Ensure the auth user reference exists
    await auth_service_client.ensure_auth_user_reference_exists(auth_user_id, db)
    
    db_badge = Badge(**badge.model_dump(), auth_user_id=auth_user_id)
    db.add(db_badge)
    await db.commit()
    await db.refresh(db_badge)
    return db_badge