from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.database import Base

class LearningGoal(Base):
    __tablename__ = "learning_goals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    status = Column(String)
    streak_count = Column(Integer)
    # Reference to auth-service user ID
    auth_user_id = Column(Integer, ForeignKey("auth_users.id"))