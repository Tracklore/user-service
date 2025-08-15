import httpx
from typing import Optional, Dict, Any
from app.core.settings import settings

class AuthServiceClient:
    def __init__(self):
        self.base_url = getattr(settings, 'AUTH_SERVICE_URL', 'http://localhost:8001')
        self.client = httpx.AsyncClient()
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Fetch user data from auth-service by ID"""
        try:
            response = await self.client.get(f"{self.base_url}/users/{user_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Fetch user data from auth-service by email"""
        try:
            response = await self.client.get(f"{self.base_url}/users/email/{email}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    async def create_auth_user_reference(self, user_id: int, db):
        """Create a reference to an auth-service user in our database"""
        from app.models.auth_user_reference import AuthUserReference
        auth_user_ref = AuthUserReference(id=user_id)
        db.add(auth_user_ref)
        await db.commit()
        await db.refresh(auth_user_ref)
        return auth_user_ref
    
    async def ensure_auth_user_reference_exists(self, user_id: int, db):
        """Ensure a reference to an auth-service user exists in our database"""
        from app.models.auth_user_reference import AuthUserReference
        from sqlalchemy import select
        
        # Use select() correctly without await on the execute result
        stmt = select(AuthUserReference).where(AuthUserReference.id == user_id)
        result = await db.execute(stmt)
        auth_user_ref = result.scalar_one_or_none()
        
        if not auth_user_ref:
            return await self.create_auth_user_reference(user_id, db)
        return auth_user_ref

# Global instance
auth_service_client = AuthServiceClient()