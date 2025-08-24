from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.badge import Badge
from app.schemas.badge import BadgeCreate
from app.services.auth_service import auth_service_client

async def get_badges_by_user(db: AsyncSession, auth_user_id: int, skip: int = 0, limit: int = 100):
    """Get badges for a user by auth-service user ID."""
    try:
        # Ensure the auth user reference exists
        await auth_service_client.ensure_auth_user_reference_exists(auth_user_id, db)
        
        result = await db.execute(
            select(Badge)
            .filter(Badge.auth_user_id == auth_user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    except Exception as e:
        raise Exception(f"Error fetching badges for user {auth_user_id}: {str(e)}")

async def get_badges_count_by_user(db: AsyncSession, auth_user_id: int) -> int:
    """Get the total count of badges for a user."""
    try:
        # Ensure the auth user reference exists
        await auth_service_client.ensure_auth_user_reference_exists(auth_user_id, db)
        
        result = await db.execute(
            select(func.count(Badge.id))
            .filter(Badge.auth_user_id == auth_user_id)
        )
        return result.scalar_one()
    except Exception as e:
        raise Exception(f"Error counting badges for user {auth_user_id}: {str(e)}")

async def create_user_badge(db: AsyncSession, badge: BadgeCreate, auth_user_id: int):
    """Create a new badge for a user."""
    try:
        # Ensure the auth user reference exists
        await auth_service_client.ensure_auth_user_reference_exists(auth_user_id, db)
        
        db_badge = Badge(**badge.model_dump(), auth_user_id=auth_user_id)
        db.add(db_badge)
        await db.commit()
        await db.refresh(db_badge)
        return db_badge
    except Exception as e:
        await db.rollback()
        raise Exception(f"Error creating badge for user {auth_user_id}: {str(e)}")