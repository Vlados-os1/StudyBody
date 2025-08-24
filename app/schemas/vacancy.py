from pydantic import BaseModel, UUID4, field_validator
from datetime import datetime
import uuid

from app.schemas.user import UserBase


class VacancyBase(BaseModel):
    title: str
    description: str | None = None
    tags: str | None = None
    created_at: datetime
    updated_at: datetime

class Vacancy(VacancyBase):
    id: UUID4

    @field_validator("id", mode="before")
    @classmethod
    def convert_to_str(cls, v):
        return str(v) if v else v

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

class UserVacancyResponse(VacancyBase):
    id: UUID4

    model_config = {
        "from_attributes": True
    }

    @field_validator("id", mode="before")
    @classmethod
    def convert_to_str(cls, v):
        return str(v) if v else v

class VacancyResponse(UserVacancyResponse):
    user: UserBase

    model_config = {
        "from_attributes": True
    }