from pydantic import BaseModel
from app.models.user import UserDepartment


class User(BaseModel):
    telegram_id: int
    department: UserDepartment | None = None
    interests: str | None = None

class UserCharacteristics(BaseModel):
    department: UserDepartment | None = None
    interests: str | None = None