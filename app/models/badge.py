from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.db.database import Base
from datetime import datetime

class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    icon_url = Column(String)
    date_achieved = Column(DateTime, default=datetime.utcnow)
    # Reference to user ID in auth_users table
    user_id = Column(Integer, ForeignKey("auth_users.id"))