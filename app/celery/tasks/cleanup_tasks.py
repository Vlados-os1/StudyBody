from datetime import datetime, timezone, timedelta
from sqlalchemy import delete, select


from app.database.database import async_session
from app.models.token import BlackListToken
from app.models.user import UserOrm
from app.celery.celery_config import celery_app

@celery_app.task
def cleanup_expired_blacklist_tokens():
    import asyncio
    asyncio.run(_cleanup_blacklist())


@celery_app.task
def cleanup_expired_unconfirmed_users():
    import asyncio
    asyncio.run(_cleanup_users())


async def _cleanup_blacklist():
    async with async_session() as db:
        now = datetime.now(timezone.utc)
        await db.execute(
            delete(BlackListToken).where(BlackListToken.expire < now)
        )

        await db.commit()


async def _cleanup_users():
    async with async_session() as db:
        threshold_time = datetime.now(timezone.utc) - timedelta(hours=2)
        await db.execute(
            delete(UserOrm).where(UserOrm.is_active == False, UserOrm.created_at < threshold_time)
        )

        await db.commit()
