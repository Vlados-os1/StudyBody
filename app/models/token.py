from app.database.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import TIMESTAMP
from datetime import datetime
from app.utils import utcnow
import uuid


class BlackListToken(Base):
    __tablename__ = "blacklisttokens"
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, index=True, default=uuid.uuid4
    )
    expire: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=utcnow()
    )