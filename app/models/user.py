from sqlalchemy import Text, select, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, selectinload, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid
import enum

from app.utils import utcnow
from app.database.database import Base
from app.core.security import verify_password


# id_type = Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]


class UserDepartment(enum.Enum):
    iu = "ИУ"
    mt = "МТ"
    ibm = "ИБМ"
    sm = "СМ"
    fn = "ФН"
    bmt = "БМТ"
    rk = "РК"
    rl = "РЛ"
    energy = "Э"
    ur = "ЮР"
    sgn = "СГН"
    ling = "Л"


class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    is_active: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=utcnow())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=utcnow(), server_onupdate=utcnow(), onupdate=utcnow()
    )

    department: Mapped[UserDepartment | None] = mapped_column(
        Enum(UserDepartment, name="userdepartment", create_type=False), nullable=True
    )

    interests: Mapped[str | None] = mapped_column(Text, nullable=True)

    vacancies: Mapped[list["VacancyOrm"]] = relationship("VacancyOrm", back_populates="user",
                                                         cascade="all, delete-orphan")


    @classmethod
    async def find_by_email(cls, db: AsyncSession, email: str):
        query = select(cls).where(cls.email == email)
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def authenticate(cls, db: AsyncSession, email: str, password: str):
        user = await cls.find_by_email(db=db, email=email)
        if not user or not verify_password(password, user.password):
            return False
        return user