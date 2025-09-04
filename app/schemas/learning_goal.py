from pydantic import BaseModel, Field
from typing import Optional

class LearningGoalBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: str = Field(..., min_length=1, max_length=50)
    streak_count: int = Field(0, ge=0)

class LearningGoalCreate(LearningGoalBase):
    pass

class LearningGoalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None, min_length=1, max_length=50)
    streak_count: Optional[int] = Field(None, ge=0)

class LearningGoal(LearningGoalBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
