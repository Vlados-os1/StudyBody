from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'cleanup-blacklist-tokens': {
        'task': 'app.celery.tasks.cleanup_tasks.cleanup_expired_blacklist_tokens',
        'schedule': crontab(hour=0, minute=0),
    },
}
