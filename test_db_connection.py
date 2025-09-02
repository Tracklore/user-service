#!/usr/bin/env python3
"""
Simple test script to verify database connection changes.
"""

import asyncio
import sys
from app.db.database import engine, SessionLocal
from app.core.settings import settings

async def test_database_connection():
    """Test database connection with the new pooling settings."""
    print("Testing database connection...")
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Pool size: {settings.DATABASE_POOL_SIZE}")
    print(f"Max overflow: {settings.DATABASE_MAX_OVERFLOW}")
    
    try:
        # Test creating a session
        async with SessionLocal() as session:
            # Test executing a simple query
            result = await session.execute("SELECT 1")
            row = result.fetchone()
            print(f"Database connection test result: {row[0]}")
        
        print("Database connection test passed!")
        return True
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_database_connection())
    sys.exit(0 if result else 1)