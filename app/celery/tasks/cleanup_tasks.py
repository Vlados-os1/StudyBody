from datetime import datetime, timezone
from sqlalchemy import delete
from app.core.database import async_session
from app.models.token import BlackListToken

from app.celery.celery_config import celery_app

@celery_app.task
def cleanup_expired_blacklist_tokens():
    import asyncio
    asyncio.run(_cleanup())

async def _cleanup():
    async with async_session() as db:
        now = datetime.now(timezone.utc)
        await db.execute(
            delete(BlackListToken).where(BlackListToken.expire < now)
        )
        await db.commit()
