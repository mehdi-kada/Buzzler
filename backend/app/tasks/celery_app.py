from app.config import Settings
from celery import Celery
import logging

logger = logging.getLogger(__name__)

# Instantiate settings (assumes Settings is a pydantic BaseSettings-style class or similar)
settings = Settings()

celery_app = Celery(
    'buzzler_upload',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        'app.tasks.upload_tasks',
        'app.tasks.cleanup_tasks',
    ],
)

celery_app.conf.update(
    # Serialization
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],

    # Timezone
    timezone='UTC',
    enable_utc=True,

    # Task routing
    task_routes={
        'upload.*': {'queue': 'upload'},
        'cleanup.*': {'queue': 'cleanup'},
    },

    # Worker settings
    worker_max_tasks_per_child=100,
    worker_prefetch_multiplier=1,
    task_acks_late=True,

    # Task settings (timeouts)
    task_soft_time_limit=1800,  # 30 minutes soft limit
    task_time_limit=3600,       # 60 minutes hard limit
    task_reject_on_worker_lost=True,

    # Retry settings
    task_default_retry_delay=60,
    task_max_retries=5,

    # Result settings
    result_expires=3600,  # 1 hour

    # Beat scheduler for cleanup tasks
    beat_schedule={
        'cleanup-temp-files': {
            'task': 'app.tasks.cleanup_tasks.cleanup_temp_files',
            'schedule': 1800.0,  # every 30 minutes
        },
        'cleanup-orphaned-records': {
            'task': 'app.tasks.cleanup_tasks.cleanup_orphaned_records',
            'schedule': 3600.0,  # every hour
        },
    },
)

# Optional detailed logging format controlled by settings
if getattr(settings, 'ENABLE_DETAILED_LOGGING', False):
    celery_app.conf.update(
        worker_log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        worker_task_log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

logger.info("Celery app initialized with settings: %s", {
    'broker': settings.REDIS_URL,
    'backend': settings.REDIS_URL,
    'task_routes': celery_app.conf.get('task_routes'),
    'beat_schedule_keys': list(celery_app.conf.get('beat_schedule', {}).keys()),
})

__all__ = ('celery_app',)
