from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Response, Cookie
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

import app.schemas.user as schemas_user
from app.api.auth import oauth2_scheme
from app.dependencies import get_db
from app.core.database import async_session
import app.models.user as models_user
from app.exceptions.httpex import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.core.jwt import (
    create_token_pair,
    decode_access_token,
    mail_token,
    add_refresh_token_cookie,
    SUB,
    JTI,
    EXP,
)


router_user = APIRouter()

@router_user.get("/api/main")
async def profile(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
):
    payload = await decode_access_token(token=token, db=db)
    user = await models_user.UserOrm.find_by_id(db=db, id=payload[SUB])
    if not user:
        raise NotFoundException(detail="User not found")

    return {"email": user.email, "full_name": user.full_name, "department": user.department, "interests": user.interests}

@router_user.patch("/api/main/update")
async def update_profile(
    token: Annotated[str, Depends(oauth2_scheme)],
    data: schemas_user.UserStudentFacts,
    db: AsyncSession = Depends(get_db),
):
    payload = await decode_access_token(token=token, db=db)
    user = await models_user.UserOrm.find_by_id(db=db, id=payload[SUB])
    if not user:
        raise NotFoundException(detail="User not found")

    user_data = data.model_dump(exclude_unset=True)
    for field, value in user_data.items():
        setattr(user, field, value)

    await user.save(db=db)

    return {
        "email": user.email,
        "full_name": user.full_name,
        "department": user.department,
        "interests": user.interests,
    }
