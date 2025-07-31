from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Boolean, Enum, Text, Index
from sqlalchemy.sql import func
import enum

from app.db.database import Base


class AuthProviders(enum.Enum):
    EMAIL = "email"
    GOOGLE = "google"
    X = "twitter"

class UserPlan(enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"

class User(Base):
    """
        core user table , stores all related user information 
    """
    __tablename__ = "user"

    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Auth related fields
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hashed : Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)  # null for auth users
    auth_provider : Mapped[AuthProviders] = mapped_column(Enum(AuthProviders), nullable=False, default=AuthProviders.EMAIL)
    oauth_id : Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)    # external OAuth ID
    last_login_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    refresh_token : Mapped[str] = mapped_column(String(255), nullable=True)  # For token refresh
    password_reset_expires_at: Mapped[Optional[DateTime]] =  mapped_column(DateTime(timezone=True),nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)

    # user info
    first_name : Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url : Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # account status 
    is_active : Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified : Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_verification_token : Mapped[Optional[str]] = mapped_column(String, nullable=False)
    password_reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    created_at : Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at : Mapped[DateTime] = mapped_column(DateTime(timezone=True),server_default=func.now(), onupdate=func.now())

    projects : Mapped[list["Project"]] = relationship("Project", back_populates="user")
    social_accounts: Mapped[list["SocialAccount"]] = relationship("SocialAccount", back_populates="user")
    templates: Mapped[list["ContentTemplate"]] = relationship("ContentTemplate", back_populates="user")

    __table_args__ = (
        Index('idx_auth_provider', "auth_provider", "oauth_id"),
    )


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.social_account import SocialAccount
    from app.models.content_template import ContentTemplate