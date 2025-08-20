from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.users import router_user
from app.api.auth import router_auth


app = FastAPI(title="StudyBody")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],        # Разрешить все источники
    allow_credentials=True,     # Разрешить передавать куки и заголовки авторизации
    allow_methods=["*"],        # Разрешить все HTTP-методы (GET, POST, и т.д.)
    allow_headers=["*"],        # Разрешить все заголовки
)

app.include_router(router_user)
app.include_router(router_auth)