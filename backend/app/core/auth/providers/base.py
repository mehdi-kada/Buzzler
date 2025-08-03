from abc import ABC, abstractmethod

class OAuthProvider(ABC):
    @abstractmethod
    async def get_user_info(self, code: str) -> dict:
        """
        Exchange the authorization code for an access token and get user info.
        """
        pass
