from app.core.database import async_session

async def get_db():
    async with async_session() as db:
        try:
            yield db
        except:
            await db.rollback()
            raise
