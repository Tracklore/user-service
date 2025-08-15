from sqlalchemy import Column, Integer, String
from app.db.database import Base

# This model represents a reference to a user in the auth-service
# It's used to maintain foreign key relationships while keeping services separate
class AuthUserReference(Base):
    __tablename__ = "auth_users"

    id = Column(Integer, primary_key=True, index=True)
    # We only store the ID to maintain referential integrity
    # All other user data is managed by the auth-service