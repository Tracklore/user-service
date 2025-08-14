from pydantic import BaseModel
from typing import Optional, List
from app.schemas.badge import Badge
from app.schemas.learning_goal import LearningGoal

class UserBase(BaseModel):
    username: str
    bio: Optional[str] = None
    skills: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    bio: Optional[str] = None
    skills: Optional[str] = None

class User(UserBase):
    id: int
    # Note: These relationships are not included in the Pydantic model for direct serialization
    # to avoid issues with async ORM loading. They are handled separately in the service layer.
    # badges: List[Badge] = []
    # learning_goals: List[LearningGoal] = []

    class Config:
        from_attributes = True  # Updated from orm_mode

class UserProfileResponse(BaseModel):
    id: int
    username: str
    bio: Optional[str] = None
    skills: Optional[str] = None
    badges: List[Badge] = []
    learning_goals: List[LearningGoal] = []

    class Config:
        from_attributes = True  # Updated from orm_mode
