from app.core.database import async_session


async def get_db():
    db = async_session()
    try:
        yield db
    finally:
        await db.close()