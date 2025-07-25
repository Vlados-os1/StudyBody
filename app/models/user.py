from app.core.database import Base, async_engine, async_session
from sqlalchemy import BigInteger, String, Text, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from typing import Annotated
import uuid
import enum
import asyncio


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

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    telegram_id = mapped_column(BigInteger, unique=True)
    department: Mapped[UserDepartment | None]
    interests: Mapped[str | None] = mapped_column(Text)
