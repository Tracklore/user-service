from pydantic import BaseModel, Field
from typing import Optional, List
from shared_libs import UserBase as SharedUserBase
from app.schemas.badge import Badge
from app.schemas.learning_goal import LearningGoal

class UserCreate(SharedUserBase):
    """Schema for creating a new user."""
    bio: Optional[str] = Field(None, max_length=500)
    skills: Optional[str] = Field(None, max_length=500)

class UserUpdate(BaseModel):
    """Schema for updating a user."""
    bio: Optional[str] = Field(None, max_length=500)
    skills: Optional[str] = Field(None, max_length=500)

class User(SharedUserBase):
    """Schema for user data."""
    # Note: These relationships are not included in the Pydantic model for direct serialization
    # to avoid issues with async ORM loading. They are handled separately in the service layer.
    # badges: List[Badge] = []
    # learning_goals: List[LearningGoal] = []

    class Config:
        from_attributes = True  # Updated from orm_mode

class UserProfileResponse(BaseModel):
    """Schema for user profile response."""
    id: int
    username: str
    bio: Optional[str] = None
    skills: Optional[str] = None
    badges: List[Badge] = []
    learning_goals: List[LearningGoal] = []

    class Config:
        from_attributes = True  # Updated from orm_mode