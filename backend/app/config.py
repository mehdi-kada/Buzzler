from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

class Settings:
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))
    CSRF_SECRET_KEY: str = os.getenv("CSRF_SECRET_KEY", "your-csrf-secret-key-change-in-production")
    CSRF_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("CSRF_TOKEN_EXPIRE_MINUTES", "60"))
    CSRF_COOKIE_NAME: str = "csrf_token"
    CSRF_HEADER_NAME: str = "X-CSRF-Token"
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # Email settings
    SMTP_HOST: str = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL")
    
    # OAuth settings
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
    X_CLIENT_ID: str = os.getenv("X_CLIENT_ID")
    X_CLIENT_SECRET: str = os.getenv("X_CLIENT_SECRET")
    REDIRECT_URI: str = os.getenv("REDIRECT_URI")
    
    # Cookie settings
    COOKIE_DOMAIN: str = os.getenv("COOKIE_DOMAIN", None)
    SECURE_COOKIES: bool = os.getenv("ENVIRONMENT", "development") == "production"
    COOKIE_SAMESITE: str = "lax"
    
    # URL settings
    BACKEND_URL: str = os.getenv("BACKEND_URL")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL")
    
    # Verification settings
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = int(os.getenv("VERIFICATION_TOKEN_EXPIRE_HOURS", "24"))
    
    # Redis settings
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Video processing settings
    # Temporary storage settings
    TEMP_BASE_DIR: Path = Path(os.getenv('TEMP_BASE_DIR', '/tmp/buzzler'))
    MAX_TEMP_STORAGE_GB: float = float(os.getenv('MAX_TEMP_STORAGE_GB', '20'))
    TEMP_FILE_TTL_HOURS: int = int(os.getenv('TEMP_FILE_TTL_HOURS', '4'))
    
    # Video upload settings
    MAX_VIDEO_SIZE_MB: int = int(os.getenv('MAX_VIDEO_SIZE_MB', '1000'))
    MAX_CONCURRENT_UPLOADS: int = int(os.getenv('MAX_CONCURRENT_UPLOADS', '10'))
    ALLOWED_VIDEO_FORMATS: list = ['mp4', 'mov', 'avi', 'mkv', 'webm', 'flv']
    ALLOWED_MIME_TYPES: list = [
        'video/mp4', 'video/quicktime', 'video/x-msvideo', 
        'video/x-matroska', 'video/webm', 'video/x-flv'
    ]
    
    # Azure storage settings
    AZURE_STORAGE_CONNECTION_STRING: str = os.getenv('AZURE_STORAGE_CONNECTION_STRING', '')
    AZURE_CONTAINER_NAME: str = os.getenv('AZURE_CONTAINER_NAME', 'buzzler-videos')
    AZURE_UPLOAD_TIMEOUT: int = int(os.getenv('AZURE_UPLOAD_TIMEOUT', '300'))
    
    # Audio processing settings
    FFMPEG_PATH: str = os.getenv('FFMPEG_PATH', 'ffmpeg')
    FFPROBE_PATH: str = os.getenv('FFPROBE_PATH', 'ffprobe')
    AUDIO_BITRATE: str = os.getenv('AUDIO_BITRATE', '128k')
    AUDIO_SAMPLE_RATE: str = os.getenv('AUDIO_SAMPLE_RATE', '44100')
    
    # Logging settings
    ENABLE_DETAILED_LOGGING: bool = os.getenv('ENABLE_DETAILED_LOGGING', 'false').lower() == 'true'
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

settings = Settings()

# Create necessary directories
settings.TEMP_BASE_DIR.mkdir(parents=True, exist_ok=True)
(settings.TEMP_BASE_DIR / "videos").mkdir(exist_ok=True)
(settings.TEMP_BASE_DIR / "audio").mkdir(exist_ok=True)
(settings.TEMP_BASE_DIR / "processing").mkdir(exist_ok=True)