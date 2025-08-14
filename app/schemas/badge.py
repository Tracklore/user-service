from pydantic import BaseModel
from datetime import datetime

class BadgeBase(BaseModel):
    name: str
    description: str
    icon_url: str

class BadgeCreate(BadgeBase):
    pass

class Badge(BadgeBase):
    id: int
    date_achieved: datetime
    owner_id: int

    class Config:
        orm_mode = True
