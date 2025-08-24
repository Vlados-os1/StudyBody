from sqlalchemy import Text, String, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, selectinload, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid

from app.database.database import Base
from app.models.user import UserOrm
from app.utils import utcnow


class VacancyOrm(Base):
    __tablename__ = "vacancies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=utcnow())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=utcnow(), server_onupdate=utcnow(), onupdate=utcnow()
    )

    user: Mapped["UserOrm"] = relationship("UserOrm", back_populates="vacancies")


    @classmethod
    async def get_all(cls, db: AsyncSession):
        query = select(cls).options(selectinload(cls.user))
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_user_id(cls, db: AsyncSession, user_id: str):
        query = select(cls).options(selectinload(cls.user)).where(cls.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_id_with_user(cls, db: AsyncSession, vacancy_id: uuid.UUID):
        query = select(cls).options(selectinload(cls.user)).where(cls.id == vacancy_id)
        result = await db.execute(query)
        return result.scalars().first()


