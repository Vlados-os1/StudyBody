from datetime import timedelta, datetime, timezone
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
import uuid

from app.core.configs.config import settings
from app.schemas.jwt import JwtTokenSchema, TokenPair
from app.schemas.user import User
from app.models.token import BlackListToken
from app.models.user import UserOrm
from app.exceptions.httpex import AuthFailedException


REFRESH_COOKIE_NAME = "refresh"
SUB = "sub"
EXP = "exp"
IAT = "iat"
JTI = "jti"

SECRET_KEY = settings.JWT_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRES_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRES_MINUTES =settings.REFRESH_TOKEN_EXPIRES_MINUTES


def _get_utc_now():
    current_utc_time = datetime.now(timezone.utc)
    return current_utc_time


def _create_access_token(payload: dict, minutes: int | None = None) -> JwtTokenSchema:
    expire = _get_utc_now() + timedelta(
        minutes=minutes or ACCESS_TOKEN_EXPIRES_MINUTES
    )

    payload[EXP] = expire

    token = JwtTokenSchema(
        token=jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM),
        payload=payload,
        expire=expire,
    )

    return token

def _create_refresh_token(payload: dict) -> JwtTokenSchema:
    expire = _get_utc_now() + timedelta(minutes=REFRESH_TOKEN_EXPIRES_MINUTES)

    payload[EXP] = expire

    token = JwtTokenSchema(
        token=jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM),
        expire=expire,
        payload=payload,
    )

    return token

def create_token_pair(user: User) -> TokenPair:
    payload = {SUB: str(user.id), JTI: str(uuid.uuid4()), IAT: _get_utc_now()}

    return TokenPair(
        access=_create_access_token(payload={**payload}),
        refresh=_create_refresh_token(payload={**payload}),
    )


async def decode_access_token(token: str, db: AsyncSession):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload[JTI]
        black_list_token = await BlackListToken.find_by_id(db=db, id=jti)
        if black_list_token and black_list_token.expire > datetime.now(timezone.utc):
            raise JWTError("Token is blacklisted")
    except JWTError:
        raise AuthFailedException()

    return payload


async def refresh_token_state(
        token: str,
        db: AsyncSession,

):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload["jti"]
        user_id = payload["sub"]
        exp = payload["exp"]
    except JWTError as ex:
        print(str(ex))
        raise AuthFailedException()

    blacklisted = await BlackListToken.find_by_id(db, jti)
    if blacklisted:
        raise AuthFailedException()

    expire = datetime.fromtimestamp(exp, timezone.utc)
    db.add(BlackListToken(id=jti, expire=expire))
    await db.commit()

    user = await UserOrm.find_by_id(db=db, id=user_id)
    if user is None:
        raise AuthFailedException()
    user = User.model_validate(user, from_attributes=True)
    token_pair = create_token_pair(user=user)

    return token_pair


def mail_token(user: User):
    """Return 2 hour lifetime access_token"""
    payload = {SUB: str(user.id), JTI: str(uuid.uuid4()), IAT: _get_utc_now()}
    return _create_access_token(payload=payload, minutes=2 * 60).token


def add_refresh_token_cookie(response: Response, token: str):
    exp = _get_utc_now() + timedelta(minutes=REFRESH_TOKEN_EXPIRES_MINUTES)
    exp.replace(tzinfo=timezone.utc)

    response.set_cookie(
        key="refresh",
        value=token,
        expires=int(exp.timestamp()),
        httponly=True,
    )

# secure=True,
# samesite='strict'