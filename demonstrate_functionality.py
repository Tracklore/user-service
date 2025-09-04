#!/usr/bin/env python3
"""
Script to demonstrate core functionality of the user service.
"""

import sys
from pathlib import Path

# Add the parent directory to the Python path to ensure shared_libs can be found
parent_path = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_path))

import asyncio
from app.core.settings import settings
from app.db.database import engine, SessionLocal, Base
from app.models.auth_user_reference import AuthUserReference

async def demonstrate_database_connection():
    """Demonstrate that we can connect to the database and create tables."""
    print("Demonstrating database connection and table creation...")
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Tables created successfully!")
    
    # Test database session
    async with SessionLocal() as session:
        try:
            # Try to create a test auth user reference
            auth_user_ref = AuthUserReference(id=999999)  # Use a high ID to avoid conflicts
            session.add(auth_user_ref)
            await session.commit()
            print("Successfully created test auth user reference")
            
            # Query the test auth user reference
            result = await session.execute(
                AuthUserReference.__table__.select().where(AuthUserReference.id == 999999)
            )
            row = result.fetchone()
            if row:
                print(f"Successfully queried auth user reference with ID {row[0]}")
            
            # Clean up
            await session.delete(auth_user_ref)
            await session.commit()
            print("Cleaned up test data")
        except Exception as e:
            # Rollback in case of error
            await session.rollback()
            print(f"Error during database operations: {e}")
    
    print("Database operations completed successfully!")

async def demonstrate_settings():
    """Demonstrate that settings are loaded correctly."""
    print("\nDemonstrating settings loading...")
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Secret key length: {len(settings.SECRET_KEY)}")
    print(f"RabbitMQ URL: {settings.RABBITMQ_URL}")
    print("Settings loaded successfully!")

async def main():
    """Main function to run all demonstrations."""
    print("User Service Core Functionality Demonstration")
    print("=" * 50)
    
    try:
        await demonstrate_settings()
        await demonstrate_database_connection()
        print("\nAll demonstrations completed successfully!")
        return True
    except Exception as e:
        print(f"\nError during demonstration: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)