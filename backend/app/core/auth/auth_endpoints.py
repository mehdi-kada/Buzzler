# Depenedcry to get user (verify them )
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urlencode
from app.db.database import get_db
from app.models.user import AuthProviders, User
from app.core.auth.helpers_functions import clear_refresh_cookie, create_access_token, create_refresh_token, generate_verification_token, hash_password, hash_token, issue_tokens_and_set_cookie, send_password_verification_email, send_verification_email, set_refresh_token_cookie, verify_hash_token, verify_password, verify_token
from app.schemas.user import EmailSchema, PasswordReset, TokenResponse, UserBase, UserResponse
from app.core.config import Settings
from httpx import AsyncClient
from app.core.auth.providers import get_provider
from app.core.security.csrf import csrf_protection
from jose import jwt, JWTError

router = APIRouter()
oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """
        Dependency to get get the user 
    """
    payload = verify_token(token)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "Incorrect token type"
        )
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "Invalid Token"
        )
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or Inactive user"
        )
    return user 

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED )
async def register(user_data: UserBase ,response: Response, db: AsyncSession= Depends(get_db) ):
    """ register user and send verification email """
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalars().first():
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "Email already exists"
        )
    
    hashed_password = hash_password(user_data.password)
    verification_token = generate_verification_token(user_data.email)
    new_user= User(
        email= user_data.email,
        password_hashed= hashed_password,
        first_name= user_data.first_name,
        auth_provider= AuthProviders.EMAIL,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # send the verification email 
    await send_verification_email(new_user.email, verification_token)

    return new_user

@router.post("/login", response_model=TokenResponse)
async def login(response: Response ,user_form: OAuth2PasswordRequestForm = Depends() ,  db: AsyncSession= Depends(get_db)):
    """
    Logs user in, returns access token and sets refresh token in cookie.
    """
    result = await db.execute(select(User).where(User.email == user_form.username))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )

    # check if the user account is locked 
    if user.account_lockout_expiry:
        if user.account_lockout_expiry > datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_423_LOCKED,
                                detail=f"Account locked until {user.account_lockout_expiry.isoformat()}")
        user.failed_login_attempts = 0
        user.account_lockout_expiry = None

    if not verify_password(user_form.password, user.password_hashed) : 
        user.failed_login_attempts += 1
        # check for the number of login attempts to lock the user's account
        if user.failed_login_attempts >= 5:
            user.account_lockout_expiry = datetime.utcnow() + timedelta(hours=1)
            await db.commit()
            raise HTTPException(
                status_code= status.HTTP_403_FORBIDDEN,
                detail= "account locked"
            )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail= "Account not verified"
        )
    # reset the failed attemptes
    user.failed_login_attempts= 0
    user.last_login_at= datetime.utcnow()
    user.account_lockout_expiry = None
    
    access_token = await issue_tokens_and_set_cookie(user, response, db)

    # also generate a CSRF token and set cookie (double-submit pattern)
    csrf_token = csrf_protection.generate_csrf_token()
    csrf_protection.set_csrf_cookie(response, csrf_token)

    return TokenResponse(access_token=access_token, token_type="bearer")

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request:Request,response: Response, db : AsyncSession = Depends(get_db) ):
    """
        refresh the access token using the refresh token from cookie
    """
    # enforce CSRF for cookie auth action
    if not csrf_protection.verify_csrf_protection(request):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF validation failed")

    refresh_token= request.cookies.get("refresh_token")
    if not refresh_token: 
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "No refresh token provided. Please log in again."
        )
    
    try:
        # verify the token:
        payload = verify_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        if not user or not verify_hash_token(refresh_token, user.refresh_token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        # if everything is valid , generate an new access token and a new refresh token
        access_token = create_access_token(data={"sub": user.email})
        new_refresh_token = create_refresh_token(data={"sub": user.email})
        user.refresh_token = hash_token(new_refresh_token)
        await db.commit()

        set_refresh_token_cookie(response, new_refresh_token)

        return TokenResponse(
            access_token= access_token,
            token_type= "bearer" 
        )
    except Exception as e:
        # Clear invalid refresh token
        clear_refresh_cookie(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or expired refresh token. Please log in again."
        )

@router.post("/logout")
async def log_out(request: Request, response: Response, db: AsyncSession= Depends(get_db), user: User = Depends(get_current_user)):
    # CSRF verify for state-changing action
    if not csrf_protection.verify_csrf_protection(request):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF validation failed")
    user.refresh_token = None
    await db.commit()
    clear_refresh_cookie(response)
    return{
        "message": "logged out successfully "
    }


@router.get("/verify-account")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    try : 
        payload = jwt.decode(token, Settings.SECRET_KEY, algorithms=[Settings.ALGORITHM])
        if payload.get("type") != "verification" : 
            raise ValueError("Invalid token type")
        
        email = payload.get("sub")
        if not email:
            raise ValueError("Invalid token")
    except JWTError :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token")
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
  
    user.is_verified = True
    await db.commit()
    return RedirectResponse(f"http://localhost:3000/auth/verify-account?status=success")


@router.post("/password-reset-request")
async def password_reset_request (data: EmailSchema, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalars().first()
    if user:
        # Create a password reset token (JWT) that includes email and type
        reset_claims = {
            "sub": user.email,
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        raw_token = jwt.encode(reset_claims, Settings.SECRET_KEY, algorithm=Settings.ALGORITHM)
        user.password_reset_token = hash_token(raw_token)
        user.password_reset_expires_at = datetime.utcnow() + timedelta(hours=1)
        await db.commit()

        await send_password_verification_email(user.email, raw_token)
    
    return{
        "message": "If an account with that email exists, a password reset link has been sent."
    }

@router.post("/password-reset")
async def password_reset(data: PasswordReset, db: AsyncSession = Depends(get_db)):
    # Decode token to determine target user
    try:
        payload = jwt.decode(data.token, Settings.SECRET_KEY, algorithms=[Settings.ALGORITHM])
        if payload.get("type") != "password_reset":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token")
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user or not user.password_reset_token or not user.password_reset_expires_at or user.password_reset_expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")
    # Verify the provided token against stored bcrypt hash
    if not verify_hash_token(data.token, user.password_reset_token):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    user.password_hashed = hash_password(data.password)
    user.password_reset_token = None
    user.password_reset_expires_at = None
    await db.commit()
    return{
        "message" : "Password reset successfuly"
    }

@router.get("/google/login")
async def google_login():
    params = {
        "client_id": Settings.GOOGLE_CLIENT_ID,
        "redirect_uri": Settings.REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
    }
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return {"redirect_url": google_auth_url}


@router.get("/oauth/callback")
async def oauth_callback(
    code: str,
    provider: str,
    db: AsyncSession = Depends(get_db),
    response: Response = None,
):
    """handle OAuth callback and redirect user to frontend."""
    try:
        oauth_provider = get_provider(provider)
        # exchange the code for an access token
        user_data = await oauth_provider.get_user_info(code)

        email = user_data["email"]
        oauth_id = user_data["oauth_id"]
        first_name = user_data.get("first_name", "User")
        
        if provider == "google":
            auth_provider = AuthProviders.GOOGLE
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported provider")

        result = await db.execute(select(User).where(User.oauth_id == oauth_id))
        user = result.scalars().first()

        if not user:
            # check if the email exists with any provider, if it does link it to user account
            result = await db.execute(select(User).where(User.email == email))
            existing_user = result.scalars().first()

            if existing_user:
                existing_user.oauth_id = oauth_id
                existing_user.auth_provider = auth_provider
                existing_user.is_verified = True
                user = existing_user
                await db.commit()
            
            else:
                user = User(
                    email= email,
                    oauth_id= oauth_id,
                    auth_provider= auth_provider,
                    first_name= first_name,
                    is_verified= True
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)

        # create access token but not the refresh token yet
        # refresh token will be set by the setup-session endpoint
        access_token = create_access_token(data={"sub": user.email})
        
        # redirect to frontend with success
        frontend_url = "http://localhost:3000/auth/oauth/success"
        redirect_url = f"{frontend_url}?token={access_token}&user={urlencode({'email': user.email, 'first_name': user.first_name})}"
        
        return RedirectResponse(url=redirect_url, status_code=302)
        
    except Exception as e:
        # Redirect to frontend with error
        error_url = f"http://localhost:3000/auth/login?error={urlencode({'message': str(e)})}"
        return RedirectResponse(url=error_url, status_code=302)

@router.post("/setup-session")
async def setup_session(response: Response, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """
    setup session with refresh token cookie after OAuth login.
    """

    refresh_token = create_refresh_token(data={"sub": user.email})
    
    user.refresh_token = hash_token(refresh_token)
    await db.commit()
    
    set_refresh_token_cookie(response, refresh_token)
    
    csrf_token = csrf_protection.generate_csrf_token()
    csrf_protection.set_csrf_cookie(response, csrf_token)
    
    return {
        "message": "Session setup successful",
        "csrf_token": csrf_token
    }

@router.get("/csrf-token")
async def generate_csrf_token(requsest: Request, response: Response):
    csrf_token = csrf_protection.generate_csrf_token()
    csrf_protection.set_csrf_cookie(response, csrf_token)

    return{
        "csrf_token": csrf_token,
        "header_name": Settings.CSRF_HEADER_NAME
    }
        

