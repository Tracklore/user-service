import asyncio
import sys
from pathlib import Path

# Add the parent directory to the Python path to ensure shared_libs can be found
parent_path = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_path))

from app.db.database import engine, SessionLocal, Base
from app.models.user import User
from app.crud.user import create_user
from app.schemas.user import UserCreate

async def test_user_creation():
    """Test creating a user"""
    print("Testing user creation...")
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Tables created successfully!")
    
    # Test database session
    async with SessionLocal() as session:
        # Create a test user
        user_create = UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            display_name="Test User",
            bio="This is a test user",
            avatar_url="http://example.com/avatar.jpg",
            location="Test City"
        )
        
        user = await create_user(session, user_create)
        print(f"Successfully created user with ID: {user.id}")
        
        # Query the test user
        from app.crud.user import get_user
        retrieved_user = await get_user(session, user.id)
        if retrieved_user:
            print(f"Successfully retrieved user: {retrieved_user.username}")
            print(f"User email: {retrieved_user.email}")
            print(f"User display name: {retrieved_user.display_name}")
        
        # Clean up
        from app.crud.user import delete_user
        await delete_user(session, user.id)
        print("Cleaned up test data")
    
    print("User creation test completed successfully!")

async def main():
    """Main function to run all tests."""
    print("User Service Schema Implementation Test")
    print("=" * 50)
    
    try:
        await test_user_creation()
        print("\nAll tests completed successfully!")
        return True
    except Exception as e:
        print(f"\nError during testing: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)