from fastapi import FastAPI
from app.api import routes
from app.db.database import engine, Base
from app.services.message_queue_consumer import message_queue_consumer

app = FastAPI(
    title="User Service API",
    description="API for managing user profiles, badges, and learning goals in the Tracklore application",
    version="1.0.0",
    contact={
        "name": "Tracklore Team",
        "url": "https://github.com/Tracklore/user-service",
    },
    license_info={
        "name": "MIT License",
        "url": "https://github.com/Tracklore/user-service/blob/main/LICENSE",
    }
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Use this to drop tables for a clean start
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize and start consuming messages from the queue
    await message_queue_consumer.connect()
    await message_queue_consumer.consume_user_events()

@app.on_event("shutdown")
async def shutdown():
    """Stop consuming messages and close the connection on shutdown."""
    await message_queue_consumer.stop_consuming()
    await message_queue_consumer.close()

app.include_router(routes.router)

@app.get("/", summary="Root endpoint", description="Welcome message for the User Service API")
async def root():
    """
    Returns a welcome message for the User Service API.
    
    Returns:
        dict: A dictionary containing a welcome message.
    """
    return {"message": "Welcome to the User Service"}