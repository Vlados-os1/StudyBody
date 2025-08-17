from celery import Celery
from app.core.configs.config import settings


celery_app = Celery(
    main="email_service",
    broker=settings.redis_url,
    backend=settings.redis_url
)


celery_app.autodiscover_tasks(['app.celery.tasks.mail_tasks'])


celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    result_expires=3600,
)
