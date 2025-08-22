from typing import Any
from fastapi import HTTPException, status

class BaseAPIException(HTTPException):
    def __init__(self, status_code: int, detail: Any, error_code: str):
        super().__init__(
            status_code=status_code,
            detail={"message": detail, "error_code": error_code}
        )

class BadRequestException(BaseAPIException):
    def __init__(self, detail: Any = "Bad request"):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, "BAD_REQUEST")

class AuthFailedException(BaseAPIException):
    def __init__(self, detail: Any = "Authentication failed"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, "AUTHENTICATION_FAILED")

class AuthTokenExpiredException(BaseAPIException):
    def __init__(self, detail: Any = "Expired token"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, "TOKEN_EXPIRED")

class NotFoundException(BaseAPIException):
    def __init__(self, detail: Any = "Not found"):
        super().__init__(status.HTTP_404_NOT_FOUND, detail, "NOT_FOUND")

class ForbiddenException(BaseAPIException):
    def __init__(self, detail: Any = "Forbidden"):
        super().__init__(status.HTTP_403_FORBIDDEN, detail, "FORBIDDEN")
