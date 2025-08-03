from app.models.enums import ActionType
from app.db.database import Base

class AuditLog(Base):

    __tablename__ = 'audit_logs'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=True, index=True)  # Null for system actions

    action: Mapped[ActionType] = mapped_column(Enum(ActionType), nullable=False, index=True)
    resource_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)    # video, clip, post, etc.
    resource_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    description: Mapped[str] = mapped_column(Text, nullable=False)
    log_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)                          # JSON with additional context

    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True, index=True)      # IPv4/IPv6
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    user : Mapped["User"] = relationship("User")

    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action', 'created_at'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_time_action', 'created_at', 'action'),
    )