from celery import Celery
from app.config import Settings


celery_app = Celery(
    "buzzler",
    broker=Settings.REDIS_URL,
    backend=Settings.REDIRECT_URI,
    incude=["app.celery.audio_processing", "app.celery.video_processing", "app.celery.cleanup"]
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    
    task_routes={
        'app.celery.audio_processing.*': {'queue': 'audio_processing'},
        'app.celery.video_processing.*': {'queue': 'video_processing'},
        'app.celery.cleanup.*': {'queue': 'cleanup'},
    },
    
    worker_prefetched_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=100,
    
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,  # 10 minutes
    
    beat_schedule={
        'cleanup_temp_files': {
            'task': 'app.celery.cleanup.cleanup_temp_files',
            'schedule': 1800.0,  # Every hour
            'args': (),
        },
        'cleanup_orphaned_files': {
            'task': 'app.celery.cleanup.cleanup_orphaned_files',
            'schedule': 3600.0,  # Every day
            'args': (),
        },
    }
)

celery_app.autodiscover_tasks()