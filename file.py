# from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from datetime import datetime, timedelta
# from .schemas import UserCreate, UserResponse, TokenResponse, PasswordReset
# from ...models.user import User, AuthProvider
# from ...core.auth import (
#     hash_password,
#     verify_password,
#     hash_token,
#     verify_token_hash,
#     create_access_token,
#     create_refresh_token,
#     verify_token,
#     generate_verification_token,
#     set_refresh_token_cookie,
#     clear_refresh_token_cookie,
# )
# from ...core.config import settings
# from ...core.database import get_db
# import aiosmtplib
# from email.message import EmailMessage
# from httpx import AsyncClient

# router = APIRouter(prefix="/auth", tags=["auth"])
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
#     """Dependency to get the current user from an access token."""
#     payload = verify_token(token)
#     if payload.get("type") != "access":
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
#     email = payload.get("sub")
#     if not email:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
#     result = await db.execute(select(User).where(User.email == email))
#     user = result.scalars().first()
#     if not user or not user.is_active:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or inactive user")
#     return user

# @router.post("/register", response_model=UserResponse)
# async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db), response: Response = None):
#     """Register a new user with email and password."""
#     # Check if email exists
#     result = await db.execute(select(User).where(User.email == user_data.email))
#     if result.scalars().first():
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
#     # Create user
#     hashed_password = hash_password(user_data.password)
#     verification_token = generate_verification_token()
#     new_user = User(
#         email=user_data.email,
#         password_hashed=hashed_password,
#         first_name=user_data.first_name,
#         auth_provider=AuthProvider.EMAIL,
#         email_verification_token=verification_token,
#     )
#     db.add(new_user)
#     await db.commit()
#     await db.refresh(new_user)
    
#     # Send verification email
#     await send_verification_email(new_user.email, verification_token)
    
#     return new_user

# @router.post("/login", response_model=TokenResponse)
# async def login(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: AsyncSession = Depends(get_db),
#     response: Response = None,
# ):
#     """Login a user and return access token with refresh token in cookie."""
#     result = await db.execute(select(User).where(User.email == form_data.username))
#     user = result.scalars().first()
#     if not user or not verify_password(form_data.password, user.password_hashed):
#         if user:
#             user.failed_login_attempts += 1
#             await db.commit()
#             if user.failed_login_attempts >= 5:
#                 raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account locked")
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
#     if not user.is_verified:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")
    
#     # Reset failed login attempts
#     user.failed_login_attempts = 0
#     user.last_login_at = datetime.utcnow()
    
#     # Generate tokens
#     access_token = create_access_token(data={"sub": user.email})
#     refresh_token = create_refresh_token(data={"sub": user.email})
#     user.refresh_token = hash_token(refresh_token)  # Store hashed refresh token
#     await db.commit()
    
#     # Set refresh token cookie
#     set_refresh_token_cookie(response, refresh_token)
    
#     return {"access_token": access_token, "token_type": "bearer"}

# @router.post("/refresh", response_model=TokenResponse)
# async def refresh_token(request: Request, db: AsyncSession = Depends(get_db), response: Response = None):
#     """Refresh an access token using the refresh token from cookie."""
#     refresh_token = request.cookies.get("refresh_token")
#     if not refresh_token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token provided")
    
#     # Verify refresh token
#     payload = verify_token(refresh_token)
#     if payload.get("type") != "refresh":
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
#     email = payload.get("sub")
#     if not email:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
#     # Check user and refresh token
#     result = await db.execute(select(User).where(User.email == email))
#     user = result.scalars().first()
#     if not user or not verify_token_hash(refresh_token, user.refresh_token):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
#     # Generate new access token
#     access_token = create_access_token(data={"sub": user.email})
    
#     return {"access_token": access_token, "token_type": "bearer"}

# @router.post("/logout")
# async def logout(db: AsyncSession = Depends(get_db), response: Response = None, current_user: User = Depends(get_current_user)):
#     """Log out a user and clear refresh token."""
#     current_user.refresh_token = None
#     await db.commit()
#     clear_refresh_token_cookie(response)
#     return {"message": "Logged out successfully"}

# @router.post("/verify-email")
# async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
#     """Verify a user's email using the verification token."""
#     result = await db.execute(select(User).where(User.email_verification_token == token))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token")
#     user.is_verified = True
#     user.email_verification_token = None
#     await db.commit()
#     return {"message": "Email verified successfully"}

# @router.post("/password-reset-request")
# async def password_reset_request(email: str, db: AsyncSession = Depends(get_db)):
#     """Request a password reset and send a reset link."""
#     result = await db.execute(select(User).where(User.email == email))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
    
#     reset_token = generate_verification_token()
#     user.password_reset_token = reset_token
#     user.password_reset_expires_at = datetime.utcnow() + timedelta(hours=1)
#     await db.commit()
    
#     await send_password_reset_email(user.email, reset_token)
#     return {"message": "Password reset email sent"}

# @router.post("/password-reset")
# async def password_reset(data: PasswordReset, db: AsyncSession = Depends(get_db)):
#     """Reset a user's password using the reset token."""
#     result = await db.execute(select(User).where(User.password_reset_token == data.token))
#     user = result.scalars().first()
#     if not user or user.password_reset_expires_at < datetime.utcnow():
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")
    
#     user.password_hashed = hash_password(data.new_password)
#     user.password_reset_token = None
#     user.password_reset_expires_at = None
#     await db.commit()
#     return {"message": "Password reset successfully"}

