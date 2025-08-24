from pydantic import BaseModel, Field
from datetime import datetime

class BadgeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    icon_url: str = Field(..., min_length=1, max_length=500)

class BadgeCreate(BadgeBase):
    pass

class Badge(BadgeBase):
    id: int
    date_achieved: datetime
    auth_user_id: int

    class Config:
        from_attributes = True