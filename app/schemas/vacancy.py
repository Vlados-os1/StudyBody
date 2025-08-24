from pydantic import BaseModel, UUID4, field_validator
from datetime import datetime
import uuid

from app.schemas.user import UserBase


class VacancyBase(BaseModel):
    title: str
    description: str | None = None
    tags: str | None = None

class VacancyCreate(BaseModel):
    title: str
    description: str | None = None
    tags: str | None = None

    model_config = {
        "from_attributes": True
    }

class VacancyUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    tags: str | None = None

    model_config = {
        "from_attributes": True
    }

class VacancyResponse(VacancyBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    user: UserBase

    @field_validator("id", mode="before")
    @classmethod
    def convert_to_str(cls, v):
        return str(v) if v else v

    model_config = {
        "from_attributes": True
    }