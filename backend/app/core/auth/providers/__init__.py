from fastapi import HTTPException, status
from .base import OAuthProvider
from .google import GoogleProvider

PROVIDER_MAP = {
    "google": GoogleProvider(),
}

def get_provider(provider_name: str) -> OAuthProvider:
    provider = PROVIDER_MAP.get(provider_name)
    if not provider:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported provider")
    return provider
