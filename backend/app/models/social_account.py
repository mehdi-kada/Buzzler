from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON, String, Integer, DateTime, Enum, Text, ForeignKey, Index, UniqueConstraint, func
import enum

from app.db.database import Base



class SocialPlatform(enum.Enum):
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"
    YOUTUBE_SHORTS = "youtube"

class AccountStatus(enum.Enum):
    CONNECTED = "connected"
    EXPIRED = "expired"        
    REVOKED = "revoked"       
    ERROR = "error"            



class SocialAccount(Base):
    """
        connects social media accounts with Oauth2 tokens
        supports multiple social media accounts per user
    """

    __tablename__ = "social_account"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False, index=True)

    # platform details 
    platform: Mapped[SocialPlatform] = mapped_column(Enum(SocialPlatform), nullable=False)
    platform_user_id: Mapped[str] = mapped_column(String(255), nullable=False)    # Platform's user ID
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # OAuth credentials 
    access_token: Mapped[str] = mapped_column(Text, nullable=False)               
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)               
    token_expires_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # account status and health
    status: Mapped[AccountStatus] = mapped_column(Enum(AccountStatus), default=AccountStatus.CONNECTED, index=True)
    last_health_check: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  


    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now())


    user : Mapped["User"] = relationship("User", back_populates="social_accounts")
    posts : Mapped[list["Post"]] = relationship("Post", back_populates="account")


    __table_args__ = (
        Index('idx_social_user_platform', 'user_id', 'platform'),
        Index('idx_social_status', 'status', 'last_health_check'),
        # unique constraint: one account per platform per user
        UniqueConstraint("user_id", "platform_user_id", "platform", name="uq_user_platform_account"),
    )

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.post import Post
    from app.models.user import User