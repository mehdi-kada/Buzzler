"""Enum definitions used across the application.

Note:
- The classes in this module are Python Enum types used throughout the models.
- The string values for enum members are intentionally preserved (they are the persisted/serialized
  representations used in the database). Do NOT change the string values without creating the
  appropriate database migrations and updating existing data.
- This module uses direct `Enum` imports and consistent class bases to make usage clearer in models.
"""

from enum import Enum

class AuthProviders(Enum):
    EMAIL = "EMAIL"
    GOOGLE = "GOOGLE"
    X = "X"

class UserPlan(Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"

class SocialPlatform(Enum):
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"
    YOUTUBE_SHORTS = "youtube"

class AccountStatus(Enum):
    CONNECTED = "connected"
    EXPIRED = "expired"
    REVOKED = "revoked"
    ERROR = "error"

class TemplateType(Enum):
    POST_TEMPLATE = "post_template"
    HASHTAG_SET = "hashtag_set"
    CONTENT_SERIES = "content_series"
    CAMPAIGN = "campaign"

class ClipFormat(Enum):
    VERTICAL_9_16 = "9:16"
    SQUARE_1_1 = "1:1"
    HORIZONTAL_16_9 = "16:9"

class ClipStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"

class PostStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"

class VideoSource(Enum):
    UPLOAD = "upload"
    URL_IMPORT = "url_import"

class VideoStatus(Enum):
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    READY = "ready"
    FAILED = "failed"
    PENDING_UPLOAD = "pending_upload"

class ActionType(Enum):
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    VIDEO_UPLOAD = "video_upload"
    CLIP_GENERATED = "clip_generated"
    POST_PUBLISHED = "post_published"
    ACCOUNT_CONNECTED = "account_connected"
    SETTINGS_CHANGED = "settings_changed"
    FILE_DOWNLOADED = "file_downloaded"

class InsightType(Enum):
    BEST_POSTING_TIME = "best_posting_time"
    TRENDING_TOPICS = "trending_topics"
    VIRAL_PREDICTION = "viral_prediction"
    AUDIENCE_PREFERENCE = "audience_preference"
    CONTENT_OPTIMIZATION = "content_optimization"

class AnalyticsType(Enum):
    POST_PERFORMANCE = "post_performance"
    ACCOUNT_GROWTH = "account_growth"
    ENGAGEMENT_TRENDS = "engagement_trends"
    AUDIENCE_INSIGHTS = "audience_insights"

class EntityType(Enum):
    VIDEO = "video"
    CLIP = "clip"
    USER_AVATAR = "user_avatar"
    POST = "post"
    TRANSCRIPT = "transcript"

class FileType(Enum):
    VIDEO = "video"
    THUMBNAIL = "thumbnail"
    AUDIO = "audio"
    TRANSCRIPT = "transcript"
    EXPORT = "export"
