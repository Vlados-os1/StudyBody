from sqlalchemy import select

from app.core.database import async_session
from app.models.user import UserOrm, UserDepartment
from app.schemas.user import UserCharacteristics


async def get_user(tg_id: int):
    async with async_session() as session:
        stmt = select(UserOrm).where(UserOrm.telegram_id == tg_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        return user

async def add_user(tg_id: int, characteristics: UserCharacteristics):
    user = await get_user(tg_id)
    if user:
        return user

    async with async_session() as session:
        new_user = UserOrm(telegram_id=tg_id, department=characteristics.department, interests=characteristics.interests)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

async def change_user_data(tg_id: int, characteristics: UserCharacteristics):
    async with async_session() as session:
        stmt = select(UserOrm).where(UserOrm.telegram_id == tg_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return None

        if characteristics.department is not None:
            user.department = characteristics.department
        if characteristics.interests is not None:
            user.interests = characteristics.interests
        await session.commit()
        await session.refresh(user)

        return user

# async def main():
#     await init_db()
#     result = await add_user(123, interests="Я люблю морковь")
#     print(result)
#     await change_user_data(123, new_interests="Я не люблю морковь")
#     result = await add_user(123)
#     print(result)
#
# if __name__ == "__main__":
#     asyncio.run(main())