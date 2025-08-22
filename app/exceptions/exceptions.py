from typing import Any
from fastapi import HTTPException, status

class BaseAPIException(HTTPException):
    def __init__(self, status_code: int, detail: Any, error_code: str):
        super().__init__(
            status_code=status_code,
            detail={"message": detail, "error_code": error_code}
        )

class BadRequestException(BaseAPIException):
    def __init__(self, detail: Any = "Некорректный запрос"):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, "BAD_REQUEST")

class ValidationErrorException(BaseAPIException):
    def __init__(self, detail: Any = "Ошибка валидации данных"):
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, detail, "VALIDATION_ERROR")

class AuthFailedException(BaseAPIException):
    def __init__(self, detail: Any = "Неверный email или пароль"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, "AUTHENTICATION_FAILED")

class AuthTokenExpiredException(BaseAPIException):
    def __init__(self, detail: Any = "Срок действия токена истёк"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, "TOKEN_EXPIRED")

class NotFoundException(BaseAPIException):
    def __init__(self, detail: Any = "Объект не найден"):
        super().__init__(status.HTTP_404_NOT_FOUND, detail, "NOT_FOUND")

class ForbiddenException(BaseAPIException):
    def __init__(self, detail: Any = "Доступ запрещён"):
        super().__init__(status.HTTP_403_FORBIDDEN, detail, "FORBIDDEN")

# Специфичные ошибки для регистрации и пользователей

class UserAlreadyExistsException(BaseAPIException):
    def __init__(self, detail: Any = "Пользователь с таким email уже зарегистрирован"):
        super().__init__(status.HTTP_409_CONFLICT, detail, "USER_ALREADY_EXISTS")

class UserNotActiveException(BaseAPIException):
    def __init__(self, detail: Any = "Аккаунт не активирован. Проверьте почту для подтверждения"):
        super().__init__(status.HTTP_403_FORBIDDEN, detail, "ACCOUNT_NOT_ACTIVE")

class PasswordMismatchException(BaseAPIException):
    def __init__(self, detail: Any = "Пароли не совпадают"):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, "PASSWORD_MISMATCH")

class OldPasswordIncorrectException(BaseAPIException):
    def __init__(self, detail: Any = "Старый пароль неверен"):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, "OLD_PASSWORD_INCORRECT")

class EmailSendErrorException(BaseAPIException):
    def __init__(self, detail: Any = "Ошибка отправки письма. Попробуйте позже"):
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, detail, "EMAIL_SEND_ERROR")

class ResetTokenInvalidException(BaseAPIException):
    def __init__(self, detail: Any = "Недействительный или просроченный токен сброса пароля"):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, "RESET_TOKEN_INVALID")

class RateLimitExceededException(BaseAPIException):
    def __init__(self, detail: Any = "Превышено количество запросов. Попробуйте позже"):
        super().__init__(status.HTTP_429_TOO_MANY_REQUESTS, detail, "RATE_LIMIT_EXCEEDED")
