from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from app.core.config import settings
import jwt


# Клиент должен отправить имя пользователя и пароль POST-запросом по адресу `/login`, чтобы получить токен доступа
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.JWT_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES



class JWT:
    @staticmethod
    def create_jwt_token(data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def get_user_from_token(token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload.get("sub")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token is out of date")  # Токен просрочен
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Authorization error")  # Невалидный токен

# class PasswordManager:
#     def __init__(self):
#         self.pwd_context = CryptContext(
#             schemes=["bcrypt"],
#             deprecated="auto"
#         )
#     def hash_pass(self, password) -> str:
#         return self.pwd_context.hash(password)
#
#     def verify_pass(self, password, hashed_password) -> bool:
#         return self.pwd_context.verify(password, hashed_password)