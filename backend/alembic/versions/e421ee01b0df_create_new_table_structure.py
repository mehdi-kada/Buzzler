"""create_new_table_structure

Revision ID: e421ee01b0df
Revises: 75e2aacb0ea8
Create Date: 2025-08-17 10:37:02.482226

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e421ee01b0df'
down_revision: Union[str, Sequence[str], None] = '75e2aacb0ea8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create new tables using raw SQL to avoid enum creation issues
    
    # Create users table
    op.execute("""
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hashed VARCHAR(255),
            auth_provider authproviders NOT NULL,
            oauth_id VARCHAR(255),
            last_login_at TIMESTAMPTZ,
            failed_login_attempts INTEGER NOT NULL DEFAULT 0,
            account_lockout_expiry TIMESTAMPTZ,
            first_name VARCHAR(255) NOT NULL,
            avatar_url VARCHAR(500),
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            is_verified BOOLEAN NOT NULL DEFAULT FALSE,
            email_verification_token VARCHAR,
            password_reset_token VARCHAR(255),
            password_reset_expires_at TIMESTAMPTZ,
            refresh_token VARCHAR(255),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """)
    
    # Create indexes for users
    op.execute("CREATE INDEX idx_auth_provider ON users (auth_provider, oauth_id);")
    op.execute("CREATE INDEX ix_users_email ON users (email);")
    op.execute("CREATE INDEX ix_users_oauth_id ON users (oauth_id);")
    op.execute("CREATE INDEX ix_users_password_hashed ON users (password_hashed);")
    
    # Create social_accounts table
    op.execute("""
        CREATE TABLE social_accounts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            platform socialplatform NOT NULL,
            platform_user_id VARCHAR(255) NOT NULL,
            username VARCHAR(255) NOT NULL,
            display_name VARCHAR(255),
            avatar_url VARCHAR(500),
            access_token TEXT NOT NULL,
            refresh_token TEXT,
            token_expires_at TIMESTAMPTZ,
            status accountstatus NOT NULL,
            last_health_check TIMESTAMPTZ,
            error_message TEXT,
            settings JSON,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE(user_id, platform_user_id, platform)
        );
    """)
    
    # Create indexes for social_accounts
    op.execute("CREATE INDEX idx_social_status ON social_accounts (status, last_health_check);")
    op.execute("CREATE INDEX idx_social_user_platform ON social_accounts (user_id, platform);")
    op.execute("CREATE INDEX ix_social_accounts_status ON social_accounts (status);")
    op.execute("CREATE INDEX ix_social_accounts_user_id ON social_accounts (user_id);")
    
    # Create videos table
    op.execute("""
        CREATE TABLE videos (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            source videosource NOT NULL,
            original_filename VARCHAR(255) NOT NULL,
            file_size_bytes INTEGER,
            mime_type VARCHAR(100),
            file_extension VARCHAR(10),
            azure_file_path VARCHAR(512) UNIQUE,
            azure_video_url TEXT,
            azure_audio_url TEXT,
            upload_url TEXT,
            upload_expires_at TIMESTAMPTZ,
            status videostatus NOT NULL,
            duration_seconds FLOAT,
            resolution_width INTEGER,
            resolution_height INTEGER,
            error_message TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            upload_completed_at TIMESTAMPTZ,
            processing_completed_at TIMESTAMPTZ
        );
    """)
    
    # Create indexes for videos
    op.execute("CREATE INDEX idx_videos_status_created ON videos (status, created_at);")
    op.execute("CREATE INDEX ix_videos_status ON videos (status);")
    op.execute("CREATE INDEX ix_videos_user_id ON videos (user_id);")
    
    # Create file_storages table
    op.execute("""
        CREATE TABLE file_storages (
            id SERIAL PRIMARY KEY,
            file_path VARCHAR(500) NOT NULL UNIQUE,
            file_name VARCHAR(255) NOT NULL,
            file_type filetype NOT NULL,
            mime_type VARCHAR(100),
            file_size INTEGER NOT NULL,
            storage_provider VARCHAR(50) NOT NULL,
            storage_bucket VARCHAR(100),
            entity_type entitytype NOT NULL,
            entity_id INTEGER NOT NULL,
            is_temporary BOOLEAN NOT NULL,
            expires_at TIMESTAMPTZ,
            is_deleted BOOLEAN NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """)
    
    # Create indexes for file_storages
    op.execute("CREATE INDEX idx_file_cleanup ON file_storages (is_temporary, expires_at);")
    op.execute("CREATE INDEX idx_file_entity ON file_storages (entity_type, entity_id);")
    op.execute("CREATE INDEX idx_file_storage_stats ON file_storages (storage_provider, file_type, created_at);")
    op.execute("CREATE INDEX ix_file_storages_entity_id ON file_storages (entity_id);")
    op.execute("CREATE INDEX ix_file_storages_entity_type ON file_storages (entity_type);")
    op.execute("CREATE INDEX ix_file_storages_expires_at ON file_storages (expires_at);")
    op.execute("CREATE INDEX ix_file_storages_file_type ON file_storages (file_type);")
    op.execute("CREATE INDEX ix_file_storages_is_deleted ON file_storages (is_deleted);")
    op.execute("CREATE INDEX ix_file_storages_is_temporary ON file_storages (is_temporary);")
    
    # Create clips table
    op.execute("""
        CREATE TABLE clips (
            id SERIAL PRIMARY KEY,
            video_id INTEGER NOT NULL REFERENCES videos(id),
            start_time INTEGER NOT NULL,
            end_time INTEGER NOT NULL,
            format clipformat NOT NULL,
            file_path VARCHAR(500),
            file_size INTEGER,
            thumbnail_url VARCHAR(500),
            title VARCHAR(500),
            description TEXT,
            transcript JSON,
            ai_score INTEGER,
            ai_reasoning TEXT,
            status clipstatus NOT NULL,
            error_message TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """)
    
    # Create indexes for clips
    op.execute("CREATE INDEX idx_clip_score_format ON clips (ai_score, format);")
    op.execute("CREATE INDEX idx_clip_video_status ON clips (video_id, status);")
    op.execute("CREATE INDEX ix_clips_status ON clips (status);")
    op.execute("CREATE INDEX ix_clips_video_id ON clips (video_id);")
    
    # Create posts table
    op.execute("""
        CREATE TABLE posts (
            id SERIAL PRIMARY KEY,
            clip_id INTEGER REFERENCES clips(id),
            account_id INTEGER NOT NULL REFERENCES social_accounts(id),
            content TEXT NOT NULL,
            hashtags JSON,
            media_urls JSON,
            status poststatus NOT NULL,
            scheduled_at TIMESTAMPTZ,
            published_at TIMESTAMPTZ,
            platform_post_id VARCHAR(255),
            platform_url VARCHAR(1000),
            error_message TEXT,
            retry_count INTEGER NOT NULL,
            views INTEGER NOT NULL,
            likes INTEGER NOT NULL,
            shares INTEGER NOT NULL,
            comments INTEGER NOT NULL,
            engagement_rate FLOAT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            last_analytics_update TIMESTAMPTZ
        );
    """)
    
    # Create indexes for posts
    op.execute("CREATE INDEX idx_post_account_status ON posts (account_id, status);")
    op.execute("CREATE INDEX idx_post_performance ON posts (published_at, engagement_rate);")
    op.execute("CREATE INDEX idx_post_scheduled ON posts (status, scheduled_at);")
    op.execute("CREATE INDEX ix_posts_account_id ON posts (account_id);")
    op.execute("CREATE INDEX ix_posts_clip_id ON posts (clip_id);")
    op.execute("CREATE INDEX ix_posts_scheduled_at ON posts (scheduled_at);")
    op.execute("CREATE INDEX ix_posts_status ON posts (status);")

    # Update existing table foreign keys to point to new tables
    op.drop_constraint('ai_insights_user_id_fkey', 'ai_insights', type_='foreignkey')
    op.create_foreign_key(None, 'ai_insights', 'users', ['user_id'], ['id'])
    
    op.drop_constraint('analytics_data_account_id_fkey', 'analytics_data', type_='foreignkey')
    op.drop_constraint('analytics_data_post_id_fkey', 'analytics_data', type_='foreignkey')
    op.create_foreign_key(None, 'analytics_data', 'posts', ['post_id'], ['id'])
    op.create_foreign_key(None, 'analytics_data', 'social_accounts', ['account_id'], ['id'])
    
    op.drop_constraint('audit_logs_user_id_fkey', 'audit_logs', type_='foreignkey')
    op.create_foreign_key(None, 'audit_logs', 'users', ['user_id'], ['id'])
    
    op.drop_constraint('content_templates_user_id_fkey', 'content_templates', type_='foreignkey')
    op.create_foreign_key(None, 'content_templates', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop new tables
    op.drop_table('posts')
    op.drop_table('clips')
    op.drop_table('file_storages')
    op.drop_table('videos')
    op.drop_table('social_accounts')
    op.drop_table('users')
    
    # Restore old foreign keys (this would need to be implemented based on original schema)
    pass
