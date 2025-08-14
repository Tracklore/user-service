from fastapi import FastAPI
from app.api import routes
from app.db.database import engine, Base

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Use this to drop tables for a clean start
        await conn.run_sync(Base.metadata.create_all)

app.include_router(routes.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the User Service"}
