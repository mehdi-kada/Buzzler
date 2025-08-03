import enum

class AuthProviders(enum.Enum):
    EMAIL = "EMAIL"
    GOOGLE = "GOOGLE"
    X = "X"

class UserPlan(enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"

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

class TemplateType(enum.Enum):
    POST_TEMPLATE = "post_template"
    HASHTAG_SET = "hashtag_set"
    CONTENT_SERIES = "content_series"
    CAMPAIGN = "campaign"

class ClipFormat(enum.Enum):
    VERTICAL_9_16 = "9:16"
    SQUARE_1_1 = "1:1"
    HORIZONTAL_16_9 = "16:9"

class ClipStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"

class PostStatus(enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"

class VideoSource(enum.Enum):
    UPLOAD = "upload"
    URL_IMPORT  = "url_import"

class VideoStatus(enum.Enum):
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    READY = "ready"
    FAILED = "failed"

class ProjectStatus(enum.Enum):
    DRAFT = "draft"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"

class ActionType(enum.Enum):
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    VIDEO_UPLOAD = "video_upload"
    CLIP_GENERATED = "clip_generated"
    POST_PUBLISHED = "post_published"
    ACCOUNT_CONNECTED = "account_connected"
    SETTINGS_CHANGED = "settings_changed"
    FILE_DOWNLOADED = "file_downloaded"

class InsightType(enum.Enum):
    BEST_POSTING_TIME = "best_posting_time"
    TRENDING_TOPICS = "trending_topics"
    VIRAL_PREDICTION = "viral_prediction"
    AUDIENCE_PREFERENCE = "audience_preference"
    CONTENT_OPTIMIZATION = "content_optimization"

class AnalyticsType(enum.Enum):
    POST_PERFORMANCE = "post_performance"
    ACCOUNT_GROWTH = "account_growth"
    ENGAGEMENT_TRENDS = "engagement_trends"
    AUDIENCE_INSIGHTS = "audience_insights"

class EntityType(enum.Enum):
    VIDEO = "video"
    CLIP = "clip"
    USER_AVATAR = "user_avatar"
    POST = "post"
    TRANSCRIPT = "transcript"

class FileType(enum.Enum):
    VIDEO = "video"
    THUMBNAIL = "thumbnail"
    AUDIO = "audio"
    TRANSCRIPT = "transcript"
    EXPORT = "export"
