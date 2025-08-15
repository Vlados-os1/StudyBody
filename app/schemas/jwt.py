from pydantic import BaseModel, UUID4
from datetime import datetime


class JwtTokenSchema(BaseModel):
    token: str
    payload: dict
    expire: datetime


class TokenPair(BaseModel):
    access: JwtTokenSchema
    refresh: JwtTokenSchema

class RefreshToken(BaseModel):
    refresh: str


class BlackListToken(BaseModel):
    id: UUID4
    expire: datetime

    model_config = {
        "from_attributes": True
    }