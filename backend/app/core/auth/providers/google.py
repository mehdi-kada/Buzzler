from fastapi import HTTPException, status
from httpx import AsyncClient
from app.core.config import Settings
from app.core.auth.providers.base import OAuthProvider

class GoogleProvider(OAuthProvider):
    def __init__(self):
        self.client_id = Settings.GOOGLE_CLIENT_ID
        self.client_secret = Settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = Settings.REDIRECT_URI
        self.token_url = "https://oauth2.googleapis.com/token"
        self.user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"

    async def get_user_info(self, code: str) -> dict:
        async with AsyncClient() as client:
            token_response = await client.post(
                self.token_url,
                data={
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            
            token_data = token_response.json()
            if "error" in token_data:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"OAuth error: {token_data.get('error_description')}")

            access_token = token_data.get("access_token")
            if not access_token:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not retrieve access token.")

            user_info_response = await client.get(
                self.user_info_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user_data = user_info_response.json()

            return {
                "email": user_data.get("email"),
                "oauth_id": user_data.get("id"),
                "first_name": user_data.get("given_name", "User"),
            }
