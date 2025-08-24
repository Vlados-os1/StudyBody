from fastapi import APIRouter, Depends
from typing import Annotated, List
from sqlalchemy.ext.asyncio import AsyncSession

import app.schemas.user as schemas_user
import app.schemas.vacancy as schemas_vacancy
from app.api.auth import oauth2_scheme
from app.dependencies import get_db
import app.models.user as models_user
import app.models.vacancy as models_vacancy
from app.exceptions.exceptions import NotFoundException, ForbiddenException
from app.core.jwt import decode_access_token, SUB

router_vacancies = APIRouter()


@router_vacancies.get("/api/vacancies", response_model=List[schemas_vacancy.VacancyResponse])
async def get_all_vacancies(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: AsyncSession = Depends(get_db),
):
    payload = await decode_access_token(token=token, db=db)
    user = await models_user.UserOrm.find_by_id(db=db, id=payload[SUB])
    if not user:
        raise NotFoundException(detail="User not found")

    vacancies = await models_vacancy.VacancyOrm.get_all(db=db)

    return vacancies


@router_vacancies.get("/api/main/vacancies", response_model=List[schemas_vacancy.VacancyResponse])
async def get_my_vacancies(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: AsyncSession = Depends(get_db),
):
    payload = await decode_access_token(token=token, db=db)
    user = await models_user.UserOrm.find_by_id(db=db, id=payload[SUB])
    if not user:
        raise NotFoundException(detail="User not found")

    vacancies = await models_vacancy.VacancyOrm.get_by_user_id(db=db, user_id=payload[SUB])

    vacancies_schema = [schemas_vacancy.VacancyResponse.model_validate(vacancy, from_attributes=True) for vacancy in vacancies]

    return vacancies_schema


@router_vacancies.get("/api/vacancy", response_model=schemas_vacancy.VacancyResponse)
async def get_vacancy(
        token: Annotated[str, Depends(oauth2_scheme)],
        vacancy_id: str,
        db: AsyncSession = Depends(get_db),
):
    payload = await decode_access_token(token=token, db=db)
    user = await models_user.UserOrm.find_by_id(db=db, id=payload[SUB])
    if not user:
        raise NotFoundException(detail="User not found")

    vacancy = await models_vacancy.VacancyOrm.find_by_id(db=db, id=vacancy_id)
    if not vacancy:
        raise NotFoundException(detail="Vacancy not found")

    vacancy_schema = schemas_vacancy.VacancyResponse.model_validate(vacancy, from_attributes=True)

    return vacancy_schema


@router_vacancies.post("/api/main/create_vacancy", response_model=schemas_vacancy.VacancyResponse)
async def create_vacancy(
        token: Annotated[str, Depends(oauth2_scheme)],
        data: schemas_vacancy.VacancyCreate,
        db: AsyncSession = Depends(get_db),
):
    payload = await decode_access_token(token=token, db=db)
    user = await models_user.UserOrm.find_by_id(db=db, id=payload[SUB])
    if not user:
        raise NotFoundException(detail="User not found")

    vacancy_data = data.model_dump()
    vacancy_data['user_id'] = user.id
    vacancy = models_vacancy.VacancyOrm(**vacancy_data)
    await vacancy.save(db=db)

    vacancy_schema = schemas_vacancy.VacancyResponse.model_validate(vacancy, from_attributes=True)
    return vacancy_schema


@router_vacancies.patch("/api/main/update_vacancy/{vacancy_id}", response_model=schemas_user.SuccessResponseScheme)
async def update_vacancy(
        vacancy_id: str,
        data: schemas_vacancy.VacancyUpdate,
        token: Annotated[str, Depends(oauth2_scheme)],
        db: AsyncSession = Depends(get_db),
):
    payload = await decode_access_token(token=token, db=db)
    user = await models_user.UserOrm.find_by_id(db=db, id=payload[SUB])
    if not user:
        raise NotFoundException(detail="User not found")

    vacancy = await models_vacancy.VacancyOrm.find_by_id(db=db, id=vacancy_id)
    if not vacancy:
        raise NotFoundException(detail="Vacancy not found")

    if str(vacancy.user_id) != str(user.id):
        raise ForbiddenException(detail="You can only edit your own vacancies")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vacancy, field, value)

    await vacancy.save(db=db)

    return {"msg": "Vacancy successfully updated"}


@router_vacancies.delete("/api/delete_vacancy/{vacancy_id}", response_model=schemas_user.SuccessResponseScheme)
async def delete_vacancy(
        vacancy_id: str,
        token: Annotated[str, Depends(oauth2_scheme)],
        db: AsyncSession = Depends(get_db),
):
    payload = await decode_access_token(token=token, db=db)
    user = await models_user.UserOrm.find_by_id(db=db, id=payload[SUB])
    if not user:
        raise NotFoundException(detail="User not found")

    vacancy = await models_vacancy.VacancyOrm.find_by_id(db=db, id=vacancy_id)
    if not vacancy:
        raise NotFoundException(detail="Vacancy not found")

    if str(vacancy.user_id) != str(user.id):
        raise ForbiddenException(detail="You can only delete your own vacancies")

    await db.delete(vacancy)
    await db.commit()

    return {"msg": "Vacancy successfully deleted"}