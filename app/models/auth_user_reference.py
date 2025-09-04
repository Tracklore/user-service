from sqlalchemy import Column, Integer
from app.db.database import Base

class AuthUserReference(Base):
    __tablename__ = "auth_users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    def __repr__(self):
        return f"<AuthUserReference(id={self.id})>"