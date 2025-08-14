from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    bio = Column(String)
    skills = Column(String)

    badges = relationship("Badge", back_populates="owner")
    learning_goals = relationship("LearningGoal", back_populates="owner")
