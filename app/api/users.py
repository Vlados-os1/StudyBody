from fastapi import APIRouter, Request

from app.services.user_service import add_user, change_user_data
from app.schemas.user import UserCharacteristics

router_user = APIRouter()

@router_user.get("/api/main/{tg_id}")
async def profile(tg_id: int, characteristics: UserCharacteristics):
    user = await add_user(tg_id, characteristics)
    return {'User': user}

@router_user.get("/api/main/change/{tg_id}")
async def change_profile(tg_id: int, characteristics: UserCharacteristics):
    user = await change_user_data(tg_id, characteristics)
    return {'Changed user': user}