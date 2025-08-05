import time
from collections import defaultdict, deque
from typing import Dict, Deque
from fastapi import HTTPException, Request, status

class RateLimiter:
    def __init__(self):
        # Store request times per IP
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)
    
    def is_allowed(self, request: Request, max_requests: int = 5, window_seconds: int = 300) -> bool:
        """
        Default: 5 requests per 5 minutes for login attempts
        """
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Clean old requests outside the window
        request_times = self.requests[client_ip]
        while request_times and request_times[0] < current_time - window_seconds:
            request_times.popleft()
        
        # Check if limit exceeded
        if len(request_times) >= max_requests:
            return False
        
        # Add current request
        request_times.append(current_time)
        return True
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP, considering reverse proxy headers"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

# Global instance
rate_limiter = RateLimiter()

def check_rate_limit(request: Request, max_requests: int = 5, window_seconds: int = 300):
    """Dependency to check rate limiting"""
    if not rate_limiter.is_allowed(request, max_requests, window_seconds):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )
