from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.badge import Badge
from app.schemas.learning_goal import LearningGoal

class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str = Field(..., max_length=50)
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=1000)
    avatar_url: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=100)

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    """Schema for creating a new user from message queue event."""
    id: int
    username: str = Field(..., max_length=50)

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """Schema for updating a user."""
    username: Optional[str] = Field(None, max_length=50)
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=1000)
    avatar_url: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=100)

    class Config:
        from_attributes = True

class User(UserBase):
    """Schema for user data returned by the API."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    """Schema for user profile response."""
    id: int
    username: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    badges: List[Badge] = []
    learning_goals: List[LearningGoal] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True