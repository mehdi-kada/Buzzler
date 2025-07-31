from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate
from sqlalchemy.future import select


app = FastAPI()

origins = ["http://localhost:3000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,
    allow_credentials= True,
    allow_methods= ["*"],
    allow_headers= ["*"] 
)

@app.get("/")
async def hello():
    return {
        "axcel": "you got this , push your limits "
    }

@app.get("/test-db")
async def test_db(db : AsyncSession = Depends(get_db)):
    return {
        "message" : "DataBase Seccessful"
    }




# Endpoint to add a user for testing
@app.post("/test-user/")
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    user_data = user_in.model_dump()
    user_data["auth_provider"] = user_data["auth_provider"].upper()
    user = User(**user_data)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

