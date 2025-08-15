from fastapi import FastAPI
from app.api import routes
from app.db.database import engine, Base
from app.services.message_queue_consumer import message_queue_consumer

app = FastAPI()

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

@app.get("/")
async def root():
    return {"message": "Welcome to the User Service"}