# @router.get("/google/login")
# async def google_login():
#     """Redirect to Google OAuth login page."""
#     google_auth_url = (
#         f"https://accounts.google.com/o/oauth2/v2/auth?"
#         f"client_id={settings.GOOGLE_CLIENT_ID}&"
#         f"redirect_uri={settings.REDIRECT_URI}&"
#         f"response_type=code&scope=openid%20email%20profile"
#     )
#     return {"redirect_url": google_auth_url}

# @router.get("/x/login")
# async def x_login():
#     """Redirect to X OAuth login page."""
#     x_auth_url = (
#         f"https://api.twitter.com/2/oauth2/authorize?"
#         f"client_id={settings.X_CLIENT_ID}&"
#         f"redirect_uri={settings.REDIRECT_URI}&"
#         f"response_type=code&scope=users.read%20tweet.read"
#     )
#     return {"redirect_url": x_auth_url}

# @router.post("/oauth/callback", response_model=TokenResponse)
# async def oauth_callback(
#     code: str,
#     provider: str,
#     db: AsyncSession = Depends(get_db),
#     response: Response = None,
# ):
#     """Handle OAuth callback and create/login user."""
#     async with AsyncClient() as client:
#         if provider == "google":
#             token_response = await client.post(
#                 "https://oauth2.googleapis.com/token",
#                 data={
#                     "code": code,
#                     "client_id": settings.GOOGLE_CLIENT_ID,
#                     "client_secret": settings.GOOGLE_CLIENT_SECRET,
#                     "redirect_uri": settings.REDIRECT_URI,
#                     "grant_type": "authorization_code",
#                 },
#             )
#             token_data = token_response.json()
#             if "error" in token_data:
#                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth error")
            
#             user_info = await client.get(
#                 "https://www.googleapis.com/oauth2/v2/userinfo",
#                 headers={"Authorization": f"Bearer {token_data['access_token']}"},
#             )
#             user_data = user_info.json()
#             email = user_data["email"]
#             oauth_id = user_data["id"]
#             first_name = user_data.get("given_name", "User")
#             auth_provider = AuthProvider.GOOGLE
        
#         elif provider == "x":
#             token_response = await client.post(
#                 "https://api.twitter.com/2/oauth2/token",
#                 data={
#                     "code": code,
#                     "client_id": settings.X_CLIENT_ID,
#                     "client_secret": settings.X_CLIENT_SECRET,
#                     "redirect_uri": settings.REDIRECT_URI,
#                     "grant_type": "authorization_code",
#                 },
#             )
#             token_data = token_response.json()
#             if "error" in token_data:
#                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth error")
            
#             user_info = await client.get(
#                 "https://api.twitter.com/2/users/me",
#                 headers={"Authorization": f"Bearer {token_data['access_token']}"},
#             )
#             user_data = user_info.json()
#             email = user_data["data"].get("email", f"{user_data['data']['id']}@x-placeholder.com")  # X may not provide email
#             oauth_id = user_data["data"]["id"]
#             first_name = user_data["data"].get("name", "User")
#             auth_provider = AuthProvider.X
#         else:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported provider")
    
#     # Check if user exists
#     result = await db.execute(select(User).where(User.oauth_id == oauth_id, User.auth_provider == auth_provider))
#     user = result.scalars().first()
#     if not user:
#         # Check for email conflict
#         result = await db.execute(select(User).where(User.email == email))
#         if result.scalars().first():
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered with another provider")
        
#         # Create new user
#         user = User(
#             email=email,
#             oauth_id=oauth_id,
#             auth_provider=auth_provider,
#             first_name=first_name,
#             is_verified=True,  # OAuth users are auto-verified
#         )
#         db.add(user)
#         await db.commit()
#         await db.refresh(user)
    
#     # Generate tokens
#     access_token = create_access_token(data={"sub": user.email})
#     refresh_token = create_refresh_token(data={"sub": user.email})
#     user.refresh_token = hash_token(refresh_token)
#     await db.commit()
    
#     # Set refresh token cookie
#     set_refresh_token_cookie(response, refresh_token)
    
#     return {"access_token": access_token, "token_type": "bearer"}

# async def send_verification_email(email: str, token: str):
#     """Send an email verification link."""
#     message = EmailMessage()
#     message["From"] = settings.SENDER_EMAIL
#     message["To"] = email
#     message["Subject"] = "Verify Your SocialFlow Account"
#     verification_url = f"http://localhost:3000/auth/verify?token={token}"
#     message.set_content(f"Please verify your email by clicking this link: {verification_url}")
    
#     await aiosmtplib.send(
#         message,
#         hostname=settings.SMTP_HOST,
#         port=settings.SMTP_PORT,
#         username=settings.SMTP_USERNAME,
#         password=settings.SMTP_PASSWORD,
#         use_tls=True,
#     )

# async def send_password_reset_email(email: str, token: str):
#     """Send a password reset link."""
#     message = EmailMessage()
#     message["From"] = settings.SENDER_EMAIL
#     message["To"] = email
#     message["Subject"] = "Reset Your SocialFlow Password"
#     reset_url = f"http://localhost:3000/auth/reset-password?token={token}"
#     message.set_content(f"Reset your password by clicking this link: {reset_url}")
    
#     await aiosmtplib.send(
#         message,
#         hostname=settings.SMTP_HOST,
#         port=settings.SMTP_PORT,
#         username=settings.SMTP_USERNAME,
#         password=settings.SMTP_PASSWORD,
#         use_tls=True,
#     )