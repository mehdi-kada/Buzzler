from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security.csrf import csrf_protection

class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.safe_methods = {"GET", "HEAD", "OPTIONS", "TRACE"}
        self.exempt_paths = {
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/auth/oauth/callback",  
            "/auth/csrf-token",      
            "/auth/refresh",         
            "/auth/setup-session",  
            "/health",               
        }

        self.exempt_patterns = [
            "/auth/oauth/",  
        ]

    async def dispatch(self, request: Request, call_next):
        if request.method in self.safe_methods: 
            response = await call_next(request)
            return response

        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            response = await call_next(request)
            return response

        if not csrf_protection.verify_csrf_protection(request):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "CSRF token missing or invalid"}
            )
        
        response = await call_next(request)
        return response