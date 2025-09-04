#!/usr/bin/env python3
"""
Script to demonstrate proper database connection management.
This script shows how to properly manage database connections with context managers.
"""

import asyncio
import aiosqlite
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_connection(database_url="./test.db"):
    """
    Context manager for database connections.
    
    Args:
        database_url (str): The database URL
        
    Yields:
        aiosqlite.Connection: Database connection
    """
    conn = None
    try:
        # Create connection
        conn = await aiosqlite.connect(database_url)
        yield conn
    except Exception as e:
        # If we have a connection, rollback any pending transactions
        if conn:
            await conn.rollback()
        raise e
    finally:
        # Always close the connection
        if conn:
            await conn.close()

async def example_database_operations():
    """
    Example of proper database connection management.
    """
    print("Demonstrating proper database connection management...")
    
    # Using context manager to ensure connection is properly closed
    async with get_db_connection() as conn:
        # Enable foreign key constraints
        await conn.execute("PRAGMA foreign_keys = ON")
        
        # Create a test table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        
        # Insert test data
        await conn.execute(
            "INSERT INTO test_table (name) VALUES (?)",
            ("Test User",)
        )
        
        # Commit the transaction
        await conn.commit()
        
        # Query the data
        cursor = await conn.execute("SELECT * FROM test_table")
        rows = await cursor.fetchall()
        
        print(f"Found {len(rows)} rows in test_table:")
        for row in rows:
            print(f"  ID: {row[0]}, Name: {row[1]}")
        
        # Clean up test data
        await conn.execute("DELETE FROM test_table")
        await conn.commit()
    
    print("Database connection properly closed.")

if __name__ == "__main__":
    asyncio.run(example_database_operations())