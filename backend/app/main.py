from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth.endpoints import router as auth_router
from app.api.users.endpoints import router as users_router
from app.core.security.csrf_middleware import CSRFMiddleware



app = FastAPI()


#app.add_middleware(CSRFMiddleware) 

app.add_middleware(CORSMiddleware)

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(users_router, tags=["Users"])

