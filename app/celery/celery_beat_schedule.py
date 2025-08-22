from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'cleanup-blacklist-tokens': {
        'task': 'app.celery.tasks.cleanup_tasks.cleanup_expired_blacklist_tokens',
        'schedule': crontab(hour=0, minute=0),
    },
    'delete_expired_unconfirmed_users_every_30min': {
        'task': 'app.celery.tasks.cleanup_tasks.cleanup_expired_unconfirmed_users',
        'schedule': 1800.0,  # каждые 30 минут
    },
}