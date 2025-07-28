from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


async_engine = create_async_engine(
    url=settings.DATA_URL_asyncpg,
    echo=False,
    # poll_size=5,
    # max_overflow=10,
)

async_session = async_sessionmaker(
    async_engine, expire_on_commit=False
)

class Base(DeclarativeBase):
    def __repr__(self):
        cols = []
        for col in self.__table__.columns.keys():
            cols.append(f"{col}={getattr(self, col)}")
        return f"<{self.__class__.__name__} {','.join(cols)}>"

async def drop_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def create_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def init_db():
    await drop_db()
    await create_db()