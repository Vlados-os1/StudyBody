from pydantic import BaseModel, UUID4, field_validator, EmailStr
from app.models.user import UserDepartment


class UserStudentFacts(BaseModel):
    department: UserDepartment | None = None
    interests: str | None = None


class UserBase(UserStudentFacts):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: UUID4

    model_config = {
        "from_attributes": True
    }

    @field_validator("id", mode="before")
    @classmethod
    def convert_to_str(cls, v):
        return str(v) if v else v


class UserRegister(UserBase):
    password: str
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def verify_password_match(cls, v, info):
        password = info.data.get("password")
        if v != password:
            raise ValueError("The two passwords did not match.")

        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class PasswordResetSchema(BaseModel):
    password: str
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def verify_password_match(cls, v, info):
        password = info.data.get("password")
        if v != password:
            raise ValueError("The two passwords did not match.")
        return v


class PasswordUpdateSchema(PasswordResetSchema):
    old_password: str


class OldPasswordErrorSchema(BaseModel):
    old_password: bool

    @field_validator("old_password")
    @classmethod
    def check_old_password_status(cls, v):
        if not v:
            raise ValueError("Old password is not correct")
        return v


class SuccessResponseScheme(BaseModel):
    msg: str