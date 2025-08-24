from app.database.database import async_session

async def get_db():
    async with async_session() as db:
        try:
            yield db
        except Exception:
            await db.rollback()
            raise
        finally:
            await db.close()