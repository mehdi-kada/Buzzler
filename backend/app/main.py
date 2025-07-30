from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db


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