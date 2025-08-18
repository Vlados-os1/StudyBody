from fastapi import APIRouter, HTTPException, Depends, Response, Cookie
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from datetime import datetime, timezone
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

import app.schemas.user as schemas_user
import app.schemas.mail as schemas_mail
import app.models.user as models_user
import app.models.token as models_token
from app.dependencies import get_db
from app.core.security import get_password_hash, verify_password
from app.celery.tasks.mail_tasks import user_mail_event
from app.exceptions.httpex import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.core.jwt import (
    create_token_pair,
    refresh_token_state,
    decode_access_token,
    mail_token,
    add_refresh_token_cookie,
    SUB,
    JTI,
    EXP,
)


# Клиент должен отправить имя пользователя и пароль POST-запросом по адресу `api/login`, чтобы получить токен доступа
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")


router_auth = APIRouter()


@router_auth.post("/api/register", response_model=schemas_user.User)
async def register(
    data: schemas_user.UserRegister,
    db: AsyncSession = Depends(get_db),
):
    user = await models_user.UserOrm.find_by_email(db=db, email=data.email)
    if user:
        raise HTTPException(status_code=400, detail="Email has already registered")


    user_data = data.model_dump(exclude={"confirm_password"})
    user_data["password"] = get_password_hash(user_data["password"])


    user = models_user.UserOrm(**user_data)
    user.is_active = False
    await user.save(db=db)

    # send verify email
    user_schema = schemas_user.User.model_validate(user, from_attributes=True)
    verify_token = mail_token(user_schema)

    user_mail_event.delay(
        token=verify_token,
        recipients=[str(user_schema.email)]
    )

    return user_schema


@router_auth.post("/api/resend-verification", response_model=schemas_user.SuccessResponseScheme)
async def resend_verification(
        data: schemas_user.ForgotPasswordSchema,
        db: AsyncSession = Depends(get_db)
):
    user = await models_user.UserOrm.find_by_email(db=db, email=data.email)
    if not user:
        return {"msg": "If you have an account, check your email."}
    if user.is_active:
        return {"msg": "Account already activated."}

    user_schema = schemas_user.User.model_validate(user, from_attributes=True)
    verify_token = mail_token(user_schema)

    user_mail_event.delay(
        token=verify_token,
        recipients=[str(user_schema.email)]
    )

    return {"msg": "Verification email sent, check your inbox."}


@router_auth.post("/api/login")
async def login(
    data: schemas_user.UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user = await models_user.UserOrm.authenticate(
        db=db, email=data.email, password=data.password
    )

    if not user:
        raise BadRequestException(detail="Incorrect email or password")

    if not user.is_active:
        raise ForbiddenException()

    user = schemas_user.User.model_validate(user, from_attributes=True)

    token_pair = create_token_pair(user=user)

    add_refresh_token_cookie(response=response, token=token_pair.refresh.token)

    return {"token": token_pair.access.token}


@router_auth.post("/api/refresh")
async def refresh(
        response: Response,
        refresh: Annotated[str | None, Cookie()] = None,
        db: AsyncSession = Depends(get_db)
):
    if not refresh:
        raise BadRequestException(detail="refresh token required")

    token_pair = await refresh_token_state(refresh, db)

    add_refresh_token_cookie(response=response, token=token_pair.refresh.token)

    return {"token": token_pair.access.token}


@router_auth.get("/api/verify", response_model=schemas_user.SuccessResponseScheme)
async def verify(
        token: str,
        db: AsyncSession = Depends(get_db)
):
    payload = await decode_access_token(token=token, db=db)
    user = await models_user.UserOrm.find_by_id(db=db, id=payload[SUB])
    if not user:
        raise NotFoundException(detail="User not found")

    user.is_active = True
    await user.save(db=db)
    return {"msg": "Successfully activated"}


@router_auth.post("/api/logout", response_model=schemas_user.SuccessResponseScheme)
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
):
    payload = await decode_access_token(token=token, db=db)
    jti = payload[JTI]
    expire = datetime.fromtimestamp(payload[EXP], tz=timezone.utc)

    black_listed = models_token.BlackListToken(
        id=jti,
        expire=expire
    )
    await black_listed.save(db=db)

    return {"msg": "Succesfully logout"}


@router_auth.post("/api/forgot-password", response_model=schemas_user.SuccessResponseScheme)
async def forgot_password(
    data: schemas_user.ForgotPasswordSchema,
    db: AsyncSession = Depends(get_db),
):
    user = await models_user.UserOrm.find_by_email(db=db, email=data.email)
    if user:
        user_schema = schemas_user.User.model_validate(user, from_attributes=True)
        reset_token = mail_token(user_schema)

        user_mail_event.delay(
            token=reset_token,
            recipients=[str(user_schema.email)]
        )

    return {"msg": "Reset token sent successfully, check your email"}


@router_auth.post("/password-reset", response_model=schemas_user.SuccessResponseScheme)
async def password_reset_token(
    token: str,
    data: schemas_user.PasswordResetSchema,
    db: AsyncSession = Depends(get_db),
):
    payload = await decode_access_token(token=token, db=db)
    user = await models_user.UserOrm.find_by_id(db=db, id=payload[SUB])
    if not user:
        raise NotFoundException(detail="User not found")

    user.password = get_password_hash(data.password)
    await user.save(db=db)

    return {"msg": "Password succesfully updated"}


@router_auth.post("/api/password-update", response_model=schemas_user.SuccessResponseScheme)
async def password_update(
    token: Annotated[str, Depends(oauth2_scheme)],
    data: schemas_user.PasswordUpdateSchema,
    db: AsyncSession = Depends(get_db),
):
    payload = await decode_access_token(token=token, db=db)
    user = await models_user.UserOrm.find_by_id(db=db, id=payload[SUB])
    if not user:
        raise NotFoundException(detail="User not found")

    # raise Validation error
    if not verify_password(data.old_password, user.password):
        try:
            schemas_user.OldPasswordErrorSchema(old_password=False)
        except ValidationError as e:
            raise RequestValidationError(e.errors())
    user.password = get_password_hash(data.password)
    await user.save(db=db)

    return {"msg": "Successfully updated"}
