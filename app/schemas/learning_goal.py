from pydantic import BaseModel
from typing import Optional

class LearningGoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str
    streak_count: int = 0

class LearningGoalCreate(LearningGoalBase):
    pass

class LearningGoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    streak_count: Optional[int] = None

class LearningGoal(LearningGoalBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
