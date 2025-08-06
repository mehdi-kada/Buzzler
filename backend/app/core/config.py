from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SMTP_HOST: str = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL")
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
    X_CLIENT_ID: str = os.getenv("X_CLIENT_ID")
    X_CLIENT_SECRET: str = os.getenv("X_CLIENT_SECRET")
    REDIRECT_URI: str = os.getenv("REDIRECT_URI")
    COOKIE_DOMAIN: str = os.getenv("COOKIE_DOMAIN", None)
    CSRF_SECRET_KEY: str = os.getenv("CSRF_SECRET_KEY", "your-csrf-secret-key-change-in-production")
    CSRF_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("CSRF_TOKEN_EXPIRE_MINUTES", "60"))
    CSRF_COOKIE_NAME: str = "csrf_token"
    CSRF_HEADER_NAME: str = "X-CSRF-Token"
    SECURE_COOKIES: bool = os.getenv("ENVIRONMENT", "development") == "production"
    COOKIE_SAMESITE: str = "lax"  
    BACKEND_URL: str = os.getenv("BACKEND_URL")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL")
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = os.getenv("VERIFICATION_TOKEN_EXPIRE_HOURS")
settings = Settings()