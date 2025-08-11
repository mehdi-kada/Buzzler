
import secrets
import time
from typing import Optional
from fastapi import Request, Response
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.core.config import Settings


class CSRFProtection:
    """
        class to implement double cookie submit to ensure CSRF security 
        token is set in a non httponly cookie to be accessed by js to be sent back to be accessed by the frontend and sent back in the headers
        the browser will automatically send the csrf cookie back
        server would compare the csrf token in the cookie and header 
    """
    def __init__(self):
        self.serializer = URLSafeTimedSerializer(
            Settings.CSRF_SECRET_KEY,
            salt="csrf-token"
        )
        self.token_expire_seconds = Settings.CSRF_TOKEN_EXPIRE_MINUTES * 60
    
    def generate_csrf_token(self) -> str:
        token_data = {
            "random": secrets.token_urlsafe(32),
            "timestamp": int(time.time())
        }
        return self.serializer.dumps(token_data)
    
    def validate_csrf_token(self, token: str) -> bool:
        try:
            token_data = self.serializer.loads(token, max_age=self.token_expire_seconds)
            current_time = int(time.time())
            token_timestamp = token_data.get("timestamp", 0)
            if current_time - token_timestamp > self.token_expire_seconds:
                return False
            return True
        except (BadSignature, SignatureExpired):
            return False
    
    def set_csrf_cookie(self, response: Response, token: str) -> None:
        response.set_cookie(
            key=Settings.CSRF_COOKIE_NAME,
            value=token,
            max_age=self.token_expire_seconds,
            secure=Settings.SECURE_COOKIES,  
            httponly=False,  
            samesite=Settings.COOKIE_SAMESITE,
            domain=Settings.COOKIE_DOMAIN 
        )

    def get_csrf_token_from_cookie(self, request: Request) -> Optional[str]:
        return request.cookies.get(Settings.CSRF_COOKIE_NAME)

    def get_csrf_token_from_header(self, request: Request) -> Optional[str]:
        return request.headers.get(Settings.CSRF_HEADER_NAME)

    def verify_csrf_protection(self, request: Request) -> bool:
        cookie_token = self.get_csrf_token_from_cookie(request)
        header_token = self.get_csrf_token_from_header(request)

        if not cookie_token or not header_token:
            return False

        if not self.validate_csrf_token(cookie_token) or not self.validate_csrf_token(header_token):
            return False

        # double-submit pattern
        return cookie_token == header_token


csrf_protection = CSRFProtection()
