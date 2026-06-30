"""
Celery application configuration.
"""
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "ai_document_analyzer",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks.document"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_annotations={
        "app.workers.tasks.document.process_document": {"rate_limit": "10/m"}
    },
    beat_schedule={
        "cleanup-expired-sessions": {
            "task": "app.workers.tasks.document.cleanup_sessions",
            "schedule": crontab(hour=3, minute=0),
        },
        "retry-failed-documents": {
            "task": "app.workers.tasks.document.retry_failed_documents",
            "schedule": crontab(minute="*/30"),
        }
    }
)

# Make tasks available
from app.workers.tasks import document