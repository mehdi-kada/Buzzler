from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.auth.auth_endpoints import router as auth_router
from app.api.users.user_endpoints import router as users_router
from app.core.security.headers_middleware import SecurityHeadersMiddleware


app = FastAPI()

app.add_middleware(SecurityHeadersMiddleware)

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

