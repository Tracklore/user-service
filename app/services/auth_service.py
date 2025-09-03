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
            response.raise_for_status()  # This will raise an exception for 4xx and 5xx status codes
            return response.json()
        except Exception:
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Fetch user data from auth-service by email"""
        try:
            response = await self.client.get(f"{self.base_url}/users/email/{email}")
            response.raise_for_status()  # This will raise an exception for 4xx and 5xx status codes
            return response.json()
        except Exception:
            return None

# Global instance
auth_service_client = AuthServiceClient()