#!/usr/bin/env python3
"""
Script to apply database migrations for the user-service.
"""

import asyncio
import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db.database import engine, Base
from app.models import *
from sqlalchemy import text

async def apply_migrations():
    """Apply the database migrations."""
    # Create all tables based on the current models
    async with engine.begin() as conn:
        # Drop existing tables
        await conn.run_sync(Base.metadata.drop_all)
        # Create new tables
        await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database migrations applied successfully!")

if __name__ == "__main__":
    asyncio.run(apply_migrations())