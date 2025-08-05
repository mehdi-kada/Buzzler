
import secrets
import time
from typing import Optional
from fastapi import Request, Response
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.core.config import Settings


class CSRFProtection:
    def __init__(self):
        self.serializer = URLSafeTimedSerializer(
            Settings.CSRF_SECRET_KEY,
            salt="csrf-token"
        )
        self.token_expire_seconds = Settings.CSRF_TOKEN_EXPIRE_MINUTES * 60
    
    def generate_csrf_token(self) -> str:
        """Generate a new CSRF token"""
        # Create a token with current timestamp
        token_data = {
            "random": secrets.token_urlsafe(32),
            "timestamp": int(time.time())
        }
        return self.serializer.dumps(token_data)
    
    def validate_csrf_token(self, token: str) -> bool:
        try:
            self.serializer.loads(token, max_age=self.token_expire_seconds)
            return True
        except (BadSignature, SignatureExpired):
            return False
    
    def set_csrf_cookie(self, response: Response, token: str) -> None:
        """Set CSRF token as a cookie"""
        response.set_cookie(
            key=Settings.CSRF_COOKIE_NAME,
            value=token,
            max_age=self.token_expire_seconds,
            secure=Settings.SECURE_COOKIES,  # HTTPS only in production
            httponly=False,  # Must be False so JavaScript can read it
            samesite=Settings.COOKIE_SAMESITE,
            domain=Settings.COOKIE_DOMAIN 
        )

    def get_csrf_token_from_cookie(self, request: Request) -> Optional[str]:
        """Get CSRF token from cookie"""
        return request.cookies.get(Settings.CSRF_COOKIE_NAME)

    def get_csrf_token_from_header(self, request: Request) -> Optional[str]:
        """Get CSRF token from header"""
        return request.headers.get(Settings.CSRF_HEADER_NAME)

    def verify_csrf_protection(self, request: Request) -> bool:
        """Verify CSRF protection for a request"""
        # Get tokens from cookie and header
        cookie_token = self.get_csrf_token_from_cookie(request)
        header_token = self.get_csrf_token_from_header(request)

        if not cookie_token or not header_token:
            return False

        if not self.validate_csrf_token(cookie_token) or not self.validate_csrf_token(header_token):
            return False

        # double-submit pattern
        return cookie_token == header_token

# Global instance
csrf_protection = CSRFProtection()
