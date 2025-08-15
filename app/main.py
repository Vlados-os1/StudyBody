from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db, drop_db
from app.api.users import router_user
from app.api.auth import router_auth


@asynccontextmanager
async def lifespan(app_: FastAPI):
    await init_db()
    yield
    await drop_db()

app = FastAPI(title="StudyBody", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],        # Разрешить все источники
    allow_credentials=True,     # Разрешить передавать куки и заголовки авторизации
    allow_methods=["*"],        # Разрешить все HTTP-методы (GET, POST, и т.д.)
    allow_headers=["*"],        # Разрешить все заголовки
)

app.include_router(router_user)
app.include_router(router_auth)
